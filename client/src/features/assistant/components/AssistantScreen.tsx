"use client";

import { type FormEvent, useRef, useEffect, type ComponentProps } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Bot, Send, Trash2, User } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { useAssistant } from "../useAssistantQuery";

const markdownComponents: ComponentProps<typeof ReactMarkdown>["components"] = {
  p: ({ children }) => <p className="mb-2 last:mb-0 leading-6">{children}</p>,
  ul: ({ children }) => <ul className="mb-2 list-disc pl-5 space-y-1 last:mb-0">{children}</ul>,
  ol: ({ children }) => <ol className="mb-2 list-decimal pl-5 space-y-1 last:mb-0">{children}</ol>,
  li: ({ children }) => <li className="leading-6">{children}</li>,
  strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
  em: ({ children }) => <em className="italic">{children}</em>,
  code: ({ children, className }) => {
    const isInline = !className;
    if (isInline) {
      return (
        <code className="rounded bg-muted px-1.5 py-0.5 text-xs font-mono">
          {children}
        </code>
      );
    }
    return (
      <pre className="mb-3 mt-1 overflow-x-auto rounded-lg border bg-muted p-3 text-xs leading-5 last:mb-0">
        <code className="font-mono">{children}</code>
      </pre>
    );
  },
  pre: ({ children }) => <>{children}</>,
  h1: ({ children }) => <h1 className="mb-2 mt-3 text-base font-semibold last:mb-0">{children}</h1>,
  h2: ({ children }) => <h2 className="mb-2 mt-3 text-sm font-semibold last:mb-0">{children}</h2>,
  h3: ({ children }) => <h3 className="mb-1 mt-2 text-sm font-semibold last:mb-0">{children}</h3>,
  hr: () => <hr className="my-3 border-border" />,
  blockquote: ({ children }) => (
    <blockquote className="mb-2 border-l-2 border-muted-foreground/30 pl-3 italic last:mb-0">
      {children}
    </blockquote>
  ),
  a: ({ href, children }) => (
    <a href={href} target="_blank" rel="noreferrer" className="underline underline-offset-2 hover:text-primary">
      {children}
    </a>
  ),
  table: ({ children }) => (
    <div className="mb-3 overflow-x-auto last:mb-0">
      <table className="w-full border-collapse text-xs">{children}</table>
    </div>
  ),
  th: ({ children }) => (
    <th className="border border-border bg-muted px-2 py-1 text-left font-semibold">{children}</th>
  ),
  td: ({ children }) => (
    <td className="border border-border px-2 py-1">{children}</td>
  ),
};

function MarkdownRenderer({ content }: { content: string }) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={markdownComponents}
    >
      {content}
    </ReactMarkdown>
  );
}

function formatCitationDate(date: string | null) {
  if (!date) return null;
  const parsed = new Date(date);
  if (Number.isNaN(parsed.getTime())) return null;
  return parsed.toLocaleDateString();
}

export function AssistantScreen({ threadId }: { threadId: string }) {
  const { messages, isLoading, sendMessage, clearMessages } = useAssistant(threadId);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    const val = inputRef.current?.value.trim();
    if (!val || isLoading) return;
    sendMessage(val);
    if (inputRef.current) inputRef.current.value = "";
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="flex min-h-0 flex-1 flex-col">
      {messages.length === 0 ? (
        <div className="flex flex-1 items-center justify-center">
          <div className="mx-auto max-w-md text-center">
            <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-primary/10 text-primary">
              <Bot className="h-7 w-7" />
            </div>
            <h2 className="mb-2 text-xl font-semibold">AI Assistant</h2>
            <p className="text-sm text-muted-foreground">
              Ask about meetings, decisions, risks, action items, and more.
            </p>
          </div>
        </div>
      ) : (
        <div className="flex-1 overflow-y-auto px-4 py-4 md:px-6">
          <div className="mx-auto max-w-4xl space-y-4">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex gap-3 ${msg.role === "user" ? "justify-end" : ""}`}
              >
                {msg.role === "assistant" && (
                  <div className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary/10 text-primary">
                    <Bot className="h-4 w-4" />
                  </div>
                )}

                <div
                  className={`max-w-[80%] space-y-2 ${
                    msg.role === "user" ? "order-first" : ""
                  }`}
                >
                  <div
                    className={`rounded-2xl px-4 py-2.5 text-sm leading-6 ${
                      msg.role === "user"
                        ? "bg-primary text-primary-foreground"
                        : "bg-muted/50"
                    }`}
                  >
                    {msg.content ? (
                      <MarkdownRenderer content={msg.content} />
                    ) : msg.role === "assistant" && isLoading && msg === messages[messages.length - 1] ? (
                      <span className="inline-flex gap-0.5">
                        <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-muted-foreground" style={{ animationDelay: "0ms" }} />
                        <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-muted-foreground" style={{ animationDelay: "150ms" }} />
                        <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-muted-foreground" style={{ animationDelay: "300ms" }} />
                      </span>
                    ) : null}
                  </div>

                  {msg.role === "assistant" && msg.citations && msg.citations.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 px-1">
                      {msg.citations.map((c, i) => (
                        <span
                          key={i}
                          className="inline-flex items-center gap-1 rounded-full border bg-background px-2.5 py-0.5 text-[11px] text-muted-foreground"
                        >
                          {c.meeting_title || "Untitled"}
                          {c.chunk_index !== null && ` #${c.chunk_index}`}
                          {formatCitationDate(c.meeting_date) && (
                            <span className="opacity-60">
                              {formatCitationDate(c.meeting_date)}
                            </span>
                          )}
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                {msg.role === "user" && (
                  <div className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary text-primary-foreground">
                    <User className="h-4 w-4" />
                  </div>
                )}
              </div>
            ))}
            <div ref={bottomRef} />
          </div>
        </div>
      )}

      <div className="border-t bg-background px-4 py-3 md:px-6">
        <div className="mx-auto flex max-w-4xl items-center gap-2">
          {messages.length > 0 && (
            <Button
              variant="ghost"
              size="icon"
              onClick={clearMessages}
              title="Clear conversation"
              className="shrink-0"
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          )}
          <form onSubmit={handleSubmit} className="flex flex-1 items-end gap-2">
            <Textarea
              ref={inputRef}
              placeholder="Ask about meetings, decisions, risks..."
              className="min-h-10 max-h-32 resize-none"
              rows={1}
              onKeyDown={handleKeyDown}
              onInput={(e) => {
                const el = e.currentTarget;
                el.style.height = "auto";
                el.style.height = `${Math.min(el.scrollHeight, 128)}px`;
              }}
            />
            <Button
              type="submit"
              size="icon"
              disabled={isLoading}
              className="shrink-0"
            >
              <Send className="h-4 w-4" />
            </Button>
          </form>
        </div>
      </div>
    </div>
  );
}
