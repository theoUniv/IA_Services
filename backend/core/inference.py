"""Module d'inférence pour la classification d'images de tennis."""

from __future__ import annotations

import io
from pathlib import Path
from typing import TypedDict

import numpy as np
from PIL import Image, UnidentifiedImageError
import tensorflow as tf

CHEMIN_MODELE: Path = Path(__file__).resolve().parent.parent / "models" / "modele_tennis_vision.keras"
TAILLE_IMAGE: tuple[int, int] = (224, 224)
LABELS_CLASSES: list[str] = ["backhand", "forehand", "ready_position", "serve"]


class ResultatPrediction(TypedDict):
    classe: str
    confiance: float


class PredicteurTennis:
    """Classe singleton qui gère le chargement du modèle et les prédictions."""

    _instance: PredicteurTennis | None = None
    _modele: tf.keras.Model | None = None

    def __new__(cls) -> PredicteurTennis:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def charger_modele(self, chemin: Path | str | None = None) -> None:
        """Charge le modèle Keras depuis le disque (une seule fois)."""
        if self._modele is not None:
            return

        chemin = Path(chemin) if chemin else CHEMIN_MODELE

        if not chemin.exists():
            raise FileNotFoundError(
                f"Le fichier du modèle est introuvable : {chemin}"
            )

        try:
            import keras
            original_init = keras.layers.Dense.__init__
            def new_init(self, *args, **kwargs):
                kwargs.pop("quantization_config", None)
                original_init(self, *args, **kwargs)
            keras.layers.Dense.__init__ = new_init

            self._modele = tf.keras.models.load_model(str(chemin))
        except Exception as exc:
            raise RuntimeError(
                f"Impossible de charger le modèle depuis {chemin}"
            ) from exc

    @staticmethod
    def _pretraiter_image(contenu: bytes) -> np.ndarray:
        """Convertit les octets bruts d'une image en tensor prêt pour l'inférence."""
        try:
            image = Image.open(io.BytesIO(contenu))
        except (UnidentifiedImageError, Exception) as exc:
            raise ValueError(
                "Le fichier fourni n'est pas une image valide."
            ) from exc

        image = image.convert("RGB").resize(TAILLE_IMAGE)

        tableau: np.ndarray = np.array(image, dtype=np.float32) / 255.0
        tableau = np.expand_dims(tableau, axis=0)

        return tableau

    def predire(self, contenu_image: bytes) -> ResultatPrediction:
        """Effectue une prédiction sur une image et renvoie la classe et la confiance."""
        if self._modele is None:
            raise RuntimeError(
                "Le modèle n'est pas chargé. Appelez charger_modele() d'abord."
            )

        image_preprocessed = self._pretraiter_image(contenu_image)
        predictions: np.ndarray = self._modele.predict(image_preprocessed, verbose=0)

        indice_classe: int = int(np.argmax(predictions[0]))
        confiance: float = float(predictions[0][indice_classe])

        return ResultatPrediction(
            classe=LABELS_CLASSES[indice_classe],
            confiance=round(confiance, 4),
        )


predicteur = PredicteurTennis()
