import { Box } from "@mui/material";
import { useTheme } from "@mui/material/styles";
import { FormattedMessage } from "react-intl";

export const Footer = () => {
  const theme = useTheme();

  return (
    <Box
      sx={{
        backgroundColor: theme.palette.primary.main,
        color: theme.palette.secondary.main,
        textAlign: "center",
      }}
    >
      <FormattedMessage
        id="footer.impressum"
        defaultMessage="© 2023- 2026 GeoHarvester | Ein Projekt in Zusammenarbeit mit dem Institut Geomatik, FHNW und Swisstopo"
      />
    </Box>
  );
};
