import {
  TableRow,
  TableCell,
  Collapse,
  Button,
  Tooltip,
  useTheme,
  Stack,
  Typography,
  Chip,
} from "@mui/material";
import { useIntl } from "react-intl";
import DownloadIcon from "@mui/icons-material/Download";
import LaunchIcon from "@mui/icons-material/Launch";
import InsertPhotoIcon from "@mui/icons-material/InsertPhoto";
import { styled } from "@mui/material/styles";
import {
  getArcgisproWFS,
  getArcgisproWMS,
  getArcgisproWMTS,
  getQgisWFS,
  getQgisWMS,
  getQgisWMTS,
} from "../../requests";
import { Geoservice, SearchParameters } from "../../types";
import { PROVIDER } from "../../appConstants";
import { alpha, Box } from "@mui/system";

export const SubRow = ({
  row,
  open,
  index,
  mobileMode,
  triggerSearchbyKeyword,
}: {
  row: Geoservice;
  open: boolean;
  index: number;
  mobileMode: boolean;
  triggerSearchbyKeyword: (parameters: SearchParameters) => void;
}) => {
  const intl = useIntl();
  const theme = useTheme();

  const NULLVALUES = ["", "nan", "n.a", null];

  const handleChipClick = (label: string) => {
    triggerSearchbyKeyword({ searchString: label, page: 0 });
  };

  const routeObjectBuilder = () => {
    if (!row || !row.service) {
      return {
        arcgis_handler: () => "error",
        qgis_handler: () => "error",
      };
    }

    return row.service.includes("WFS")
      ? {
          arcgis_handler: () => getArcgisproWFS(row),
          qgis_handler: () => getQgisWFS(row),
        }
      : row.service.includes("WMS")
        ? {
            arcgis_handler: () => getArcgisproWMS(row),
            qgis_handler: () => getQgisWMS(row),
          }
        : {
            arcgis_handler: () => getArcgisproWMTS(row),
            qgis_handler: () => getQgisWMTS(row),
          };
  };

  const StyledTableRow = styled(TableRow)(() => ({
    "&": {
      backgroundColor: "#fdfdfd",
    },
  }));

  return (
    <StyledTableRow
      key={index}
      sx={{
        visibility: open ? "visible" : "collapse",
      }}
    >
      <TableCell
        style={{
          textAlign: "left",
          padding: 0,
          backgroundColor: alpha(theme.palette.primary.main, 0.04),
        }}
        colSpan={2}
      >
        <Collapse in={open} timeout="auto" unmountOnExit>
          <Box sx={{ p: 1 }}>
            <Typography variant="button" sx={{ paddingBottom: 1 }}>
              {intl.formatMessage({
                id: "subrow.details",
                defaultMessage: "Details: ",
              })}
            </Typography>
            <Typography variant="body2" sx={{ paddingBottom: 2 }}>
              {intl.formatMessage({
                id: "subrow.contact",
                defaultMessage: "Kontakt: ",
              })}
              {row.contact}
            </Typography>
            <Stack>
              <Typography variant="caption">
                <span className="bold">Name:</span>
                <span className="long-url">{row.name}</span>
              </Typography>
              <Typography variant="caption">
                <span className="bold">Endpoint:</span>
                <span className="long-url"> {row.endpoint}</span>
              </Typography>
              <Typography variant="caption">
                <span className="bold">Tree:</span>
                <span className="long-url">{row.tree}</span>
              </Typography>
              <Typography variant="caption">
                <span className="bold">Group:</span>
                <span className="long-url">{row.group}</span>
              </Typography>
            </Stack>
          </Box>
        </Collapse>
      </TableCell>
      {!mobileMode && (
        <TableCell
          style={{
            textAlign: "left",
            padding: 0,
            backgroundColor: alpha(theme.palette.primary.main, 0.04),
          }}
        >
          <Collapse in={open} timeout="auto" unmountOnExit>
            <Box sx={{ p: 1 }}>
              <div id="subRowField2">
                <div>
                  <Typography variant="button">
                    {intl.formatMessage({
                      id: "subrow.keywords",
                      defaultMessage: "Schlüsselwörter: ",
                    })}
                  </Typography>
                </div>
                {row.keywords.sort().map((keyword, i) => (
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
                      sx={{
                        mt: 1,
                        mr: 0.5,
                        color: theme.palette.info.main,
                        maxWidth: 200,
                      }}
                    />
                  </Tooltip>
                ))}
                <br />
                <div style={{ paddingTop: 10 }}>
                  <Typography variant="caption" sx={{ paddingBottom: 2 }}>
                    {intl.formatMessage({
                      id: "subrow.keywords_nlp",
                      defaultMessage: "Schlüsselwörter: ",
                    })}
                  </Typography>
                  <br />
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
                        sx={{
                          mt: 1,
                          mr: 0.5,
                          color: theme.palette.info.main,
                          maxWidth: 200,
                        }}
                      />
                    </Tooltip>
                  ))}
                </div>
              </div>
            </Box>
          </Collapse>
        </TableCell>
      )}
      <TableCell
        colSpan={1}
        style={{
          textAlign: "left",
          padding: 0,
          backgroundColor: alpha(theme.palette.primary.main, 0.04),
        }}
      ></TableCell>
      <TableCell
        colSpan={2}
        style={{
          textAlign: "left",
          padding: 0,
          backgroundColor: alpha(theme.palette.primary.main, 0.04),
        }}
      >
        <Collapse in={open} timeout="auto" unmountOnExit>
          <Box sx={{ p: 1 }}>
            <Typography variant="subtitle1">
              {intl.formatMessage({
                id: "subrow.tools",
                defaultMessage: "Tools: ",
              })}
            </Typography>
            <Stack spacing={1}>
              <Tooltip
                title={intl.formatMessage({ id: "button.preview" })}
                arrow
              >
                <Button
                  sx={{ justifyContent: "flex-start" }}
                  fullWidth
                  startIcon={<LaunchIcon />}
                  variant="text"
                  onClick={() => {
                    const url =
                      row.provider === PROVIDER.BUND
                        ? row.preview.replace("??", "'")
                        : row.preview;
                    window.open(url);
                  }}
                  disabled={NULLVALUES.includes(row.preview)}
                >
                  MapGeo
                </Button>
              </Tooltip>
              {row.legend && row.legend.includes("http") && (
                <Tooltip
                  title={intl.formatMessage({ id: "button.legend" })}
                  arrow
                >
                  <Button
                    sx={{ justifyContent: "flex-start" }}
                    fullWidth
                    startIcon={<InsertPhotoIcon />}
                    variant="text"
                    onClick={() => {
                      window.open(row.legend);
                    }}
                    disabled={NULLVALUES.includes(row.legend)}
                  >
                    Legende
                  </Button>
                </Tooltip>
              )}
              <Tooltip
                title={intl.formatMessage({ id: "button.arcgis_handler" })}
                arrow
              >
                <Button
                  sx={{ justifyContent: "flex-start" }}
                  fullWidth
                  variant="text"
                  onClick={routeObjectBuilder().arcgis_handler}
                  startIcon={<DownloadIcon />}
                  disabled={NULLVALUES.includes(row.endpoint)}
                >
                  ArcGIS
                </Button>
              </Tooltip>
              <Tooltip
                title={intl.formatMessage({ id: "button.qgis_handler" })}
                arrow
              >
                <Button
                  sx={{ justifyContent: "flex-start" }}
                  fullWidth
                  variant="text"
                  onClick={routeObjectBuilder().qgis_handler}
                  startIcon={<DownloadIcon />}
                  disabled={NULLVALUES.includes(row.endpoint)}
                >
                  QGIS
                </Button>
              </Tooltip>
            </Stack>
          </Box>
        </Collapse>
      </TableCell>
    </StyledTableRow>
  );
};
