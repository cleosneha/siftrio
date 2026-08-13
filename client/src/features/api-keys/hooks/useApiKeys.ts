"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { notifyError } from "@/lib/error";
import { apiKeyService } from "../services/apiKey.service";

const QUERY_KEY = ["api-keys"];

export function useApiKeys() {
  return useQuery({
    queryKey: QUERY_KEY,
    queryFn: () => apiKeyService.list(),
  });
}

export function useCreateApiKey() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (name: string) => apiKeyService.create(name),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEY });
    },
    onError: (err: unknown) => notifyError(err, "Failed to create API key"),
  });
}

export function useRevokeApiKey() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => apiKeyService.revoke(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEY });
      toast.success("API key revoked");
    },
    onError: (err: unknown) => notifyError(err, "Failed to revoke API key"),
  });
}

export function useDeleteApiKey() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => apiKeyService.remove(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEY });
      toast.success("API key deleted");
    },
    onError: (err: unknown) => notifyError(err, "Failed to delete API key"),
  });
}
