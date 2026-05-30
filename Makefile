.PHONY: build run file repl code up down logs examples example notebook

NOTEBOOK_PORT ?= 8888

build:
	docker compose build

run:
	docker compose run --rm python-pos

examples:
	docker compose run --rm python-pos python -u src/main.py --list

example:
	docker compose run --rm python-pos python -u src/main.py --example "$(EXAMPLE)" $(if $(DATA),--data-file "$(DATA)",)

file:
	docker compose run --rm python-pos python -u $(FILE)

repl:
	docker compose run --rm python-pos python

notebook:
	mkdir -p notebooks
	JUPYTER_PORT=$(NOTEBOOK_PORT) docker compose run --rm --service-ports python-pos jupyter notebook --ip 0.0.0.0 --port 8888 --no-browser --allow-root --notebook-dir /app/notebooks

code:
	docker compose run --rm python-pos python -u -c "$(CODE)"

up:
	docker compose up --build

down:
	docker compose down

logs:
	docker compose logs -f python-pos
