"use client";

import { useRef } from "react";
import { Menu } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useAppContext } from "@/lib/app-context";
import { AssistantScreen } from "@/features/assistant/components/AssistantScreen";

function generateId(): string {
  if (typeof crypto !== "undefined" && crypto.randomUUID) {
    return crypto.randomUUID();
  }
  return `${Date.now()}-${Math.random().toString(36).slice(2, 11)}`;
}

export default function AssistantPage() {
  const { setSidebarOpen } = useAppContext();
  const threadId = useRef(generateId());

  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <header className="flex items-center gap-3 border-b px-4 py-3 md:px-6">
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setSidebarOpen(true)}
          className="md:hidden"
        >
          <Menu className="h-5 w-5" />
        </Button>
        <h1 className="text-xl font-semibold">AI Assistant</h1>
      </header>

      <div className="flex min-h-0 flex-1">
        <AssistantScreen threadId={threadId.current} />
      </div>
    </div>
  );
}
