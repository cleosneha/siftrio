export interface AssistantCitation {
  meeting_id: string | null;
  meeting_title: string;
  meeting_date: string | null;
  chunk_index: number | null;
}

export interface AssistantQueryResponse {
  answer: string;
  citations: AssistantCitation[];
  ambiguous_entities?: Record<string, { id: string; name: string }[]> | null;
}

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  citations?: AssistantCitation[];
  ambiguous_entities?: Record<string, { id: string; name: string }[]> | null;
}
