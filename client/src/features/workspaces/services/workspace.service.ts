import { api } from "@/lib/api";
import type { ApiResponse, Workspace } from "@/types";

export const workspaceService = {
  async create(data: { name: string; description?: string | null }) {
    const res = await api.post<ApiResponse<Workspace>>("/workspaces", data);
    return res.data;
  },

  async list() {
    const res = await api.get<ApiResponse<Workspace[]>>("/workspaces");
    return res.data;
  },

  async getById(id: string) {
    const res = await api.get<ApiResponse<Workspace>>(`/workspaces/${id}`);
    return res.data;
  },
};
