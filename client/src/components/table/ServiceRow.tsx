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
import { getIcon } from "../../custom/getIcon";
import "../../styles.css";

export const ServiceRow = ({
  row,
  index,
  page,
  total,
  mobileMode,
}: {
  row: Geoservice;
  index: number;
  page: number;
  total: number;
  mobileMode: boolean;
}) => {
  const [open, setOpen] = useState(false);

  useEffect(() => setOpen(false), [page, total]);

  const CenteredTableCell = styled(TableCell)(() => ({
    "&": {
      width: mobileMode ? 0 : 100,
      padding: mobileMode ? 0 : 8,
      textAlign: "center",
    },
  }));

  const LeftAlignedTableCell = styled(TableCell)(() => ({
    "&": {
      padding: mobileMode ? 0 : 8,
      textAlign: "left",
    },
  }));
  const LeftAlignedTableCellMaxWidth = styled(TableCell)(() => ({
    "&": {
      padding: mobileMode ? 0 : 8,
      textAlign: "left",
      minWidth: mobileMode ? 60 : 180,
      wordBreak: "break-word",
    },
  }));

  const abstract =
    row && row.abstract && row.abstract.length > 450
      ? `${row.abstract.slice(0, 450)}...`
      : row.abstract;

  const qualitynum = `chart x-${row.metaquality}`;

  return (
    <>
      <TableRow key={index} onClick={() => setOpen(!open)}>
        <CenteredTableCell>
          <IconButton
            aria-label="expand row"
            size="small"
            onClick={() => setOpen(!open)}
            style={{ color: "#007CC3", padding: 0, cursor: "pointer" }}
          >
            {open ? <KeyboardArrowUpIcon /> : <KeyboardArrowDownIcon />}
          </IconButton>
        </CenteredTableCell>
        <LeftAlignedTableCellMaxWidth>{row.title}</LeftAlignedTableCellMaxWidth>
        {!mobileMode && <LeftAlignedTableCell>{abstract}</LeftAlignedTableCell>}
        <CenteredTableCell>
          <Tooltip title={row.provider}>
            <Icon>
              <img
                alt="sourceIcon"
                src={getIcon(row.provider)}
                height={25}
                width={25}
              />
            </Icon>
          </Tooltip>
        </CenteredTableCell>
        <CenteredTableCell>{row.service}</CenteredTableCell>
        <CenteredTableCell>
          <div id="metaqual" className={qualitynum}>
            <p className="percentage">{row.metaquality}</p>
          </div>
        </CenteredTableCell>
      </TableRow>
      <SubRow row={row} open={open} index={index} mobileMode={mobileMode} />
    </>
  );
};
