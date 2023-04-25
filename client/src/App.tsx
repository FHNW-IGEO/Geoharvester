import React, { useEffect, useState } from "react";
import { SearchBar } from "./components/search/SearchBar";
import { Footer } from "./components/footer/Footer";
import { ResultArea, StatisticsBox } from "./components/results/ResultArea";
import { getServerStatus } from "./requests";
import { ThemeProvider, createTheme } from "@mui/material/styles";
import { MenuBar } from "./components/menu/MenuBar";
import { Geoservice } from "./types";
import "./App.css";

const theme = createTheme({
  palette: {
    primary: {
      // main: "#ED7D31",
      main: "#ffbe92",
      // main: "#e69138",
      contrastText: "#000000",
    },
    secondary: {
      // main: "#ED7D31",
      // main: "#ffbe92",
      main: "#e69138",
      contrastText: "#000000",
    }
  },
});

export type SearchResult = {
  duration: number;
  total: number;
  docs: Geoservice[];
  fields: string[];
};

function App() {
  const [statusString, setStatusString] = useState("not connected");
  const [searchResult, setSearchResult] = useState({} as SearchResult);

  const checkServerStatus = () =>
    getServerStatus()
      .then((res) => {
        setStatusString(res ? res : "error");
      })
      .catch((e) => console.error(e));

  useEffect(() => {
    checkServerStatus();
  }, []);

  const { docs, total, fields } = searchResult;

  return (
    <ThemeProvider theme={theme}>
    {/* <ThemeProvider theme={theme}> */}
      <header className="App-header">
        {/* NDGI Project Geoharvester */}
        <MenuBar/>
      </header>
      {/* <div>
      <FilterAltIcon variant="contained">Hello World</FilterAltIcon>
      </div> */}
      <main className="App-main">
        <SearchBar setSearchResult={setSearchResult} />
        <StatisticsBox total={total || 0}></StatisticsBox>
        <ResultArea docs={docs || [[]]} fields={fields}></ResultArea>
      </main>
      <footer className="App-footer">
        <Footer status={statusString} checkServerStatus={checkServerStatus} />
      </footer>
    </ThemeProvider>
  );
}

export default App;
