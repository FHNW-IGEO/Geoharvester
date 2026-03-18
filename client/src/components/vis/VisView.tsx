import { useState } from "react";
import { Close } from "@mui/icons-material";
import {
  AppBar,
  Drawer,
  IconButton,
  Toolbar,
  Typography,
  useTheme,
  Tab,
} from "@mui/material";
import { Box } from "@mui/system";
import { TabContext, TabList, TabPanel } from "@mui/lab";
import { WordCloud } from "./tab1/WordCloud";
import { LANGUAGE } from "appConstants";
import { SearchParameters } from "types";
import { useIntl } from "react-intl";

export type VisViewProps = {
  visViewOpen: boolean;
  setVisViewOpen: (state: boolean) => void;
  language: LANGUAGE;
  triggerSearchbyKeyword: (parameters: SearchParameters) => void;
};

export const VisView = ({
  visViewOpen,
  setVisViewOpen,
  language,
  triggerSearchbyKeyword,
}: VisViewProps) => {
  const theme = useTheme();
  const intl = useIntl();

  const [tabNr, setTabNr] = useState("1");
  return (
    <Drawer
      anchor="bottom"
      open={visViewOpen}
      onClose={() => setVisViewOpen(false)}
    >
      <Box style={{ height: "90vh", display: "flex", flexDirection: "column" }}>
        <AppBar
          position="static"
          sx={{
            backgroundColor: theme.palette.primary.main,
            padding: 0,
            height: 40,
            display: "flex",
            justifyContent: "center",
          }}
        >
          <Toolbar>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              {intl.formatMessage({
                id: "vis.header",
                defaultMessage: "Visualisierungen",
              })}
            </Typography>
            <IconButton
              size="small"
              edge="start"
              color="inherit"
              aria-label="menu"
              sx={{ mr: 0 }}
              onClick={() => setVisViewOpen(false)}
            >
              <Close />
            </IconButton>
          </Toolbar>
        </AppBar>
        <Box
          sx={{
            flex: 1,
            display: "flex",
            flexDirection: "column",
            width: "100%",
            overflow: "hidden",
          }}
        >
          <TabContext value={tabNr}>
            <Box sx={{ borderBottom: 1, borderColor: "divider" }}>
              <TabList
                variant="fullWidth"
                centered
                onChange={(_e: React.SyntheticEvent, v: string) => setTabNr(v)}
              >
                <Tab label="Wordcloud" value="1" />
              </TabList>
            </Box>
            <TabPanel
              value="1"
              sx={{
                flex: 1,
                padding: 0,
                display: "flex",
                flexDirection: "column",
                overflow: "hidden",
              }}
            >
              <WordCloud
                open={visViewOpen}
                closeVisView={() => setVisViewOpen(false)}
                active={tabNr === "1"}
                language={language}
                triggerSearchbyKeyword={triggerSearchbyKeyword}
              />
            </TabPanel>
            <TabPanel value="2">Item Two</TabPanel>
            <TabPanel value="3">Item Three</TabPanel>
          </TabContext>
        </Box>
      </Box>
    </Drawer>
  );
};
