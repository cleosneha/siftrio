"use client";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useRevokeApiKey, useDeleteApiKey } from "../hooks/useApiKeys";
import type { ApiKey } from "../types/apiKey.types";
import { formatDistanceToNow } from "@/lib/utils";

interface ApiKeyListProps {
  keys: ApiKey[];
}

export function ApiKeyList({ keys }: ApiKeyListProps) {
  const revokeKey = useRevokeApiKey();
  const deleteKey = useDeleteApiKey();

  if (keys.length === 0) {
    return (
      <div className="py-8 text-center text-sm text-muted-foreground">
        No API keys yet. Create one to get started with MCP clients.
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {keys.map((key) => {
        const isRevoked = key.revoked_at !== null;
        return (
          <div
            key={key.id}
            className="flex items-center justify-between rounded-lg border p-4"
          >
            <div className="flex items-center gap-3">
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-medium">{key.name}</span>
                  {isRevoked ? (
                    <Badge variant="destructive">Revoked</Badge>
                  ) : (
                    <Badge variant="secondary">Active</Badge>
                  )}
                </div>
                <div className="mt-1 text-xs text-muted-foreground">
                  <span className="font-mono">{key.key_prefix}...</span>
                  {key.last_used_at && (
                    <span className="ml-2">
                      Last used {formatDistanceToNow(new Date(key.last_used_at))} ago
                    </span>
                  )}
                  {!key.last_used_at && !isRevoked && (
                    <span className="ml-2">Never used</span>
                  )}
                </div>
              </div>
            </div>
            <div className="flex items-center gap-2">
              {!isRevoked && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => revokeKey.mutate(key.id)}
                  disabled={revokeKey.isPending}
                >
                  Revoke
                </Button>
              )}
              <Button
                variant="ghost"
                size="sm"
                onClick={() => deleteKey.mutate(key.id)}
                disabled={deleteKey.isPending}
              >
                Delete
              </Button>
            </div>
          </div>
        );
      })}
    </div>
  );
}
