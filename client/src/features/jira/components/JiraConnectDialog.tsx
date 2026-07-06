"use client";

import { useState, useEffect } from "react";
import { Loader2, Plus, Check, ExternalLink } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button, buttonVariants } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";
import { Separator } from "@/components/ui/separator";
import {
  useAvailableJiraProjects,
  useConnectProjectToJira,
  useCreateAndConnectJiraProject,
} from "@/features/jira/hooks/useJira";
import type { ProjectJira } from "@/features/jira/types/jira.types";
import { api } from "@/lib/api";

interface JiraConnectDialogProps {
  open: boolean;
  onClose: () => void;
  projectId: string;
  clientId: string;
  existingMapping?: ProjectJira;
}

type Step = "checking" | "oauth" | "select-project" | "create-project" | "done";

export function JiraConnectDialog({
  open,
  onClose,
  projectId,
  clientId,
  existingMapping,
}: JiraConnectDialogProps) {
  const [step, setStep] = useState<Step>("checking");
  const [workspaceId, setWorkspaceId] = useState<string | null>(null);
  const [selectedProjectId, setSelectedProjectId] = useState<string>("");
  const [projectName, setProjectName] = useState("");
  const [projectKey, setProjectKey] = useState("");
  const [projectType, setProjectType] = useState("software");

  const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";
  const connectUrl = workspaceId ? `${backendUrl}/workspaces/${workspaceId}/jira/connect` : "#";

  const { data: projectsData, isLoading: projectsLoading } = useAvailableJiraProjects(
    step === "select-project" ? projectId : undefined
  );
  const connectProject = useConnectProjectToJira();
  const createProject = useCreateAndConnectJiraProject();

  useEffect(() => {
    async function resolveWorkspace() {
      if (!open) return;
      try {
        const res = await api.get(`/clients/${clientId}`);
        if (res.data?.data?.workspace_id) {
          setWorkspaceId(res.data.data.workspace_id);
        }
      } catch {
        // fallback: try connecting directly
      }
    }
    resolveWorkspace();
  }, [open, clientId]);

  useEffect(() => {
    if (!workspaceId) return;
    (async () => {
      try {
        const res = await api.get(`/workspaces/${workspaceId}/jira`);
        if (res.data?.success && res.data?.data) {
          setStep("select-project");
        } else {
          setStep("oauth");
        }
      } catch {
        setStep("oauth");
      }
    })();
  }, [workspaceId]);

  const handleSelectProject = (jiraProjectId: string) => {
    const project = projectsData?.data?.find((p) => p.id === jiraProjectId);
    if (!project) return;
    setSelectedProjectId(jiraProjectId);
    connectProject.mutate(
      {
        projectId,
        data: {
          jira_project_id: project.id,
          jira_project_key: project.key,
          jira_project_name: project.name,
          jira_project_type: project.projectTypeKey,
        },
      },
      {
        onSuccess: () => {
          setStep("done");
        },
      }
    );
  };

  const handleCreateProject = () => {
    createProject.mutate(
      {
        projectId,
        data: {
          key: projectKey,
          name: projectName,
          project_type_key: projectType,
        },
      },
      {
        onSuccess: () => {
          setStep("done");
        },
      }
    );
  };

  return (
    <Dialog open={open} onOpenChange={(v) => {
      if (!v) {
        setStep("checking");
        setSelectedProjectId("");
        setProjectName("");
        setProjectKey("");
        setProjectType("software");
        setWorkspaceId(null);
        onClose();
      }
    }}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>
            {existingMapping ? "Change Jira Project" : "Connect Jira"}
          </DialogTitle>
          <DialogDescription>
            {step === "oauth" && "Connect your workspace to Atlassian to get started."}
            {step === "select-project" && "Choose a Jira project to connect."}
            {step === "create-project" && "Create a new Jira project."}
            {step === "done" && "Jira project connected successfully."}
          </DialogDescription>
        </DialogHeader>

        {step === "checking" && (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
          </div>
        )}

        {step === "oauth" && (
          <div className="space-y-4 py-4">
            <p className="text-sm text-muted-foreground">
              Your workspace needs to be connected to Atlassian first. You will be redirected to
              Atlassian to authorize the connection.
            </p>
            <a
              href={connectUrl}
              target="_blank"
              rel="noopener noreferrer"
              className={cn(buttonVariants({ className: "w-full" }))}
              onClick={() => sessionStorage.setItem("jira_project_redirect", projectId)}
            >
              <ExternalLink className="mr-2 h-4 w-4" />
              Connect to Atlassian
            </a>
          </div>
        )}

        {step === "select-project" && (
          <div className="space-y-3 py-4">
            {projectsLoading ? (
              <div className="flex items-center justify-center py-4">
                <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
              </div>
            ) : (
              <>
                <div className="max-h-48 space-y-1 overflow-y-auto">
                  {(projectsData?.data ?? []).map((proj) => (
                    <button
                      key={proj.id}
                      type="button"
                      className={`w-full rounded-md border px-3 py-2 text-left text-sm transition-colors hover:bg-accent ${
                        selectedProjectId === proj.id
                          ? "border-primary bg-primary/5"
                          : "border-border"
                      }`}
                      onClick={() => setSelectedProjectId(proj.id)}
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <span className="font-medium">{proj.key}</span>
                          <span className="ml-2 text-muted-foreground">{proj.name}</span>
                        </div>
                        {selectedProjectId === proj.id && (
                          <Check className="h-4 w-4 text-primary" />
                        )}
                      </div>
                    </button>
                  ))}
                </div>

                <Separator />

                <Button
                  variant="ghost"
                  className="w-full"
                  onClick={() => setStep("create-project")}
                >
                  <Plus className="mr-2 h-4 w-4" />
                  Create New Jira Project
                </Button>

                <Button
                  className="w-full"
                  disabled={!selectedProjectId || connectProject.isPending}
                  onClick={() => handleSelectProject(selectedProjectId)}
                >
                  {connectProject.isPending ? (
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  ) : null}
                  Connect Selected Project
                </Button>
              </>
            )}
          </div>
        )}

        {step === "create-project" && (
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <label htmlFor="project-name" className="text-sm font-medium">Project Name</label>
              <Input
                id="project-name"
                value={projectName}
                onChange={(e) => {
                  setProjectName(e.target.value);
                  if (!projectKey || projectKey === autoSuggestKey(projectName)) {
                    setProjectKey(autoSuggestKey(e.target.value));
                  }
                }}
                placeholder="CRM Portal"
              />
            </div>
            <div className="space-y-2">
              <label htmlFor="project-key" className="text-sm font-medium">Project Key</label>
              <Input
                id="project-key"
                value={projectKey}
                onChange={(e) => setProjectKey(e.target.value.toUpperCase())}
                placeholder="CRM"
              />
            </div>
            <div className="space-y-2">
              <label htmlFor="project-type" className="text-sm font-medium">Project Type</label>
              <select
                id="project-type"
                value={projectType}
                onChange={(e) => setProjectType(e.target.value)}
                className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
              >
                <option value="software">Software</option>
                <option value="business">Business</option>
              </select>
            </div>
            <div className="flex gap-2">
              <Button
                variant="outline"
                onClick={() => setStep("select-project")}
              >
                Back
              </Button>
              <Button
                className="flex-1"
                disabled={!projectName || !projectKey || createProject.isPending}
                onClick={handleCreateProject}
              >
                {createProject.isPending ? (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                ) : null}
                Create
              </Button>
            </div>
          </div>
        )}

        {step === "done" && (
          <div className="space-y-4 py-4">
            <div className="flex items-center justify-center">
              <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary/10">
                <Check className="h-6 w-6 text-primary" />
              </div>
            </div>
            <p className="text-center text-sm text-muted-foreground">
              Your project is now connected to Jira.
            </p>
            <Button className="w-full" onClick={onClose}>
              Done
            </Button>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}

function autoSuggestKey(name: string): string {
  if (!name) return "";
  const words = name.trim().split(/\s+/);
  if (words.length === 1) {
    const w = words[0].toUpperCase();
    return w.slice(0, 10);
  }
  const key = words
    .map((w) => w.charAt(0).toUpperCase())
    .join("")
    .slice(0, 10);
  return key;
}
