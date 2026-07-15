"use client";

import { useState } from "react";
import {
  ExternalLink,
  Calendar,
  X,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { cn } from "@/lib/utils";
import type { MeetingAnalysis, ActionItem, SuggestedMeeting } from "@/types";
import { AnalysisSection } from "./AnalysisSection";

const TABS = [
  "Overview",
  "Action Items",
  "Outcomes & Decisions",
  "Questions",
  "Risks & Blockers",
  "Follow-ups",
] as const;

type Tab = (typeof TABS)[number];

interface AnalysisContentProps {
  analysis: MeetingAnalysis;
  actionItems: ActionItem[];
  hasJira: boolean;
  pendingSuggestions: SuggestedMeeting[];
  onOpenJira: (item: ActionItem) => void;
  onViewIssue: (item: ActionItem) => void;
  onDismiss: (suggestionId: string) => void;
  onSchedule: (suggestion: {
    title: string;
    suggested_date: string | null;
    start_time: string | null;
    end_time: string | null;
  }) => void;
  isDismissing: boolean;
}

export function AnalysisContent({
  analysis,
  actionItems,
  hasJira,
  pendingSuggestions,
  onOpenJira,
  onViewIssue,
  onDismiss,
  onSchedule,
  isDismissing,
}: AnalysisContentProps) {
  const [activeTab, setActiveTab] = useState<Tab>("Overview");

  return (
    <div className="space-y-6">
      <div className="flex gap-1 overflow-x-auto rounded-lg border bg-muted p-1">
        {TABS.map((tab) => (
          <button
            key={tab}
            type="button"
            onClick={() => setActiveTab(tab)}
            className={cn(
              "flex-1 whitespace-nowrap rounded-md px-3 py-2 text-sm font-medium transition-colors",
              activeTab === tab
                ? "bg-background text-foreground shadow-sm"
                : "text-muted-foreground hover:text-foreground",
            )}
          >
            {tab}
          </button>
        ))}
      </div>

      {activeTab === "Overview" && (
        <div className="space-y-6">
          {analysis.summary && (
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Summary</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  {analysis.summary}
                </p>
              </CardContent>
            </Card>
          )}
          {analysis.goal && (
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Goal</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  {analysis.goal}
                </p>
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {activeTab === "Action Items" && (
        <ActionItemsPanel
          analysis={analysis}
          actionItems={actionItems}
          hasJira={hasJira}
          onOpenJira={onOpenJira}
          onViewIssue={onViewIssue}
        />
      )}

      {activeTab === "Outcomes & Decisions" && (
        <div className="grid gap-6 md:grid-cols-2">
          <AnalysisSection
            title="Outcomes"
            items={analysis.outcomes}
            emptyText="No outcomes recorded"
          />
          <AnalysisSection
            title="Decisions"
            items={analysis.decisions}
            emptyText="No decisions recorded"
          />
        </div>
      )}

      {activeTab === "Questions" && (
        <div className="grid gap-6 md:grid-cols-2">
          <AnalysisSection
            title="Answered Questions"
            items={analysis.answered_questions}
            emptyText="No questions answered"
          />
          <AnalysisSection
            title="Unanswered Questions"
            items={analysis.unanswered_questions}
            emptyText="No unanswered questions"
          />
        </div>
      )}

      {activeTab === "Risks & Blockers" && (
        <div className="grid gap-6 md:grid-cols-2">
          <AnalysisSection
            title="Risks"
            items={analysis.risks}
            emptyText="No risks identified"
          />
          <AnalysisSection
            title="Blockers"
            items={analysis.blockers}
            emptyText="No blockers"
          />
        </div>
      )}

      {activeTab === "Follow-ups" && (
        <div className="space-y-6">
          {pendingSuggestions.length > 0 && (
            <SuggestionsCard
              suggestions={pendingSuggestions}
              onSchedule={onSchedule}
              onDismiss={onDismiss}
              isDismissing={isDismissing}
            />
          )}
          <AnalysisSection
            title="Future Meetings"
            items={analysis.future_meetings}
            emptyText="No future meetings mentioned"
          />
        </div>
      )}
    </div>
  );
}

function ActionItemsPanel({
  analysis,
  actionItems,
  hasJira,
  onOpenJira,
  onViewIssue,
}: {
  analysis: MeetingAnalysis;
  actionItems: ActionItem[];
  hasJira: boolean;
  onOpenJira: (item: ActionItem) => void;
  onViewIssue: (item: ActionItem) => void;
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Action Items</CardTitle>
      </CardHeader>
      <CardContent>
        {actionItems.length === 0 ? (
          analysis.action_items.length > 0 ? (
            <ul className="space-y-2">
              {analysis.action_items.map((item, i) => (
                <li key={i} className="flex gap-2 text-sm">
                  <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-primary" />
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          ) : (
            <CardDescription>No action items</CardDescription>
          )
        ) : (
          <div className="space-y-3">
            {actionItems.map((ai) => (
              <div key={ai.id} className="rounded-lg border p-3">
                <div className="mb-1 text-sm font-medium">{ai.title}</div>
                {ai.description && (
                  <div className="mb-2 text-xs text-muted-foreground">
                    {ai.description}
                  </div>
                )}
                <div className="flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
                  {ai.assignee && <span>Assignee: {ai.assignee}</span>}
                  {ai.due_date && (
                    <span>
                      Due: {new Date(ai.due_date).toLocaleDateString()}
                    </span>
                  )}
                  {ai.jira_issue_url && ai.sync_status === "synced" ? (
                    <button
                      type="button"
                      onClick={() => onViewIssue(ai)}
                      className="inline-flex items-center gap-1 text-xs hover:text-foreground"
                    >
                      <ExternalLink className="h-3 w-3" />
                      View Issue
                    </button>
                  ) : (
                    <button
                      type="button"
                      disabled={!hasJira}
                      title={
                        !hasJira
                          ? "Connect a Jira project first"
                          : "Create Jira issue"
                      }
                      onClick={() => onOpenJira(ai)}
                      className="inline-flex items-center gap-1 text-xs disabled:opacity-50 disabled:cursor-not-allowed hover:text-foreground"
                    >
                      <ExternalLink className="h-3 w-3" />
                      {!hasJira ? "Jira Unavailable" : "Create Jira Issue"}
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

function SuggestionsCard({
  suggestions,
  onSchedule,
  onDismiss,
  isDismissing,
}: {
  suggestions: SuggestedMeeting[];
  onSchedule: (suggestion: {
    title: string;
    suggested_date: string | null;
    start_time: string | null;
    end_time: string | null;
  }) => void;
  onDismiss: (suggestionId: string) => void;
  isDismissing: boolean;
}) {
  return (
    <Card className="border-primary/30">
      <CardHeader>
        <CardTitle className="text-base flex items-center gap-2">
          <Calendar className="h-4 w-4 text-primary" />
          AI Suggested Follow-up Meetings
        </CardTitle>
        <CardDescription>
          The AI detected these follow-up meeting suggestions in the transcript
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {suggestions.map((suggestion) => (
          <Card key={suggestion.id}>
            <CardContent className="pt-4">
              <div className="flex items-start justify-between gap-4">
                <div className="min-w-0 flex-1">
                  <h4 className="font-medium">{suggestion.title}</h4>
                  {suggestion.description && (
                    <p className="mt-1 text-sm text-muted-foreground">
                      {suggestion.description}
                    </p>
                  )}
                  <div className="mt-2 flex flex-wrap items-center gap-3 text-xs text-muted-foreground">
                    {suggestion.suggested_date && (
                      <span className="inline-flex items-center gap-1">
                        <Calendar className="h-3 w-3" />
                        {new Date(
                          suggestion.suggested_date,
                        ).toLocaleDateString()}
                      </span>
                    )}
                    {suggestion.start_time && (
                      <span>{suggestion.start_time}</span>
                    )}
                    {suggestion.end_time && (
                      <span>– {suggestion.end_time}</span>
                    )}
                    <Badge variant="outline" className="text-[10px]">
                      {Math.round(suggestion.confidence * 100)}% confidence
                    </Badge>
                  </div>
                  <p className="mt-1.5 text-xs italic text-muted-foreground">
                    &ldquo;{suggestion.reason}&rdquo;
                  </p>
                </div>
              </div>
              <div className="mt-3 flex gap-2">
                <Button size="sm" onClick={() => onSchedule(suggestion)}>
                  <Calendar className="mr-1 h-3.5 w-3.5" />
                  Schedule Meeting
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => onSchedule(suggestion)}
                >
                  Edit &amp; Schedule
                </Button>
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => onDismiss(suggestion.id)}
                  disabled={isDismissing}
                >
                  <X className="mr-1 h-3.5 w-3.5" />
                  Dismiss
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </CardContent>
    </Card>
  );
}
