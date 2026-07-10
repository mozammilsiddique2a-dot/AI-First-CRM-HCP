import { Box, Typography } from "@mui/material";
import { AiChatAssistant } from "../components/AiChatAssistant";
import { InteractionForm } from "../components/InteractionForm";

export function LogHcpInteractionPage() {
  return (
    <Box
      component="main"
      sx={{
        minHeight: "100vh",
        bgcolor: "background.default",
        px: { xs: 1.25, md: 2.5 },
        py: { xs: 1.25, md: 1.2 },
      }}
    >
      <Box sx={{ width: "100%", maxWidth: 875, mx: { xs: "auto", md: 0 } }}>
        <Typography variant="h1" sx={{ mb: 1.15 }}>
          Log HCP Interaction
        </Typography>

        <Box
          sx={{
            display: "grid",
            gridTemplateColumns: { xs: "1fr", md: "minmax(0, 1fr) 278px" },
            gap: { xs: 1.5, md: 2.1 },
            alignItems: "start",
          }}
        >
          <InteractionForm />
          <AiChatAssistant />
        </Box>
      </Box>
    </Box>
  );
}
