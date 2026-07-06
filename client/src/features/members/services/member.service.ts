import { api } from "@/lib/api";
import type { ApiResponse, Member } from "@/types";

export const memberService = {
  async listWorkspaceMembers(workspaceId: string) {
    const res = await api.get<ApiResponse<Member[]>>(`/members/workspace/${workspaceId}`);
    return res.data;
  },

  async listClientMembers(clientId: string) {
    const res = await api.get<ApiResponse<Member[]>>(`/members/client/${clientId}`);
    return res.data;
  },

  async listProjectMembers(projectId: string) {
    const res = await api.get<ApiResponse<Member[]>>(`/members/project/${projectId}`);
    return res.data;
  },

  async removeWorkspaceMember(workspaceId: string, userId: string) {
    const res = await api.delete<ApiResponse<null>>(`/members/workspace/${workspaceId}/users/${userId}`);
    return res.data;
  },

  async removeClientMember(clientId: string, userId: string) {
    const res = await api.delete<ApiResponse<null>>(`/members/client/${clientId}/users/${userId}`);
    return res.data;
  },

  async removeProjectMember(projectId: string, userId: string) {
    const res = await api.delete<ApiResponse<null>>(`/members/project/${projectId}/users/${userId}`);
    return res.data;
  },
};
