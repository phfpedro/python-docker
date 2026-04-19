from __future__ import annotations

import argparse
from importlib import import_module
from pathlib import Path
from pkgutil import iter_modules
from typing import Callable


ExampleRunner = Callable[[str | None], None]
EXAMPLES_DIR = Path(__file__).resolve().parent / "examples"


def carregar_runner(module_name: str) -> ExampleRunner:
    module = import_module(f"examples.{module_name}")
    return module.run


def descobrir_examples() -> dict[str, ExampleRunner]:
    examples: dict[str, ExampleRunner] = {}

    for module_info in iter_modules([str(EXAMPLES_DIR)]):
        module_name = module_info.name
        if module_name.startswith("_"):
            continue

        module = import_module(f"examples.{module_name}")
        runner = getattr(module, "run", None)
        if callable(runner):
            examples[module_name] = runner

    return dict(sorted(examples.items()))


EXAMPLES = descobrir_examples()
DEFAULT_EXAMPLE = next(iter(EXAMPLES), None)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Runner de exemplos Python no container")
    parser.add_argument("--example", default=DEFAULT_EXAMPLE, help="Nome do exemplo para executar")
    parser.add_argument("--data-file", default=None, help="Arquivo de dados/config do exemplo")
    parser.add_argument("--list", action="store_true", help="Lista exemplos disponiveis")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if not EXAMPLES:
        raise SystemExit("Nenhum exemplo com funcao run() foi encontrado em src/examples")

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
