# Análise de Código Local com SonarQube

Esta ferramenta facilita a execução de análises de código com o SonarQube em seu ambiente local. O objetivo é permitir
que você, desenvolvedor(a), verifique a qualidade e a aderência aos padrões do código em suas alterações *antes* de
submetê-las para a revisão, usando a `origin/dev` como base de comparação.

O processo é automatizado através de um único comando, que cuida de iniciar o ambiente, executar a análise e limpar os
recursos ao final.

## Pré-requisitos

Antes de começar, garanta que você tenha as seguintes ferramentas instaladas e em execução:

- **Make**
- **Docker**

## Como Executar

Com sual branch atual pronto para análise, execute o seguinte comando na raiz do projeto:

```sh
make sonar
```

O comando irá executar o script `scripts/run_sonarqube.sh` com as configurações necessárias.

**O que o comando faz?**

1. Inicia contêineres Docker do SonarQube e SonarScanner.
2. Identifica os arquivos modificados em sua branch em comparação com a `origin/dev` (diff).
3. Executa a análise do SonarQube focada apenas nessas modificações.
4. Gera um relatório com o resultado.
5. Para e remove os contêineres do SonarQube e SonarScanner.

A primeira execução pode demorar um pouco mais para baixar a imagem do Docker. As execuções seguintes serão
consideravelmente mais rápidas.

## Resultado

Ao final da execução, um arquivo chamado `sonar-report.md` será criado (ou atualizado) na raiz do seu projeto. Ele
contém um resumo com os principais indicadores de qualidade do seu código, como *code smells*, *bugs* e
*vulnerabilities*.
