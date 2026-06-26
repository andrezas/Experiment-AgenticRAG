# Linter e Formatador de Markdown

## Visão Geral

O projeto utiliza **mdformat** para garantir consistência e qualidade na documentação em arquivos Markdown (`.md`). A
ferramenta é executada automaticamente através do hook de `pre-commit`, garantindo que todos os arquivos submetidos ao
repositório sigam um padrão de formatação uniforme.

## Ferramentas Utilizadas

### mdformat

- **Descrição**: Formatador automático para arquivos Markdown
- **Site**: [mdformat.readthedocs.io](https://mdformat.readthedocs.io/)
- **Versão**: 0.7.21

### Plugins

1. **mdformat-gfm** (0.3.8): Suporte a GitHub Flavored Markdown

   - Tabelas
   - Strikethrough (`~~texto~~`)
   - Task lists (`- [ ] tarefa`)
   - Autolinks
   - Alinhamento automático de colunas
   - Espaçamento padronizado

## Configuração

A configuração do mdformat está localizada em `.mdformat.toml`:

```toml
# Largura máxima da linha (compatível com ruff)
wrap = 120

# Numerar automaticamente listas ordenadas
number = true

# Diretórios excluídos
exclude = [
    ".venv",
    ".pytest_cache",
    "build",
    "dist",
]
```

## Uso

### Formatação Automática (via pre-commit)

Ao fazer commit, o hook de pre-commit executará automaticamente o mdformat em arquivos `.md` modificados:

```bash
git add docs/novo-arquivo.md
git commit -m "docs: adiciona nova documentação"
# mdformat será executado automaticamente
```

### Formatação Manual

**Usando Makefile:**

```bash
make format-md
```

**Formatar todos os arquivos Markdown:**

```bash
uv run mdformat .
```

**Formatar arquivos específicos:**

```bash
uv run mdformat docs/api.md README.md
```

**Verificar formatação sem modificar arquivos:**

```bash
uv run mdformat --check .
```

**Formatar excluindo diretórios:**

```bash
uv run mdformat . --exclude .venv --exclude build
```

### Executar Todos os Hooks Manualmente

```bash
uv run pre-commit run --all-files
```

## Regras de Formatação

O mdformat aplica as seguintes regras automaticamente:

1. **Linhas**: Quebra automática em 120 caracteres
2. **Listas Ordenadas**: Numeração sequencial automática
3. **Tabelas**: Alinhamento consistente de colunas
4. **Espaçamento**: Normalização de espaços em branco
5. **Headers**: Formatação padronizada de cabeçalhos
6. **Links**: Formatação consistente de links e referências
7. **Blocos de Código**: Preservação de sintaxe e indentação

## Integração com CI/CD

O linter está configurado no `.pre-commit-config.yaml`:

```yaml
- repo: https://github.com/executablebooks/mdformat
  rev: 0.7.21
  hooks:
    - id: mdformat
      name: Format Markdown files
      args: [--wrap, "120", --number]
      additional_dependencies:
        - mdformat-gfm>=0.3.8
      files: \.md$
      stages: [pre-commit]
```

## Exemplos

### Antes da Formatação

```markdown
# Título

Lista sem ordem:
* item 1
* item 2
    * subitem

Tabela desalinhada:
| Nome | Idade |
|---|---|
| João | 30 |
| Maria Silva | 25 |
```

### Depois da Formatação

```markdown
# Título

Lista sem ordem:

- item 1
- item 2
  - subitem

Tabela desalinhada:

| Nome        | Idade |
| ----------- | ----- |
| João        | 30    |
| Maria Silva | 25    |
```

## Troubleshooting

### Erro: "File is not formatted"

Execute o formatador para corrigir automaticamente:

```bash
uv run mdformat arquivo.md
```

### Hook do pre-commit falha

Certifique-se de que o pre-commit está instalado:

```bash
uv run pre-commit install
```

Reinstale os ambientes se necessário:

```bash
uv run pre-commit clean
uv run pre-commit install --install-hooks
```

## Referências

- [Documentação oficial do mdformat](https://mdformat.readthedocs.io/)
- [mdformat-gfm](https://github.com/hukkin/mdformat-gfm)
- [Pre-commit](https://pre-commit.com/)
