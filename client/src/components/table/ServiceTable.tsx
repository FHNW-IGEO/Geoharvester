import React, { useState } from "react";
import { FormattedMessage, useIntl } from "react-intl";
import {
  TableContainer,
  Table,
  TableBody,
  TableHead,
  TableFooter,
  TablePagination,
  TableRow,
  TableCell,
  TableSortLabel,
  Paper,
  Box,
  useTheme,
} from "@mui/material";
import { styled } from "@mui/material/styles";
import { visuallyHidden } from "@mui/utils";
import { Geoservice, SearchParameters } from "../../types";
import { ServiceRow } from "./ServiceRow";
import { TablePaginationActions } from "./TablePaginationActions";
import {
  DEFAULTCHUNKSIZE,
  RESPONSESTATE,
  BREAKPOINT600,
} from "../../appConstants";
import { useViewport } from "../../custom/ViewportHook";
import { PlaceholderWidget } from "./PlaceholderUI";

type TableProps = {
  docs: Geoservice[];
  responseState: RESPONSESTATE;
  total: number;
  currentApiPage: number;
  setRowsPerPage: (size: number) => void;
  tablePage: number;
  setTablePage: (page: number) => void;
  rowsPerPage: number;
  triggerSearch: (parameters: SearchParameters) => void;
  triggerSearchbyKeyword: (parameters: SearchParameters) => void;
  searchParameters: SearchParameters;
};

type Order = "asc" | "desc";

export const ServiceTable = ({
  docs,
  responseState,
  total,
  currentApiPage,
  tablePage,
  setTablePage,
  setRowsPerPage,
  rowsPerPage,
  triggerSearch,
  triggerSearchbyKeyword,
  searchParameters,
}: TableProps) => {
  const [order, setOrder] = useState<Order>("asc");
  const [orderBy, setOrderBy] = useState<string>("");
  const [tableRef, setTableReference] = useState<any>();

  const { width } = useViewport();
  const mobileMode = width < BREAKPOINT600;

  const theme = useTheme();
  const intl = useIntl();

  const scrollToTop = () => tableRef && tableRef.scrollIntoView();

  const displayedRecordsStart =
    currentApiPage * DEFAULTCHUNKSIZE + tablePage * rowsPerPage;
  const displayedRecordsEnd = displayedRecordsStart + rowsPerPage;

  const handleChangePageForward = (
    event: React.MouseEvent<HTMLButtonElement> | null,
    newPage: number,
  ) => {
    const processedResults = rowsPerPage * newPage;
    if (processedResults >= DEFAULTCHUNKSIZE && processedResults <= total) {
      triggerSearch({ ...searchParameters, page: currentApiPage + 1 });
      setTablePage(0);
    } else {
      setTablePage(newPage);
    }
    scrollToTop();
  };
  const handleChangePageBackward = (
    event: React.MouseEvent<HTMLButtonElement> | null,
    newPage: number,
  ) => {
    const processedResults = Math.abs(rowsPerPage * newPage);
    const pagesBeforeReload = DEFAULTCHUNKSIZE / rowsPerPage;

    if (
      processedResults <= DEFAULTCHUNKSIZE * currentApiPage &&
      processedResults > 0
    ) {
      triggerSearch({ ...searchParameters, page: currentApiPage - 1 });
      setTablePage(Math.abs(pagesBeforeReload) - 1);
    } else {
      setTablePage(newPage);
    }
    scrollToTop();
  };

  const handleChangeRowsPerPage = (
    event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>,
  ) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setTablePage(0);
  };

  const handleRequestSort = (
    event: React.MouseEvent<unknown>,
    property: string,
  ) => {
    const isAsc = orderBy === property && order === "asc";
    setOrder(isAsc ? "desc" : "asc");
    setOrderBy(property);
  };

  const createSortHandler =
    (property: string) => (event: React.MouseEvent<unknown>) => {
      handleRequestSort(event, property.toLocaleLowerCase());
    };

  const sortedData = docs.sort((a: Geoservice, b: Geoservice) =>
    order === "asc"
      ? a[orderBy as keyof Geoservice] > b[orderBy as keyof Geoservice]
        ? 1
        : -1
      : a[orderBy as keyof Geoservice] < b[orderBy as keyof Geoservice]
        ? 1
        : -1,
  );

  const CenteredTableCell = styled(TableCell)(() => ({
    "&": {
      padding: "0 1px",
      textAlign: "center",
      color: theme.palette.primary.main,
    },
  }));
  const LeftAlignedTableCell = styled(TableCell)(() => ({
    "&": {
      backgroundColor: theme.palette.primary.contrastText,
      padding: 8,
      textAlign: "left",
      color: theme.palette.primary.main,
    },
  }));

  switch (responseState) {
    case RESPONSESTATE.EMPTY:
      return (
        <PlaceholderWidget
          placeholderText={intl.formatMessage({
            id: "placeholder.noResults",
            defaultMessage: "Keine Treffer...",
          })}
        />
      );
    case RESPONSESTATE.ERROR:
      return (
        <PlaceholderWidget
          placeholderText={intl.formatMessage({
            id: "placeholder.error",
            defaultMessage: "Error",
          })}
        />
      );
    case RESPONSESTATE.WAITING:
      return <PlaceholderWidget />;
    case RESPONSESTATE.SUCCESS:
      return (
        <TableContainer
          component={Paper}
          sx={{
            overflowX: "auto",
          }}
        >
          <Table stickyHeader aria-label="sticky table" ref={setTableReference}>
            <TableHead>
              <TableRow>
                <CenteredTableCell></CenteredTableCell>
                <LeftAlignedTableCell>
                  <FormattedMessage
                    id="table.header.title"
                    defaultMessage="Title"
                  />
                </LeftAlignedTableCell>
                {width > BREAKPOINT600 && (
                  <LeftAlignedTableCell>
                    <FormattedMessage
                      id="table.header.abstract"
                      defaultMessage="Abstract"
                    />
                  </LeftAlignedTableCell>
                )}
                {[
                  {
                    col_header: intl.formatMessage({
                      id: "table.header.provider",
                      defaultMessage: "Anbieter",
                    }),
                    sortProperty: "provider",
                  },
                  {
                    col_header: intl.formatMessage({
                      id: "table.header.service",
                      defaultMessage: "Dienst",
                    }),
                    sortProperty: "service",
                  },
                  {
                    col_header: intl.formatMessage({
                      id: "table.header.metaquality",
                      defaultMessage: "Metaqualität",
                    }),
                    sortProperty: "metaquality",
                  },
                ].map((column, index) => {
                  const { col_header, sortProperty } = column;
                  return (
                    <>
                      <CenteredTableCell
                        key={index}
                        sortDirection={orderBy === sortProperty ? order : false}
                        sx={{
                          padding: "0 !important",
                          cursor: "pointer",
                          color: "#000 !important",
                        }}
                      >
                        <TableSortLabel
                          sx={{
                            color: "#007CC3 !important",
                            "& .MuiTableSortLabel-icon": {
                              color: "#007CC3 !important",
                            },
                          }}
                          active={true}
                          direction={orderBy === sortProperty ? order : "desc"}
                          onClick={createSortHandler(sortProperty)}
                        >
                          {mobileMode ? col_header.slice(0, 8) : col_header}
                          {orderBy === sortProperty ? (
                            <Box component="span" sx={visuallyHidden}>
                              {order === "desc"
                                ? "sorted descending"
                                : "sorted ascending"}
                              + ro
                            </Box>
                          ) : null}
                        </TableSortLabel>
                      </CenteredTableCell>
                    </>
                  );
                })}
              </TableRow>
            </TableHead>
            <TableBody>
              {(rowsPerPage > 0
                ? sortedData.slice(
                    tablePage * rowsPerPage,
                    tablePage * rowsPerPage + rowsPerPage,
                  )
                : sortedData
              ).map((row, index) => (
                <ServiceRow
                  row={row}
                  index={index}
                  page={tablePage}
                  total={total}
                  mobileMode={mobileMode}
                  triggerSearchbyKeyword={triggerSearchbyKeyword}
                />
              ))}
            </TableBody>
            <TableFooter
              sx={{
                position: "sticky",
                bottom: 0,
                zIndex: 20,
              }}
            >
              <TableRow sx={{ height: 28 }}>
                <TableCell
                  colSpan={6}
                  sx={{
                    padding: 0,
                    backgroundColor: "#f9f9f9",
                    borderTop: "1px solid #C0C0C0",
                  }}
                >
                  <TablePagination
                    rowsPerPageOptions={[20, 50, 100, 200]}
                    colSpan={mobileMode ? 5 : 6}
                    count={total}
                    rowsPerPage={rowsPerPage}
                    page={tablePage}
                    sx={{
                      "& .MuiToolbar-root": {
                        minHeight: 36,
                        height: 36,
                        paddingLeft: 1,
                        paddingRight: 1,
                        justifyContent: "flex-end",
                      },
                      "& .MuiTablePagination-selectLabel, & .MuiTablePagination-displayedRows":
                        {
                          margin: 0,
                        },
                    }}
                    labelDisplayedRows={({
                      from,
                      to,
                      count,
                      page,
                    }): React.ReactNode => {
                      return width > BREAKPOINT600
                        ? `${displayedRecordsStart}–${Math.min(
                            total,
                            displayedRecordsEnd,
                          )} of ${count !== -1 ? count : `more than ${to}`}`
                        : "";
                    }}
                    SelectProps={{
                      inputProps: {
                        "aria-label": "rows per page",
                      },
                      native: true,
                    }}
                    onRowsPerPageChange={handleChangeRowsPerPage}
                    onPageChange={() => null}
                    ActionsComponent={(props) => (
                      <TablePaginationActions
                        handleChangePageForward={handleChangePageForward}
                        handleChangePageBackward={handleChangePageBackward}
                        currentApiPage={currentApiPage}
                        displayedRecordsStart={displayedRecordsStart}
                        displayedRecordsEnd={displayedRecordsEnd}
                        handleSetPageZero={() => setTablePage(0)}
                        mobileMode={mobileMode}
                        {...props}
                      />
                    )}
                  />
                </TableCell>
              </TableRow>
            </TableFooter>
          </Table>
        </TableContainer>
      );

    default:
      return (
        <PlaceholderWidget
          placeholderText={intl.formatMessage({
            id: "search.inputPlaceholder",
            defaultMessage: "Webservice suchen...",
          })}
        />
      );
  }
};
