"use client";

import { useState } from "react";
import { ExternalLink, Loader2, Unlink } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  useProjectJira,
  useDisconnectProjectFromJira,
} from "@/features/jira/hooks/useJira";
import { JiraConnectDialog } from "@/features/jira/components/JiraConnectDialog";

interface JiraIntegrationSectionProps {
  projectId: string;
  clientId: string;
}

export function JiraIntegrationSection({
  projectId,
  clientId,
}: JiraIntegrationSectionProps) {
  const [showConnect, setShowConnect] = useState(() => {
    if (typeof window !== "undefined") {
      try {
        const autoOpen = sessionStorage.getItem("jira_auto_open_project");
        if (autoOpen === projectId) {
          sessionStorage.removeItem("jira_auto_open_project");
          return true;
        }
      } catch {
        // sessionStorage unavailable
      }
    }
    return false;
  });

  const { data: jiraData, isLoading: jiraLoading } = useProjectJira(projectId);
  const { mutate: disconnect, isPending: disconnecting } =
    useDisconnectProjectFromJira();

  const jiraMapping = jiraData?.data;

  if (jiraLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">Integrations</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Loader2 className="h-4 w-4 animate-spin" />
            Loading...
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <>
      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">Integrations</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg border bg-muted">
                <ExternalLink className="h-4 w-4" />
              </div>
              <div>
                <p className="text-sm font-medium">Jira</p>
                {jiraMapping ? (
                  <div className="flex items-center gap-2">
                    <Badge variant="default" className="h-5 text-xs">
                      Connected
                    </Badge>
                    <span className="text-xs text-muted-foreground">
                      {jiraMapping.jira_project_key} &mdash;{" "}
                      {jiraMapping.jira_project_name}
                    </span>
                  </div>
                ) : (
                  <p className="text-xs text-muted-foreground">Not Connected</p>
                )}
              </div>
            </div>
            <div className="flex gap-2">
              {jiraMapping ? (
                <>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setShowConnect(true)}
                  >
                    Change Project
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => disconnect(projectId)}
                    disabled={disconnecting}
                  >
                    {disconnecting ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <Unlink className="h-4 w-4" />
                    )}
                    Disconnect
                  </Button>
                </>
              ) : (
                <Button size="sm" onClick={() => setShowConnect(true)}>
                  Connect
                </Button>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      <JiraConnectDialog
        open={showConnect}
        onClose={() => setShowConnect(false)}
        projectId={projectId}
        clientId={clientId}
        existingMapping={jiraMapping ?? undefined}
      />
    </>
  );
}
