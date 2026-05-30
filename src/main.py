import argparse
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from typing import Callable, Optional


ExampleRunner = Callable[[Optional[str]], None]
ExampleFileMap = dict[str, Path]
EXAMPLES_DIR = Path(__file__).resolve().parent / "examples"


def gerar_nome_exemplo(example_file: Path) -> str:
    """Converte o caminho do arquivo em um identificador amigável para a CLI."""
    return example_file.relative_to(EXAMPLES_DIR).with_suffix("").as_posix()


def gerar_nome_modulo(example_file: Path) -> str:
    """Cria um nome de módulo seguro para importar um arquivo de exemplo por caminho."""
    raw_name = gerar_nome_exemplo(example_file)
    normalized = "".join(char if char.isalnum() else "_" for char in raw_name)
    return f"examples_{normalized}"

def carregar_runner(example_file: Path) -> ExampleRunner:
    """Importa dinamicamente um arquivo de exemplo e devolve sua função run."""
    module_name = gerar_nome_modulo(example_file)
    spec = spec_from_file_location(module_name, example_file)
    if spec is None or spec.loader is None:
        raise ImportError(f"Nao foi possivel carregar o exemplo: {example_file}")

    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    runner = getattr(module, "run", None)
    if not callable(runner):
        raise AttributeError(f"O exemplo '{example_file}' nao possui uma funcao run() valida")

    return runner


def descobrir_examples() -> ExampleFileMap:
    """Varre a pasta de exemplos recursivamente e monta um mapa nome -> arquivo."""
    examples: ExampleFileMap = {}

    for example_file in sorted(EXAMPLES_DIR.rglob("*.py")):
        relative_parts = example_file.relative_to(EXAMPLES_DIR).parts
        if example_file.name == "__init__.py":
            continue
        if any(part.startswith("_") for part in relative_parts):
            continue

        examples[gerar_nome_exemplo(example_file)] = example_file

    return dict(sorted(examples.items()))


EXAMPLES = descobrir_examples()
DEFAULT_EXAMPLE = next(iter(EXAMPLES), None)


def parse_args() -> argparse.Namespace:
    """Define e interpreta os argumentos de linha de comando do runner."""
    parser = argparse.ArgumentParser(description="Runner de exemplos Python no container")
    parser.add_argument("--example", default=DEFAULT_EXAMPLE, help="Nome do exemplo para executar, ex.: 'Machine Learning/1_integracao_modelo'")
    parser.add_argument("--data-file", default=None, help="Arquivo de dados/config do exemplo")
    parser.add_argument("--list", action="store_true", help="Lista exemplos disponiveis")
    return parser.parse_args()


# Exemplo prático de uso:
# docker compose run --rm python-pos python -u src/main.py --example "Machine Learning/1_integracao_modelo" --data-file src/sample_data/rh_turnover_inputs.json
def main() -> None:
    """Coordena o fluxo principal: lista exemplos ou executa o exemplo escolhido."""
    args = parse_args()

    if not EXAMPLES:
        raise SystemExit("Nenhum exemplo com funcao run() foi encontrado em src/examples")

    if args.list:
        print("Exemplos disponiveis:")
        for name in sorted(EXAMPLES):
            print(f"- {name}")
        return

    example_file = EXAMPLES.get(args.example)
    if example_file is None:
        valid = ", ".join(sorted(EXAMPLES))
        raise SystemExit(f"Exemplo '{args.example}' nao encontrado. Opcoes: {valid}")

    runner = carregar_runner(example_file)
    runner(args.data_file)


if __name__ == "__main__":
    main()
