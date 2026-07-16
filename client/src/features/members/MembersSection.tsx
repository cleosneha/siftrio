"use client";
import { useState } from "react";
import { Plus, UserMinus, Mail } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { InviteMemberModal } from "./InviteMemberModal";
import type { Member, PendingInvitation } from "@/types";

interface MembersSectionProps {
  resourceType: "workspace" | "client" | "project";
  resourceId: string;
  members: Member[];
  pendingInvitations: PendingInvitation[];
  currentUserId?: string;
  onRemove?: (userId: string) => void;
  isLoading?: boolean;
}

export function MembersSection({
  resourceType,
  resourceId,
  members,
  pendingInvitations,
  currentUserId,
  onRemove,
  isLoading,
}: MembersSectionProps) {
  const [showInviteModal, setShowInviteModal] = useState(false);

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Members</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">Loading...</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <>
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg">Members</CardTitle>
            <Button size="xs" onClick={() => setShowInviteModal(true)}>
              <Plus className="h-3 w-3" />
              Invite
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {members.length === 0 && pendingInvitations.length === 0 ? (
            <p className="text-sm text-muted-foreground">No members yet.</p>
          ) : (
            <div className="space-y-2">
              {members.map((member) => (
                <div
                  key={member.user_id}
                  className="flex items-center justify-between rounded-md bg-muted/50 px-3 py-2"
                >
                  <div className="flex items-center gap-2 min-w-0">
                    <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary/10 text-xs font-medium text-primary">
                      {(member.full_name ?? member.email)?.[0]?.toUpperCase() ?? "?"}
                    </div>
                    <div className="min-w-0">
                      <p className="truncate text-sm font-medium">
                        {member.full_name || member.email}
                      </p>
                      {member.full_name && (
                        <p className="truncate text-xs text-muted-foreground">
                          {member.email}
                        </p>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    <span className="text-xs text-muted-foreground px-2">
                      {member.role}
                    </span>
                    {onRemove && member.user_id !== currentUserId && member.role !== "owner" && (
                      <Button
                        variant="ghost"
                        size="icon-xs"
                        onClick={() => onRemove(member.user_id)}
                      >
                        <UserMinus className="h-3 w-3" />
                      </Button>
                    )}
                  </div>
                </div>
              ))}
              {pendingInvitations.map((inv) => (
                <div
                  key={inv.id}
                  className="flex items-center justify-between rounded-md border border-dashed px-3 py-2 opacity-60"
                >
                  <div className="flex items-center gap-2 min-w-0">
                    <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-muted text-xs font-medium text-muted-foreground">
                      <Mail className="h-4 w-4" />
                    </div>
                    <div className="min-w-0">
                      <p className="truncate text-sm">{inv.email}</p>
                      <p className="text-xs text-muted-foreground">Pending invitation</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
      <InviteMemberModal
        open={showInviteModal}
        onClose={() => setShowInviteModal(false)}
        resourceType={resourceType}
        resourceId={resourceId}
      />
    </>
  );
}
