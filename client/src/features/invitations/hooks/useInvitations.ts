"use client";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { invitationService } from "@/features/invitations/services/invitation.service";

export function useInviteMember(resourceType: string, resourceId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (email: string) => invitationService.invite(resourceType, resourceId, email),
    onSuccess: (res) => {
      queryClient.invalidateQueries({ queryKey: ["pending-invitations", resourceType, resourceId] });
      queryClient.invalidateQueries({ queryKey: [`${resourceType}-members`, resourceId] });
      toast.success(res.message || "Invitation sent");
    },
    onError: (err: unknown) => {
      const error = err as { response?: { data?: { message?: string } } };
      toast.error(error.response?.data?.message || "Failed to send invitation");
    },
  });
}

export function usePendingInvitations(resourceType: string, resourceId: string) {
  return useQuery({
    queryKey: ["pending-invitations", resourceType, resourceId],
    queryFn: () => invitationService.listPending(resourceType, resourceId),
    enabled: !!resourceType && !!resourceId,
  });
}
