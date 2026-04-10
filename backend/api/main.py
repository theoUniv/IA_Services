"""API FastAPI pour la prédiction de coups de tennis à partir d'images."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel, Field

from core.inference import predicteur
from core.llm import analyser_image_llm

logger = logging.getLogger("api.tennis")


class ReponsePrediction(BaseModel):
    """Schéma de la réponse JSON de prédiction."""

    classe: str = Field(
        ...,
        description="Classe prédite parmi : backhand, forehand, ready_position, serve.",
        examples=["serve"],
    )
    confiance: float = Field(
        ...,
        description="Score de confiance du modèle (entre 0 et 1).",
        ge=0.0,
        le=1.0,
        examples=[0.9732],
    )


class ReponseErreur(BaseModel):
    """Schéma pour les réponses d'erreur."""

    detail: str = Field(..., description="Message d'erreur détaillé.")


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Charge le modèle au démarrage et libère les ressources à l'arrêt."""
    logger.info("Chargement du modèle de classification tennis...")
    try:
        predicteur.charger_modele()
        logger.info("Modèle chargé avec succès.")
    except (FileNotFoundError, RuntimeError) as exc:
        logger.error("Échec du chargement du modèle : %s", exc)
        raise
    yield
    logger.info("Arrêt de l'application.")


app = FastAPI(
    title="Tennis Vision API",
    description=(
        "API de classification d'images de tennis. "
        "Prédit le type de coup (backhand, forehand, ready_position, serve) "
        "à partir d'une image uploadée."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TYPES_MIME_AUTORISES: set[str] = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/bmp",
    "image/tiff",
}


@app.post(
    "/predict/vision",
    response_model=ReponsePrediction,
    summary="Prédire le type de coup de tennis",
    description=(
        "Accepte une image (JPEG, PNG, WebP, BMP, TIFF) et retourne "
        "la classe prédite ainsi que le score de confiance."
    ),
    responses={
        400: {"model": ReponseErreur, "description": "Fichier invalide ou non lisible."},
        422: {"model": ReponseErreur, "description": "Paramètre manquant."},
        500: {"model": ReponseErreur, "description": "Erreur interne du serveur."},
    },
)
async def predire_vision(
    fichier: UploadFile = File(
        ...,
        description="Image du joueur de tennis à analyser (JPEG, PNG…).",
    ),
) -> ReponsePrediction:
    """Reçoit une image, la passe au modèle et retourne la prédiction."""
    if fichier.content_type not in TYPES_MIME_AUTORISES:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Type de fichier non supporté : {fichier.content_type}. "
                f"Types acceptés : {', '.join(sorted(TYPES_MIME_AUTORISES))}."
            ),
        )

    try:
        contenu: bytes = await fichier.read()
    except Exception as exc:
        logger.error("Erreur lors de la lecture du fichier : %s", exc)
        raise HTTPException(
            status_code=400,
            detail="Impossible de lire le fichier uploadé.",
        ) from exc
    finally:
        await fichier.close()

    if not contenu:
        raise HTTPException(
            status_code=400,
            detail="Le fichier uploadé est vide.",
        )

    try:
        resultat = predicteur.predire(contenu)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc
    except RuntimeError as exc:
        logger.error("Erreur d'inférence : %s", exc)
        raise HTTPException(
            status_code=500,
            detail="Erreur interne lors de la prédiction.",
        ) from exc

    return ReponsePrediction(
        classe=resultat["classe"],
        confiance=resultat["confiance"],
    )

@app.post("/predict/llm", response_model=ReponsePrediction)
async def predire_vision_llm(fichier: UploadFile = File(...)) -> ReponsePrediction:
    if fichier.content_type not in TYPES_MIME_AUTORISES:
        raise HTTPException(status_code=400, detail="Type de fichier non supporté.")
    try:
        contenu: bytes = await fichier.read()
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Impossible de lire le fichier uploadé.") from exc
    finally:
        await fichier.close()
    if not contenu:
        raise HTTPException(status_code=400, detail="Le fichier uploadé est vide.")
    try:
        resultat = await analyser_image_llm(contenu)
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Erreur interne lors de la prédiction LLM.") from exc
    return ReponsePrediction(classe=resultat["classe"], confiance=resultat["confiance"])

@app.get(
    "/health",
    summary="Vérification de l'état du service",
    description="Retourne l'état de santé de l'API.",
)
async def health_check() -> dict[str, str]:
    """Retourne un statut OK si le serveur est opérationnel."""
    return {"status": "ok"}
