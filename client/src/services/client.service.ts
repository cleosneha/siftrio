import { api } from "@/lib/api";
import type { ApiResponse, Client } from "@/types";

export const clientService = {
  async create(data: { workspace_id: string; name: string; description?: string | null }) {
    const res = await api.post<ApiResponse<Client>>("/clients", data);
    return res.data;
  },

  async list(workspaceId?: string) {
    const params = workspaceId ? { workspace_id: workspaceId } : {};
    const res = await api.get<ApiResponse<Client[]>>("/clients", { params });
    return res.data;
  },

  async getById(id: string) {
    const res = await api.get<ApiResponse<Client>>(`/clients/${id}`);
    return res.data;
  },
};
