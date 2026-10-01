import Button from "@mui/material/Button";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogContentText from "@mui/material/DialogContentText";
import DialogTitle from "@mui/material/DialogTitle";

export function EolPopup({
  popupOpen,
  setPopupOpen,
}: {
  popupOpen: boolean;
  setPopupOpen: (state: boolean) => void;
}) {
  return (
    <Dialog
      open={popupOpen}
      onClose={() => setPopupOpen(false)}
      aria-labelledby="alert-dialog-title"
      aria-describedby="alert-dialog-description"
      role="alertdialog"
    >
      <DialogTitle id="alert-dialog-title">
        {"End of Life geoharvester.ch"}
      </DialogTitle>
      <DialogContent>
        <DialogContentText id="alert-dialog-description">
          <h3>Deutsch</h3> Der Proof of Concept geoharvester.ch wird am 31. März
          2027 eingestellt. Ab diesem Datum steht der Dienst nicht mehr zur
          Verfügung. Wir danken Ihnen für die Nutzung von geoharvester.ch sowie
          für Ihren Beitrag und das während dieser Pilotphase gegebene Feedback.
          <hr></hr>
          <h3>Italiano</h3>
          Il Proof of Concept geoharvester.ch sarà dismesso il 31 marzo 2027. A
          partire da quella data il servizio non sarà più disponibile. Grazie
          per aver utilizzato geoharvester.ch e per il contributo e il feedback
          forniti durante questa fase sperimentale.
          <hr></hr>
          <h3>Français</h3>
          Le Proof of Concept geoharvester.ch sera mis hors service le 31 mars
          2027. À partir de cette date, le service ne sera plus disponible. Nous
          vous remercions d'avoir utilisé geoharvester.ch ainsi que pour votre
          contribution et les retours fournis durant cette phase expérimentale.
        </DialogContentText>
      </DialogContent>
      <DialogActions>
        <Button onClick={() => setPopupOpen(false)}>Ok</Button>
      </DialogActions>
    </Dialog>
  );
}
