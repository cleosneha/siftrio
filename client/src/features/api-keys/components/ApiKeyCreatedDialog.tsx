"use client";

import { useState } from "react";
import { Copy, Check } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import type { ApiKeyCreatedResponse } from "../types/apiKey.types";

interface ApiKeyCreatedDialogProps {
  apiKey: ApiKeyCreatedResponse | null;
  onClose: () => void;
}

export function ApiKeyCreatedDialog({
  apiKey,
  onClose,
}: ApiKeyCreatedDialogProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    if (!apiKey?.secret) return;
    await navigator.clipboard.writeText(apiKey.secret);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <Dialog open={!!apiKey} onOpenChange={(o) => { if (!o) onClose(); }}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>API Key Created</DialogTitle>
          <DialogDescription>
            Copy your secret key now. It will not be shown again.
          </DialogDescription>
        </DialogHeader>

        {apiKey && (
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium">Name</label>
              <p className="text-sm text-muted-foreground">{apiKey.name}</p>
            </div>
            <div>
              <label className="text-sm font-medium">Secret</label>
              <div className="mt-1 flex gap-2">
                <Input
                  readOnly
                  value={apiKey.secret}
                  className="font-mono text-sm"
                />
                <Button
                  variant="outline"
                  size="icon"
                  onClick={handleCopy}
                  className="shrink-0"
                >
                  {copied ? (
                    <Check className="h-4 w-4" style={{ color: "var(--success)" }} />
                  ) : (
                    <Copy className="h-4 w-4" />
                  )}
                </Button>
              </div>
            </div>
          </div>
        )}

        <div className="rounded-lg bg-muted/30 p-3">
          <p className="text-sm font-medium">Next Steps</p>
          <ul className="mt-1 list-inside list-disc space-y-1 text-sm text-muted-foreground">
            <li>Copy the secret key above</li>
            <li>Scroll down to "MCP Client Setup" for configuration instructions</li>
            <li>Paste the key into your AI client config file</li>
          </ul>
        </div>

        <DialogFooter>
          <Button onClick={onClose}>Done</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
