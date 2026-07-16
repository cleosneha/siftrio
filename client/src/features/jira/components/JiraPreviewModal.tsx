"use client";

import { useState, useMemo, useRef } from "react";
import { Loader2, Search, ExternalLink } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  useActionItemJiraPreview,
  useActionItemJiraIssueTypes,
  useCreateActionItemJiraIssue,
} from "@/features/jira/hooks/useJira";
import { jiraService } from "@/features/jira/services/jira.service";
import type { JiraUser, ActionItemJiraPreview as PreviewData } from "@/features/jira/types/jira.types";

interface JiraPreviewModalProps {
  open: boolean;
  onClose: () => void;
  projectId: string;
  actionItemId: string;
}

export function JiraPreviewModal({
  open,
  onClose,
  projectId,
  actionItemId,
}: JiraPreviewModalProps) {
  return (
    <Dialog open={open} onOpenChange={(v) => { if (!v) onClose(); }}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>Create Jira Issue</DialogTitle>
          <DialogDescription>
            Review and confirm the action item before creating a Jira issue.
          </DialogDescription>
        </DialogHeader>

        {open && actionItemId ? (
          <JiraPreviewForm
            key={actionItemId}
            projectId={projectId}
            actionItemId={actionItemId}
            onClose={onClose}
          />
        ) : null}
      </DialogContent>
    </Dialog>
  );
}

function JiraPreviewForm({
  projectId,
  actionItemId,
  onClose,
}: {
  projectId: string;
  actionItemId: string;
  onClose: () => void;
}) {
  const { data: previewData, isLoading: previewLoading } = useActionItemJiraPreview(projectId, actionItemId);
  const { data: issueTypesData } = useActionItemJiraIssueTypes(projectId, actionItemId);
  const createMutation = useCreateActionItemJiraIssue();

  const preview = previewData?.data ?? null;
  const issueTypes = useMemo(() => issueTypesData?.data ?? [], [issueTypesData?.data]);

  const defaultIssueTypeId = useMemo(() => {
    if (issueTypes.length === 0) return "";
    const task = issueTypes.find((t) => t.name.toLowerCase() === "task");
    return task?.id ?? issueTypes[0].id;
  }, [issueTypes]);

  if (previewLoading || !preview) {
    return (
      <div className="flex items-center justify-center py-8">
        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <JiraPreviewFormFields
      preview={preview}
      issueTypes={issueTypes}
      projectId={projectId}
      actionItemId={actionItemId}
      onClose={onClose}
      createMutation={createMutation}
      defaultIssueTypeId={defaultIssueTypeId}
    />
  );
}

function JiraPreviewFormFields({
  preview,
  issueTypes,
  projectId,
  actionItemId,
  onClose,
  createMutation,
  defaultIssueTypeId,
}: {
  preview: PreviewData;
  issueTypes: { id: string; name: string; description: string | null; subtask: boolean }[];
  projectId: string;
  actionItemId: string;
  onClose: () => void;
  createMutation: ReturnType<typeof useCreateActionItemJiraIssue>;
  defaultIssueTypeId: string;
}) {
  const [summary, setSummary] = useState(preview.summary);
  const [description, setDescription] = useState(preview.description);
  const [issueTypeId, setIssueTypeId] = useState(defaultIssueTypeId);
  const [labelsStr, setLabelsStr] = useState(preview.labels.join(", "));
  const [assigneeQuery, setAssigneeQuery] = useState("");
  const [users, setUsers] = useState<JiraUser[]>([]);
  const [selectedUser, setSelectedUser] = useState<JiraUser | null>(null);
  const [searchingUsers, setSearchingUsers] = useState(false);
  const searchTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const handleSearchUsers = (q: string) => {
    setAssigneeQuery(q);
    if (searchTimer.current) clearTimeout(searchTimer.current);
    if (!q.trim()) {
      setUsers([]);
      return;
    }
    searchTimer.current = setTimeout(async () => {
      setSearchingUsers(true);
      try {
        const res = await jiraService.searchActionItemJiraUsers(projectId, actionItemId, q);
        setUsers(res.data ?? []);
      } catch {
        setUsers([]);
      } finally {
        setSearchingUsers(false);
      }
    }, 300);
  };

  const handleCreate = async () => {
    if (!summary.trim() || !issueTypeId) return;
    await createMutation.mutateAsync({
      projectId,
      actionItemId,
      data: {
        summary: summary.trim(),
        description: description.trim(),
        issue_type_id: issueTypeId,
        priority: "Medium",
        labels: labelsStr
          .split(",")
          .map((l) => l.trim())
          .filter(Boolean),
        assignee_account_id: selectedUser?.account_id ?? null,
        assignee_name: selectedUser?.display_name ?? null,
        assignee_email: selectedUser?.email_address ?? null,
      },
    });
    onClose();
  };

  const isCreating = createMutation.isPending;

  return (
    <>
      <div className="grid gap-4">
        <div>
          <label className="mb-1 block text-sm font-medium">Summary</label>
          <Input value={summary} onChange={(e) => setSummary(e.target.value)} />
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium">Description</label>
          <Textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={5}
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="mb-1 block text-sm font-medium">Issue Type</label>
            <select
              className="h-8 w-full rounded-lg border border-input bg-transparent px-2.5 text-sm"
              value={issueTypeId}
              onChange={(e) => setIssueTypeId(e.target.value)}
            >
              <option value="">Select type...</option>
              {issueTypes.map((t) => (
                <option key={t.id} value={t.id}>
                  {t.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium">Labels</label>
            <Input
              value={labelsStr}
              onChange={(e) => setLabelsStr(e.target.value)}
              placeholder="comma-separated"
            />
          </div>
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium">
            Assignee {selectedUser ? `(${selectedUser.display_name})` : "(Unassigned)"}
          </label>
          <div className="relative">
            <Search className="absolute left-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              className="pl-8"
              placeholder="Search Jira users..."
              value={assigneeQuery}
              onChange={(e) => handleSearchUsers(e.target.value)}
            />
          </div>
          {searchingUsers && (
            <div className="mt-1 flex items-center gap-1 text-xs text-muted-foreground">
              <Loader2 className="h-3 w-3 animate-spin" />
              Searching...
            </div>
          )}
          {users.length > 0 && (
            <div className="mt-1 max-h-32 overflow-y-auto rounded-lg border">
              {users.map((u) => (
                <button
                  key={u.account_id}
                  type="button"
                  className={`w-full px-3 py-1.5 text-left text-sm hover:bg-muted ${
                    selectedUser?.account_id === u.account_id ? "bg-muted font-medium" : ""
                  }`}
                  onClick={() => {
                    setSelectedUser(u);
                    setAssigneeQuery(u.display_name);
                    setUsers([]);
                  }}
                >
                  {u.display_name}
                  {u.email_address ? (
                    <span className="ml-2 text-xs text-muted-foreground">
                      {u.email_address}
                    </span>
                  ) : null}
                </button>
              ))}
            </div>
          )}
          {selectedUser && (
            <button
              type="button"
              className="mt-1 text-xs text-muted-foreground hover:text-foreground"
              onClick={() => {
                setSelectedUser(null);
                setAssigneeQuery("");
              }}
            >
              Clear assignee
            </button>
          )}
        </div>
      </div>

      <DialogFooter>
        <Button variant="outline" onClick={onClose} disabled={isCreating}>
          Cancel
        </Button>
        <Button onClick={handleCreate} disabled={!summary.trim() || !issueTypeId || isCreating}>
          {isCreating ? (
            <>
              <Loader2 className="mr-1 h-3 w-3 animate-spin" />
              Creating...
            </>
          ) : (
            <>
              <ExternalLink className="mr-1 h-3 w-3" />
              Create Issue
            </>
          )}
        </Button>
      </DialogFooter>
    </>
  );
}
