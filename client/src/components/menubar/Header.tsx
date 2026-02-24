import { useState } from "react";
import { AppBar, Toolbar } from "@mui/material";
import { SelectChangeEvent } from "@mui/material/Select";
import { MenuComponent } from "./MenuComponent";
import { Filter } from "./Filter";
import {
  PROVIDER,
  SERVICE,
  BREAKPOINT1000,
  RESPONSESTATE,
} from "../../appConstants";
import { SearchField } from "./SearchField";
import { useTheme } from "@mui/material/styles";
import { useViewport } from "../../custom/ViewportHook";
import { SearchDrawer } from "./SearchDrawer";
import { SearchParameters } from "types";
import "../../styles.css";
import { Stack } from "@mui/system";

export type SearchBarProps = {
  localSearchString: string;
  setLocalSearchString: (searchstring: string) => void;
  searchParameters: SearchParameters;
  responseState: RESPONSESTATE;
  triggerSearch: (parameters: SearchParameters) => void;
  updateSearchParameters: (parameters: SearchParameters) => void;
};

export const Header = ({
  localSearchString,
  setLocalSearchString,
  searchParameters,
  responseState,
  triggerSearch,
  updateSearchParameters,
}: SearchBarProps) => {
  const theme = useTheme();
  const { width } = useViewport();
  const [drawerOpen, setDrawerOpen] = useState(false);

  const handleChangeService = (event: SelectChangeEvent) => {
    triggerSearch({
      ...searchParameters,
      service: event.target.value as SERVICE,
      page: 0,
    });
  };

  const handleChangeProvider = (event: SelectChangeEvent) => {
    triggerSearch({
      ...searchParameters,
      provider: event.target.value as PROVIDER,
      page: 0,
    });
  };
  return (
    <Stack direction="column">
      <AppBar
        position="sticky"
        sx={{
          backgroundColor: theme.palette.secondary.main,
          boxShadow: 0,
          borderBottom: "1px solid #E0E0E0",
        }}
      >
        <div className="AppBarSpacing">
          <MenuComponent />
        </div>
      </AppBar>
      <AppBar
        position="sticky"
        sx={{
          backgroundColor: theme.palette.primary.main,
          padding: 1,
          boxShadow:
            "0px 2px 4px -1px rgba(0,0,0,0.2),0px 4px 5px 0px rgba(0,0,0,0.14),0px 1px 10px 0px rgba(0,0,0,0)",
        }}
      >
        <div className="AppBarSpacing">
          {responseState === RESPONSESTATE.UNINITIALIZED ? (
            <div />
          ) : width > BREAKPOINT1000 ? (
            <SearchField
              fromDrawer={false}
              {...{
                localSearchString,
                setLocalSearchString,
                setDrawerOpen,
                triggerSearch,
                searchParameters,
                updateSearchParameters,
                responseState,
              }}
            />
          ) : (
            <SearchDrawer
              {...{
                localSearchString,
                setLocalSearchString,
                setDrawerOpen,
                triggerSearch,
                searchParameters,
                updateSearchParameters,
                responseState,
              }}
              drawerOpen={drawerOpen}
            />
          )}
          <Filter
            handleChangeService={handleChangeService}
            handleChangeProvider={handleChangeProvider}
            searchParameters={searchParameters}
          />
        </div>
      </AppBar>
    </Stack>
  );
};
