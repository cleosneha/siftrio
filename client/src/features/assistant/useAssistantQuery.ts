"use client";

import { useState, useCallback, useRef } from "react";
import { assistantService } from "./assistant.service";
import type { Message } from "./assistant.types";

let msgIdCounter = 0;
function nextId() {
  msgIdCounter += 1;
  return `msg-${Date.now()}-${msgIdCounter}`;
}

function getRetrySeconds(err: unknown): number {
  const e = err as any;
  if (e?.retryAfter) return parseInt(e.retryAfter, 10);
  if (e?.response?.headers?.["retry-after"]) return parseInt(e.response.headers["retry-after"], 10);
  return 60;
}

export function useAssistant(threadId: string) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [rateLimited, setRateLimited] = useState(false);
  const rateTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

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
      const status = (err as any)?.status ?? (err as any)?.response?.status;
      const errMsg =
        err instanceof Error ? err.message : "";
      const isRateLimit =
        status === 429 ||
        errMsg.includes("rate_limit_exceeded") ||
        errMsg.includes("Too many requests");

      if (isRateLimit) {
        const seconds = getRetrySeconds(err);
        setRateLimited(true);
        if (rateTimer.current) clearTimeout(rateTimer.current);
        rateTimer.current = setTimeout(() => setRateLimited(false), seconds * 1000);
      } else {
        setMessages((prev) => {
          const next = [...prev];
          const last = next[next.length - 1];
          if (last?.role === "assistant") {
            next[next.length - 1] = {
              ...last,
              content: errMsg
                ? `Error: ${errMsg}`
                : "Error: Request failed",
            };
          }
          return next;
        });
      }
    } finally {
      setIsLoading(false);
    }
  }, [threadId]);

  const clearMessages = useCallback(() => {
    setMessages([]);
    msgIdCounter = 0;
  }, []);

  return { messages, isLoading, sendMessage, clearMessages, rateLimited };
}
