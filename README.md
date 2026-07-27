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
  - [Geração de Casos de Teste (NoLiMa)](#gera%C3%A7%C3%A3o-de-casos-de-teste-nolima)
  - [Indexação](#indexa%C3%A7%C3%A3o)
  - [Avaliação (RAG e AgenticRAG)](#avalia%C3%A7%C3%A3o-rag-e-agenticrag)
- [Fluxo de Desenvolvimento](#fluxo-de-desenvolvimento)
  - [Makefile](#makefile)
  - [Hooks de Pre-commit](#hooks-de-pre-commit)
- [Padrão de Commits](#padr%C3%A3o-de-commits)
  - [Formato da Mensagem](#formato-da-mensagem)
  - [Exemplos](#exemplos)
  - [Tipos Permitidos](#tipos-permitidos)
- [Documentação Complementar](#documenta%C3%A7%C3%A3o-complementar)

## Funcionalidades Principais

O principal objetivo deste repositório é conduzir experimentos comparando a eficácia da abordagem RAG tradicional com a
abordagem AgenticRAG na recuperação e geração de respostas em contextos longos sem correspondência lexical explícita. O
repositório oferece ferramentas para a geração de datasets de avaliação, indexação de documentos e execução de
avaliações com diferentes abordagens.

Os experimentos baseiam-se no benchmark NoLiMa (desenvolvido por Modarressi et al.). A base de dados utilizada provém do
[repositório original do NoLiMa](https://github.com/adobe-research/NoLiMa). Foram feitos apenas alguns ajustes na
geração para adaptação ao experimento e, para este estudo, **apenas os casos de teste com janela de contexto de 8k
tokens (8.000 tokens) foram executados**. A avaliação considerou 7.540 instâncias, utilizando o banco de dados vetorial
Qdrant com o modelo de embeddings `Qwen/Qwen3-Embedding-0.6B` e o modelo de linguagem `llama3.1:8b`.

## Visão Geral da Arquitetura

A arquitetura do experimento envolve as etapas de geração de dados base, indexação de contexto para recuperação, e
orquestração de chamadas aos modelos de linguagem tanto no fluxo tradicional quanto com agentes.

![Visão Geral da Arquitetura](caminho/para/imagem.png)

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

### Geração de Casos de Teste (NoLiMa)

Para gerar casos de teste a partir dos dados em `resources/data/haystack` e `resources/data/needlesets` (conforme o
NoLiMa original), execute:

```bash
make nolima-tests
```

### Indexação

Para realizar a indexação dos contextos dos casos de teste previamente gerados, utilize:

```bash
make index
```

### Avaliação (RAG e AgenticRAG)

Para gerar as avaliações com RAG e AgenticRAG pelos modelos configurados, execute:

```bash
make eval
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
