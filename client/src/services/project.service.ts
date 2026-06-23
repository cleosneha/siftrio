import { api } from "@/lib/api";
import type { ApiResponse, Project } from "@/types";

export const projectService = {
  async create(data: { client_id: string; name: string; description?: string | null }) {
    const res = await api.post<ApiResponse<Project>>("/projects", data);
    return res.data;
  },

  async list(clientId?: string) {
    const params = clientId ? { client_id: clientId } : {};
    const res = await api.get<ApiResponse<Project[]>>("/projects", { params });
    return res.data;
  },

  async getById(id: string) {
    const res = await api.get<ApiResponse<Project>>(`/projects/${id}`);
    return res.data;
  },
};
