import hcpInteractionReducer from "./hcpInteractionSlice";
import type { HcpAssistantResponse } from "../types/interaction";

function assertEqual<T>(actual: T, expected: T, label: string) {
  if (actual !== expected) {
    throw new Error(`${label}: expected ${String(expected)}, got ${String(actual)}`);
  }
}

function assertDeepEqual<T>(actual: T, expected: T, label: string) {
  if (JSON.stringify(actual) !== JSON.stringify(expected)) {
    throw new Error(`${label}: expected ${JSON.stringify(expected)}, got ${JSON.stringify(actual)}`);
  }
}

function fulfilled(response: HcpAssistantResponse) {
  return {
    type: "hcpInteraction/sendDraftMessage/fulfilled",
    payload: response,
  };
}

function logResponse(data: Record<string, unknown>): HcpAssistantResponse {
  return {
    tool_used: "log_interaction",
    success: true,
    data,
    assistant_response: "ok",
    conversation_id: "regression-conversation",
    conversation_history: [],
  };
}

let state = hcpInteractionReducer(
  undefined,
  fulfilled(
    logResponse({
      hcp_name: "Dr. Rahul Verma",
      interaction_type: "meeting",
      interaction_date: "2026-07-11",
      interaction_time: "11:00:00",
      attendees: ["Dr. Rahul Verma"],
      topics_discussed: "Initial meeting",
      materials_shared: ["brochure"],
      samples_distributed: [],
      sentiment: "positive",
      outcomes: "Interested",
      follow_up_actions: "Send follow-up email",
    }),
  ),
);

assertEqual(state.form.hcpName, "Dr. Rahul Verma", "first hcpName");
assertEqual(state.form.interactionTime, "11:00", "first interactionTime");
assertDeepEqual(state.form.materialsShared, ["brochure"], "first materialsShared");
assertEqual(state.form.followUpActions, "Send follow-up email", "first followUpActions");

state = hcpInteractionReducer(
  state,
  fulfilled(
    logResponse({
      hcp_name: "Dr. Rohan",
      interaction_type: "meeting",
      interaction_date: "2026-07-11",
      topics_discussed: "Discussed new product",
      sentiment: "neutral",
    }),
  ),
);

assertEqual(state.form.hcpName, "Dr. Rohan", "second hcpName");
assertEqual(state.form.interactionTime, "", "second interactionTime");
assertEqual(state.form.attendees, "", "second attendees");
assertDeepEqual(state.form.materialsShared, [], "second materialsShared");
assertDeepEqual(state.form.samplesDistributed, [], "second samplesDistributed");
assertEqual(state.form.followUpActions, "", "second followUpActions");

console.log("hcpInteractionSlice regression passed: log_interaction resets stale form state.");
