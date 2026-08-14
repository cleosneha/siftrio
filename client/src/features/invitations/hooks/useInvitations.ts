"use client";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { notifyError } from "@/lib/error";
import { invitationService } from "@/features/invitations/services/invitation.service";

export function useInviteMember(resourceType: string, resourceId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ email, role }: { email: string; role: string }) =>
      invitationService.invite(resourceType, resourceId, email, role),
    onSuccess: (res) => {
      queryClient.invalidateQueries({ queryKey: ["pending-invitations", resourceType, resourceId] });
      queryClient.invalidateQueries({ queryKey: [`${resourceType}-members`, resourceId] });
      toast.success(res.message || "Invitation sent");
    },
    onError: (err: unknown) => notifyError(err, "Failed to send invitation"),
  });
}

export function useBulkInviteMembers(resourceType: string, resourceId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ emails, role }: { emails: string[]; role: string }) =>
      Promise.all(
        emails.map((email) =>
          invitationService.invite(resourceType, resourceId, email, role),
        ),
      ),
    onSuccess: () => {
      toast.success("Invitations sent");
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["pending-invitations", resourceType, resourceId] });
      queryClient.invalidateQueries({ queryKey: [`${resourceType}-members`, resourceId] });
    },
    onError: (err: unknown) => notifyError(err, "Failed to send invitations"),
  });
}

export function usePendingInvitations(resourceType: string, resourceId: string) {
  return useQuery({
    queryKey: ["pending-invitations", resourceType, resourceId],
    queryFn: () => invitationService.listPending(resourceType, resourceId),
    enabled: !!resourceType && !!resourceId,
  });
}

export function useWithdrawInvitation(resourceType: string, resourceId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (invitationId: string) => invitationService.withdraw(invitationId),
    onSuccess: (res) => {
      queryClient.invalidateQueries({ queryKey: ["pending-invitations", resourceType, resourceId] });
      toast.success(res.message || "Invitation withdrawn");
    },
    onError: (err: unknown) => notifyError(err, "Failed to withdraw invitation"),
  });
}
