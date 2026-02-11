import { Components } from "@mui/material/styles";
import { COLWIDTH } from "components/table/settings";

const sharedStyles = {
  overflow: "hidden",
  textOverflow: "ellipsis",
  borderBottom: "none !important",
  padding: 4,
  border: "1px solid black",
};

export const components: Components = {
  MuiTableCell: {
    variants: [
      {
        props: { variant: "FillerSubCell" },
        style: {
          ...sharedStyles,
        },
      },

      {
        props: { variant: "LeftAlignedSubCell" },
        style: {
          ...sharedStyles,
        },
      },
    ],
  },
  MuiTooltip: {
    styleOverrides: {
      tooltip: {
        backgroundColor: "#ffffff",
        color: "rgba(0, 0, 0, 0.87)",
        boxShadow: "0px 2px 8px rgba(0,0,0,0.15)",
        fontSize: 14,
        fontWeight: 500,
        border: "1px solid grey",
      },
      arrow: {
        color: "#ffffff",
      },
    },
  },
};
