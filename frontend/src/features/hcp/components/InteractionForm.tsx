import {
  Box,
  Button,
  Card,
  CardContent,
  FormControl,
  FormControlLabel,
  MenuItem,
  Radio,
  RadioGroup,
  Select,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import type { ReactNode } from "react";
import KeyboardArrowDownRoundedIcon from "@mui/icons-material/KeyboardArrowDownRounded";
import MicNoneRoundedIcon from "@mui/icons-material/MicNoneRounded";
import SearchRoundedIcon from "@mui/icons-material/SearchRounded";
import Inventory2OutlinedIcon from "@mui/icons-material/Inventory2Outlined";
import AutoAwesomeOutlinedIcon from "@mui/icons-material/AutoAwesomeOutlined";
import CalendarTodayRoundedIcon from "@mui/icons-material/CalendarTodayRounded";
import AccessTimeRoundedIcon from "@mui/icons-material/AccessTimeRounded";
import { useAppDispatch, useAppSelector } from "../../../store/hooks";
import { updateFormField } from "../slices/hcpInteractionSlice";
import type { InteractionFormState, InteractionType, Sentiment } from "../types/interaction";

type TextFormField = Exclude<
  keyof InteractionFormState,
  "materialsShared" | "samplesDistributed" | "interactionType" | "sentiment"
>;

const fieldLabelSx = {
  color: "#26324a",
  fontSize: "0.62rem",
  fontWeight: 700,
  mb: 0.35,
};

const smallFieldSx = {
  "& .MuiOutlinedInput-root": {
    minHeight: 21,
    borderRadius: "4px",
    fontSize: "0.62rem",
  },
  "& .MuiOutlinedInput-input": {
    py: 0.28,
    px: 1,
  },
  "& textarea.MuiOutlinedInput-input": {
    py: 0,
    lineHeight: 1.2,
  },
  "& .MuiOutlinedInput-root.MuiInputBase-multiline": {
    p: "5px 8px",
    alignItems: "flex-start",
  },
};

function FieldLabel({ children }: { children: ReactNode }) {
  return <Typography sx={fieldLabelSx}>{children}</Typography>;
}

function EmptyAssetRow({
  title,
  emptyText,
  buttonLabel,
  icon,
}: {
  title: string;
  emptyText: string;
  buttonLabel: string;
  icon: ReactNode;
}) {
  return (
    <Box
      sx={{
        border: "1px solid #dfe4ec",
        borderRadius: "5px",
        px: 1.15,
        py: 0.75,
        bgcolor: "#fff",
      }}
    >
      <Stack direction="row" sx={{ alignItems: "center", justifyContent: "space-between", gap: 1 }}>
        <Box>
          <Typography sx={{ fontSize: "0.64rem", fontWeight: 700, color: "#26324a" }}>
            {title}
          </Typography>
          <Typography sx={{ mt: 0.55, color: "#7a8494", fontSize: "0.58rem", fontStyle: "italic" }}>
            {emptyText}
          </Typography>
        </Box>
        <Button
          size="small"
          variant="outlined"
          startIcon={icon}
          sx={{
            minHeight: 19,
            px: 1.05,
            py: 0.2,
            borderColor: "#cfd6e0",
            color: "#18243a",
            fontSize: "0.58rem",
            fontWeight: 800,
            whiteSpace: "nowrap",
          }}
        >
          {buttonLabel}
        </Button>
      </Stack>
    </Box>
  );
}

export function InteractionForm() {
  const dispatch = useAppDispatch();
  const form = useAppSelector((state) => state.hcpInteraction.form);

  const updateTextField = (field: TextFormField, value: string) => {
    dispatch(updateFormField({ field, value }));
  };

  return (
    <Card sx={{ height: "100%", overflow: "hidden" }}>
      <Box
        sx={{
          px: 1.45,
          py: 0.75,
          borderBottom: "1px solid #dfe4ec",
          bgcolor: "#ffffff",
        }}
      >
        <Typography variant="h2">Interaction Details</Typography>
      </Box>

      <CardContent sx={{ p: 1.35, "&:last-child": { pb: 1.35 } }}>
        <Stack spacing={0.58}>
          <Box
            sx={{
              display: "grid",
              gridTemplateColumns: { xs: "1fr", md: "1fr 1fr" },
              gap: 1.15,
            }}
          >
            <Box>
              <FieldLabel>HCP Name</FieldLabel>
              <TextField
                fullWidth
                size="small"
                placeholder="Search or select HCP..."
                value={form.hcpName}
                onChange={(event) => updateTextField("hcpName", event.target.value)}
                sx={smallFieldSx}
              />
            </Box>

            <Box>
              <FieldLabel>Interaction Type</FieldLabel>
              <FormControl fullWidth size="small" sx={smallFieldSx}>
                <Select
                  value={form.interactionType}
                  IconComponent={KeyboardArrowDownRoundedIcon}
                  displayEmpty
                  onChange={(event) =>
                    dispatch(
                      updateFormField({
                        field: "interactionType",
                        value: event.target.value as InteractionType,
                      }),
                    )
                  }
                >
                  <MenuItem value="meeting">Meeting</MenuItem>
                  <MenuItem value="call">Call</MenuItem>
                  <MenuItem value="email">Email</MenuItem>
                  <MenuItem value="field-visit">Field Visit</MenuItem>
                </Select>
              </FormControl>
            </Box>
          </Box>

          <Box
            sx={{
              display: "grid",
              gridTemplateColumns: { xs: "1fr", md: "1fr 1fr" },
              gap: 1.15,
            }}
          >
            <Box>
              <FieldLabel>Date</FieldLabel>
              <TextField
                fullWidth
                size="small"
                value={form.interactionDate}
                onChange={(event) => updateTextField("interactionDate", event.target.value)}
                sx={smallFieldSx}
                slotProps={{
                  input: {
                    endAdornment: <CalendarTodayRoundedIcon sx={{ color: "#303a4e", fontSize: 13 }} />,
                  },
                }}
              />
            </Box>
            <Box>
              <FieldLabel>Time</FieldLabel>
              <TextField
                fullWidth
                size="small"
                value={form.interactionTime}
                onChange={(event) => updateTextField("interactionTime", event.target.value)}
                sx={smallFieldSx}
                slotProps={{
                  input: {
                    endAdornment: <AccessTimeRoundedIcon sx={{ color: "#303a4e", fontSize: 12 }} />,
                  },
                }}
              />
            </Box>
          </Box>

          <Box>
            <FieldLabel>Attendees</FieldLabel>
            <TextField
              fullWidth
              size="small"
              placeholder="Enter names or search..."
              value={form.attendees}
              onChange={(event) => updateTextField("attendees", event.target.value)}
              sx={smallFieldSx}
            />
          </Box>

          <Box>
            <FieldLabel>Topics Discussed</FieldLabel>
            <TextField
              fullWidth
              multiline
              minRows={2}
              placeholder="Enter key discussion points..."
              value={form.topicsDiscussed}
              onChange={(event) => updateTextField("topicsDiscussed", event.target.value)}
              sx={smallFieldSx}
              slotProps={{
                input: {
                  endAdornment: (
                    <MicNoneRoundedIcon
                      sx={{ color: "#27344d", fontSize: 13, alignSelf: "flex-end", mb: 0.1 }}
                    />
                  ),
                },
              }}
            />
          </Box>

          <Box sx={{ mt: 0.15 }}>
            <Button
              size="small"
              variant="outlined"
              startIcon={<AutoAwesomeOutlinedIcon />}
              sx={{
                minHeight: 19,
                px: 1.15,
                py: 0.05,
                borderColor: "#d5dbe4",
                color: "#1e2b44",
                fontSize: "0.62rem",
                fontWeight: 800,
              }}
            >
              Summarize from Voice Note (Requires Consent)
            </Button>
          </Box>

          <Box>
            <Typography sx={{ ...fieldLabelSx, mb: 0.75 }}>
              Materials Shared / Samples Distributed
            </Typography>
            <Stack spacing={0.55}>
              <EmptyAssetRow
                title="Materials Shared"
                emptyText="No materials added."
                buttonLabel="Search/Add"
                icon={<SearchRoundedIcon sx={{ fontSize: 14 }} />}
              />
              <EmptyAssetRow
                title="Samples Distributed"
                emptyText="No samples added."
                buttonLabel="Add Sample"
                icon={<Inventory2OutlinedIcon sx={{ fontSize: 14 }} />}
              />
            </Stack>
          </Box>

          <Box>
            <FieldLabel>Observed/Inferred HCP Sentiment</FieldLabel>
            <RadioGroup
              row
              value={form.sentiment}
              onChange={(event) =>
                dispatch(
                  updateFormField({
                    field: "sentiment",
                    value: event.target.value as Sentiment,
                  }),
                )
              }
              sx={{
                gap: 0.9,
                "& .MuiFormControlLabel-root": { mr: 0 },
                "& .MuiFormControlLabel-label": {
                  color: "#29354e",
                  fontSize: "0.62rem",
                  fontWeight: 600,
                },
                "& .MuiRadio-root": { p: 0.2 },
                "& .MuiSvgIcon-root": { fontSize: 12 },
              }}
            >
              <FormControlLabel value="positive" control={<Radio size="small" />} label="Positive" />
              <FormControlLabel value="neutral" control={<Radio size="small" />} label="Neutral" />
              <FormControlLabel value="negative" control={<Radio size="small" />} label="Negative" />
            </RadioGroup>
          </Box>

          <Box>
            <FieldLabel>Outcomes</FieldLabel>
            <TextField
              fullWidth
              multiline
              minRows={1}
              placeholder="Key outcomes or agreements..."
              value={form.outcomes}
              onChange={(event) => updateTextField("outcomes", event.target.value)}
              sx={smallFieldSx}
            />
          </Box>

          <Box>
            <FieldLabel>Follow-up Actions</FieldLabel>
            <TextField
              fullWidth
              multiline
              minRows={1}
              placeholder="Enter next steps or tasks..."
              value={form.followUpActions}
              onChange={(event) => updateTextField("followUpActions", event.target.value)}
              sx={smallFieldSx}
            />
          </Box>

          <Box>
            <Typography sx={{ color: "#2b63d9", fontSize: "0.58rem", fontWeight: 800 }}>
              AI Suggested Follow-ups:
            </Typography>
            <Stack spacing={0.2} sx={{ mt: 0.35 }}>
              {[
                "Schedule follow-up meeting in 2 weeks",
                "Send OncoBoost Phase III PDF",
                "Add Dr. Sharma to advisory board invite list",
              ].map((item) => (
                <Typography key={item} sx={{ color: "#2d6cdf", fontSize: "0.56rem" }}>
                  + {item}
                </Typography>
              ))}
            </Stack>
          </Box>
        </Stack>
      </CardContent>
    </Card>
  );
}
