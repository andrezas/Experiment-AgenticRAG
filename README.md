# agent-rag

A concise description of the project.

## Tabela de Conteúdos

- [Funcionalidades Principais](#funcionalidades-principais)
- [Visão Geral da Arquitetura](#vis%C3%A3o-geral-da-arquitetura)
- [Guia de Inicialização](#guia-de-inicializa%C3%A7%C3%A3o)
  - [Pré-requisitos](#pr%C3%A9-requisitos)
  - [1. Instalação](#1-instala%C3%A7%C3%A3o)
  - [2. Configuração de Ambiente](#2-configura%C3%A7%C3%A3o-de-ambiente)
- [Execução da Aplicação](#execu%C3%A7%C3%A3o-da-aplica%C3%A7%C3%A3o)
  - [Ambiente de Desenvolvimento](#ambiente-de-desenvolvimento)
  - [Ambiente de Produção Simulado](#ambiente-de-produ%C3%A7%C3%A3o-simulado)
  - [1. Gerar os builds](#1-gerar-os-builds)
  - [2. Subir os contêineres](#2-subir-os-cont%C3%AAineres)
- [Fluxo de Desenvolvimento](#fluxo-de-desenvolvimento)
  - [Makefile](#makefile)
  - [Hooks de Pre-commit](#hooks-de-pre-commit)
- [Padrão de Commits](#padr%C3%A3o-de-commits)
  - [Formato da Mensagem](#formato-da-mensagem)
  - [Exemplos](#exemplos)
  - [Tipos Permitidos](#tipos-permitidos)
- [Documentação Complementar](#documenta%C3%A7%C3%A3o-complementar)

## Funcionalidades Principais

TODO

## Visão Geral da Arquitetura

TODO

## Guia de Inicialização

### Pré-requisitos

- [Docker](https://www.docker.com/)
- [Docker Compose v2](https://docs.docker.com/compose/)
- [uv](https://docs.astral.sh/uv/getting-started/installation/)

### 1. Instalação

```bash
git clone <repositorio>
cd <repositorio>
make init
```

### 2. Configuração de Ambiente

TODO

## Execução da Aplicação

### Ambiente de Desenvolvimento

1. **Subir os contêineres do Docker** Execute o seguinte comando para iniciar os serviços configurados no
   `docker-compose.dev.yml`:

   ```bash
   make up
   ```

   > Isso equivale a: `docker compose -f docker-compose.dev.yml --env-file .env up -d`

### Ambiente de Produção Simulado

Para rodar o projeto como se tivesse em um ambiente de produção, utilize os seguintes comandos com `env=prod`. Os
seguintes arquivos serão utilizados:

- `.env.production`
- `docker-compose.prod.yml`

### 1. Gerar os builds

Execute o build completo dos serviços:

```bash
make build env=prod
```

### 2. Subir os contêineres

Inicie os serviços com configuração de produção:

```bash
make up env=prod
```

## Fluxo de Desenvolvimento

### Makefile

Não é obrigatório as aplicações serem executadas pelos targets definidos no `Makefile`, sendo possível utilizar
diretamente os comandos nas referentes aplicações, e, obtendo o mesmo resultado. Para verificar os comandos disponiveis,
basta fazer `make help` na pasta raiz.

### Hooks de Pre-commit

O projeto utiliza `pre-commit` com validações do `ruff` e conformidade de **Conventional Commits**.

```bash
pre-commit install
```

## Padrão de Commits

Este projeto segue o padrão [Conventional Commits](https://www.conventionalcommits.org/pt-br/v1.0.0/), o que permite uma
melhor organização do histórico de alterações e possibilita automações como geração de changelogs.

### Formato da Mensagem

tipo(escopo opcional): descrição breve

### Exemplos

- feat(api): adiciona endpoint de login
- fix(ui): corrige bug de alinhamento no botão
- docs: atualiza instruções de instalação
- refactor(core): melhora performance do parser

### Tipos Permitidos

- `feat`: nova funcionalidade
- `fix`: correção de bug
- `docs`: mudanças na documentação
- `style`: formatação (sem alteração de código)
- `refactor`: refatorações que não alteram o comportamento
- `test`: adição ou modificação de testes
- `chore`: tarefas de manutenção (build, configs, etc)

Commits fora desse padrão serão rejeitados automaticamente pelo hook de pré-commit.

Para aplicar os hooks corretamente, é necessário que o pre-commit esteja corretamente configurado.

## Documentação Complementar

Para informações detalhadas sobre a arquitetura, utilização da API e diretrizes de contribuição, consulte os documentos
disponíveis no diretório **`/docs`**.
