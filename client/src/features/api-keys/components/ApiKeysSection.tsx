"use client";

import { useState } from "react";
import { Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { useApiKeys } from "../hooks/useApiKeys";
import { ApiKeyList } from "./ApiKeyList";
import { CreateApiKeyDialog } from "./CreateApiKeyDialog";
import { ApiKeyCreatedDialog } from "./ApiKeyCreatedDialog";
import type { ApiKeyCreatedResponse } from "../types/apiKey.types";

export function ApiKeysSection() {
  const [showCreate, setShowCreate] = useState(false);
  const [createdKey, setCreatedKey] = useState<ApiKeyCreatedResponse | null>(null);
  const { data: keysData, isLoading } = useApiKeys();
  const keys = keysData?.data ?? [];

  return (
    <>
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0">
          <div>
            <CardTitle>MCP API Keys</CardTitle>
            <CardDescription>
              Manage API keys for connecting external MCP clients like Claude Desktop, VS Code, and Cursor.
            </CardDescription>
          </div>
          <Button size="sm" onClick={() => setShowCreate(true)}>
            <Plus className="mr-1 h-4 w-4" />
            Create API Key
          </Button>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="py-8 text-center text-sm text-muted-foreground">
              Loading API keys...
            </div>
          ) : (
            <ApiKeyList keys={keys} />
          )}
        </CardContent>
      </Card>

      <CreateApiKeyDialog
        open={showCreate}
        onClose={() => setShowCreate(false)}
        onCreated={(key) => {
          setShowCreate(false);
          setCreatedKey(key);
        }}
      />

      <ApiKeyCreatedDialog
        apiKey={createdKey}
        onClose={() => setCreatedKey(null)}
      />
    </>
  );
}
