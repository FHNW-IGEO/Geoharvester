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

export type VisViewProps = {
  visViewOpen: boolean;
  setVisViewOpen: (state: boolean) => void;
};

export const VisView = ({ visViewOpen, setVisViewOpen }: VisViewProps) => {
  const theme = useTheme();
  const [tabNr, setTabNr] = useState("1");
  return (
    <Drawer
      anchor="bottom"
      open={visViewOpen}
      onClose={() => setVisViewOpen(false)}
    >
      <div style={{ minHeight: "90vh" }}>
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
              Visualisierungen
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
        <Box sx={{ width: "100%", typography: "body1" }}>
          <TabContext value={tabNr}>
            <Box sx={{ borderBottom: 1, borderColor: "divider" }}>
              <TabList
                variant="fullWidth"
                centered
                onChange={(_e: React.SyntheticEvent, v: string) => setTabNr(v)}
              >
                <Tab label="Wordcloud" value="1" />
                <Tab label="tbd" value="2" />
                <Tab label="tbd" value="3" />
              </TabList>
            </Box>
            <TabPanel value="1">
              <WordCloud />
            </TabPanel>
            <TabPanel value="2">Item Two</TabPanel>
            <TabPanel value="3">Item Three</TabPanel>
          </TabContext>
        </Box>
      </div>
    </Drawer>
  );
};
