# Documentação do Projeto

Este diretório contém a documentação técnica, operacional e as diretrizes de desenvolvimento do projeto.

## Índice

### Arquitetura e Decisões

- [Architecture Decision Records (ADRs)](./adr/README.md) - Histórico de decisões arquiteturais importantes, como a
  estratégia de tabela única e a adoção do Dagster.

### Desenvolvimento e Padrões

- [Diretrizes de Codificação](./guidelines.md) - Guia de estilo, convenções de nomenclatura, tipagem, design de API e
  fluxo de Git (Branchs/Commits).

### Ferramentas e Qualidade

- [SonarQube](./sonar.md) - Instruções para executar a análise de qualidade de código e *security hotspots* localmente.
- [SecScan](./secscan.md) - Ferramenta CLI para varredura de vulnerabilidades em dependências (SCA).
- [Linter de Markdown](./markdown-linter.md) - Padrões de formatação para a documentação e integração com pre-commit.
