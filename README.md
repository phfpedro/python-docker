# python-pos com Docker

Projeto pronto para rodar Python via Docker, sem precisar instalar Python localmente.

## Comandos curtos (recomendado)

Use os atalhos do Makefile:

```bash
make run
```

`make run` executa o runner generico em `src/main.py` (padrao: exemplo `rh_turnover`).

Outros atalhos uteis:

```bash
make file FILE=src/main.py
make code CODE="print('ok')"
make repl
make build
make examples
make example EXAMPLE=rh_turnover
make example EXAMPLE=rh_turnover DATA=src/sample_data/rh_turnover_inputs.json
make example EXAMPLE=google
```

## Subir e executar

```bash
docker compose up --build
```

Isso executa o arquivo padrao: `src/main.py`.

## Rodar outro arquivo Python

```bash
PYTHON_FILE=src/outro_script.py docker compose up --build
```

## Executar comandos Python avulsos

```bash
docker compose run --rm python-pos python -u src/main.py
docker compose run --rm python-pos python -u -c "print('ok')"
```

## Dependencias Python

- Adicione pacotes no arquivo `requirements.txt`.
- Depois reconstrua:

```bash
docker compose build --no-cache
```

## Estrutura

- `Dockerfile`: imagem Python 3.12
- `docker-compose.yml`: servico principal
- `src/main.py`: runner generico de exemplos
- `src/examples/`: exemplos executaveis
- `src/sample_data/rh_turnover_inputs.json`: dados do exemplo de turnover
- `requirements.txt`: dependencias Python
