"use client";

import { useState, useCallback } from "react";
import { assistantService } from "./assistant.service";
import type { Message } from "./assistant.types";

let msgIdCounter = 0;
function nextId() {
  msgIdCounter += 1;
  return `msg-${Date.now()}-${msgIdCounter}`;
}

export function useAssistant(threadId: string) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const sendMessage = useCallback(async (content: string) => {
    const trimmed = content.trim();
    if (!trimmed) return;

    const userMsg: Message = { id: nextId(), role: "user", content: trimmed };
    const assistantMsg: Message = { id: nextId(), role: "assistant", content: "" };

    setMessages((prev) => [...prev, userMsg, assistantMsg]);
    setIsLoading(true);

    try {
      let fullAnswer = "";
      let hasStreamedData = false;

      for await (const event of assistantService.queryStream(trimmed, threadId)) {
        hasStreamedData = true;
        if (event.token) {
          fullAnswer += event.token;
          setMessages((prev) => {
            const next = [...prev];
            const last = next[next.length - 1];
            if (last?.role === "assistant") {
              next[next.length - 1] = { ...last, content: fullAnswer };
            }
            return next;
          });
        }
        if (event.done) {
          setMessages((prev) => {
            const next = [...prev];
            const last = next[next.length - 1];
            if (last?.role === "assistant") {
              next[next.length - 1] = {
                ...last,
                content: fullAnswer,
                citations: event.citations || [],
              };
            }
            return next;
          });
        }
        if (event.error) {
          setMessages((prev) => {
            const next = [...prev];
            const last = next[next.length - 1];
            if (last?.role === "assistant") {
              next[next.length - 1] = { ...last, content: `Error: ${event.error}` };
            }
            return next;
          });
        }
      }

      if (!hasStreamedData) {
        const res = await assistantService.query(trimmed, threadId);
        setMessages((prev) => {
          const next = [...prev];
          const last = next[next.length - 1];
          if (last?.role === "assistant") {
            next[next.length - 1] = {
              ...last,
              content: res.answer,
              citations: res.citations,
              ambiguous_entities: res.ambiguous_entities,
            };
          }
          return next;
        });
      }
    } catch (err) {
      setMessages((prev) => {
        const next = [...prev];
        const last = next[next.length - 1];
        if (last?.role === "assistant") {
          next[next.length - 1] = {
            ...last,
            content:
              err instanceof Error ? `Error: ${err.message}` : "Error: Request failed",
          };
        }
        return next;
      });
    } finally {
      setIsLoading(false);
    }
  }, [threadId]);

  const clearMessages = useCallback(() => {
    setMessages([]);
    msgIdCounter = 0;
  }, []);

  return { messages, isLoading, sendMessage, clearMessages };
}
