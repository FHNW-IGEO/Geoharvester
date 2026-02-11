import { SearchField, SearchProps } from "../menubar/SearchField";
import Box from "@mui/material/Box";

export const FirstSearchUI = ({
  localSearchString,
  setLocalSearchString,
  setDrawerOpen,
  fromDrawer,
  triggerSearch,
  searchParameters,
  updateSearchParameters,
}: SearchProps & {
  fromDrawer: boolean;
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
            updateSearchParameters,
          }}
        />
      </Box>
    </div>
  );
};
