import { useTheme } from "@mui/material/styles";
import Box from "@mui/material/Box";
import IconButton from "@mui/material/IconButton";
import FirstPageIcon from "@mui/icons-material/FirstPage";
import KeyboardArrowLeft from "@mui/icons-material/KeyboardArrowLeft";
import KeyboardArrowRight from "@mui/icons-material/KeyboardArrowRight";

interface TablePaginationActionsProps {
  mobileMode: boolean;
  count: number;
  page: number;
  currentApiPage: number;
  displayedRecordsStart: number;
  displayedRecordsEnd: number;
  onPageChange: (
    event: React.MouseEvent<HTMLButtonElement>,
    newPage: number,
  ) => void;
  handleChangePageForward?: (
    event: React.MouseEvent<HTMLButtonElement>,
    newPage: number,
  ) => void;
  handleChangePageBackward?: (
    event: React.MouseEvent<HTMLButtonElement>,
    newPage: number,
  ) => void;
  handleSetPageZero?: (event: React.MouseEvent<HTMLButtonElement>) => void;
}

// MUI Default, source: https://mui.com/material-ui/react-table/#customization
export const TablePaginationActions = (props: TablePaginationActionsProps) => {
  const theme = useTheme();
  const {
    count,
    page,
    handleChangePageForward,
    handleChangePageBackward,
    handleSetPageZero,
    currentApiPage,
    displayedRecordsStart,
    displayedRecordsEnd,
    mobileMode,
  } = props;

  const handleBackButtonClick = (
    event: React.MouseEvent<HTMLButtonElement>,
  ) => {
    handleChangePageBackward && handleChangePageBackward(event, page - 1);
  };

  const handleNextButtonClick = (
    event: React.MouseEvent<HTMLButtonElement>,
  ) => {
    handleChangePageForward && handleChangePageForward(event, page + 1);
  };

  const handleFirstPageButtonClick = (
    event: React.MouseEvent<HTMLButtonElement>,
  ) => {
    handleSetPageZero && handleSetPageZero(event);
  };

  return (
    <Box
      sx={{
        flexShrink: 0,
        ml: mobileMode ? 0 : 3.5,
      }}
    >
      <IconButton
        onClick={handleFirstPageButtonClick}
        disabled={page === 0 && currentApiPage === 0}
        aria-label="first page"
      >
        {theme.direction === "rtl" ? <div /> : <FirstPageIcon />}
      </IconButton>
      <IconButton
        onClick={handleBackButtonClick}
        disabled={currentApiPage === 0 && displayedRecordsStart === 0}
        aria-label="previous page"
      >
        {theme.direction === "rtl" ? (
          <KeyboardArrowRight />
        ) : (
          <KeyboardArrowLeft />
        )}
      </IconButton>
      <IconButton
        onClick={handleNextButtonClick}
        disabled={displayedRecordsEnd >= count}
        aria-label="next page"
      >
        {theme.direction === "rtl" ? (
          <KeyboardArrowLeft />
        ) : (
          <KeyboardArrowRight />
        )}
      </IconButton>
      {!mobileMode && (
        <IconButton
          onClick={handleFirstPageButtonClick}
          disabled
          aria-label="first page"
        >
          {theme.direction === "ltr" ? <div /> : <FirstPageIcon />}
        </IconButton>
      )}
    </Box>
  );
};
