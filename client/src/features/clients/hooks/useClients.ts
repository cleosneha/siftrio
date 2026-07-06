"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { clientService } from "@/features/clients/services/client.service";

export function useCreateClient() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: {
      workspace_id: string;
      name: string;
      description?: string | null;
    }) => clientService.create(data),
    onSuccess: (res) => {
      queryClient.invalidateQueries({ queryKey: ["clients"] });
      queryClient.invalidateQueries({ queryKey: ["workspaces"] });
      toast.success(res.message || "Client created");
    },
    onError: () => {
      toast.error("Failed to create client");
    },
  });
}

export function useClients(workspaceId?: string) {
  return useQuery({
    queryKey: ["clients", workspaceId],
    queryFn: () => clientService.list(workspaceId),
    enabled: !!workspaceId,
  });
}

export function useClient(id: string) {
  return useQuery({
    queryKey: ["client", id],
    queryFn: () => clientService.getById(id),
    enabled: !!id,
  });
}
