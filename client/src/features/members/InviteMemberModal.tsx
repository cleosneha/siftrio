"use client";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Loader2 } from "lucide-react";
import {
  Form,
  FormField,
  FormItem,
  FormLabel,
  FormControl,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { TabBar } from "@/components/ui/tab-bar";
import { toastFormErrors } from "@/lib/form";
import { useInviteMember } from "@/features/invitations/hooks/useInvitations";
import { useAuth } from "@/features/auth/AuthProvider";
import { AddExistingMembersTab } from "./AddExistingMembersTab";

const INVITE_ROLES = ["admin", "member", "viewer"] as const;

const inviteSchema = z.object({
  email: z.string().email("Invalid email address"),
  role: z.enum(INVITE_ROLES),
});

type InviteForm = z.infer<typeof inviteSchema>;

interface InviteMemberModalProps {
  open: boolean;
  onClose: () => void;
  resourceType: string;
  resourceId: string;
  workspaceId?: string;
}

export function InviteMemberModal({
  open,
  onClose,
  resourceType,
  resourceId,
  workspaceId,
}: InviteMemberModalProps) {
  const { user } = useAuth();
  const inviteMutation = useInviteMember(resourceType, resourceId);
  const [tab, setTab] = useState<"new" | "existing">("new");

  const schema = inviteSchema.refine(
    (data) => data.email.trim().toLowerCase() !== (user?.email ?? "").trim().toLowerCase(),
    { path: ["email"], message: "You cannot invite yourself" },
  );

  const form = useForm<InviteForm>({
    resolver: zodResolver(schema),
    defaultValues: { email: "", role: "member" },
  });

  async function onSubmit(data: InviteForm) {
    await inviteMutation.mutateAsync({ email: data.email, role: data.role });
    form.reset();
    onClose();
  }

  const showExistingTab = resourceType !== "workspace" && !!workspaceId;

  return (
    <Dialog open={open} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Invite Member</DialogTitle>
          <DialogDescription>
            Invite someone to join this {resourceType}.
          </DialogDescription>
        </DialogHeader>
        {showExistingTab && (
          <TabBar
            className="mb-4"
            tabs={[
              { value: "new", label: "Add New Member" },
              { value: "existing", label: "Add Existing Workspace Member" },
            ]}
            activeTab={tab}
            onTabChange={(value) => setTab(value as "new" | "existing")}
          />
        )}
        {tab === "existing" && showExistingTab ? (
          <AddExistingMembersTab
            resourceType={resourceType as "client" | "project"}
            resourceId={resourceId}
            workspaceId={workspaceId ?? ""}
            onClose={onClose}
          />
        ) : (
          <Form {...form}>
            <form
              onSubmit={form.handleSubmit(onSubmit, toastFormErrors)}
              className="space-y-4"
            >
              <FormField
                control={form.control}
                name="email"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Email</FormLabel>
                    <FormControl>
                      <Input placeholder="colleague@company.com" {...field} />
                    </FormControl>
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="role"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Role</FormLabel>
                    <FormControl>
                      <Select value={field.value} onValueChange={field.onChange}>
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {INVITE_ROLES.map((role) => (
                            <SelectItem key={role} value={role}>
                              {role.charAt(0).toUpperCase() + role.slice(1)}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </FormControl>
                  </FormItem>
                )}
              />
              <div className="flex justify-end gap-2">
                <Button
                  type="button"
                  variant="outline"
                  onClick={onClose}
                  disabled={inviteMutation.isPending}
                >
                  Cancel
                </Button>
                <Button type="submit" disabled={inviteMutation.isPending}>
                  {inviteMutation.isPending && (
                    <Loader2 className="animate-spin" />
                  )}
                  {inviteMutation.isPending ? "Sending..." : "Send Invitation"}
                </Button>
              </div>
            </form>
          </Form>
        )}
      </DialogContent>
    </Dialog>
  );
}
