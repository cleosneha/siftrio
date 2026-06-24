import { api } from "@/lib/api";
import type { ApiResponse, Meeting, MeetingAnalysis } from "@/types";

export const meetingService = {
  async create(data: {
    client_id: string;
    project_id?: string | null;
    title: string;
    meeting_type: string;
    tags?: string[];
    meeting_date?: string | null;
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
};
