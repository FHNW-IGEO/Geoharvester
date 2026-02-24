import { Close } from "@mui/icons-material";
import {
  AppBar,
  Drawer,
  IconButton,
  Toolbar,
  Typography,
  useTheme,
} from "@mui/material";

export type VisViewProps = {
  visViewOpen: boolean;
  setVisViewOpen: (state: boolean) => void;
};

export const VisView = ({ visViewOpen, setVisViewOpen }: VisViewProps) => {
  const theme = useTheme();
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

            {/* <Button color="inherit">Login</Button> */}
          </Toolbar>
        </AppBar>
        123
      </div>
    </Drawer>
  );
};
