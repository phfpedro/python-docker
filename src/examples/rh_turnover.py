from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.metrics import ConfusionMatrixDisplay, accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier


def run(data_file: str | None = None) -> None:
    base_dir = Path(__file__).resolve().parent.parent
    dataset_path = base_dir / "sample_data" / "rh_turnover_200.csv"
    inputs_path = Path(data_file) if data_file else base_dir / "sample_data" / "rh_turnover_inputs.json"

    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset nao encontrado: {dataset_path}")
    if not inputs_path.exists():
        raise FileNotFoundError(f"Arquivo de entrada nao encontrado: {inputs_path}")

    with inputs_path.open("r", encoding="utf-8") as f:
        inputs = json.load(f)

    salary_map = inputs["salary_map"]
    novos_colaboradores_raw = inputs["novos_colaboradores"]

    df = pd.read_csv(dataset_path)
    print("Primeiras linhas:")
    print(df.head())

    print("\nValores faltantes:")
    print(df.isna().sum())

    df["salario"] = df["salario"].map(salary_map)
    df["sobrecarga"] = (df["horas_mes"] > 210).astype(int)
    df["sem_promocao"] = (df["promocoes"] == 0).astype(int)

    print("\nBase apos feature engineering:")
    print(df.head())

    feature_columns = ["tempo_empresa", "satisfacao", "horas_mes", "sobrecarga", "sem_promocao", "promocoes", "salario"]
    X = df[feature_columns]
    y = df["saiu"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    imputer = SimpleImputer(strategy="mean")
    X_train = imputer.fit_transform(X_train)
    X_test = imputer.transform(X_test)

    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    model = DecisionTreeClassifier(max_depth=3, random_state=42)
    model.fit(X_train, y_train)

    y_pred_train = model.predict(X_train)
    print("\n=== Avaliacao TRAIN ===")
    print("Acuracia:", accuracy_score(y_train, y_pred_train))

    print("\nMatriz de confusao:")
    print(confusion_matrix(y_train, y_pred_train))

    y_pred = model.predict(X_test)

    print("\n=== Avaliacao TEST ===")
    print("Acuracia:", accuracy_score(y_test, y_pred))

    print("\nMatriz de confusao:")
    cm = confusion_matrix(y_test, y_pred)
    print(cm)

    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=["Permaneceu", "Saiu"])
    disp.plot()
    plt.title("Matriz de Confusao")
    plt.show()

    print("\nRelatorio:")
    print(classification_report(y_test, y_pred))

    novos_colaboradores = pd.DataFrame(novos_colaboradores_raw)
    novos_colaboradores["sobrecarga"] = (novos_colaboradores["horas_mes"] > 210).astype(int)
    novos_colaboradores["sem_promocao"] = (novos_colaboradores["promocoes"] == 0).astype(int)
    novos_colaboradores["salario"] = novos_colaboradores["salario"].map(salary_map)

    novos_features = novos_colaboradores[feature_columns]
    novos_scaled = scaler.transform(novos_features)

    predicoes = model.predict(novos_scaled)
    probabilidades = model.predict_proba(novos_scaled)[:, 1]

    resultado = novos_colaboradores.copy()
    resultado["classe_prevista"] = pd.Series(predicoes).map({0: "Permaneceu", 1: "Saiu"})
    resultado["prob_saida"] = probabilidades

    print("\nPrevisao para novos colaboradores:")
    print(resultado)
