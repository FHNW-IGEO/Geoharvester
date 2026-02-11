import {
  Button,
  Dialog,
  DialogTitle,
  DialogActions,
  DialogContent,
  DialogContentText,
  Typography,
} from "@mui/material";

export function ImpressumDialog(props: any) {
  const { open, setOpen } = props;

  const handleClose = () => setOpen(false);

  return (
    <Dialog open={open} onClose={handleClose} fullWidth={true} maxWidth="lg">
      <DialogTitle>
        <Typography variant="h4">Impressum</Typography>
      </DialogTitle>
      <DialogContent>
        <DialogContentText>
          <Typography variant="h5" sx={{ mt: 4 }}>
            Finanzierung
          </Typography>
          <Typography variant="body1">
            Strategie Geoinformation Schweiz
          </Typography>
          <Typography variant="h5" sx={{ mt: 4 }}>
            Projektteam
          </Typography>
          <Typography variant="body1">
            Pia Bereuter (FHNW), Pasquale Di Donato (swisstopo), Elia Ferrari
            (FHNW), David Oesch (swisstopo), Friedrich Striewski (FHNW), Fiona
            Tiefenbacher (FHNW)
          </Typography>
          <Typography variant="h5" sx={{ mt: 4 }}>
            Realisierung
          </Typography>
          <Typography variant="body1">
            {" "}
            Institut Geomatik FHNW, Muttenz in Zusammenarbeit mit swisstopo,
            Wabern{" "}
          </Typography>
          <Typography variant="h5" sx={{ mt: 4 }}>
            Github
          </Typography>
          <Typography variant="body1">
            <a
              href="https://github.com/FHNW-IGEO/Geoharvester"
              target="_blank"
              rel="noreferrer"
            >
              https://github.com/FHNW-IGEO/Geoharvester
            </a>
          </Typography>
          <Typography variant="h5" sx={{ mt: 4 }}>
            Technische Hinweise
          </Typography>
          <Typography variant="body1">
            {" "}
            Im Rahmen der GeoUnconference Veranstaltung vom 13.10.2022, wurde
            verdeutlicht, dass ein "Portal" fehlt, welches als Single Point of
            Entry die Daten in den öffentlichen Geodiensten in einem Katalog
            zusammengefasst (aggregiert und harmonisiert) und den Nutzenden den
            Swiss Geo Data Lake aufzeigt. Dieser Harvester, welcher
            kontinuierlich die öffentlichen Geodienste (OGC Services) der
            Schweiz automatisiert auf- und nachführt, ist ein erster Schritt in
            die Richtung eines solchen Online Portals, welches die verfügbaren
            öffentlichen Geodienste als Katalog bündelt und zur Verfügung
            stellt.{" "}
          </Typography>
          <Typography variant="h5" sx={{ mt: 4 }}>
            Kontakt-Adresse
          </Typography>
          <Typography variant="body1">
            Institut Geomatik FHNW, Hofackerstrasse 30, 4231 Muttenz, Schweiz,
            geomatik.habg@fhnw.ch{" "}
          </Typography>
          <Typography variant="h5" sx={{ mt: 4 }}>
            Verantwortliche Person
          </Typography>
          <Typography variant="body1">
            {" "}
            Pia Bereuter (FHNW) and Pasquale Di Donato (swisstopo){" "}
          </Typography>
          <Typography variant="h5" sx={{ mt: 4 }}>
            Haftungsausschluss
          </Typography>
          <Typography variant="body1">
            Der Autor übernimmt keinerlei Gewähr hinsichtlich der inhaltlichen
            Richtigkeit, Genauigkeit, Aktualität, Zuverlässigkeit und
            Vollständigkeit der Informationen. Haftungsansprüche gegen den Autor
            wegen Schäden materieller oder immaterieller Art, welche aus dem
            Zugriff oder der Nutzung bzw. Nichtnutzung der veröffentlichten
            Informationen, durch Missbrauch der Verbindung oder durch technische
            Störungen entstanden sind, werden ausgeschlossen. Alle Angebote sind
            unverbindlich. Der Autor behält es sich ausdrücklich vor, Teile der
            Seiten oder das gesamte Angebot ohne besondere Ankündigung zu
            verändern, zu ergänzen, zu löschen oder die Veröffentlichung
            zeitweise oder endgültig einzustellen.{" "}
          </Typography>
          <Typography variant="h5" sx={{ mt: 4 }}>
            Haftungsausschluss für Links
          </Typography>
          <Typography variant="body1">
            {" "}
            Verweise und Links auf Webseiten Dritter liegen ausserhalb unseres
            Verantwortungsbereichs. Es wird jegliche Verantwortung für solche
            Webseiten abgelehnt. Der Zugriff und die Nutzung solcher Webseiten
            erfolgen auf eigene Gefahr des jeweiligen Nutzers.{" "}
          </Typography>
          <Typography variant="h5" sx={{ mt: 4 }}>
            Urheberrechte
          </Typography>
          <Typography variant="body1">
            {" "}
            Die Urheber- und alle anderen Rechte an Inhalten, Bildern, Fotos
            oder anderen Dateien auf dieser Website, gehören ausschliesslich der
            Fachhochschule Nordwestschweiz oder den speziell genannten
            Rechteinhabern. Für die Reproduktion jeglicher Elemente ist die
            schriftliche Zustimmung des Urheberrechtsträgers im Voraus
            einzuholen.{" "}
          </Typography>
        </DialogContentText>
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose}>Schliessen</Button>
      </DialogActions>
    </Dialog>
  );
}
