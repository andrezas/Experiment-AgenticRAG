# Guia de Boas Práticas para Testes com Pytest

Este documento serve como o guia oficial para a criação de testes de unidade no projeto. Testes não são uma tarefa
secundária; eles são uma parte integral do desenvolvimento que garante a qualidade, facilita a refatoração e nos dá
confiança para evoluir o software.

A filosofia é simples: **cada teste deve ser pequeno, focado, rápido e independente.**

## Índice

- [Parte 1: A Filosofia e a Estrutura Fundamental](#parte-1-a-filosofia-e-a-estrutura-fundamental)
- [Parte 2: Estrutura e Organização do Projeto](#parte-2-estrutura-e-organiza%C3%A7%C3%A3o-do-projeto)
- [Parte 3: As Ferramentas Essenciais do Pytest](#parte-3-as-ferramentas-essenciais-do-pytest)
- [Parte 4: Executando os Testes e Analisando os Resultados](#parte-4-executando-os-testes-e-analisando-os-resultados)

______________________________________________________________________

### **Parte 1: A Filosofia e a Estrutura Fundamental**

Antes de escrever qualquer código, entenda estes princípios.

#### **1. O Padrão AAA: Arrange, Act, Assert**

Todo teste de unidade deve seguir esta estrutura clara:

- **Arrange (Preparação):** Prepare o cenário. Crie os objetos, configure os mocks e defina os dados de entrada. Todo o
  "setup" acontece aqui.
- **Act (Ação):** Execute a única ação que você quer testar. Geralmente, é a chamada de um único método.
- **Assert (Verificação):** Verifique se o resultado da ação foi o esperado. Use `assert` para validar saídas, estados
  ou interações com mocks.

#### **2. Teste em Isolamento (A Importância dos Mocks)**

Um **teste de unidade** testa uma única "unidade" (uma função, um método, uma classe) de forma isolada. Ele **não** deve
depender de sistemas externos como bancos de dados, APIs, ou o sistema de arquivos. Para alcançar esse isolamento,
usamos **Mocks** (dublês).

> **Regra de Ouro:** Se o seu teste se conecta a uma rede ou a um banco de dados, ele não é um teste de unidade, é um
> teste de integração.

#### **3. Teste Apenas Uma Coisa de Cada Vez**

Cada função de teste deve ter uma única responsabilidade. Se o teste falhar, você deve saber exatamente qual
funcionalidade quebrou sem precisar depurar.

- **Ruim:** `def test_user_creation_and_login(): ...`
- **Bom:** `def test_user_creation_succeeds(): ...` e `def test_user_login_with_valid_credentials(): ...`

#### **4. Teste os Caminhos Felizes e os Tristes**

Não teste apenas o cenário de sucesso. A maior parte do valor dos testes vem da verificação de como seu código lida com
erros.

- **Caminho Feliz:** O que acontece quando tudo funciona como esperado.
- **Caminhos Tristes:** O que acontece quando há erros (ex: input inválido, um dependência falha, um objeto não é
  encontrado). Teste se as exceções corretas são lançadas.

______________________________________________________________________

### **Parte 2: Estrutura e Organização do Projeto**

Consistência é a chave.

1. **Espelhe o Diretório `src`**: A estrutura do diretório `tests` deve ser um espelho da `src`.

   - Código: `src/api/services/meu_servico.py`
   - Teste: `tests/unit/api/services/test_meu_servico.py`

2. **Nomenclatura**:

   - **Arquivos**: Devem começar com `test_`. Ex: `test_knowledge_base_service.py`.
   - **Classes**: Devem começar com `Test`. Ex: `class TestKnowledgeBaseService:`.
   - **Funções**: Devem começar com `test_`. Ex: `def test_succeeds_when_collection_does_not_exist():`.

3. **`__init__.py`**: Sempre adicione um arquivo `__init__.py` (mesmo que vazio) em todos os diretórios e subdiretórios
   de teste. Isso transforma as pastas em pacotes Python, garantindo a descoberta de testes e a consistência dos
   imports.

#### **4. Configuração Centralizada (`pyproject.toml`)**

Toda a configuração do Pytest está centralizada no arquivo `pyproject.toml`, na seção `[tool.pytest.ini_options]`. Isso
garante que todos os desenvolvedores rodem os testes com os mesmos parâmetros.

```toml
[tool.pytest.ini_options]
python_files = ["test_*.py"]
testpaths = ["tests"]
pythonpath = ["."]
addopts = "-v -ra --cov=src --cov-report=term-missing"
norecursedirs = [".git", ".tox", "dist", "build"]
```

- **`python_files`**: Define o padrão de nome que o Pytest deve procurar para encontrar arquivos de teste.
- **`testpaths`**: Diz ao Pytest para procurar testes apenas no diretório `tests`, tornando a busca mais rápida.
- **`pythonpath`**: Adiciona diretórios ao caminho de busca do Python. Usar `"."` (o diretório raiz) ajuda a resolver
  imports, especialmente após instalar o projeto em modo editável.
- **`addopts`**: Define as opções padrão que serão usadas em toda execução do `pytest`. `-v` (verboso), `-ra` (relatório
  de erros), `--cov=src` (medir cobertura do código em `src`) e `--cov-report=term-missing` (mostrar relatório de
  cobertura com linhas faltantes no terminal).
- **`norecursedirs`**: Lista de diretórios que o Pytest deve ignorar durante a busca por testes, evitando pastas de
  ambiente virtual, build, etc.

______________________________________________________________________

### **Parte 3: As Ferramentas Essenciais do Pytest**

Pytest é poderoso. Vamos usar seus recursos para escrever testes melhores e mais limpos.

#### **1. Fixtures (`@pytest.fixture`): Nossos Blocos de Construção**

Fixtures são a melhor ferramenta do Pytest para a fase de **Arrange**. Elas preparam dados, mocks ou instâncias de
classes que podem ser reutilizadas por múltiplos testes.

- **Por que usar?** Para evitar repetição de código (princípio DRY - Don't Repeat Yourself).
- **Como funciona?** Pytest injeta o retorno da fixture em qualquer teste que a declare como um argumento.

```python
# Exemplo do nosso projeto:
@pytest.fixture
def mock_dependencies():
    # ... cria e retorna mocks

@pytest.fixture
def knowledge_base_service(mock_dependencies):
    # ... usa outra fixture para criar o serviço
    return KnowledgeBaseService(...)

# O teste simplesmente usa a fixture pronta!
def test_alguma_coisa(knowledge_base_service):
    # ...
```

#### **2. Mocks (`pytest-mock`): Nossos Atores**

Usamos o plugin `pytest-mock`, que nos dá acesso à fixture `mocker`. Ela simplifica a criação de mocks.

```python
def test_com_mocker(mocker):
    # Mockando um método de um objeto
    mock_db = MagicMock()
    mocker.patch.object(mock_db, 'get_user', return_value={'name': 'Eduarda'})
    
    # Mockando uma classe inteira
    mocker.patch("shared.connectors.qdrant.QdrantClient")
```

#### **3. Testando Exceções (`pytest.raises`): Verificando o Caos Esperado**

Para testar os "caminhos tristes", usamos `pytest.raises` para garantir que uma exceção específica é lançada.

```python
def test_raises_error_when_collection_already_exists(knowledge_base_service, ...):
    with pytest.raises(CollectionAlreadyExistsError) as excinfo:
        knowledge_base_service.create_collection(...)

    # Opcional: Verifique a mensagem de erro
    assert "already exists" in str(excinfo.value)
```

#### **4. Parametrização (`@pytest.mark.parametrize`): Teste Múltiplos Cenários com Um Só Teste**

Quando você tem a mesma lógica de teste, mas com entradas e saídas diferentes, a parametrização é a ferramenta ideal
para evitar código duplicado.

```python
@pytest.mark.parametrize("a, b, expected", [
    (1, 2, 3),         # Cenário 1: Positivos
    (-1, -1, -2),      # Cenário 2: Negativos
    (5, -3, 2),        # Cenário 3: Misto
    (0, 0, 0),         # Cenário 4: Zeros
])
def test_soma(a, b, expected):
    assert soma(a, b) == expected
```

______________________________________________________________________

### **Parte 4: Executando os Testes e Analisando os Resultados**

Aqui estão os comandos essenciais do dia a dia para rodar a suíte de testes e verificar a qualidade do código.

#### **Rodando Todos os Testes**

Para executar a suíte de testes completa e ver o relatório de cobertura inicial no terminal, use:

```bash
uv run pytest
```

*Este comando executa todos os arquivos que começam com `test_` dentro da pasta `tests/`.*

#### **Gerando o Relatório de Cobertura HTML**

Para uma análise visual e detalhada de quais linhas de código foram cobertas pelos testes, gere o relatório HTML:

```bash
uv run coverage html
```

Após executar o comando, uma pasta `htmlcov/` será criada. Abra o arquivo `htmlcov/index.html` em seu navegador para
explorar o relatório interativo.

#### **Visualizando Relatório de Cobertura no Terminal**

Se preferir um relatório rápido no terminal com detalhes sobre as linhas não cobertas, execute:

```bash
uv run coverage report -m
```
