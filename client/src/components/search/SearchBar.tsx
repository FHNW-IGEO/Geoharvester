import React, { useState } from "react";
import {
  IconButton,
  OutlinedInput,
  InputLabel,
  FormControl,
  InputAdornment,
  Button,
} from "@mui/material";
import CancelIcon from "@mui/icons-material/Cancel";
import { getData } from "../../requests";
import "./search.css";
import SearchIcon from "@mui/icons-material/Search";

type SearchBarProps = {
  setSearchResult: (searchResult: any) => void;
};

export const SearchBar = ({ setSearchResult }: SearchBarProps) => {
  const [searchString, setSearchString] = useState("");

  const triggerSearch = async () =>
    await getData(searchString)
      .then((res) => {
        const { data } = res;
        setSearchResult(data);
      })
      .catch((e) => {
        console.error(e);
        setSearchResult([]); // Fallback on error
      });

  return (
    <div id="search">
      <FormControl sx={{ m: 1, width: "100ch" }} variant="outlined">
        <InputLabel htmlFor="search-bar">Webservices durchsuchen</InputLabel>
        <OutlinedInput
          id="search-bar"
          type="text"
          value={searchString}
          onChange={(e) => setSearchString(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && triggerSearch()}
          startAdornment={<SearchIcon color="disabled"/>}
          endAdornment={
            <InputAdornment position="end">
              <IconButton
                aria-label="trigger-cancel"
                onClick={() => setSearchString("")}
                edge="end"
              >
                <CancelIcon />
              </IconButton>
            </InputAdornment>
          }
          label="Webservices durchsuchen"
        />
      </FormControl>
      <Button id="search-button" size="large" onClick={triggerSearch}>
        Suchen
      </Button>
    </div>
  );
};
