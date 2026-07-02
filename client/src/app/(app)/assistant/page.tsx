"use client";

import { Menu } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useAppContext } from "@/lib/app-context";
import { AssistantScreen } from "@/features/assistant/components/AssistantScreen";

export default function AssistantPage() {
  const { setSidebarOpen } = useAppContext();

  return (
    <>
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

      <AssistantScreen />
    </>
  );
}
