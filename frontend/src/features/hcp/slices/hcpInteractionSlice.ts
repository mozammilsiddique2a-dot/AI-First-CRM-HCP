import { createAsyncThunk, createSlice, type PayloadAction } from "@reduxjs/toolkit";
import { sendHcpAssistantMessage } from "../api/hcpAssistantApi";
import type {
  ChatMessage,
  HcpAssistantResponse,
  InteractionFormState,
  InteractionType,
  Sentiment,
} from "../types/interaction";

type FormFieldUpdate =
  | { field: "materialsShared" | "samplesDistributed"; value: string[] }
  | {
      field: Exclude<keyof InteractionFormState, "materialsShared" | "samplesDistributed">;
      value: string;
    };

interface HcpInteractionState {
  form: InteractionFormState;
  draftMessage: string;
  messages: ChatMessage[];
  conversationId: string | null;
  structuredData: Record<string, unknown> | null;
  lastToolUsed: string | null;
  isSending: boolean;
  error: string | null;
}

const blankInteractionFormState: InteractionFormState = {
  hcpName: "",
  interactionDate: "",
  interactionTime: "",
  interactionType: "meeting",
  attendees: "",
  topicsDiscussed: "",
  materialsShared: [],
  samplesDistributed: [],
  sentiment: "neutral",
  outcomes: "",
  followUpActions: "",
};

const initialState: HcpInteractionState = {
  form: {
    hcpName: "",
    interactionDate: "19-04-2025",
    interactionTime: "19:36",
    interactionType: "meeting",
    attendees: "",
    topicsDiscussed: "",
    materialsShared: [],
    samplesDistributed: [],
    sentiment: "neutral",
    outcomes: "",
    followUpActions: "",
  },
  draftMessage: "",
  messages: [
    {
      id: "assistant-welcome",
      role: "assistant",
      content:
        'Log interaction details here (e.g., "Met Dr. Smith, discussed Product X efficacy, positive sentiment, shared brochure") or ask for help.',
      timestamp: "Now",
    },
  ],
  conversationId: null,
  structuredData: null,
  lastToolUsed: null,
  isSending: false,
  error: null,
};

export const sendDraftMessage = createAsyncThunk<
  HcpAssistantResponse,
  string,
  { state: { hcpInteraction: HcpInteractionState }; rejectValue: string }
>("hcpInteraction/sendDraftMessage", async (inputValue, { getState, rejectWithValue }) => {
  const { conversationId } = getState().hcpInteraction;
  const message = inputValue.trim();

  if (!message) {
    return rejectWithValue("Please enter a message.");
  }

  const payload = {
    message,
    conversation_id: conversationId,
  };

  console.log("Thunk payload:", payload);

  try {
    return await sendHcpAssistantMessage(payload);
  } catch (error) {
    return rejectWithValue(error instanceof Error ? error.message : "Assistant request failed.");
  }
});

const hcpInteractionSlice = createSlice({
  name: "hcpInteraction",
  initialState,
  reducers: {
    updateFormField(state, action: PayloadAction<FormFieldUpdate>) {
      const { field, value } = action.payload;

      if (field === "materialsShared") {
        state.form.materialsShared = value;
        return;
      }

      if (field === "samplesDistributed") {
        state.form.samplesDistributed = value;
        return;
      }

      switch (field) {
        case "hcpName":
          state.form.hcpName = value;
          break;
        case "interactionDate":
          state.form.interactionDate = value;
          break;
        case "interactionTime":
          state.form.interactionTime = value;
          break;
        case "interactionType":
          state.form.interactionType = value as InteractionType;
          break;
        case "attendees":
          state.form.attendees = value;
          break;
        case "topicsDiscussed":
          state.form.topicsDiscussed = value;
          break;
        case "sentiment":
          state.form.sentiment = value as Sentiment;
          break;
        case "outcomes":
          state.form.outcomes = value;
          break;
        case "followUpActions":
          state.form.followUpActions = value;
          break;
      }
    },
    setDraftMessage(state, action: PayloadAction<string>) {
      state.draftMessage = action.payload;
      state.error = null;
    },
    setDraftMessageError(state, action: PayloadAction<string>) {
      state.error = action.payload;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(sendDraftMessage.pending, (state, action) => {
        const trimmed = action.meta.arg.trim();

        if (!trimmed) {
          return;
        }

        state.isSending = true;
        state.error = null;
        state.messages.push({
          id: `user-${Date.now()}`,
          role: "user",
          content: trimmed,
          timestamp: "Now",
        });
        state.draftMessage = "";
      })
      .addCase(sendDraftMessage.fulfilled, (state, action) => {
        const response = action.payload;

        state.isSending = false;
        state.error = null;
        state.conversationId = response.conversation_id;
        state.structuredData = response.data;
        state.lastToolUsed = response.tool_used;
        state.messages.push({
          id: `assistant-${Date.now()}`,
          role: "assistant",
          content: response.assistant_response,
          timestamp: "Now",
        });

        if (
          response.success &&
          ["log_interaction", "edit_interaction", "summarize_interaction", "suggest_follow_up_actions"].includes(
            response.tool_used,
          )
        ) {
          applyAssistantDataToForm(state.form, response.tool_used, response.data);
        }
      })
      .addCase(sendDraftMessage.rejected, (state, action) => {
        const message = action.payload ?? "Assistant request failed.";

        state.isSending = false;
        state.error = message;
        state.messages.push({
          id: `assistant-error-${Date.now()}`,
          role: "assistant",
          content: message,
          timestamp: "Now",
        });
      });
  },
});

function applyAssistantDataToForm(
  form: InteractionFormState,
  toolUsed: string,
  data: Record<string, unknown>,
) {
  if (toolUsed === "log_interaction") {
    resetForm(form);
    applyInteractionDataToForm(form, data, "replace");
  }

  if (toolUsed === "edit_interaction") {
    applyInteractionDataToForm(form, data, "merge");
  }

  if (toolUsed === "summarize_interaction") {
    const discussionParts = [
      getString(data.summary),
      ...getArray(data.key_discussion_points),
    ].filter(Boolean);
    const actionItems = getArray(data.action_items);

    if (discussionParts.length > 0) {
      form.topicsDiscussed = discussionParts.join("\n");
    }
    if (actionItems.length > 0) {
      form.followUpActions = actionItems.join("\n");
    }
  }

  if (toolUsed === "suggest_follow_up_actions") {
    const recommendedActions = getArray(data.recommended_actions);
    if (recommendedActions.length > 0) {
      form.followUpActions = recommendedActions.join("\n");
    }
  }
}

function resetForm(form: InteractionFormState) {
  Object.assign(form, {
    ...blankInteractionFormState,
    materialsShared: [],
    samplesDistributed: [],
  });
}

function applyInteractionDataToForm(
  form: InteractionFormState,
  data: Record<string, unknown>,
  mode: "replace" | "merge",
) {
  if (hasField(data, "hcp_name")) {
    setString(data.hcp_name, (value) => {
      form.hcpName = value;
    });
  }

  if (hasField(data, "interaction_date")) {
    setString(data.interaction_date, (value) => {
      form.interactionDate = formatDateForForm(value);
    });
  }

  if (hasField(data, "interaction_time")) {
    setString(data.interaction_time, (value) => {
      form.interactionTime = normalizeTime(value);
    });
  }

  if (hasField(data, "interaction_type")) {
    setString(data.interaction_type, (value) => {
      form.interactionType = normalizeInteractionType(value);
    });
  }

  if (hasField(data, "attendees")) {
    setArray(data.attendees, (value) => {
      form.attendees = value.join(", ");
    });
  }

  if (hasField(data, "topics_discussed")) {
    setString(data.topics_discussed, (value) => {
      form.topicsDiscussed = value;
    });
  }

  if (hasField(data, "materials_shared")) {
    setArray(data.materials_shared, (value) => {
      form.materialsShared = value;
    });
  }

  if (hasField(data, "samples_distributed")) {
    setArray(data.samples_distributed, (value) => {
      form.samplesDistributed = value;
    });
  }

  if (hasField(data, "sentiment")) {
    setString(data.sentiment, (value) => {
      form.sentiment = normalizeSentiment(value);
    });
  }

  if (hasField(data, "outcomes")) {
    setString(data.outcomes, (value) => {
      form.outcomes = value;
    });
  }

  if (hasField(data, "follow_up_actions")) {
    setString(data.follow_up_actions, (value) => {
      form.followUpActions = value;
    });
  }

  if (mode === "replace") {
    form.materialsShared = hasField(data, "materials_shared") ? form.materialsShared : [];
    form.samplesDistributed = hasField(data, "samples_distributed") ? form.samplesDistributed : [];
  }
}

function hasField(data: Record<string, unknown>, field: string): boolean {
  return Object.prototype.hasOwnProperty.call(data, field);
}

function setString(value: unknown, setter: (value: string) => void) {
  const stringValue = getString(value);
  if (stringValue) {
    setter(stringValue);
  }
}

function setArray(value: unknown, setter: (value: string[]) => void) {
  const arrayValue = getArray(value);
  if (arrayValue.length > 0) {
    setter(arrayValue);
  }
}

function getString(value: unknown): string {
  return typeof value === "string" ? value.trim() : "";
}

function getArray(value: unknown): string[] {
  if (!Array.isArray(value)) {
    return [];
  }

  return value.map((item) => String(item).trim()).filter(Boolean);
}

function formatDateForForm(value: string): string {
  const match = value.match(/^(\d{4})-(\d{2})-(\d{2})/);
  return match ? `${match[3]}-${match[2]}-${match[1]}` : value;
}

function normalizeTime(value: string): string {
  return value.slice(0, 5);
}

function normalizeInteractionType(value: string): InteractionType {
  const normalized = value.replace("_", "-") as InteractionType;
  return ["meeting", "call", "email", "field-visit"].includes(normalized)
    ? normalized
    : "meeting";
}

function normalizeSentiment(value: string): Sentiment {
  return ["positive", "neutral", "negative"].includes(value) ? (value as Sentiment) : "neutral";
}

export const { updateFormField, setDraftMessage, setDraftMessageError } = hcpInteractionSlice.actions;

export default hcpInteractionSlice.reducer;
