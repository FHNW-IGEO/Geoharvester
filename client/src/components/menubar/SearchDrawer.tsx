import Box from "@mui/material/Box";
import SwipeableDrawer from "@mui/material/SwipeableDrawer";
import { Button, useTheme } from "@mui/material";
import { SearchField, SearchProps } from "./SearchField";
import { FormattedMessage } from "react-intl";
import { RESPONSESTATE } from "appConstants";

export const SearchDrawer = ({
  localSearchString,
  setLocalSearchString,
  setDrawerOpen,
  drawerOpen,
  triggerSearch,
  searchParameters,
  responseState,
  updateSearchParameters,
}: SearchProps & { drawerOpen: boolean; responseState: RESPONSESTATE }) => {
  const theme = useTheme();

  return (
    <div>
      <Button
        variant="contained"
        onClick={() => setDrawerOpen(true)}
        sx={{
          ml: 1,
          backgroundColor: theme.palette.secondary.main,
          color: theme.palette.primary.main,
          width: 120,
        }}
      >
        <FormattedMessage id="search.searchButton" defaultMessage="Suchen" />
      </Button>
      <SwipeableDrawer
        anchor="bottom"
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        onOpen={() => setDrawerOpen(true)}
      >
        <Box className="SearchBox" sx={{ height: 72 }}>
          <SearchField
            fromDrawer
            {...{
              localSearchString,
              setLocalSearchString,
              setDrawerOpen,
              triggerSearch,
              searchParameters,
              responseState,
              updateSearchParameters,
            }}
          />
        </Box>
      </SwipeableDrawer>
    </div>
  );
};
