import Box from "@mui/material/Box";
import SwipeableDrawer from "@mui/material/SwipeableDrawer";
import Button from "@mui/material/Button";
import { SearchField, SearchProps } from "./SearchField";
import { FormattedMessage } from "react-intl";

import "../../styles.css";

export const SearchDrawer = ({
  localSearchString,
  setLocalSearchString,
  setDrawerOpen,
  drawerOpen,
  triggerSearch,
  searchParameters,
  updateSearchParameters,
}: SearchProps & { drawerOpen: boolean }) => {
  return (
    <div>
      <Button
        variant="contained"
        onClick={() => setDrawerOpen(true)}
        sx={{ ml: 2 }}
      >
        <FormattedMessage id="search.searchButton" defaultMessage="Suchen" />
      </Button>
      <SwipeableDrawer
        anchor="bottom"
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        onOpen={() => setDrawerOpen(true)}
      >
        <Box
          className="SearchBox"
          sx={{ height: 72, backgroundColor: "#f0f0f0" }}
        >
          <SearchField
            fromDrawer
            {...{
              localSearchString,
              setLocalSearchString,
              setDrawerOpen,
              triggerSearch,
              searchParameters,
              updateSearchParameters,
            }}
          />
        </Box>
      </SwipeableDrawer>
    </div>
  );
};
