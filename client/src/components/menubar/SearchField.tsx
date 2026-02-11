import {
  IconButton,
  OutlinedInput,
  InputAdornment,
  FormControl,
  Button,
  useTheme,
} from "@mui/material";
import CancelIcon from "@mui/icons-material/Cancel";
import SearchIcon from "@mui/icons-material/Search";
import { BREAKPOINT1000 } from "../../appConstants";
import { useViewport } from "../../custom/ViewportHook";
import { SearchParameters } from "../../types";
import { FormattedMessage, useIntl } from "react-intl";

export type SearchProps = {
  localSearchString: string;
  setLocalSearchString: (searchstring: string) => void;
  setDrawerOpen: (state: boolean) => void;
  triggerSearch: (parameter: SearchParameters) => void;
  searchParameters: SearchParameters;
  updateSearchParameters: (parameter: SearchParameters) => void;
};

export type SearchFieldProps = {
  fromDrawer: boolean;
} & SearchProps;

export const SearchField = ({
  localSearchString,
  setLocalSearchString,
  setDrawerOpen,
  fromDrawer,
  triggerSearch,
  searchParameters,
  updateSearchParameters,
}: SearchFieldProps) => {
  const theme = useTheme();
  const responsiveUI = useViewport().width < BREAKPOINT1000;
  const intl = useIntl();

  // const [localSearchString, setLocalSearchString] = useState("");
  const drawerEnabled = fromDrawer ? fromDrawer : false;

  return (
    <FormControl
      sx={{
        display: "flex",
        flexDirection: "row",
        justifyContent: "center",
        flexGrow: 2,
      }}
      variant="standard"
    >
      <OutlinedInput
        autoFocus
        autoComplete="off"
        id="webservicesearch"
        type="outlined"
        placeholder={intl.formatMessage({
          id: "search.inputPlaceholder",
          defaultMessage: "Webservice suchen...",
        })}
        value={localSearchString}
        style={{
          flexGrow: 2,
          height: responsiveUI ? 56 : 40,
          backgroundColor: theme.palette.secondary.main,
        }}
        onChange={(e) => setLocalSearchString(e.target.value)}
        onKeyDown={(e) =>
          e.key === "Enter" &&
          triggerSearch({
            ...searchParameters,
            page: 0,
            searchString: localSearchString,
          })
        }
        startAdornment={
          <SearchIcon style={{ marginLeft: -8, marginRight: 6 }} />
        }
        endAdornment={
          <InputAdornment position="end">
            <IconButton
              aria-label="clear search"
              onClick={() => {
                setLocalSearchString("");
                triggerSearch({
                  ...searchParameters,
                  page: 0,
                  searchString: "",
                });
              }}
            >
              <CancelIcon style={{ marginRight: -14, marginLeft: -8 }} />
            </IconButton>
          </InputAdornment>
        }
      />
      <Button
        id="search-button"
        size="small"
        onClick={() => {
          drawerEnabled && setDrawerOpen(false);
          triggerSearch({
            ...searchParameters,
            page: 0,
            searchString: localSearchString,
          });
        }}
        sx={{
          fontSize: 12,
          ml: 0.5,
          minWidth: 120,
        }}
        type="submit"
        variant="contained"
        aria-label="search"
      >
        <FormattedMessage id="search.searchButton" defaultMessage="Suchen" />
      </Button>
    </FormControl>
  );
};
