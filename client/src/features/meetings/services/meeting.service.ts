import { api } from "@/lib/api";
import type { ApiResponse, Meeting, MeetingAnalysis, SuggestedMeeting } from "@/types";

export const meetingService = {
  async create(data: {
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
    guest_emails?: string[];
  }) {
    const res = await api.post<ApiResponse<Meeting>>("/meetings", data);
    return res.data;
  },

  async getById(id: string) {
    const res = await api.get<ApiResponse<Meeting>>(`/meetings/${id}`);
    return res.data;
  },

  async listByClient(clientId: string) {
    const res = await api.get<ApiResponse<Meeting[]>>("/meetings", {
      params: { client_id: clientId },
    });
    return res.data;
  },

  async listByProject(projectId: string) {
    const res = await api.get<ApiResponse<Meeting[]>>("/meetings", {
      params: { project_id: projectId },
    });
    return res.data;
  },

  async listMiscellaneous(clientId: string) {
    const res = await api.get<ApiResponse<Meeting[]>>("/meetings", {
      params: { client_id: clientId, miscellaneous: true },
    });
    return res.data;
  },

  async delete(id: string) {
    const res = await api.delete<ApiResponse<null>>(`/meetings/${id}`);
    return res.data;
  },

  async uploadTranscript(meetingId: string, file: File) {
    const formData = new FormData();
    formData.append("file", file);
    const res = await api.post<ApiResponse<{
      meeting_id: string;
      chunk_count: number;
      title: string;
    }>>(`/transcripts/${meetingId}`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return res.data;
  },

  async getAnalysis(meetingId: string) {
    const res = await api.get<ApiResponse<MeetingAnalysis>>(
      `/meetings/${meetingId}/analysis`,
    );
    return res.data;
  },

  async regenerateAnalysis(meetingId: string) {
    const res = await api.post<ApiResponse<MeetingAnalysis>>(
      `/meetings/${meetingId}/analysis/regenerate`,
    );
    return res.data;
  },

  async getTranscriptStatus(meetingId: string) {
    const res = await api.get<ApiResponse<{
      transcript_status: string | null;
      fireflies_meeting_id: string | null;
    }>>(`/meetings/${meetingId}/transcript-status`);
    return res.data;
  },

  async getSuggestions(meetingId: string) {
    const res = await api.get<ApiResponse<SuggestedMeeting[]>>(
      `/meetings/${meetingId}/suggestions`,
    );
    return res.data;
  },

  async scheduleSuggestion(
    meetingId: string,
    suggestionId: string,
    overrides?: {
      title?: string;
      description?: string;
      meeting_date?: string;
      start_time?: string;
      end_time?: string;
    },
  ) {
    const res = await api.post<ApiResponse<SuggestedMeeting>>(
      `/meetings/${meetingId}/suggestions/${suggestionId}/schedule`,
      overrides || {},
    );
    return res.data;
  },

  async dismissSuggestion(meetingId: string, suggestionId: string) {
    const res = await api.post<ApiResponse<SuggestedMeeting>>(
      `/meetings/${meetingId}/suggestions/${suggestionId}/dismiss`,
    );
    return res.data;
  },
};
