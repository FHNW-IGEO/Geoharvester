import {
  IconButton,
  OutlinedInput,
  FormControl,
  InputAdornment,
  Button,
  Toolbar,
  styled,
  useTheme,
} from "@mui/material";
import CancelIcon from "@mui/icons-material/Cancel";
import SearchIcon from "@mui/icons-material/Search";
import { SelectChangeEvent } from "@mui/material/Select";
import { MenuDropdown } from "./MenuDropdown";
import { Filter } from "./Filter";
import "../../styles.css";
import { PROVIDERTYPE, SERVICE } from "src/constants";
import { useState } from "react";

export type SearchBarProps = {
  triggerSearch: (
    searchString: string | undefined,
    servicetype: SERVICE | undefined,
    provider: PROVIDERTYPE | undefined,
    page: number
  ) => void;
  servicetypeState: SERVICE;
  setServiceState: (serviceState: SERVICE) => void;
  providerState: PROVIDERTYPE;
  setProviderState: (serviceState: PROVIDERTYPE) => void;
  setSearchString: (searchString: string) => void;
  resetPageToZero: () => void;
};

export const MenuBar = ({
  triggerSearch,
  setServiceState,
  servicetypeState,
  setProviderState,
  providerState,
  setSearchString,
  resetPageToZero,
}: SearchBarProps) => {
  const theme = useTheme();
  const page = 0; // a For search triggered by Menubar we always want to start from the first pagination page.

  const [localSearchString, setlocalSearchString] = useState("");

  const handleChangeService = (event: SelectChangeEvent) => {
    setServiceState(event.target.value as SERVICE);
    triggerSearch(undefined, event.target.value as SERVICE, undefined, page);
  };

  const handleChangeProvider = (event: SelectChangeEvent) => {
    setProviderState(event.target.value as PROVIDERTYPE);
    triggerSearch(
      undefined,
      undefined,
      event.target.value as PROVIDERTYPE,
      page
    );
  };

  const SearchButton = styled(Button)(() => ({
    color: "#101010",
    backgroundColor: "white",
    "&:hover": {
      backgroundColor: "#E8E8E8",
    },
  }));

  return (
    <Toolbar variant="dense" id="menubar">
      <MenuDropdown />
      <div style={{ display: "flex", flex: "1 1 auto" }}>
        <FormControl
          sx={{
            m: 1,
            width: "100%",
            display: "flex",
            flexDirection: "row",
            justifyContent: "center",
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
              maxWidth: 600,
              height: 32,
              backgroundColor: "white",
            }}
            onChange={(e) => setlocalSearchString(e.target.value)}
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
                    setlocalSearchString("");
                  }}
                >
                  <CancelIcon style={{ marginRight: -14, marginLeft: -8 }} />
                </IconButton>
              </InputAdornment>
            }
          />
          <SearchButton
            id="search-button"
            size="small"
            onClick={() => {
              resetPageToZero();
              setSearchString(localSearchString);
              triggerSearch(localSearchString, undefined, undefined, page);
            }}
            sx={{
              fontSize: 14,
              backgroundColor: "white",
              color: theme.palette.primary.main,
            }}
            type="submit"
            variant="outlined"
            aria-label="search"
          >
            {"Suchen"}
          </SearchButton>
        </FormControl>
      </div>
      <Filter
        handleChangeService={handleChangeService}
        handleChangeProvider={handleChangeProvider}
        provider={providerState}
        servicetype={servicetypeState}
      />
    </Toolbar>
  );
};
