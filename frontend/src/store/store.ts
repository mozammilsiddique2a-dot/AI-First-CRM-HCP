import { configureStore } from "@reduxjs/toolkit";
import hcpInteractionReducer from "../features/hcp/slices/hcpInteractionSlice";

export const store = configureStore({
  reducer: {
    hcpInteraction: hcpInteractionReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

