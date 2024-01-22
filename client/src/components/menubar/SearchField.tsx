import { useState } from "react";
import {
  IconButton,
  OutlinedInput,
  InputAdornment,
  FormControl,
  Button,
  styled,
  useTheme,
} from "@mui/material";
import CancelIcon from "@mui/icons-material/Cancel";
import SearchIcon from "@mui/icons-material/Search";
import { PROVIDERTYPE, SERVICE, BREAKPOINT1000 } from "src/constants";
import { useViewport } from "src/custom/ViewportHook";

const page = 0; // a For search triggered by Menubar we always want to start from the first pagination page.

export type SearchProps = {
  triggerSearch: (
    searchString: string | undefined,
    servicetype: SERVICE | undefined,
    provider: PROVIDERTYPE | undefined,
    page: number
  ) => void;
  setSearchString: (searchString: string) => void;
  resetPageToZero: () => void;
  setDrawerOpen: (state: boolean) => void;
};

export type SearchFieldProps = {
  fromDrawer: boolean;
} & SearchProps;

export const SearchField = ({
  triggerSearch,
  setSearchString,
  resetPageToZero,
  setDrawerOpen,
  fromDrawer,
}: SearchFieldProps) => {
  const theme = useTheme();
  const responsiveUI = useViewport().width < BREAKPOINT1000;

  const [localSearchString, setLocalSearchString] = useState("");
  const drawerEnabled = fromDrawer ? fromDrawer : false;

  return (
    <FormControl
      sx={{
        display: "flex",
        flexDirection: "row",
        justifyContent: "center",
        flexGrow: 2,
        padding: "0 4px",
      }}
      variant="standard"
    >
      <OutlinedInput
        autoFocus
        autoComplete="off"
        id="webservicesearch"
        type="outlined"
        placeholder="Webservice suchen..."
        value={localSearchString}
        style={{
          flexGrow: 2,
          height: responsiveUI ? 54 : 40,
          backgroundColor: theme.palette.secondary.main,
        }}
        onChange={(e) => setLocalSearchString(e.target.value)}
        onKeyDown={(e) =>
          e.key === "Enter" &&
          triggerSearch(localSearchString, undefined, undefined, page)
        }
        startAdornment={
          <SearchIcon style={{ marginLeft: -8, marginRight: 6 }} />
        }
        endAdornment={
          <InputAdornment position="end">
            <IconButton
              aria-label="clear search"
              onClick={() => {
                setSearchString("");
                setLocalSearchString("");
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
          resetPageToZero();
          setSearchString(localSearchString);
          triggerSearch(localSearchString, undefined, undefined, page);
          drawerEnabled && setDrawerOpen(false);
        }}
        sx={{
          fontSize: 14,
          marginLeft: 1,
        }}
        type="submit"
        variant="contained"
        aria-label="search"
      >
        {"Suchen"}
      </Button>
    </FormControl>
  );
};
