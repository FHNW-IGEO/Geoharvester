import { RESPONSESTATE } from "appConstants";
import { SearchField, SearchProps } from "../menubar/SearchField";
import Box from "@mui/material/Box";

export const FirstSearchUI = ({
  localSearchString,
  setLocalSearchString,
  setDrawerOpen,
  fromDrawer,
  triggerSearch,
  searchParameters,
  responseState,
  updateSearchParameters,
}: SearchProps & {
  fromDrawer: boolean;
  responseState: RESPONSESTATE;
  setDrawerOpen: (state: boolean) => void;
}) => {
  return (
    <div className="PageWrapper">
      <Box className="SearchBox" sx={{ width: 700 }}>
        <SearchField
          {...{
            localSearchString,
            setLocalSearchString,
            setDrawerOpen,
            fromDrawer,
            triggerSearch,
            searchParameters,
            responseState,
            updateSearchParameters,
          }}
        />
      </Box>
    </div>
  );
};
