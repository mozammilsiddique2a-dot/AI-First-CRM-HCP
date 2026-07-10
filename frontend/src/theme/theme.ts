import { createTheme } from "@mui/material/styles";

export const theme = createTheme({
  palette: {
    mode: "light",
    primary: {
      main: "#1677ff",
      dark: "#0f5ed8",
    },
    secondary: {
      main: "#14b8a6",
    },
    background: {
      default: "#f1f2f4",
      paper: "#ffffff",
    },
    text: {
      primary: "#111827",
      secondary: "#5b6472",
    },
    divider: "#e4e7ec",
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontSize: "1.05rem",
      lineHeight: 1.2,
      fontWeight: 800,
      letterSpacing: 0,
    },
    h2: {
      fontSize: "0.73rem",
      lineHeight: 1.3,
      fontWeight: 800,
      letterSpacing: 0,
    },
    button: {
      fontWeight: 700,
      textTransform: "none",
    },
  },
  shape: {
    borderRadius: 8,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          boxShadow: "none",
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          border: "1px solid #dce1e8",
          boxShadow: "0 1px 4px rgba(15, 23, 42, 0.07)",
        },
      },
    },
    MuiOutlinedInput: {
      styleOverrides: {
        root: {
          backgroundColor: "#ffffff",
          fontSize: "0.68rem",
        },
      },
    },
    MuiInputLabel: {
      styleOverrides: {
        root: {
          fontSize: "0.68rem",
          fontWeight: 600,
        },
      },
    },
  },
});
