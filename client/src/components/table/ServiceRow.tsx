import { useEffect, useState } from "react";
import {
  IconButton,
  TableRow,
  TableCell,
  Icon,
  Tooltip,
  Chip,
  styled,
  useTheme,
} from "@mui/material";
import { Geoservice, SearchParameters } from "../../types";
import KeyboardArrowDownIcon from "@mui/icons-material/KeyboardArrowDown";
import KeyboardArrowUpIcon from "@mui/icons-material/KeyboardArrowUp";
import { SubRow } from "./SubRow";
import { getIcon } from "../../custom/getIcon";
import { useIntl } from "react-intl";

export const ServiceRow = ({
  row,
  index,
  page,
  total,
  mobileMode,
  triggerSearchbyKeyword,
}: {
  row: Geoservice;
  index: number;
  page: number;
  total: number;
  mobileMode: boolean;
  triggerSearchbyKeyword: (parameters: SearchParameters) => void;
}) => {
  const [open, setOpen] = useState(false);
  useEffect(() => setOpen(false), [page, total]);
  const theme = useTheme();
  const intl = useIntl();

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

  // const handleChipClick = (label: string) => {
  //   triggerSearchbyKeyword({ searchString: label, page: 0 });
  // };

  return (
    <>
      <TableRow key={index}>
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
        <LeftAlignedTableCellMaxWidth onClick={() => setOpen(!open)}>
          {row.title}
        </LeftAlignedTableCellMaxWidth>
        {!mobileMode && (
          <LeftAlignedTableCell>
            {abstract}
            {/* <br />
            {row.keywords_nlp.sort().map((keyword, i) => (
              <Tooltip
                title={intl.formatMessage({ id: "keyword.lookup" })}
                arrow
              >
                <Chip
                  key={keyword + i}
                  label={keyword}
                  variant="outlined"
                  size="small"
                  color="info"
                  onClick={() => handleChipClick(keyword)}
                  sx={{ mt: 1, mr: 0.5, color: theme.palette.info.main }}
                />
              </Tooltip>
            ))}*/}
          </LeftAlignedTableCell>
        )}
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
      <SubRow
        row={row}
        open={open}
        index={index}
        mobileMode={mobileMode}
        triggerSearchbyKeyword={triggerSearchbyKeyword}
      />
    </>
  );
};
