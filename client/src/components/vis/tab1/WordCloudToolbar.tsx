import { useMemo } from "react";
import {
  FormControl,
  useTheme,
  MenuItem,
  Select,
  Checkbox,
  FormControlLabel,
  FormGroup,
} from "@mui/material";
import {
  KEYWORDFIELD,
  LABELS,
  LANG_OPTIONS,
  LANGUAGE,
} from "../../../appConstants";
import { SpiralType } from "./WordCloud";
import { Stack } from "@mui/system";
import { useIntl } from "react-intl";

type WordCloudToolbarProps = {
  language: LANGUAGE;
  keywordfieldToSearch: KEYWORDFIELD;
  setKeywordfieldToSearch: (state: KEYWORDFIELD) => void;
  setSpiralType: (state: SpiralType) => void;
  spiralType: SpiralType;
  withRotation: boolean;
  setWithRotation: (state: boolean) => void;
};

export const WordCloudToolbar = ({
  language,
  keywordfieldToSearch,
  setKeywordfieldToSearch,
  setSpiralType,
  spiralType,
  withRotation,
  setWithRotation,
}: WordCloudToolbarProps) => {
  const theme = useTheme();
  const intl = useIntl();

  const selectOptions = useMemo(() => {
    const options = [
      {
        field: KEYWORDFIELD.KEYWORDS,
        name: LABELS.KEYWORDS[language],
      },
      {
        field: KEYWORDFIELD.KEYWORDS_NLP,
        name: LABELS.KEYWORDS_NLP[language],
      },
    ];

    options.push(
      {
        field: LANG_OPTIONS[`KEYWORDS_${language}`].field as KEYWORDFIELD,
        name: LANG_OPTIONS[`KEYWORDS_${language}`].name,
      },
      {
        field: LANG_OPTIONS[`KEYWORDS_NLP_${language}`].field as KEYWORDFIELD,
        name: LANG_OPTIONS[`KEYWORDS_NLP_${language}`].name,
      },
    );

    return options;
  }, [language]);

  return (
    <Stack
      direction="row"
      sx={{
        justifyContent: "space-between",
        alignItems: "center",
        width: "100%",
      }}
    >
      <FormControl variant="outlined">
        <Select
          className="Dropdown"
          autoComplete="off"
          autoWidth
          value={keywordfieldToSearch}
          onChange={(e) => setKeywordfieldToSearch(e.target.value)}
          MenuProps={{
            PaperProps: {
              sx: {
                display: "flex",
                alignItems: "center",
              },
            },
          }}
          sx={{
            backgroundColor: theme.palette.secondary.main,
            textAlign: "center",
            height: 40,
            color: theme.palette.primary.main,
          }}
        >
          {selectOptions.map((option, i) => {
            return (
              <MenuItem
                key={i}
                value={option.field}
                sx={{ display: "flex", alignItems: "center" }}
              >
                {option.name}
              </MenuItem>
            );
          })}
        </Select>
      </FormControl>

      <Stack direction="row" alignItems="center" spacing={2}>
        <FormControl variant="outlined">
          <Select
            className="Dropdown"
            autoWidth
            onChange={(e) => setSpiralType(e.target.value as SpiralType)}
            value={spiralType}
            MenuProps={{
              PaperProps: {
                sx: {
                  display: "flex",
                  alignItems: "center",
                },
              },
            }}
            sx={{
              backgroundColor: theme.palette.secondary.main,
              textAlign: "center",
              height: 40,
              color: theme.palette.primary.main,
            }}
          >
            <MenuItem key={"archimedean"} value={"archimedean"}>
              archimedean
            </MenuItem>
            <MenuItem key={"rectangular"} value={"rectangular"}>
              rectangular
            </MenuItem>
          </Select>
        </FormControl>
        <FormControlLabel
          sx={{ color: theme.palette.primary.main }}
          control={
            <Checkbox
              checked={withRotation}
              onChange={() => setWithRotation(!withRotation)}
              size="large"
            />
          }
          label={intl.formatMessage({
            id: "dropdown.rotation",
            defaultMessage: "Rotation",
          })}
        />
      </Stack>
    </Stack>
  );
};
