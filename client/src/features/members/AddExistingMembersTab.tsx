"use client";
import { useState } from "react";
import { Checkbox } from "@/components/ui/checkbox";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Loader2 } from "lucide-react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  useWorkspaceMembers,
  useClientMembers,
  useProjectMembers,
} from "@/features/members/hooks/useMembers";
import {
  usePendingInvitations,
  useBulkInviteMembers,
} from "@/features/invitations/hooks/useInvitations";
import { useAuth } from "@/features/auth/AuthProvider";

const INVITE_ROLES = ["admin", "member", "viewer"] as const;

interface AddExistingMembersTabProps {
  resourceType: "client" | "project";
  resourceId: string;
  workspaceId: string;
  onClose: () => void;
}

export function AddExistingMembersTab({
  resourceType,
  resourceId,
  workspaceId,
  onClose,
}: AddExistingMembersTabProps) {
  const { user } = useAuth();
  const { data: workspaceMembersData, isLoading: membersLoading } =
    useWorkspaceMembers(workspaceId);
  const { data: clientMembersData } = useClientMembers(
    resourceType === "client" ? resourceId : "",
  );
  const { data: projectMembersData } = useProjectMembers(
    resourceType === "project" ? resourceId : "",
  );
  const { data: pendingData } = usePendingInvitations(resourceType, resourceId);
  const inviteMutation = useBulkInviteMembers(resourceType, resourceId);

  const [query, setQuery] = useState("");
  const [role, setRole] = useState("member");
  const [selected, setSelected] = useState<Set<string>>(new Set());

  const workspaceMembers = workspaceMembersData?.data ?? [];
  const existingMembers =
    resourceType === "client"
      ? (clientMembersData?.data ?? [])
      : (projectMembersData?.data ?? []);
  const existingEmails = new Set(existingMembers.map((m) => m.email));
  const pendingEmails = new Set(
    (pendingData?.data ?? []).map((inv) => inv.email),
  );

  const q = query.trim().toLowerCase();
  const candidates = workspaceMembers.filter((m) => {
    if (existingEmails.has(m.email)) return false;
    if (pendingEmails.has(m.email)) return false;
    if (m.user_id === user?.id) return false;
    if (!q) return true;
    return (
      (m.full_name ?? "").toLowerCase().includes(q) ||
      m.email.toLowerCase().includes(q)
    );
  });

  const selectedMembers = workspaceMembers.filter((m) =>
    selected.has(m.user_id),
  );

  function toggle(userId: string) {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(userId)) next.delete(userId);
      else next.add(userId);
      return next;
    });
  }

  async function sendInvites() {
    await inviteMutation.mutateAsync({
      emails: selectedMembers.map((m) => m.email),
      role,
    });
    onClose();
  }

  return (
    <div className="space-y-4">
      <Input
        placeholder="Search by name or email"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />
      <div className="max-h-64 space-y-1 overflow-y-auto">
        {membersLoading ? (
          <p className="text-sm text-muted-foreground">Loading members...</p>
        ) : candidates.length === 0 ? (
          <p className="text-sm text-muted-foreground">
            No workspace members available to invite.
          </p>
        ) : (
          candidates.map((m) => (
            <label
              key={m.user_id}
              className="flex cursor-pointer items-center gap-3 rounded-md px-2 py-2 hover:bg-muted/50"
            >
              <Checkbox
                checked={selected.has(m.user_id)}
                onCheckedChange={() => toggle(m.user_id)}
              />
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary/10 text-xs font-medium text-primary">
                {(m.full_name ?? m.email)?.[0]?.toUpperCase() ?? "?"}
              </div>
              <div className="min-w-0">
                <p className="truncate text-sm font-medium">
                  {m.full_name || m.email}
                </p>
                <p className="truncate text-xs text-muted-foreground">
                  {m.email}
                </p>
              </div>
              <span className="ml-auto text-xs capitalize text-muted-foreground">
                {m.role}
              </span>
            </label>
          ))
        )}
      </div>
      <Select
        value={role}
        onValueChange={(value) => setRole(value ?? "member")}
      >
        <SelectTrigger>
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          {INVITE_ROLES.map((r) => (
            <SelectItem key={r} value={r}>
              {r.charAt(0).toUpperCase() + r.slice(1)}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
      <div className="flex justify-end gap-2">
        <Button
          type="button"
          variant="outline"
          onClick={onClose}
          disabled={inviteMutation.isPending}
        >
          Cancel
        </Button>
        <Button
          type="button"
          onClick={sendInvites}
          disabled={selectedMembers.length === 0 || inviteMutation.isPending}
        >
          {inviteMutation.isPending && <Loader2 className="animate-spin" />}
          {inviteMutation.isPending
            ? "Sending..."
            : `Send Invitation${selectedMembers.length > 1 ? "s" : ""}`}
        </Button>
      </div>
    </div>
  );
}
