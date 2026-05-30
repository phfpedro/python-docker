# python-pos com Docker

Projeto pronto para rodar Python via Docker, sem precisar instalar Python localmente.

## Variaveis de ambiente

Para usar o exemplo `google`, configure a chave no arquivo `.env`:

```bash
GOOGLE_API_KEY=sua_chave_aqui
GOOGLE_MODEL=gemini-2.5-flash
```

O arquivo `.env` nao deve ser versionado. Use `.env.example` como referencia.

## Comandos curtos (recomendado)

Use os atalhos do Makefile:

```bash
make run
```

`make run` executa o runner generico em `src/main.py` dentro do container `python-pos`.

Outros atalhos uteis:

```bash
make file FILE=src/main.py
make code CODE="print('ok')"
make repl
make build
make examples
make example EXAMPLE="Machine Learning/1_integracao_modelo"
make example EXAMPLE="Machine Learning/1_integracao_modelo" DATA=src/sample_data/rh_turnover_inputs.json
make example EXAMPLE="Machine Learning/2_integracao_tools"
make example EXAMPLE="Big Data/1_processamento_em_lotes"
make notebook
make notebook NOTEBOOK_PORT=8889
```

## Como usar o Makefile

O `Makefile` existe para evitar decorar comandos grandes de `docker compose`.

Principais alvos:

```bash
make build
```

Faz o build da imagem Docker do projeto.

```bash
make run
```

Sobe o runner padrao definido no `docker-compose.yml`.

```bash
make examples
```

Lista os exemplos disponiveis via `src/main.py --list`.

```bash
make example EXAMPLE="Machine Learning/1_integracao_modelo"
```

Executa um exemplo especifico dentro do container.

```bash
make example EXAMPLE="Machine Learning/1_integracao_modelo" DATA=src/sample_data/rh_turnover_inputs.json
```

Executa um exemplo especifico passando um arquivo de entrada.

```bash
make example EXAMPLE="Machine Learning/2_integracao_tools"
```

Executa o exemplo interativo de tools.

```bash
make example EXAMPLE="Big Data/1_processamento_em_lotes"
```

Executa um exemplo basico de processamento em lotes usando `pandas` com leitura em chunks.

```bash
make repl
```

Abre um shell Python interativo dentro do container.

```bash
make notebook
```

Sobe o Jupyter Notebook no container, publica a porta `8888` para acesso no navegador e fixa a pasta `notebooks/` como raiz dos arquivos do Jupyter.

Se a porta `8888` ja estiver em uso:

```bash
make notebook NOTEBOOK_PORT=8889
```

```bash
make file FILE=src/main.py
```

Executa diretamente qualquer arquivo Python do projeto.

```bash
make code CODE="print('ok')"
```

Executa um trecho curto de Python sem criar arquivo.

```bash
make up
make down
make logs
```

`make up` sobe o servico com build, `make down` derruba os containers e `make logs` acompanha os logs do servico `python-pos`.

## Rodar exemplos com Docker

Nao use `python3 src/main.py ...` na maquina local. O fluxo esperado deste projeto eh rodar tudo no container, que ja vem com Python 3.12 e as dependencias instaladas.

Para listar os exemplos disponiveis:

```bash
docker compose run --rm python-pos python -u src/main.py --list
```

Para rodar o exemplo de integracao de modelo:

```bash
docker compose run --rm python-pos python -u src/main.py --example "Machine Learning/1_integracao_modelo"
```

Para rodar o mesmo exemplo passando arquivo de entrada:

```bash
docker compose run --rm python-pos python -u src/main.py --example "Machine Learning/1_integracao_modelo" --data-file src/sample_data/rh_turnover_inputs.json
```

Para abrir o exemplo de ferramentas interativas:

```bash
docker compose run --rm -it python-pos python -u src/main.py --example "Machine Learning/2_integracao_tools"
```

Para rodar o exemplo basico de Big Data:

```bash
docker compose run --rm python-pos python -u src/main.py --example "Big Data/1_processamento_em_lotes"
```

Para subir o Jupyter Notebook:

```bash
mkdir -p notebooks
JUPYTER_PORT=8888 docker compose run --rm --service-ports python-pos jupyter notebook --ip 0.0.0.0 --port 8888 --no-browser --allow-root --notebook-dir /app/notebooks
```

Depois acesse no navegador o endereco informado no terminal, normalmente `http://127.0.0.1:8888/tree`. Novos notebooks criados pela interface vao para a pasta `notebooks/` em vez da raiz do projeto.

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

Se preferir, use os atalhos equivalentes do `Makefile`:

```bash
make examples
make example EXAMPLE="Machine Learning/1_integracao_modelo"
make example EXAMPLE="Machine Learning/1_integracao_modelo" DATA=src/sample_data/rh_turnover_inputs.json
make example EXAMPLE="Big Data/1_processamento_em_lotes"
make notebook
```

## Dependencias Python

- Adicione pacotes no arquivo `requirements.txt`.
- Depois reconstrua:

```bash
docker compose build --no-cache
```

Depois de adicionar o `notebook`, faca esse rebuild antes de rodar `make notebook`.

## Estrutura

- `Dockerfile`: imagem Python 3.12
- `docker-compose.yml`: servico principal
- `notebooks/`: pasta padrao para notebooks gerados pelo Jupyter
- `src/main.py`: runner generico de exemplos
- `src/examples/Machine Learning/`: exemplos de machine learning
- `src/examples/Big Data/`: exemplos de processamento em lotes e analise de grandes volumes
- `src/sample_data/rh_turnover_inputs.json`: dados do exemplo de turnover
- `requirements.txt`: dependencias Python
