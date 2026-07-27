# NoLiMa

Este diretório contém os scripts responsáveis pela geração e validação dos casos de teste, baseados na metodologia
NoLiMa. Seu papel no experimento como um todo é gerar os casos de testes a partir dos dados localizados em
`resources/data/haystack` e `resources/data/needlesets`.

> **Nota sobre a Origem dos Dados:** Os dados utilizados foram extraídos do
> [repositório original do NoLiMa](https://github.com/adobe-research/NoLiMa) (desenvolvido por Modarressi et al.).

## Componentes Principais

- **`run_tests.py`**: Script principal para execução dos testes.
- **`async_evaluate.py`**: Script responsável por rodar as avaliações de forma assíncrona.
- **`async_api_connector.py`**: Gerencia a conexão com as APIs dos modelos de linguagem de maneira assíncrona.

## Como Executar

A execução pode ser feita diretamente através do script shell disponível no diretório:

```bash
./src/NoLiMa/run_tests.sh
```

Alternativamente, e de forma recomendada, você pode executar utilizando o comando definido no `Makefile` a partir da
raiz do projeto:

```bash
make nolima-tests
```
