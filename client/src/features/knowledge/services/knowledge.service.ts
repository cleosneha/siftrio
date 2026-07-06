import { api } from "@/lib/api";
import type { ApiResponse, Requirement, ActionItem, Decision, Risk, Question } from "@/types";

export const knowledgeService = {
  async listRequirements(params?: { project_id?: string; meeting_id?: string; status?: string }) {
    const res = await api.get<ApiResponse<Requirement[]>>("/knowledge/requirements", { params });
    return res.data;
  },

  async getRequirement(id: string) {
    const res = await api.get<ApiResponse<Requirement>>(`/knowledge/requirements/${id}`);
    return res.data;
  },

  async updateRequirement(id: string, data: Partial<Requirement>) {
    const res = await api.patch<ApiResponse<Requirement>>(`/knowledge/requirements/${id}`, data);
    return res.data;
  },

  async listActionItems(params?: { project_id?: string; meeting_id?: string; status?: string }) {
    const res = await api.get<ApiResponse<ActionItem[]>>("/knowledge/action-items", { params });
    return res.data;
  },

  async getActionItem(id: string) {
    const res = await api.get<ApiResponse<ActionItem>>(`/knowledge/action-items/${id}`);
    return res.data;
  },

  async updateActionItem(id: string, data: Partial<ActionItem>) {
    const res = await api.patch<ApiResponse<ActionItem>>(`/knowledge/action-items/${id}`, data);
    return res.data;
  },

  async listDecisions(params?: { project_id?: string; meeting_id?: string; status?: string }) {
    const res = await api.get<ApiResponse<Decision[]>>("/knowledge/decisions", { params });
    return res.data;
  },

  async getDecision(id: string) {
    const res = await api.get<ApiResponse<Decision>>(`/knowledge/decisions/${id}`);
    return res.data;
  },

  async updateDecision(id: string, data: Partial<Decision>) {
    const res = await api.patch<ApiResponse<Decision>>(`/knowledge/decisions/${id}`, data);
    return res.data;
  },

  async listRisks(params?: { project_id?: string; meeting_id?: string; status?: string }) {
    const res = await api.get<ApiResponse<Risk[]>>("/knowledge/risks", { params });
    return res.data;
  },

  async getRisk(id: string) {
    const res = await api.get<ApiResponse<Risk>>(`/knowledge/risks/${id}`);
    return res.data;
  },

  async updateRisk(id: string, data: Partial<Risk>) {
    const res = await api.patch<ApiResponse<Risk>>(`/knowledge/risks/${id}`, data);
    return res.data;
  },

  async listQuestions(params?: { project_id?: string; meeting_id?: string; status?: string }) {
    const res = await api.get<ApiResponse<Question[]>>("/knowledge/questions", { params });
    return res.data;
  },

  async getQuestion(id: string) {
    const res = await api.get<ApiResponse<Question>>(`/knowledge/questions/${id}`);
    return res.data;
  },

  async updateQuestion(id: string, data: Partial<Question>) {
    const res = await api.patch<ApiResponse<Question>>(`/knowledge/questions/${id}`, data);
    return res.data;
  },
};
