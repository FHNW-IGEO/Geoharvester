import "@mui/material/TableCell";
import "@mui/material/Tooltip";

declare module "@mui/material/TableCell" {
  interface TableCellPropsVariantOverrides {
    FillerSubCell: true;
    LeftAlignedSubCell: true;
  }
}

declare module "@mui/material/Tooltip" {
  interface TooltipPropsVariantOverrides {
    lightTooltip: true;
  }
}

export {};
