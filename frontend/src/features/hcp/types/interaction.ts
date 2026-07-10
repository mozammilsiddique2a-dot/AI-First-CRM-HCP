export type InteractionType = "meeting" | "call" | "email" | "field-visit";
export type Sentiment = "positive" | "neutral" | "negative";

export interface InteractionFormState {
  hcpName: string;
  interactionDate: string;
  interactionTime: string;
  interactionType: InteractionType;
  attendees: string;
  topicsDiscussed: string;
  materialsShared: string[];
  samplesDistributed: string[];
  sentiment: Sentiment;
  outcomes: string;
  followUpActions: string;
}

export interface ChatMessage {
  id: string;
  role: "assistant" | "user";
  content: string;
  timestamp: string;
}

export interface HcpAssistantResponse {
  tool_used: string;
  success: boolean;
  data: Record<string, unknown>;
  assistant_response: string;
  conversation_id: string;
  conversation_history: Array<{
    role: string;
    content: string;
  }>;
}

export interface HcpAssistantRequest {
  message: string;
  conversation_id?: string | null;
}

