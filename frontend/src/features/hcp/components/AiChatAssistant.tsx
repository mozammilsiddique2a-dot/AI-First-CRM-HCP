import {
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  InputAdornment,
  Paper,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import SmartToyOutlinedIcon from "@mui/icons-material/SmartToyOutlined";
import WarningAmberRoundedIcon from "@mui/icons-material/WarningAmberRounded";
import { useAppDispatch, useAppSelector } from "../../../store/hooks";
import { sendDraftMessage, setDraftMessage, setDraftMessageError } from "../slices/hcpInteractionSlice";

export function AiChatAssistant() {
  const dispatch = useAppDispatch();
  const { draftMessage, error, isSending, messages } = useAppSelector((state) => state.hcpInteraction);

  const handleSend = () => {
    const inputValue = draftMessage.trim();

    if (!inputValue) {
      dispatch(setDraftMessageError("Please enter a message."));
      return;
    }

    if (!isSending) {
      dispatch(sendDraftMessage(inputValue));
    }
  };

  return (
    <Card sx={{ overflow: "hidden" }}>
      <CardContent
        sx={{
          display: "flex",
          flexDirection: "column",
          height: "100%",
          minHeight: { xs: 500, md: 548 },
          p: 0,
          "&:last-child": { pb: 0 },
        }}
      >
        <Box
          sx={{
            px: 1.35,
            py: 0.7,
            borderBottom: "1px solid #dfe4ec",
            bgcolor: "#ffffff",
          }}
        >
          <Stack direction="row" spacing={0.55} sx={{ alignItems: "center" }}>
            <SmartToyOutlinedIcon sx={{ color: "#236ce9", fontSize: 13 }} />
            <Box>
              <Typography variant="h2" sx={{ lineHeight: 1.05 }}>
                AI Assistant
              </Typography>
              <Typography sx={{ color: "#697589", fontSize: "0.62rem", mt: 0.05 }}>
                Log interaction via chat
              </Typography>
            </Box>
          </Stack>
        </Box>

        <Box
          sx={{
            position: "relative",
            flex: 1,
            overflowY: "auto",
            bgcolor: "#f6f7f9",
            px: 1.35,
            py: 1.1,
          }}
        >
          <Stack spacing={0.8}>
            {messages.map((message) => {
              const isUser = message.role === "user";

              return (
                <Stack
                  key={message.id}
                  direction="row"
                  sx={{ justifyContent: isUser ? "flex-end" : "flex-start" }}
                >
                  <Paper
                    elevation={0}
                    sx={{
                      width: isUser ? "auto" : 212,
                      maxWidth: "100%",
                      bgcolor: isUser ? "#eef4ff" : "#ffffff",
                      border: "1px solid #dfe4ec",
                      borderRadius: "5px",
                      px: 1.15,
                      py: 0.8,
                      boxShadow: "0 1px 2px rgba(15, 23, 42, 0.03)",
                    }}
                  >
                    <Typography
                      sx={{
                        color: "#202b43",
                        fontSize: "0.62rem",
                        fontWeight: isUser ? 600 : 700,
                        lineHeight: 1.35,
                      }}
                    >
                      {message.content}
                    </Typography>
                  </Paper>
                </Stack>
              );
            })}
            {isSending && (
              <Typography sx={{ color: "#697589", fontSize: "0.62rem" }}>
                AI Assistant is thinking...
              </Typography>
            )}
            {error && (
              <Typography sx={{ color: "#b42318", fontSize: "0.62rem", fontWeight: 700 }}>
                {error}
              </Typography>
            )}
          </Stack>
        </Box>

        <Box
          sx={{
            borderTop: "1px solid #dfe4ec",
            bgcolor: "#ffffff",
            p: 1.15,
          }}
        >
          <Stack direction="row" spacing={1}>
            <TextField
              fullWidth
              size="small"
              placeholder="Describe interaction..."
              value={draftMessage}
              onChange={(event) => dispatch(setDraftMessage(event.target.value))}
              onKeyDown={(event) => {
                if (event.key === "Enter" && !event.shiftKey) {
                  event.preventDefault();
                  handleSend();
                }
              }}
              disabled={isSending}
              sx={{
                "& .MuiOutlinedInput-root": {
                  minHeight: 27,
                  borderRadius: "4px",
                  fontSize: "0.62rem",
                },
                "& .MuiOutlinedInput-input": {
                  py: 0.35,
                  px: 0.95,
                },
              }}
              slotProps={{
                input: {
                  endAdornment: <InputAdornment position="end" />,
                },
              }}
            />
            <Button
              variant="contained"
              startIcon={
                isSending ? (
                  <CircularProgress size={12} sx={{ color: "#ffffff" }} />
                ) : (
                  <WarningAmberRoundedIcon sx={{ fontSize: 15 }} />
                )
              }
              onClick={handleSend}
              disabled={isSending}
              sx={{
                minWidth: 64,
                minHeight: 24,
                borderRadius: "4px",
                bgcolor: "#8a909b",
                color: "#ffffff",
                fontSize: "0.62rem",
                fontWeight: 800,
                "&:hover": { bgcolor: "#747b86" },
                "&.Mui-disabled": {
                  bgcolor: "#a4a9b2",
                  color: "#ffffff",
                },
              }}
            >
              Log
            </Button>
          </Stack>
        </Box>
      </CardContent>
    </Card>
  );
}
