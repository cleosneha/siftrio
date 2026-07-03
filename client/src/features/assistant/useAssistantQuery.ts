"use client";

import { useState, useCallback, useRef, useEffect } from "react";
import { assistantService } from "./assistant.service";
import type { Message, ConversationTurn } from "./assistant.types";

let msgIdCounter = 0;
function nextId() {
  msgIdCounter += 1;
  return `msg-${Date.now()}-${msgIdCounter}`;
}

export function useAssistant() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesRef = useRef<Message[]>([]);

  useEffect(() => {
    messagesRef.current = messages;
  }, [messages]);

  const sendMessage = useCallback(async (content: string) => {
    const trimmed = content.trim();
    if (!trimmed) return;

    const userMsg: Message = { id: nextId(), role: "user", content: trimmed };
    const assistantMsg: Message = { id: nextId(), role: "assistant", content: "" };

    setMessages((prev) => [...prev, userMsg, assistantMsg]);
    setIsLoading(true);

    try {
      const currentMessages = messagesRef.current;
      const history = buildHistory(currentMessages, trimmed);

      let fullAnswer = "";
      let hasStreamedData = false;

      for await (const event of assistantService.queryStream(trimmed, history)) {
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

      if (!hasStreamedData && assistantService.query) {
        const res = await assistantService.query(trimmed, history);
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
  }, []);

  const clearMessages = useCallback(() => {
    setMessages([]);
    msgIdCounter = 0;
  }, []);

  return { messages, isLoading, sendMessage, clearMessages };
}

function buildHistory(
  currentMessages: Message[],
  currentQuestion: string,
): ConversationTurn[] {
  const turns: ConversationTurn[] = [];
  for (const m of currentMessages) {
    if (!m.content || m.content.startsWith("Error:")) continue;
    if (m.role === "user" && m.content === currentQuestion) continue;
    turns.push({ role: m.role, content: m.content });
  }
  return turns.slice(-6);
}
