import type { HcpAssistantRequest, HcpAssistantResponse } from "../types/interaction";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api/v1";

export async function sendHcpAssistantMessage(
  payload: HcpAssistantRequest,
): Promise<HcpAssistantResponse> {
  const response = await fetch(`${API_BASE_URL}/hcp-assistant/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    let detail = `Assistant request failed with HTTP ${response.status}`;

    try {
      const errorBody = (await response.json()) as { detail?: string };
      detail = errorBody.detail ?? detail;
    } catch {
      // Keep the status-based message when the response body is not JSON.
    }

    throw new Error(detail);
  }

  return (await response.json()) as HcpAssistantResponse;
}
