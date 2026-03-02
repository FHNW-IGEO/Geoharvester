import { useMemo } from "react";
import {
  FormControl,
  useTheme,
  MenuItem,
  Select,
  SelectChangeEvent,
} from "@mui/material";
import {
  KEYWORDFIELD,
  LABELS,
  LANG_OPTIONS,
  LANGUAGE,
} from "../../../appConstants";

type WordCloudToolbarProps = {
  language: LANGUAGE;
  keywordfieldToSearch: KEYWORDFIELD;
  setKeywordfieldToSearch: (state: KEYWORDFIELD) => void;
};

export const WordCloudToolbar = ({
  language,
  keywordfieldToSearch,
  setKeywordfieldToSearch,
}: WordCloudToolbarProps) => {
  const theme = useTheme();

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
    <FormControl variant="outlined">
      <Select
        className="Dropdown"
        autoComplete="off"
        labelId="select-provider-label"
        id="select-provider"
        autoWidth
        value={keywordfieldToSearch}
        onChange={(e) => setKeywordfieldToSearch(e.target.value)}
        MenuProps={{
          PaperProps: {
            sx: {
              display: "flex",
              alignItem: "center",
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
  );
};
