import { useContext, useState } from "react";
import { ImpressumDialog } from "../ImpressumDialog";
import {
  IconButton,
  Menu,
  MenuItem,
  Divider,
  useTheme,
  Box,
  Collapse,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
} from "@mui/material";
import InfoIcon from "@mui/icons-material/Info";
import MenuIcon from "@mui/icons-material/Menu";
import DescriptionIcon from "@mui/icons-material/Description";
import TerminalIcon from "@mui/icons-material/Terminal";
import { FormattedMessage } from "react-intl";
import geoharvesterLogo from "./logo.png";
import { useIntl } from "react-intl";
import { ExpandLess, ExpandMore, Translate } from "@mui/icons-material";

import StarBorder from "@mui/icons-material/StarBorder";
import InboxIcon from "@mui/icons-material/MoveToInbox";

import "../../styles.css";
import { LanguageContext } from "src/lang/LanguageContext";

export const LanguagePicker = () => {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [openImpressum, setOpenImpressum] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);

  const open = Boolean(anchorEl);
  const theme = useTheme();
  const intl = useIntl();

  const { setLanguage, language } = useContext(LanguageContext);
  console.log(language);

  const handleClickOpenImpressum = () => setOpenImpressum(true);

  const handleClickOpen = () => {
    setMenuOpen(!menuOpen);
  };

  const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
    setAnchorEl(event.currentTarget);
  };
  const handleClose = () => {
    setAnchorEl(null);
  };

  return (
    <Box>
      <div style={{ display: "flex", alignItems: "center" }}>
        <IconButton
          size="large"
          aria-label="menu"
          sx={{ color: theme.palette.primary.main }}
          onClick={handleClick}
        >
          <MenuIcon />
        </IconButton>
        <img
          id="GeoharvesterLogo"
          alt="GeoharvesterLogo"
          src={String(geoharvesterLogo)}
          width="242"
          height="29"
          style={{ marginLeft: -10 }}
        />
      </div>
      <ListItemButton onClick={handleClickOpen}>
        <Translate style={{ marginRight: 14 }} />
        <ListItemText
          primary={intl.formatMessage({
            id: "translate.language",
            defaultMessage: "Sprache",
          })}
        />
        {menuOpen ? <ExpandLess /> : <ExpandMore />}
      </ListItemButton>
      <Collapse in={menuOpen} timeout="auto" unmountOnExit>
        <List component="div" disablePadding dense>
          <ListItemButton
            sx={{ pl: 4 }}
            id="de"
            onClick={(e) => setLanguage(e.currentTarget.id)}
          >
            <ListItemText
              primary={intl.formatMessage({
                id: "translate.german",
                defaultMessage: "Deutsch",
              })}
            />
          </ListItemButton>
          <ListItemButton
            sx={{ pl: 4 }}
            id="fr"
            onClick={(e) => setLanguage(e.currentTarget.id)}
          >
            <ListItemText
              primary={intl.formatMessage({
                id: "translate.french",
                defaultMessage: "Französisch",
              })}
            />
          </ListItemButton>
          <ListItemButton
            sx={{ pl: 4 }}
            id="it"
            onClick={(e) => setLanguage(e.currentTarget.id)}
          >
            <ListItemText
              primary={intl.formatMessage({
                id: "translate.italian",
                defaultMessage: "Italienisch",
              })}
            />
          </ListItemButton>
          <ListItemButton
            sx={{ pl: 4 }}
            id="en"
            onClick={(e) => setLanguage(e.currentTarget.id)}
          >
            <ListItemText
              primary={intl.formatMessage({
                id: "translate.english",
                defaultMessage: "Englisch",
              })}
            />
          </ListItemButton>
        </List>
      </Collapse>
      <Menu
        id="basic-menu"
        anchorEl={anchorEl}
        open={open}
        onClose={handleClose}
        style={{ marginLeft: -16 }}
        MenuListProps={{
          "aria-labelledby": "basic-button",
        }}
      >
        <MenuItem
          onClick={() => {
            setAnchorEl(null);
            window.open("https://github.com/FHNW-IVGI/Geoharvester");
          }}
        >
          <DescriptionIcon style={{ marginRight: 14 }} />
          <FormattedMessage
            id="menu.documentation"
            defaultMessage="Dokumentation"
          />
        </MenuItem>
        <Divider />
        <MenuItem
          onClick={() => {
            setAnchorEl(null);
            window.open("https://geoharvester.ch/api/docs");
          }}
        >
          <TerminalIcon style={{ marginRight: 14 }} />
          <FormattedMessage id="menu.api" defaultMessage="API" />
        </MenuItem>
        <Divider />
        <MenuItem onClick={handleClickOpenImpressum}>
          <InfoIcon style={{ marginRight: 14 }} />
          <FormattedMessage id="menu.impressum" defaultMessage="Impressum" />
        </MenuItem>
      </Menu>

      <ImpressumDialog open={openImpressum} setOpen={setOpenImpressum} />
    </Box>
  );
};
