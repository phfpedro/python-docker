from __future__ import annotations
from pathlib import Path
import os
import joblib
from google import genai
from google.genai import types

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "sample_data" / "modelo_cluster_cafeteria.joblib"

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "").strip()
if not GOOGLE_API_KEY:
    raise RuntimeError("Defina GOOGLE_API_KEY no arquivo .env para usar o exemplo google")

client = genai.Client(api_key=GOOGLE_API_KEY)

def list_cardapio():
    return ["Hamburguer", "Pizza", "Salada", "Sopa", "Sanduíche", "Frango Fritso"]

def recomendar(pergunta: str, model: object) -> str:
    _ = model

    # O modelo gemini-3-flash nao esta disponivel neste endpoint/v1beta.
    preferred = os.getenv("GOOGLE_MODEL", "").strip()
    model_candidates = [
        preferred,
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-1.5-flash",
    ]
    model_candidates = [m for m in model_candidates if m]

    last_error: Exception | None = None
    for model_name in model_candidates:
        try:
            resposta = client.models.generate_content(
                model=model_name, 
                contents=pergunta, 
                config=types.GenerateContentConfig(tools=[list_cardapio])
            )
            return resposta.text or "Sem resposta do modelo"
        except Exception as exc:
            last_error = exc
            continue

    raise RuntimeError(f"Falha ao gerar conteudo com os modelos: {', '.join(model_candidates)}") from last_error
    # _ = pergunta
    # _ = model
    # return "Uma recomendacao"


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


