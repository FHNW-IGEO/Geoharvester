import { useEffect, useState } from "react";
import {
  IconButton,
  TableRow,
  TableCell,
  Icon,
  Tooltip,
  styled,
} from "@mui/material";
import { Geoservice } from "../../types";
import KeyboardArrowDownIcon from "@mui/icons-material/KeyboardArrowDown";
import KeyboardArrowUpIcon from "@mui/icons-material/KeyboardArrowUp";
import { SubRow } from "./SubRow";
import "../../styles.css";

export const ServiceRow = ({
  row,
  index,
  page,
  total,
}: {
  row: Geoservice;
  index: number;
  page: number;
  total: number;
}) => {
  const [open, setOpen] = useState(false);

  useEffect(() => setOpen(false), [page, total]);

  const getIcon = () => {
    const target =
      row.OWNER === "Bund" ? "ch" : row.OWNER.slice(3, 5).toLocaleLowerCase();
    return `/cantonIcons/${target}.svg`;
  };

  const CenteredTableCell = styled(TableCell)(() => ({
    "&": {
      width: 120,
      padding: 8,
      textAlign: "center",
    },
  }));

  const LeftAlignedTableCell = styled(TableCell)(() => ({
    "&": {
      padding: 8,
      textAlign: "left",
    },
  }));
  const LeftAlignedTableCellMaxWidth = styled(TableCell)(() => ({
    "&": {
      padding: 8,
      textAlign: "left",
      minWidth: 180,
      wordBreak: "break-word",
    },
  }));

  const abstract =
    row && row.ABSTRACT && row.ABSTRACT.length > 450
      ? `${row.ABSTRACT.slice(0, 450)}...`
      : row.ABSTRACT;

  const qualitynum = `chart x-${row.METAQUALITY}`;

  return (
    <>
      <TableRow key={index} onClick={() => setOpen(!open)}>
        <TableCell>
          <IconButton
            aria-label="expand row"
            size="small"
            onClick={() => setOpen(!open)}
            style={{ color: "#007CC3" }}
          >
            {open ? <KeyboardArrowUpIcon /> : <KeyboardArrowDownIcon />}
          </IconButton>
        </TableCell>
        <LeftAlignedTableCellMaxWidth>{row.TITLE}</LeftAlignedTableCellMaxWidth>
        <LeftAlignedTableCell>{abstract}</LeftAlignedTableCell>
        <CenteredTableCell>
          <Tooltip title={row.OWNER}>
            <Icon>
              <img alt="sourceIcon" src={getIcon()} height={25} width={25} />
            </Icon>
          </Tooltip>
        </CenteredTableCell>
        <CenteredTableCell>{row.SERVICETYPE}</CenteredTableCell>
        <CenteredTableCell>
          <div id="metaqual" className={qualitynum}>
            <p className="percentage">{row.METAQUALITY}</p>
          </div>
        </CenteredTableCell>
      </TableRow>
      <SubRow row={row} open={open} index={index} />
    </>
  );
};
