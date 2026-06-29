"use client";

import { useState } from "react";

import { Button } from "@/components/ui/button";

type TabType = "requirements" | "action-items" | "decisions" | "risks" | "questions";

import { RequirementsTab } from "./tabs/RequirementsTab";
import { ActionItemsTab } from "./tabs/ActionItemsTab";
import { DecisionsTab } from "./tabs/DecisionsTab";
import { RisksTab } from "./tabs/RisksTab";
import { QuestionsTab } from "./tabs/QuestionsTab";

export function KnowledgeSection({ projectId }: { projectId: string }) {
  const [activeTab, setActiveTab] = useState<TabType>("requirements");

  const tabs: { key: TabType; label: string }[] = [
    { key: "requirements", label: "Requirements" },
    { key: "action-items", label: "Action Items" },
    { key: "decisions", label: "Decisions" },
    { key: "risks", label: "Risks" },
    { key: "questions", label: "Questions" },
  ];

  return (
    <div>
      <div className="mb-4 flex flex-wrap gap-1 border-b">
        {tabs.map((tab) => (
          <Button
            key={tab.key}
            variant={activeTab === tab.key ? "default" : "ghost"}
            size="sm"
            onClick={() => setActiveTab(tab.key)}
            className="rounded-none data-[slot='button']:rounded-none"
            style={
              activeTab === tab.key
                ? { borderBottom: "2px solid var(--primary)" }
                : { borderBottom: "2px solid transparent" }
            }
          >
            {tab.label}
          </Button>
        ))}
      </div>
      {activeTab === "requirements" && <RequirementsTab projectId={projectId} />}
      {activeTab === "action-items" && <ActionItemsTab projectId={projectId} />}
      {activeTab === "decisions" && <DecisionsTab projectId={projectId} />}
      {activeTab === "risks" && <RisksTab projectId={projectId} />}
      {activeTab === "questions" && <QuestionsTab projectId={projectId} />}
    </div>
  );
}
