import { api } from "@/lib/api";
import type { AssistantQueryResponse } from "./assistant.types";

export const assistantService = {
  async query(question: string, threadId: string) {
    const res = await api.post<AssistantQueryResponse>("/assistant/query", {
      question,
      thread_id: threadId,
    });
    return res.data;
  },

  async *queryStream(question: string, threadId: string) {
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_BACKEND_URL}/assistant/query/stream`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question,
          thread_id: threadId,
        }),
        credentials: "include",
      },
    );

    if (!response.ok) {
      const errBody = await response.text();
      throw new Error(errBody || `Request failed: ${response.status}`);
    }

    const reader = response.body?.getReader();
    if (!reader) throw new Error("No response body");

    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() || "";

      for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed.startsWith("data: ")) continue;
        try {
          const data = JSON.parse(trimmed.slice(6));
          yield data;
        } catch {
          // skip malformed JSON
        }
      }
    }
  },
};
