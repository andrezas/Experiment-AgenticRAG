# SecScan

Este documento descreve como utilizar o **SecScan** como ferramenta de linha de comando para análise de segurança e
detecção de vulnerabilidades de dependências em projetos de software.

## Tabela de Conteúdos

- [Visão Geral](#vis%C3%A3o-geral)
- [Como Funciona](#como-funciona)
- [Requisitos](#requisitos)
- [Uso](#uso)
  - [Instalação](#instala%C3%A7%C3%A3o)
  - [Execução Básica](#execu%C3%A7%C3%A3o-b%C3%A1sica)
  - [Formatando a Saída](#formatando-a-sa%C3%ADda)
  - [Opções Avançadas](#op%C3%A7%C3%B5es-avan%C3%A7adas)
- [O que o Output Fornece](#o-que-o-output-fornece)
- [Pontos Fortes](#pontos-fortes)

## Visão Geral

O **SecScan** é uma ferramenta de linha de comando que realiza a varredura de dependências de um projeto, identificando
vulnerabilidades conhecidas em bibliotecas utilizadas.\
Ele integra-se à [API OSV.dev](https://osv.dev) para consulta de falhas de segurança e pode ser facilmente adicionado em
pipelines de **CI/CD**.

## Como Funciona

O funcionamento do SecScan segue as seguintes etapas:

1. **Detecção de idioma**\
   Examina o diretório do projeto em busca de arquivos de manifesto (ex.: `package.json`, `requirements.txt`, `pom.xml`)
   para determinar o ecossistema.

2. **Análise de dependência**\
   Extrai todas as dependências diretas e indiretas a partir do manifesto identificado.

3. **Verificação de vulnerabilidade**\
   Cada dependência é consultada na [API OSV.dev](https://osv.dev) para identificar vulnerabilidades conhecidas.

4. **Filtragem**\
   Os resultados podem ser filtrados por:

   - Severidade
   - Pontuação **CVSS**
   - Disponibilidade de **exploit**
   - Existência de **correção** (patch disponível)

5. **Verificação de políticas**\
   Os achados são comparados com políticas e limites definidos pelo usuário, permitindo automação em **pipelines
   CI/CD**.

6. **Formatação de resultados**\
   Os resultados podem ser exibidos em diferentes formatos (`table`, `json`, `yaml`), incluindo **comandos de correção**
   recomendados.

## Requisitos

- **Python 3.7+**
- Biblioteca **requests**
- Biblioteca **pyyaml** (para arquivos de configuração)
- Conexão com a **Internet** (necessária para consultas ao OSV.dev)

## Uso

### Instalação

- Via **pip** (recomendado):

  ```bash
  uv add secscan-cli
  ```

- Via repositório GitHub:

  ```bash
  git clone https://github.com/deosha/secscan.git
  cd secscan
  uv pip install -e .
  ```

### Execução Básica

- Se já estiver no diretório do projeto que deseja analisar:

  ```bash
  uv run -- secscan
  ```

- Se estiver em outro diretório, basta passar o caminho:

  ```bash
  uv run -- secscan /path/to/project
  ```

### Formatando a Saída

O `secscan` suporta diferentes formatos de output, como `table`, `json` e `yaml`.\
Exemplo em **JSON**:

```bash
uv run -- secscan -f json
```

### Opções Avançadas

O `secscan` oferece parâmetros configuráveis (filtros de severidade, CVSS, exploits, correções etc.).\
Consulte todas as opções em: [Command-line options](https://pypi.org/project/secscan-cli/)

## O que o Output Fornece

Para **cada vulnerabilidade** encontrada:

- **ID** (ex.: `GHSA-xxxx`, `PYSEC-xxxx`)
- **Severidade** (Baixa, Média, Alta, Crítica)
- **Resumo da falha** com descrição explicativa
- **Versões corrigidas** disponíveis

Para **cada dependência vulnerável**:

- **Nome da biblioteca + versão instalada**
- **Comando recomendado de correção** (ex.: `pip install package==fixed_version`)

## Pontos Fortes

- **Análise detalhada**: inclui resumos explicativos para facilitar a compreensão do impacto
- **Correção facilitada**: fornece comandos prontos para corrigir pacotes vulneráveis
- **Classificação consistente**: severidade padronizada com base em critérios reconhecidos (CVSS, OSV.dev)
- **Saída estruturada**: JSON bem organizado, ideal para automação e integração em pipelines de CI/CD
