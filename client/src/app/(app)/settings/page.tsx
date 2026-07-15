"use client";

import { useState } from "react";
import { Menu, Settings } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useAppContext } from "@/lib/app-context";
import { ApiKeysSection } from "@/features/api-keys/components/ApiKeysSection";
import { McpClientConfig } from "@/features/api-keys/components/McpClientConfig";
import type { ApiKeyCreatedResponse } from "@/features/api-keys/types/apiKey.types";

export default function SettingsPage() {
  const { setSidebarOpen } = useAppContext();
  const [createdKey, setCreatedKey] = useState<ApiKeyCreatedResponse | null>(null);

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
        <Settings className="h-5 w-5" />
        <h1 className="text-xl font-semibold">Settings</h1>
      </header>

      <div className="flex-1 overflow-y-auto px-4 py-6 md:px-6">
        <div className="mx-auto max-w-2xl space-y-6">
          <div>
            <h2 className="text-lg font-medium">Developer</h2>
            <p className="text-sm text-muted-foreground">
              Manage API keys and integrations for external tools.
            </p>
          </div>
          <ApiKeysSection
            createdKey={createdKey}
            onCreated={setCreatedKey}
            onClearCreatedKey={() => setCreatedKey(null)}
          />
          <McpClientConfig apiKey={createdKey?.secret} />
        </div>
      </div>
    </div>
  );
}
