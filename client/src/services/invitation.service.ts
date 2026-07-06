import { api } from "@/lib/api";
import type { ApiResponse, Invitation, PendingInvitation } from "@/types";

export const invitationService = {
  async invite(resourceType: string, resourceId: string, email: string) {
    const res = await api.post<ApiResponse<Invitation>>(`/invitations?resource_type=${resourceType}&resource_id=${resourceId}`, { email });
    return res.data;
  },

  async listPending(resourceType: string, resourceId: string) {
    const res = await api.get<ApiResponse<PendingInvitation[]>>(`/invitations?resource_type=${resourceType}&resource_id=${resourceId}`);
    return res.data;
  },

  async accept(token: string) {
    const res = await api.post<ApiResponse<{ id: string }>>(`/invitations/accept/${token}`);
    return res.data;
  },
};
