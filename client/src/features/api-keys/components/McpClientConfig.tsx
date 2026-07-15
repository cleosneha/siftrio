"use client";

import { useState } from "react";
import { Copy, Check, ExternalLink } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { getMcpUrl } from "../utils/mcp";

type ClientType = "claude" | "vscode" | "cursor";

const CLIENTS: { id: ClientType; label: string; configPath: string }[] = [
  {
    id: "claude",
    label: "Claude Desktop",
    configPath:
      "~/Library/Application Support/Claude/claude_desktop_config.json (macOS) or %APPDATA%\\Claude\\claude_desktop_config.json (Windows)",
  },
  {
    id: "vscode",
    label: "VS Code",
    configPath: ".vscode/settings.json or extension settings",
  },
  {
    id: "cursor",
    label: "Cursor",
    configPath: ".cursor/mcp.json",
  },
];

function getConfigSnippet(mcpUrl: string, apiKey: string): string {
  const maskedKey = apiKey
    ? `${apiKey.slice(0, 12)}...${apiKey.slice(-4)}`
    : "YOUR_API_KEY";

  return JSON.stringify(
    {
      mcpServers: {
        siftrio: {
          url: mcpUrl,
          headers: {
            Authorization: `Bearer ${maskedKey}`,
          },
        },
      },
    },
    null,
    2,
  );
}

function getSteps(client: ClientType, configPath: string): string[] {
  switch (client) {
    case "claude":
      return [
        `Open Claude Desktop and go to Settings > Developer > Edit Config.`,
        `Add the following to ${configPath}:`,
        "Restart Claude Desktop to connect.",
      ];
    case "vscode":
      return [
        `Install the "Copilot" or "MCP" extension from the marketplace.`,
        `Add the following to ${configPath}:`,
        "Reload VS Code to connect.",
      ];
    case "cursor":
      return [
        `Open Cursor and go to Settings > MCP.`,
        `Add the following to ${configPath}:`,
        "Cursor will automatically connect.",
      ];
  }
}

interface CopyButtonProps {
  text: string;
}

function CopyButton({ text }: CopyButtonProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <Button
      variant="outline"
      size="icon"
      onClick={handleCopy}
      className="shrink-0"
    >
      {copied ? (
        <Check className="h-4 w-4 text-green-600" />
      ) : (
        <Copy className="h-4 w-4" />
      )}
    </Button>
  );
}

interface McpClientConfigProps {
  apiKey?: string | null;
}

export function McpClientConfig({ apiKey }: McpClientConfigProps) {
  const [selectedClient, setSelectedClient] = useState<ClientType>("claude");
  const mcpUrl = getMcpUrl();
  const client = CLIENTS.find((c) => c.id === selectedClient)!;
  const steps = getSteps(selectedClient, client.configPath);
  const configSnippet = getConfigSnippet(mcpUrl, apiKey ?? "");

  return (
    <Card>
      <CardHeader>
        <CardTitle>MCP Client Setup</CardTitle>
        <CardDescription>
          Connect external AI tools to your workspace using the MCP protocol.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-3">
          <div>
            <label className="text-sm font-medium">Server URL</label>
            <div className="mt-1 flex gap-2">
              <Input readOnly value={mcpUrl} className="font-mono text-sm" />
              <CopyButton text={mcpUrl} />
            </div>
          </div>

          {apiKey && (
            <div>
              <label className="text-sm font-medium">API Key</label>
              <div className="mt-1 flex gap-2">
                <Input
                  readOnly
                  value={apiKey}
                  className="font-mono text-sm"
                />
                <CopyButton text={apiKey} />
              </div>
            </div>
          )}

          {!apiKey && (
            <div className="rounded-lg border border-dashed p-4 text-center text-sm text-muted-foreground">
              Create an API key above to get started.
            </div>
          )}
        </div>

        {apiKey && (
          <>
            <div className="flex gap-2">
              {CLIENTS.map((c) => (
                <Button
                  key={c.id}
                  variant={selectedClient === c.id ? "default" : "outline"}
                  size="sm"
                  onClick={() => setSelectedClient(c.id)}
                >
                  {c.label}
                </Button>
              ))}
            </div>

            <div className="space-y-4">
              {steps.map((step, i) => (
                <div key={i} className="space-y-2">
                  {i === 1 ? (
                    <>
                      <p className="text-sm font-medium">
                        Step {i + 1}: {step}
                      </p>
                      <div className="relative">
                        <pre className="overflow-x-auto rounded-lg border bg-muted/50 p-4 font-mono text-xs">
                          {configSnippet}
                        </pre>
                        <div className="absolute right-2 top-2">
                          <CopyButton text={configSnippet} />
                        </div>
                      </div>
                    </>
                  ) : (
                    <p className="text-sm">
                      <span className="font-medium text-muted-foreground">
                        Step {i + 1}:{" "}
                      </span>
                      {step}
                    </p>
                  )}
                </div>
              ))}
            </div>

            <div className="rounded-lg border bg-muted/30 p-3">
              <p className="text-xs text-muted-foreground">
                The server URL and API key above are tied to your account. Your
                API key grants access to all workspaces you belong to. Never
                share your API key publicly.
              </p>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
}
