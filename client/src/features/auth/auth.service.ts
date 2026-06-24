import { api } from "@/lib/api";
import type { ApiResponse } from "@/types";
import type { User } from "./auth.types";

export const authService = {
  async me() {
    const res = await api.get<ApiResponse<User>>("/auth/me");
    return res.data;
  },

  async logout() {
    const res = await api.post<ApiResponse<null>>("/auth/logout");
    return res.data;
  },
};
