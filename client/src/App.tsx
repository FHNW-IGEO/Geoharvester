import { useContext, useEffect, useState } from "react";
import { ServiceTable } from "./components/table/ServiceTable";
import { ThemeProvider } from "@mui/material/styles";
import { Header } from "./components/menubar/Header";
import { Geoservice, SearchParameters } from "./types";
import {
  PROVIDER,
  RESPONSESTATE,
  SERVICE,
  DEFAULTROWSPERPAGE,
  DEFAULTCHUNKSIZE,
  BREAKPOINT600,
} from "./appConstants";
import { getData, getDataByKeyword } from "./requests";
import { Footer } from "./components/Footer";
import { Stack } from "@mui/material";
import { FirstSearchUI } from "./components/table/FirstSearchUI";
import { LanguageContext } from "./lang/LanguageContext";
import { theme } from "./theme/index";
import { VisView } from "./components/vis/VisView";
import { useViewport } from "./custom/ViewportHook";

import "./styles.css";

export type SearchResult = {
  page: number;
  pages: number;
  total: number;
  size: number; // Items per page
  items: Geoservice[];
};

function App() {
  const [searchResult, setSearchResult] = useState({} as SearchResult);
  const [responseState, setResponseState] = useState(
    RESPONSESTATE.UNINITIALIZED,
  );

  const [tablePage, setTablePage] = useState<number>(0); // Needed for the table UI and to dertermine when to make an API call
  const [currentApiPage, setCurrentApiPage] = useState(0); // Page of the paginated API, different than the UI table page.
  const [size, setSize] = useState(DEFAULTROWSPERPAGE);
  const [localSearchString, setLocalSearchString] = useState("");
  const [visViewOpen, setVisViewOpen] = useState(false);

  const { language } = useContext(LanguageContext);
  const { width } = useViewport();
  const mobileMode = width < BREAKPOINT600;

  const defaultSearchParameter = {
    searchString: "", // Using an empty string would cause useEffect diffing to fail when searching without text
    service: SERVICE.NONE,
    provider: PROVIDER.NONE,
    page: 0,
  };

  const [searchParameters, setSearchParameters] = useState<SearchParameters>(
    defaultSearchParameter,
  );
  const { items, total } = searchResult;

  const updateSearchParameters = (parameter: SearchParameters) => {
    // Required for resetting the search string with the x button and syncing state
    setSearchParameters(parameter);
  };

  const updateURL = (
    searchString: string | undefined,
    service: SERVICE | undefined,
    provider: PROVIDER | undefined,
    language: string,
    page: number,
  ) => {
    const url = new URL(window.location.href);
    if (searchString) {
      url.searchParams.set("searchString", searchString);
    } else {
      url.searchParams.delete("searchString");
    }

    if (provider) {
      url.searchParams.set("provider", provider);
    } else {
      url.searchParams.delete("provider");
    }

    if (service) {
      url.searchParams.set("service", service);
    } else {
      url.searchParams.delete("service");
    }

    if (language) {
      url.searchParams.set("lang", language);
    } else {
      url.searchParams.delete("lang");
    }

    if (page) {
      url.searchParams.set("page", page.toString());
    } else {
      url.searchParams.delete("page");
    }

    // Update the browser's URL without refreshing the page
    window.history.pushState({}, "", url.toString());
  };

  const handleResponseParsing = (res: any, parameters: SearchParameters) => {
    updateSearchParameters(parameters);
    const { data } = res;
    if (data.items.length > 0) {
      setResponseState(RESPONSESTATE.SUCCESS);
      setSearchResult(data);
      setCurrentApiPage(data.page);
      setTablePage(0);
    } else {
      setResponseState(RESPONSESTATE.EMPTY);
      setSearchResult({} as SearchResult); // Fallback on error
      setTablePage(0);
    }
  };

  const handleResponseFailure = (e: any) => {
    console.error(e);
    setResponseState(RESPONSESTATE.ERROR);
    setSearchResult({} as SearchResult); // Fallback on error
    setTablePage(0);
  };

  const triggerSearch = async (parameters: SearchParameters) => {
    const { searchString, service, provider, page } = parameters;
    updateURL(searchString, service, provider, language, page);

    setResponseState(RESPONSESTATE.WAITING);

    await getData(
      searchString as string,
      service,
      provider,
      language,
      page,
      DEFAULTCHUNKSIZE,
    )
      .then((res) => handleResponseParsing(res, parameters))
      .catch((e) => handleResponseFailure(e));
  };

  const triggerSearchbyKeyword = async (parameters: SearchParameters) => {
    const { searchString, page } = parameters;
    updateURL(searchString, undefined, undefined, language, page);

    setResponseState(RESPONSESTATE.WAITING);

    await getDataByKeyword(
      searchString as string,
      language,
      page,
      DEFAULTCHUNKSIZE,
    )
      .then((res) =>
        handleResponseParsing(
          res,
          (parameters = {
            searchString,
            service: SERVICE.NONE,
            provider: PROVIDER.NONE,
            page: 0,
          }),
        ),
      )
      .catch((e) => handleResponseFailure(e));
  };

  useEffect(() => {
    // Trigger a search on copy paste with search params
    const urlParams = new URLSearchParams(window.location.search);

    const searchString = urlParams.get("searchString");
    const service = urlParams.get("service") as SERVICE | null;
    const provider = urlParams.get("provider") as PROVIDER | null;
    const page = urlParams.get("page");

    if (searchString || service || provider || page) {
      const searchParams: SearchParameters = {
        searchString: searchString || "",
        service: service || SERVICE.NONE,
        provider: provider || PROVIDER.NONE,
        page: page ? parseInt(page, 10) : 0,
      };
      setSearchParameters(searchParams);
      triggerSearch(searchParams);
    }
  }, []);

  return (
    <ThemeProvider theme={theme}>
      <Stack sx={{ height: "100vh" }}>
        <Header
          {...{
            localSearchString,
            setLocalSearchString,
            updateSearchParameters,
            searchParameters,
            responseState,
            triggerSearch,
            visViewOpen,
            setVisViewOpen,
            mobileMode,
          }}
        />
        {responseState === RESPONSESTATE.UNINITIALIZED ? (
          <FirstSearchUI
            setDrawerOpen={() => false}
            fromDrawer={false}
            {...{
              localSearchString,
              setLocalSearchString,
              updateSearchParameters,
              triggerSearch,
              responseState,
              searchParameters,
            }}
          />
        ) : (
          <ServiceTable
            docs={items || []}
            rowsPerPage={size}
            setRowsPerPage={setSize}
            {...{
              searchParameters,
              responseState,
              total,
              currentApiPage,
              triggerSearch,
              triggerSearchbyKeyword,
              mobileMode,
            }}
            tablePage={tablePage}
            setTablePage={setTablePage}
          />
        )}
        <Footer />
      </Stack>
      {visViewOpen && (
        <VisView
          {...{ visViewOpen, setVisViewOpen, language, triggerSearchbyKeyword }}
        />
      )}
    </ThemeProvider>
  );
}

export default App;
