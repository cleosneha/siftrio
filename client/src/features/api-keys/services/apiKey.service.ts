import { api } from "@/lib/api";
import type { ApiResponse } from "@/types";
import type { ApiKey, ApiKeyCreatedResponse } from "../types/apiKey.types";

export const apiKeyService = {
  async create(name: string) {
    const res = await api.post<ApiResponse<ApiKeyCreatedResponse>>("/api-keys", {
      name,
    });
    return res.data;
  },

  async list() {
    const res = await api.get<ApiResponse<ApiKey[]>>("/api-keys");
    return res.data;
  },

  async revoke(id: string) {
    const res = await api.post<ApiResponse<ApiKey>>(
      `/api-keys/${id}/revoke`,
    );
    return res.data;
  },

  async remove(id: string) {
    const res = await api.delete<ApiResponse<void>>(`/api-keys/${id}`);
    return res.data;
  },
};
