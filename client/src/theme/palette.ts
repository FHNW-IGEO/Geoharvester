import { PaletteOptions } from "@mui/material/styles";

export const palette: PaletteOptions = {
  mode: "light",
  primary: {
    main: "#007CC3",
    light: "#7FBDE1",
    contrastText: "#ffffff",
  },
  secondary: {
    main: "#ffffff",
    contrastText: "#007CC3",
  },
  info: {
    main: "#E8E8E8",
    light: "#C0C0C0",
    contrastText: "#ffffff",
  },
  warning: {
    main: "#e96200",
    light: "#F0914D",
    contrastText: "#000000",
  },
  success: {
    main: "#2e7d32",
    light: "#edf7ed",
    contrastText: "#000000",
  },
  text: {
    primary: "#000000",
    secondary: "rgba(0,0,0,0.6)",
    disabled: "rgba(0,0,0,0.38)",
  },
};
