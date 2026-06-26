# Diretrizes de Codificação

O objetivo destas diretrizes é promover consistência, legibilidade e manutenibilidade em toda a nossa base de código.
Seguir estes padrões torna mais fácil para todos entender, revisar e contribuir para o projeto, independentemente de
quem escreveu o código original.

Embora estas diretrizes sejam importantes, elas não são leis rígidas. Use o seu bom senso e sinta-se à vontade para
propor melhorias abrindo uma issue ou um pull request.

## Tabela de Conteúdos

- [Princípios Gerais](#princ%C3%ADpios-gerais)
- [Configuração de Ferramentas](#configura%C3%A7%C3%A3o-de-ferramentas)
- [Formatação](#formata%C3%A7%C3%A3o)
- [Convenções de Nomenclatura](#conven%C3%A7%C3%B5es-de-nomenclatura)
- [Comentários e Tipagem](#coment%C3%A1rios-e-tipagem) - [Antipadrões a Evitar](#antipadr%C3%B5es-a-evitar)
- [Controle de Versão](#controle-de-vers%C3%A3o)

## Princípios Gerais

- **DRY**: Evite duplicar código. Abstraia e reutilize a lógica comum em funções, classes ou módulos.

- **KISS**: Escreva o código mais simples que resolva o problema. Evite complexidade desnecessária e engenharia
  excessiva.

- **Princípio da Responsabilidade Única**: Cada função, classe ou módulo deve ter um propósito específico.

- **Legibilidade > Conciso**: O código é lido com muito mais frequência do que é escrito. Priorize um código claro e
  legível em vez de soluções inteligentes de uma linha.

## Configuração de Ferramentas

Nosso projeto utiliza um conjunto padronizado de ferramentas para garantir a qualidade e a consistência do código.

- **Gerenciador de Pacotes**: Usamos uv para um gerenciamento de dependências rápido e confiável.

- **Linter e Formatador**: O Ruff é usado tanto para linting quanto para formatação. Ele está configurado em nosso
  arquivo `pyproject.toml`.

- **Hooks de Pre-commit**: Usamos pre-commit para executar verificações automaticamente antes de cada commit.

## Formatação

Nossa configuração de pre-commit formatará automaticamente seu código usando o Ruff. Você também pode executá-lo
manualmente com `uv run ruff format`.

## Convenções de Nomenclatura

A consistência na nomenclatura é crucial. Seguimos majoritariamente guia de estilo
[PEP 8](https://peps.python.org/pep-0008/).

- **Variáveis e Funções**: Use *snake_case*.

  - Exemplo: `user_profile`, `def calculate_total():`

- **Classes e Exceções**: Use *PascalCase*.

  - Exemplo: `class UserSession:`, `class AppConfig:`

- **Constantes**: Use *UPPER_SNAKE_CASE*.

  - Exemplo: `MAX_CONNECTIONS = 10`

- **Enums**: Use `StrEnum`, que esta disponível a partir do Python 3.11, para criar enumerações. Isso garante que os
  membros sejam strings, o que é útil para serialização (ex: JSON) e depuração. Membros de Enum devem usar
  *UPPER_SNAKE_CASE*.

  - Exemplo:

    ```python
    from enum import StrEnum

    class UserStatus(StrEnum):
        ACTIVE = "ACTIVE"
        INACTIVE = "INACTIVE"
        PENDING = "PENDING"
    ```

- **Módulos e Pacotes**: Use *snake_case*. Arquivos individuais no singular e pacotes/módulos no plural.

  - Exemplo: `user_profile.py`, `api_helpers/`

- **Booleanos**: Prefixe variáveis booleanas com `is_`, `has_`, ou `should_`.

  - Exemplo: `is_logged_in = False`, `has_permission = True`

## Comentários e Tipagem

- **Idioma**: Todos os comentários internos do código devem ser escritos em Inglês.

- **Docstrings**: Use docstrings para todos os módulos, funções, classes e métodos públicos. Siga as convenções do
  [PEP 257](https://peps.python.org/pep-0257/)

  ```python
  """
  A brief summary of the module's purpose.
  """

  def get_user_by_id(user_id: int) -> dict | None:
      """
      Retrieves a user's profile from the database.

      Args:
          user_id: The unique identifier for the user.

      Returns:
          A dictionary containing the user's data, or None if not found.
      """
      # ... implementação
  ```

- **Tipagem**: Use as dicas de tipo do [PEP 484](https://peps.python.org/pep-0484/) para todas as assinaturas de função.
  Usar tipos primitivos do python como `list` e `dict`, e usar a biblioteca `Typing` apenas para tipos não
  convencionais, como `Optional` ou `Callable`.

- **TODOs**: Use `# TODO:` para tarefas que precisam ser feitas posteriormente. Inclua uma breve descrição.

  - Exemplo: `# TODO: Refactor this to use new auth service in the future.`



## Antipadrões a Evitar

- **Valores Mágicos**: Use constantes nomeadas ou Enums em vez de valores brutos.

- **Nested IFs**: Evite aninhar lógica mais de 2 níveis de profundidade.

- **Argumentos Padrão Mutáveis**: Nunca use objetos mutáveis (como `list` ou `dict`) como argumentos padrão.

  - **Ruim**: `def add_item(item, items_list=[]): ...`
  - **Bom**: `def add_item(item, items_list=None): if items_list is None: items_list = [] ...`

- **`if...else` Redundante**: Não use um bloco `else` se o bloco `if` contiver um `return`.

  - **Ruim**:

    ```python
    current_user = get_user()

    if not current_user:
      return False
    else:
      create_obj(current_user)
    ```

  - **Bom**:

    ```python
    current_user = get_user()

    if not current_user:
      return False

    create_obj(current_user)
    ```

- **Fugir do padrão**: Sempre verifique como as outras classes estão implementadas para que o padrão seja seguido em
  todo projeto.

## Controle de Versão

- **Mensagens de Commit**: Siga a especificação Conventional Commits. Cada mensagem de commit deve ter um tipo, um
  escopo opcional e uma descrição clara.

  - **Exemplos**: `feat(auth): implement password reset endpoint`, `docs: update coding guidelines`.

- **Merge Requests (MRs)**:

  - Os PRs devem ser pequenos e focados em uma única funcionalidade ou correção.

  - A descrição do PR deve explicar claramente o quê e porquê das mudanças, seguindo template definido.

  - Pelo menos 1 membro da equipe deve revisar e aprovar um PR antes que ele possa ser mesclado.
