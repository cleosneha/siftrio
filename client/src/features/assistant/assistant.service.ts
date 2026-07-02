import { api } from "@/lib/api";
import type { AssistantQueryResponse } from "./assistant.types";

export const assistantService = {
  async query(question: string) {
    const res = await api.post<AssistantQueryResponse>("/assistant/query", {
      question,
    });
    return res.data;
  },
};
