import {
  FormControl,
  useTheme,
  MenuItem,
  Select,
  SelectChangeEvent,
} from "@mui/material";
import { PROVIDER, SERVICE, BREAKPOINT600 } from "../../appConstants";
import { getIcon } from "../../custom/getIcon";
import { SearchParameters } from "types";
import { useViewport } from "../../custom/ViewportHook";
import { useIntl } from "react-intl";

export type SearchBarProps = {
  setSearchResult: (searchResult: any) => void;
  setPlaceholderText: (text: string) => void;
};

type FilterProps = {
  handleChangeService: (event: SelectChangeEvent) => void;
  handleChangeProvider: (event: SelectChangeEvent) => void;
  searchParameters: SearchParameters;
};

export const Filter = ({
  handleChangeService,
  handleChangeProvider,
  searchParameters,
}: FilterProps) => {
  const theme = useTheme();
  const intl = useIntl();
  const { width } = useViewport();
  const mobileMode = width < BREAKPOINT600;

  const serviceText = mobileMode
    ? intl.formatMessage({
        id: "dropdown.mobile",
        defaultMessage: "Alle",
      })
    : intl.formatMessage({
        id: "dropdown.service",
        defaultMessage: "Alle Services",
      });
  const providerText = mobileMode
    ? intl.formatMessage({
        id: "dropdown.mobile",
        defaultMessage: "Alle",
      })
    : intl.formatMessage({
        id: "dropdown.provider",
        defaultMessage: "Alle Quellen",
      });

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "row",
        justifyContent: "end",
      }}
    >
      <FormControl variant="outlined">
        <Select
          className="Dropdown"
          autoComplete="off"
          labelId="select-provider-label"
          id="select-provider"
          value={searchParameters.provider}
          onChange={handleChangeProvider}
          MenuProps={{
            PaperProps: {
              sx: {
                display: "flex",
                alignItem: "center",
                height: "80vh",
              },
            },
          }}
          sx={{
            backgroundColor: theme.palette.secondary.main,
            textAlign: "center",
            height: 40,
            color: theme.palette.primary.main,
            marginLeft: mobileMode ? 6 : 10,
          }}
        >
          {(Object.values(PROVIDER) as PROVIDER[]).map((provider) => {
            return (
              <MenuItem
                key={provider}
                value={provider}
                sx={{ display: "flex", alignItems: "center" }}
              >
                {provider !== PROVIDER.NONE && (
                  <img
                    alt="sourceIcon"
                    src={getIcon(provider)}
                    height={25}
                    width={25}
                    style={{ marginRight: 8 }}
                  />
                )}
                {provider === PROVIDER.NONE ? providerText : provider}
              </MenuItem>
            );
          })}
        </Select>
      </FormControl>
      <FormControl variant="outlined">
        <Select
          className="Dropdown"
          autoComplete="off"
          labelId="select-service-label"
          id="select-service"
          value={searchParameters.service}
          onChange={handleChangeService}
          style={{
            backgroundColor: theme.palette.secondary.main,
            textAlign: "center",
            height: 40,
            color: theme.palette.primary.main,
            marginLeft: mobileMode ? 6 : 10,
            marginRight: mobileMode ? 6 : 10,
          }}
        >
          {(Object.values(SERVICE) as SERVICE[]).map((servicetype) => {
            return (
              <MenuItem key={servicetype} value={servicetype}>
                {servicetype === SERVICE.NONE
                  ? serviceText
                  : servicetype.toUpperCase()}
              </MenuItem>
            );
          })}
        </Select>
      </FormControl>
    </div>
  );
};
