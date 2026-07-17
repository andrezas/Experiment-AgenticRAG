PROJECT_NAME:=agent-rag

ifeq ($(env),dev)
  COMPOSE_FILE = docker-compose.dev.yml
  ENV_FILE = .env
else ifeq ($(env),prod)
  COMPOSE_FILE = docker-compose.prod.yml
  ENV_FILE = .env.prod
else ifeq ($(env),test)
  COMPOSE_FILE = docker-compose.test.yml
  ENV_FILE = .env.test
else
  COMPOSE_FILE = docker-compose.dev.yml
  ENV_FILE = .env
endif

COMPOSE_CMD = docker compose -f $(COMPOSE_FILE) --env-file $(ENV_FILE)
MAKEFILE_DIR:=$(dir $(abspath $(lastword $(MAKEFILE_LIST))))

######### Comandos de Teste e Setup #########
.PHONY: test install
test: ## Roda a suíte de testes completa
	uv run -- pytest

######### Comandos auxiliares #########
.PHONY: help
help: ## Mostrar make targets e args
	@echo "Targets:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {sub("\\\\n",sprintf("\n%22c"," "), $$2);printf " \033[36m%-20s\033[0m  %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo "\nArgs:"
	@printf "  \033[36m%-18s\033[0m  %s\n" "env" "$(env) (default: dev). Para comandos relacionados ao docker compose, \
	passe com 'make compose-up env=prod' para usar docker-compose.prod.yml. Por padrão é utilizado docker-compose.dev.yml"

clean: clean-build clean-pyc clean-test

clean-build: ## Remove artefatos de build
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## Remove artefatos de arquivos Python
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## Remove artefatos de testes e cobertura
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache

######### Comandos para Docker Compose #########
.PHONY: up down down-volumes update prune restart logs build

up: ## Inicia os containers com Docker Compose
	$(COMPOSE_CMD) up -d

down: ## Para os containers com Docker Compose
	$(COMPOSE_CMD) down

down-volumes: ## Remove volumes junto com os containers com Docker Compose
	$(COMPOSE_CMD) down --volumes

update: ## Atualiza imagens utilizadas nos serviços com Docker Compose
	$(COMPOSE_CMD) pull && $(COMPOSE_CMD) up -d

docker-prune: ## Remove containers, volumes e imagens não utilizadas do docker
	docker system prune -a --volumes -f

restart: ## Reinicia todos os serviços com Docker Compose
	$(COMPOSE_CMD) down && $(COMPOSE_CMD) up -d

logs: ## Mostra os logs em tempo real com Docker Compose
	$(COMPOSE_CMD) logs -f

build: ## Build utilizando Docker Compose
	$(COMPOSE_CMD) build

######### Comandos para setup #########
.PHONY: init
init: ## Inicializa o projeto, instalando dependencias necessárias
	./scripts/init.sh

######### Comandos para qualidade de codigo #########
.PHONY: format lint sonar ty
format: ## Roda formatter do UV
	uv run ruff format

lint: ## Roda linter do UV
	uv run ruff check src/ --fix

format-md: ## Formata arquivos Markdown
	uv run mdformat . --exclude .venv --exclude .pytest_cache

sonar: ## Roda sonarqube na branch atual em relação a dev
	./scripts/run_sonarqube.sh $(MAKEFILE_DIR)

ty: ## Roda verificação de tipagem
	uv run ty check

.PHONY: index

index:
	@echo "A iniciar a indexação do haystack NOLIMA no Qdrant..."
	uv run python -m src.experiments.index_nolima

eval:
	@echo "A iniciar a indexação do haystack NOLIMA no Qdrant..."
	uv run python -m src.experiments.nolima_eval

plot:
	@echo "A iniciar a plots do haystack NOLIMA..."
	uv run python -m src.metrics.statistical_analysis.py