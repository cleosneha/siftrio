"use client";

import { useState } from "react";
import { Bot, Loader2, MessageSquareText, Search } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { useAssistantQuery } from "../useAssistantQuery";

function formatCitationDate(date: string | null) {
  if (!date) return null;
  const parsed = new Date(date);
  if (Number.isNaN(parsed.getTime())) return null;
  return parsed.toLocaleDateString();
}

export function AssistantScreen() {
  const [question, setQuestion] = useState("");
  const assistantQuery = useAssistantQuery();

  const submitQuestion = async () => {
    const trimmed = question.trim();
    if (!trimmed || assistantQuery.isPending) return;
    try {
      await assistantQuery.mutateAsync(trimmed);
    } catch {
      // The mutation state renders the error message for the user.
    }
  };

  const hasResult = Boolean(assistantQuery.data);

  return (
    <div className="flex-1 overflow-y-auto p-4 md:p-6">
      <div className="mx-auto flex w-full max-w-4xl flex-col gap-6">
        <header className="rounded-2xl border bg-card p-5 shadow-sm">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary/10 text-primary">
              <Bot className="h-5 w-5" />
            </div>
            <div>
              <h1 className="text-2xl font-semibold">AI Assistant</h1>
              <p className="text-sm text-muted-foreground">
                Ask a question about meetings, decisions, risks, and knowledge.
              </p>
            </div>
          </div>
        </header>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Question</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-3">
              <Textarea
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="Why are we implementing Google Login?"
                className="min-h-28"
              />
              <Button
                onClick={submitQuestion}
                disabled={assistantQuery.isPending || !question.trim()}
                className="gap-2"
              >
                {assistantQuery.isPending ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Asking...
                  </>
                ) : (
                  <>
                    <Search className="h-4 w-4" />
                    Ask
                  </>
                )}
              </Button>
            </div>

            {assistantQuery.isError && (
              <div className="rounded-lg border border-destructive/20 bg-destructive/5 p-3 text-sm text-destructive">
                {assistantQuery.error instanceof Error
                  ? assistantQuery.error.message
                  : "Something went wrong while asking the assistant."}
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <MessageSquareText className="h-4 w-4" />
              Answer
            </CardTitle>
          </CardHeader>
          <CardContent>
            {assistantQuery.isPending ? (
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Loader2 className="h-4 w-4 animate-spin" />
                Generating answer...
              </div>
            ) : hasResult ? (
              <div className="space-y-4">
                <p className="whitespace-pre-wrap text-sm leading-6">
                  {assistantQuery.data?.answer}
                </p>
                <div className="space-y-3 border-t pt-4">
                  <h2 className="text-sm font-medium text-muted-foreground">
                    Sources
                  </h2>
                  {assistantQuery.data?.citations.length ? (
                    <ul className="space-y-2">
                      {assistantQuery.data.citations.map((citation, index) => (
                        <li
                          key={`${citation.meeting_id ?? "meeting"}-${citation.chunk_index ?? "analysis"}-${index}`}
                          className="rounded-lg border bg-muted/30 p-3 text-sm"
                        >
                          <div className="font-medium text-foreground">
                            {citation.meeting_title || "Untitled meeting"}
                          </div>
                          <div className="mt-1 text-xs text-muted-foreground">
                            {formatCitationDate(citation.meeting_date) ||
                              "No meeting date"}
                            {citation.chunk_index !== null && (
                              <span className="ml-2">
                                Chunk {citation.chunk_index}
                              </span>
                            )}
                          </div>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-sm text-muted-foreground">
                      No citations were returned for this answer.
                    </p>
                  )}
                </div>
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">
                Ask a question to see the answer and relevant sources.
              </p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
