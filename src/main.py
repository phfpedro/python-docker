from __future__ import annotations

import argparse
from typing import Callable

from examples.google import run as run_google
from examples.rh_turnover import run as run_rh_turnover

ExampleRunner = Callable[[str | None], None]

EXAMPLES: dict[str, ExampleRunner] = {
    "google": run_google,
    "rh_turnover": run_rh_turnover,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Runner de exemplos Python no container")
    parser.add_argument("--example", default="rh_turnover", help="Nome do exemplo para executar")
    parser.add_argument("--data-file", default=None, help="Arquivo de dados/config do exemplo")
    parser.add_argument("--list", action="store_true", help="Lista exemplos disponiveis")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.list:
        print("Exemplos disponiveis:")
        for name in sorted(EXAMPLES):
            print(f"- {name}")
        return

    runner = EXAMPLES.get(args.example)
    if runner is None:
        valid = ", ".join(sorted(EXAMPLES))
        raise SystemExit(f"Exemplo '{args.example}' nao encontrado. Opcoes: {valid}")

    runner(args.data_file)


if __name__ == "__main__":
    main()
