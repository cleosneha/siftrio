import secrets
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.email.sender import sender
from src.exceptions.base import BaseAPIException
from src.models.member_invitation import (
    InvitationStatus,
    ResourceType,
)
from src.repositories.auth_repository import AuthRepository
from src.repositories.member_invitation_repository import MemberInvitationRepository
from src.repositories.client_member_repository import ClientMemberRepository
from src.repositories.project_member_repository import ProjectMemberRepository
from src.repositories.workspace_member_repository import WorkspaceMemberRepository
from src.repositories.project_repository import ProjectRepository
from src.repositories.client_repository import ClientRepository
from src.repositories.workspace_repository import WorkspaceRepository
from src.schemas.member_invitation_schema import InvitationResponse, PendingInvitationItem


INVITATION_EXPIRY_DAYS = 7


class InvitationService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.invitation_repo = MemberInvitationRepository(db)
        self.auth_repo = AuthRepository(db)
        self.ws_member_repo = WorkspaceMemberRepository(db)
        self.client_member_repo = ClientMemberRepository(db)
        self.project_member_repo = ProjectMemberRepository(db)
        self.ws_repo = WorkspaceRepository(db)
        self.client_repo = ClientRepository(db)
        self.project_repo = ProjectRepository(db)

    async def invite(
        self,
        email: str,
        resource_type: ResourceType,
        resource_id: UUID,
        invited_by: UUID,
    ) -> dict:
        user = await self.auth_repo.get_user_by_email(email)
        if user is None:
            raise BaseAPIException(
                message="User is not registered in the application.",
                status_code=400,
            )

        existing_member = await self._check_existing_member(resource_type, resource_id, user.id)
        if existing_member:
            raise BaseAPIException(
                message=f"User is already a member of this {resource_type.value}",
                status_code=409,
            )

        existing = await self.invitation_repo.get_pending_by_email_and_resource(
            email, resource_type, resource_id
        )
        if existing is not None:
            if existing.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
                existing.status = InvitationStatus.EXPIRED
                await self.db.flush()
            else:
                raise BaseAPIException(
                    message="An invitation has already been sent to this user.",
                    status_code=409,
                )

        token = secrets.token_urlsafe(48)
        expires_at = datetime.now(timezone.utc) + timedelta(days=INVITATION_EXPIRY_DAYS)

        invitation = await self.invitation_repo.create(
            email=email,
            user_id=user.id,
            resource_type=resource_type,
            resource_id=resource_id,
            invited_by=invited_by,
            token=token,
            expires_at=expires_at,
        )

        await self.db.commit()

        resource_name = await self._get_resource_name(resource_type, resource_id)
        inviter = await self.auth_repo.get_user_by_id(invited_by)
        inviter_name = inviter.full_name if inviter else "Someone"

        accept_url = f"{settings.FRONTEND_URL}/invitations/accept?token={token}"

        await sender.send(
            to_email=email,
            subject=f"You're invited to join {resource_name}",
            html_body=self._render_html(inviter_name, resource_name, resource_type.value, accept_url, expires_at),
            text_body=self._render_text(inviter_name, resource_name, resource_type.value, accept_url, expires_at),
        )

        return InvitationResponse.model_validate(invitation).model_dump()

    async def accept(self, token: str, user_id: UUID) -> dict:
        invitation = await self.invitation_repo.get_by_token(token)
        if invitation is None:
            raise BaseAPIException(
                message="Invalid invitation token.",
                status_code=404,
            )

        if invitation.status == InvitationStatus.ACCEPTED:
            raise BaseAPIException(
                message="This invitation has already been accepted.",
                status_code=409,
            )

        if invitation.status == InvitationStatus.REVOKED:
            raise BaseAPIException(
                message="This invitation has been revoked.",
                status_code=410,
            )

        if invitation.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
            invitation.status = InvitationStatus.EXPIRED
            await self.db.flush()
            raise BaseAPIException(
                message="This invitation has expired.",
                status_code=410,
            )

        now = datetime.now(timezone.utc)

        if invitation.resource_type == ResourceType.WORKSPACE:
            await self._accept_workspace(invitation.resource_id, user_id)
        elif invitation.resource_type == ResourceType.CLIENT:
            await self._accept_client(invitation.resource_id, user_id)
        elif invitation.resource_type == ResourceType.PROJECT:
            await self._accept_project(invitation.resource_id, user_id)

        invitation.status = InvitationStatus.ACCEPTED
        invitation.accepted_at = now
        await self.db.flush()
        await self.db.commit()

        return InvitationResponse.model_validate(invitation).model_dump()

    async def _accept_workspace(self, workspace_id: UUID, user_id: UUID) -> None:
        existing = await self.ws_member_repo.get_by_user_and_workspace(workspace_id, user_id)
        if existing is None:
            await self.ws_member_repo.create(workspace_id, user_id)

    async def _accept_client(self, client_id: UUID, user_id: UUID) -> None:
        client = await self.client_repo.get_by_id(client_id)
        if client is None:
            raise BaseAPIException(message="Client not found.", status_code=404)

        await self._accept_workspace(client.workspace_id, user_id)

        existing = await self.client_member_repo.get_by_user_and_client(client_id, user_id)
        if existing is None:
            await self.client_member_repo.create(client_id, user_id)

    async def _accept_project(self, project_id: UUID, user_id: UUID) -> None:
        project = await self.project_repo.get_by_id(project_id)
        if project is None:
            raise BaseAPIException(message="Project not found.", status_code=404)

        client = await self.client_repo.get_by_id(project.client_id)
        if client is not None:
            await self._accept_workspace(client.workspace_id, user_id)
            await self._accept_client(project.client_id, user_id)

        existing = await self.project_member_repo.get_by_user_and_project(project_id, user_id)
        if existing is None:
            await self.project_member_repo.create(project_id, user_id)

    async def list_pending(self, resource_type: ResourceType, resource_id: UUID) -> list[dict]:
        invitations = await self.invitation_repo.get_by_resource(resource_type, resource_id)
        pending = [i for i in invitations if i.status == InvitationStatus.PENDING]
        return [PendingInvitationItem.model_validate(i).model_dump() for i in pending]

    async def _check_existing_member(
        self, resource_type: ResourceType, resource_id: UUID, user_id: UUID
    ) -> bool:
        if resource_type == ResourceType.WORKSPACE:
            return await self.ws_member_repo.get_by_user_and_workspace(resource_id, user_id) is not None
        if resource_type == ResourceType.CLIENT:
            return await self.client_member_repo.get_by_user_and_client(resource_id, user_id) is not None
        if resource_type == ResourceType.PROJECT:
            return await self.project_member_repo.get_by_user_and_project(resource_id, user_id) is not None
        return False

    async def _get_resource_name(self, resource_type: ResourceType, resource_id: UUID) -> str:
        if resource_type == ResourceType.WORKSPACE:
            ws = await self.ws_repo.get_by_id(resource_id)
            return ws.name if ws else "Workspace"
        if resource_type == ResourceType.CLIENT:
            client = await self.client_repo.get_by_id(resource_id)
            return client.name if client else "Client"
        if resource_type == ResourceType.PROJECT:
            project = await self.project_repo.get_by_id(resource_id)
            return project.name if project else "Project"
        return "Resource"

    def _render_html(self, inviter_name: str, resource_name: str, resource_type: str, accept_url: str, expires_at) -> str:
        from pathlib import Path

        template_path = Path(__file__).parent.parent / "email" / "templates" / "invitation.html"
        html = template_path.read_text(encoding="utf-8")
        html = html.replace("{{ inviter_name }}", inviter_name)
        html = html.replace("{{ resource_name }}", resource_name)
        html = html.replace("{{ resource_type }}", resource_type)
        html = html.replace("{{ accept_url }}", accept_url)
        html = html.replace("{{ expires_at }}", expires_at.strftime("%B %d, %Y"))
        return html

    def _render_text(self, inviter_name: str, resource_name: str, resource_type: str, accept_url: str, expires_at) -> str:
        from pathlib import Path

        template_path = Path(__file__).parent.parent / "email" / "templates" / "invitation.txt"
        text = template_path.read_text(encoding="utf-8")
        text = text.replace("{{ inviter_name }}", inviter_name)
        text = text.replace("{{ resource_name }}", resource_name)
        text = text.replace("{{ resource_type }}", resource_type)
        text = text.replace("{{ accept_url }}", accept_url)
        text = text.replace("{{ expires_at }}", expires_at.strftime("%B %d, %Y"))
        return text
