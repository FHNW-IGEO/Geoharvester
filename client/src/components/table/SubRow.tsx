import {
  TableRow,
  TableCell,
  Collapse,
  Button,
  Tooltip,
  Table,
  TableBody,
  useTheme,
  Stack,
  Typography,
  Chip,
  Divider,
} from "@mui/material";
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
import { useIntl } from "react-intl";

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

  const rowsToInclude = mobileMode
    ? ["name", "contact", "abstract", "keywords", "metadata"]
    : ["name", "contact", "tree", "group", "keywords", "metadata", "endpoint"];

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
    <StyledTableRow key={index}>
      <TableCell
        style={{
          textAlign: "left",
          padding: 0,
          boxShadow: "inset 0px 0px 6px 0px rgba(0, 0, 0, 0.15)",
        }}
        colSpan={mobileMode ? 5 : 6}
      >
        <Collapse in={open} timeout="auto" unmountOnExit>
          <Stack direction="row" spacing={1} sx={{ width: "100%" }}>
            <Stack id="subRowField1">
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

              <Typography variant="caption">Name: {row.name}</Typography>
              <Stack>
                <Typography variant="caption">
                  Endpoint: {row.endpoint}
                </Typography>
                <Typography variant="caption">Tree: {row.tree}</Typography>
                <Typography variant="caption">Group: {row.group}</Typography>
              </Stack>
              {/* </div> */}
            </Stack>
            <Stack sx={{ minWidth: 160, maxWidth: 160 }} id="subRowField2">
              <Typography variant="button">
                {intl.formatMessage({
                  id: "subrow.tools",
                  defaultMessage: "Tools: ",
                })}
              </Typography>

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
            <Stack
              sx={{
                flexGrow: 1,
              }}
            >
              <div id="subRowField3">
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
            </Stack>
          </Stack>
          {/* <TableContainer>
            <Table>
              <TableBody>
                {rowsToInclude.map((prop) => (
                  <TableRow>
                    <FillerTableCell></FillerTableCell>
                    <LeftAlignedTableCell
                      style={{
                        width: mobileMode ? "80px" : "200px",
                        marginTop: 5,
                      }}
                    >
                      {`${
                        prop.charAt(0).toUpperCase() +
                        prop.slice(1).toLocaleLowerCase()
                      }:`}
                    </LeftAlignedTableCell>
                    <LeftAlignedTableCell
                      colSpan={2}
                      style={{
                        width: "100%",
                        display: "flex",
                        wordBreak: "break-word",
                      }}
                    >
                      {row[prop as keyof Geoservice]}
                    </LeftAlignedTableCell>
                  </TableRow>
                ))}
                <TableRow>
                  <FillerTableCell></FillerTableCell>
                  <LeftAlignedTableCell>Mapgeo:</LeftAlignedTableCell>
                  <LeftAlignedTableCell
                    colSpan={2}
                    style={{
                      display: "flex",
                      wordBreak: "break-word",
                    }}
                  >
                    <Tooltip title={row.preview} arrow>
                      <Button
                        style={{ padding: 0 }}
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
                        Service in MapGeo öffnen
                      </Button>
                    </Tooltip>
                  </LeftAlignedTableCell>
                </TableRow>
                {!mobileMode && (
                  <TableRow>
                    <FillerTableCell />
                    <LeftAlignedTableCell>Legend:</LeftAlignedTableCell>
                    <LeftAlignedTableCell
                      colSpan={2}
                      style={{
                        display: "flex",
                        wordBreak: "break-word",
                      }}
                    >
                      <Tooltip title={row.legend} arrow>
                        <Button
                          onClick={() => window.open(row.legend)}
                          style={{ padding: 0 }}
                          disabled={NULLVALUES.includes(row.legend)}
                        >
                          Legende öffnen
                        </Button>
                      </Tooltip>
                    </LeftAlignedTableCell>
                  </TableRow>
                )}
                {!mobileMode && (
                  <TableRow>
                    <FillerTableCell />
                    <LeftAlignedTableCell></LeftAlignedTableCell>
                    <LeftAlignedTableCell colSpan={2}>
                      <Button
                        variant="outlined"
                        style={{
                          marginRight: 30,
                          marginTop: 10,
                          marginBottom: 16,
                        }}
                        onClick={routeObjectBuilder().arcgis_handler}
                        startIcon={<DownloadIcon />}
                        disabled={NULLVALUES.includes(row.endpoint)}
                      >
                        For ArcGIS Pro
                      </Button>
                      <Button
                        variant="outlined"
                        onClick={routeObjectBuilder().qgis_handler}
                        startIcon={<DownloadIcon />}
                        disabled={NULLVALUES.includes(row.endpoint)}
                      >
                        For QGIS
                      </Button>
                    </LeftAlignedTableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer> */}
        </Collapse>
      </TableCell>
    </StyledTableRow>
  );
};
