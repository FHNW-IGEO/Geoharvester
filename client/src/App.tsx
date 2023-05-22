import { useState } from "react";
import { ServiceTable } from "./components/results/ServiceTable";
import { ThemeProvider, createTheme } from "@mui/material/styles";
import { MenuBar } from "./components/menubar/MenuBar";
import { Box } from "@mui/material";
import { Geoservice } from "./types";
import "./App.css";

const theme = createTheme({
  palette: {
    primary: {
      main: "#007CC3",
      contrastText: "#000000",
    },
    secondary: {
      main: "#7FBDE1",
      contrastText: "#000000",
    },
  },
});

export type SearchResult = {
  duration: number;
  total: number;
  docs: Geoservice[];
  fields: string[];
};

function App() {
  const [searchResult, setSearchResult] = useState({} as SearchResult);
  const { docs, total, fields } = searchResult;
  const [placeholderText, setPlaceholderText] = useState(
    "Webservice suchen..."
  );

const Footer = () => {
    return (
      <Box
        sx={{
          minHeight: '25px',
          backgroundColor: '#7FBDE1',
          color: 'white',
          // border: '1px solid #007CC3',
          textAlign: "center",
        }}
      >
        © 2023 GeoHarvester | Ein Projekt in Zusammenarbeit mit dem Institut Geomatik, FHNW und swisstopo
      </Box>
    );
  };

  return (
    <ThemeProvider theme={theme}>
      <div id="wrapper">
        <header className="App-header">
          <MenuBar
            setSearchResult={setSearchResult}
            setPlaceholderText={setPlaceholderText}
          />
        </header>
        <ServiceTable
          docs={docs || []}
          fields={fields}
          total={total}
          placeholderText={placeholderText}
        ></ServiceTable>
        <Footer />
      </div>
    </ThemeProvider>
  );
}

export default App;
