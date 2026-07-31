# Avaliação de Modelos de Linguagem utilizando NoLiMa

## 1. Resumo

Este repositório contém a implementação utilizada para avaliar modelos de linguagem utilizando a metodologia **NoLiMa**.
O projeto avalia se estratégias baseadas em recuperação podem mitigar as limitações de recuperação de informações em
documentos extensos quando não há sobreposição lexical entre consultas e evidências.

Para isso, comparamos o RAG tradicional e uma implementação simplificada de AgenticRAG em 7.540 instâncias com contexto
de 8.000 tokens. O pipeline gera casos de teste estruturados a partir do conjunto de dados do NoLiMa, indexa os
documentos e executa a avaliação dos modelos sobre os cenários gerados.

Os resultados demonstram que ambas as abordagens superam a estratégia de contexto completo original do NoLiMa. O RAG
tradicional alcançou maior acurácia em relação ao AgenticRAG (44,91% contra 34,12%), indicando que a recuperação
explícita reduz falhas semânticas em contextos longos, enquanto as estratégias agentivas dependem das características da
tarefa e do processo de busca utilizado.

## 2. Resultados

Ao final da execução do experimento, são produzidos os seguintes artefatos:

- Casos de teste gerados a partir do dataset NoLiMa;
- Índices utilizados pelo mecanismo de recuperação;
- Resultados das avaliações dos modelos;
- Métricas e arquivos utilizados para análise dos experimentos.

______________________________________________________________________

## 3. Estrutura do Repositório

```text
.
├── data/                     # Scripts para download dos dados
├── resources/                # (Gerado na execução) Diretório com os casos de teste
│   └── data/
│       ├── haystack/
│       └── needlesets/
├── src/
│   ├── NoLiMa/               # Geração dos casos de teste
│   ├── experiments/          # Pipelines e execução de testes
│   ├── metrics/              # Análise estatística e de métricas
│   └── shared/               # Módulos, schemas e utilitários compartilhados
├── Makefile
└── README.md
```

## 4. Ambiente Experimental

O experimento foi executado na seguinte configuração:

| Recurso | Configuração |
| -- | -- |
| Processador | 8 núcleos / 16 threads |
| Memória RAM | 64 GB |
| GPU | NVIDIA GeForce RTX 3060 Ti (8 GB VRAM) |

Nessa configuração, a execução completa do experimento levou aproximadamente **14 horas**.

______________________________________________________________________

## 5. Base de Dados

Os dados utilizados neste projeto foram obtidos do repositório oficial do **NoLiMa**.

Repositório oficial:

https://github.com/adobe-research/NoLiMa

## 6. Reprodução do Experimento

### 1. Instalação das dependências

Na raiz do projeto, execute:

```bash
make init
```

______________________________________________________________________

### 2. Download do dataset

Execute:

```bash
./data/download_NoLiMa_data.sh
```

Caso ocorra erro de permissão:

```bash
chmod +x ./data/download_NoLiMa_data.sh
./data/download_NoLiMa_data.sh
```

Após o download, organize os arquivos conforme abaixo:

```text
resources/
└── data/
    ├── haystack/
    └── needlesets/
```

______________________________________________________________________

### 3. Geração dos casos de teste

```bash
make nolima-tests
```

______________________________________________________________________

### 4. Indexação

```bash
make index
```

______________________________________________________________________

### 5. Avaliação dos modelos

```bash
make eval
```

______________________________________________________________________

## Créditos

Este projeto utiliza os dados e adapta a metodologia proposta por:

**Modarressi et al.**

Repositório original:

https://github.com/adobe-research/NoLiMa
