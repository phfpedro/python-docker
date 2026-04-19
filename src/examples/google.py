from __future__ import annotations

from pathlib import Path

import joblib
from google import genai
from google.genai import types

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "sample_data" / "modelo_cluster_cafeteria.joblib"


def recomendar(pergunta: str, model: object) -> str:
    _ = pergunta
    _ = model
    return "Uma recomendacao"


def run(data_file: str | None = None) -> None:
    _ = data_file

    if not MODEL_PATH.exists():
        print(f"Modelo nao encontrado: {MODEL_PATH}")
        return

    model = joblib.load(MODEL_PATH)
    print(f"Modelo carregado: {type(model).__name__}")

    while True:
        try:
            pergunta = input("> ")
        except EOFError:
            print("Entrada encerrada")
            break

        if pergunta.lower() == "sair":
            break

        resposta = recomendar(pergunta, model)
        print(f"< {resposta}")


