"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { meetingService } from "@/services/meeting.service";

export function useCreateMeeting() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: {
      client_id: string;
      project_id?: string | null;
      title: string;
      meeting_type: string;
      tags?: string[];
      meeting_date?: string | null;
      meeting_provider?: string;
      meeting_url?: string | null;
      start_time?: string | null;
      end_time?: string | null;
    }) => meetingService.create(data),
    onSuccess: (res) => {
      queryClient.invalidateQueries({ queryKey: ["meetings"] });
      queryClient.invalidateQueries({ queryKey: ["clients"] });
      toast.success(res.message || "Meeting created");
    },
    onError: () => {
      toast.error("Failed to create meeting");
    },
  });
}

export function useMeetingsByClient(clientId?: string) {
  return useQuery({
    queryKey: ["meetings", "client", clientId],
    queryFn: () => meetingService.listByClient(clientId!),
    enabled: !!clientId,
  });
}

export function useMeetingsByProject(projectId?: string) {
  return useQuery({
    queryKey: ["meetings", "project", projectId],
    queryFn: () => meetingService.listByProject(projectId!),
    enabled: !!projectId,
  });
}

export function useMiscellaneousMeetings(clientId?: string) {
  return useQuery({
    queryKey: ["meetings", "miscellaneous", clientId],
    queryFn: () => meetingService.listMiscellaneous(clientId!),
    enabled: !!clientId,
  });
}

export function useMeeting(id: string) {
  return useQuery({
    queryKey: ["meeting", id],
    queryFn: () => meetingService.getById(id),
    enabled: !!id,
  });
}

export function useUploadTranscript() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      meetingId,
      file,
    }: {
      meetingId: string;
      file: File;
    }) => meetingService.uploadTranscript(meetingId, file),
    onSuccess: (res) => {
      queryClient.invalidateQueries({ queryKey: ["meetings"] });
      queryClient.invalidateQueries({ queryKey: ["meeting"] });
      toast.success(
        `Transcript processed: ${res.data?.chunk_count ?? 0} chunks created`,
      );
    },
    onError: () => {
      toast.error("Failed to upload transcript");
    },
  });
}

export function useDeleteMeeting() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => meetingService.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["meetings"] });
      toast.success("Meeting deleted");
    },
    onError: () => {
      toast.error("Failed to delete meeting");
    },
  });
}

export function useMeetingAnalysis(meetingId?: string) {
  return useQuery({
    queryKey: ["meeting-analysis", meetingId],
    queryFn: () => meetingService.getAnalysis(meetingId!),
    enabled: !!meetingId,
  });
}

export function useRegenerateAnalysis() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (meetingId: string) =>
      meetingService.regenerateAnalysis(meetingId),
    onSuccess: (res) => {
      queryClient.invalidateQueries({ queryKey: ["meeting-analysis"] });
      toast.success(res.message || "Analysis regenerated");
    },
    onError: (err: unknown) => {
      const msg =
        err instanceof Error ? err.message : "Failed to regenerate analysis";
      toast.error(msg);
    },
  });
}
