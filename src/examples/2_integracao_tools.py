from pathlib import Path
import os
import joblib
import pandas as pd
from google import genai
from google.genai import errors as genai_errors
from google.genai import types

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "sample_data" / "modelo_cluster_cafeteria.joblib"

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "").strip()
if not GOOGLE_API_KEY:
    raise RuntimeError("Defina GOOGLE_API_KEY no arquivo .env para usar o exemplo google")

GOOGLE_MODEL = os.getenv("GOOGLE_MODEL", "").strip()
if not GOOGLE_MODEL:
    raise RuntimeError("Defina GOOGLE_MODEL no arquivo .env para usar o exemplo google")

client = genai.Client(api_key=GOOGLE_API_KEY)


def montar_mensagem_quota_excedida() -> str:
    return (
        "A cota da API do Google foi excedida para o modelo configurado no momento. "
        "Tente novamente em alguns segundos ou verifique o limite e o faturamento da chave configurada."
    )

def inferir(
    apimentado: int,
    leve: int,
    veggie: int,
    calorias: float,
    freq: float,
    lactose: int
) -> dict:
    print("[TOOL] inferir: inicio")
    x = pd.DataFrame({
        "apimentado": [apimentado],
        "leve": [leve],
        "veggie": [veggie],
        "caloriasMediaDia": [calorias],
        "frequenciaPedidosMes": [freq],
        "IntoleranciaLactose": [lactose],
    })

    model = joblib.load(MODEL_PATH)
    scaler = model["scaler"]
    kmeans = model["kmeans"]
    recomendacoes = model["recomendacoes"]

    x_scaled = scaler.transform(x)
    cluster = kmeans.predict(x_scaled)[0]
    resultado = {
        "cluster": int(cluster),
        "recomendacao": recomendacoes(cluster),
    }
    print("[TOOL] inferir: fim")
    return resultado

def registra_pedido(item: str) -> dict:
    print("[TOOL] registra pedido: inicio")
    resultado = {
        "status": "ok",
        "mensagem": "pedido confirmado",
    }
    print("[TOOL] registrar pedido: fim")
    return resultado

def recomendar(pergunta: str, model: object) -> str:
    _ = model

    try:
        resposta = client.models.generate_content(
            model=GOOGLE_MODEL,
            contents=pergunta,
            config=types.GenerateContentConfig(
                system_instruction="Voce e um assistente de recomendacao de pedidos para uma cafeteria. Use as ferramentas disponiveis para responder as perguntas dos clientes da melhor forma possivel, não invente itens que não existe no cardápio. não fala nada alem de registrar pedidos ou dar recomendaçoes.",
                tools=[registra_pedido, inferir]
            )
        )
        return resposta.text or "Sem resposta do modelo"
    except genai_errors.ClientError as exc:
        if getattr(exc, "status_code", None) == 429:
            return montar_mensagem_quota_excedida()
        raise RuntimeError(f"Falha ao gerar conteudo com o modelo configurado: {GOOGLE_MODEL}") from exc
    except Exception as exc:
        raise RuntimeError(f"Falha ao gerar conteudo com o modelo configurado: {GOOGLE_MODEL}") from exc
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

        try:
            resposta = recomendar(pergunta, model)
            print(f"< {resposta}")
        except RuntimeError as exc:
            print(f"< {exc}")


