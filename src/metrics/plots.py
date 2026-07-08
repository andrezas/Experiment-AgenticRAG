import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def extrair_dados_experimento(base_dir):
    linhas = []
    base_path = Path(base_dir)

    for json_file in base_path.rglob("*.json"):
        with Path(json_file).open("r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                continue

        # Ponto de atenção corrigido: a classificação agora utiliza a propriedade 'eval_name'
        eval_name = data.get("eval_name", "")

        # 1. Identifica o tipo de hop
        if "twohop" in eval_name:
            hop_type = "two_hop"
        elif "onehop" in eval_name:
            hop_type = "one_hop"
        else:
            hop_type = "unknown"

        # 2. Identifica se a informação está invertida (presença de 'Inv')
        cenario = f"inv_{hop_type}" if "Inv" in eval_name else hop_type

        # Se não mapeou corretamente o hop, define como desconhecido
        if hop_type == "unknown":
            cenario = "unknown"

        for result in data.get("results", []):
            character = result.get("selected_character", "")
            if not character:
                continue

            # Extração RAG Tradicional
            rag_data = result.get("RAG", {})
            rag_result = rag_data.get("result", "")
            # O lower() previne quebra por diferença de caixa ou pontuações (ex: "Caleb.")
            rag_accuracy = 1 if character.lower() in str(rag_result).lower() else 0

            # Extração AgenticRAG
            agentic_data = result.get("AgenticRAG", {})
            agentic_result = agentic_data.get("result", "")
            agentic_accuracy = 1 if character.lower() in str(agentic_result).lower() else 0
            agentic_iterations = agentic_data.get("iterations_count", 0)

            # Metadata de profundidade
            depth = result.get("placement_metadata", {}).get("depth", 0.0)

            linhas.append(
                {
                    "test_id": result.get("payload_filtering"),
                    "eval_name": eval_name,
                    "cenario": cenario,
                    "character": character,
                    "depth": depth,
                    "rag_accuracy": rag_accuracy,
                    "agentic_accuracy": agentic_accuracy,
                    "agentic_iterations": agentic_iterations,
                }
            )

    return pd.DataFrame(linhas)


def plotar_resultados(df):
    sns.set_theme(style="whitegrid")

    # 1. Preparar dados para o gráfico comparativo geral
    # Derrete (melt) o dataframe para facilitar o agrupamento no Seaborn
    df_melted = df.melt(
        id_vars=["test_id", "cenario", "depth"],
        value_vars=["rag_accuracy", "agentic_accuracy"],
        var_name="pipeline",
        value_name="accuracy",
    )
    df_melted["pipeline"] = df_melted["pipeline"].map({"rag_accuracy": "RAG", "agentic_accuracy": "Agentic RAG"})

    # --- Gráfico 1: Acurácia por Cenário ---
    plt.figure(figsize=(10, 6))
    ax1 = sns.barplot(data=df_melted, x="cenario", y="accuracy", hue="pipeline", errorbar=None)
    plt.title("Comparativo de Acurácia: RAG vs Agentic RAG por Cenário")
    plt.ylabel("Acurácia (Proporção de Acertos)")
    plt.xlabel("Cenário de Teste")
    plt.ylim(0, 1.1)

    # Adicionar rótulos nas barras
    for p in ax1.patches:
        ax1.annotate(
            f"{p.get_height():.2f}",
            (p.get_x() + p.get_width() / 2.0, p.get_height()),
            ha="center",
            va="bottom",
            fontsize=10,
            color="black",
            xytext=(0, 5),
            textcoords="offset points",
        )
    plt.tight_layout()
    plt.savefig("grafico_acuracia_cenarios.png")
    plt.show()

    # --- Gráfico 2: Distribuição de Iterações do Agentic RAG ---
    plt.figure(figsize=(8, 5))
    ax2 = sns.countplot(data=df, x="agentic_iterations", color="steelblue")
    plt.title("Distribuição de Chamadas de Ferramentas (Agentic RAG)")
    plt.ylabel("Frequência (Qtd de Testes)")
    plt.xlabel("Número de Iterações")

    for p in ax2.patches:
        ax2.annotate(
            f"{int(p.get_height())}",
            (p.get_x() + p.get_width() / 2.0, p.get_height()),
            ha="center",
            va="bottom",
            fontsize=10,
        )
    plt.tight_layout()
    plt.savefig("grafico_iteracoes_agentic.png")
    plt.show()

    # --- Gráfico 3: Acurácia do Agente baseada no Número de Iterações ---
    plt.figure(figsize=(8, 5))
    sns.barplot(data=df, x="agentic_iterations", y="agentic_accuracy", errorbar=None, color="steelblue")
    plt.title("Acurácia do Agentic RAG por Quantidade de Iterações")
    plt.ylabel("Taxa de Acurácia")
    plt.xlabel("Número de Iterações Utilizadas")
    plt.ylim(0, 1.1)
    plt.tight_layout()
    plt.savefig("grafico_acuracia_por_iteracao.png")
    plt.show()

    # --- Gráfico 4: Impacto da Profundidade (Scatter/Line) ---
    # Arredondar a profundidade em "buckets" de 10% para visualização clara
    df_melted["depth_bucket"] = (df_melted["depth"] * 10).round() * 10

    plt.figure(figsize=(12, 6))
    sns.lineplot(data=df_melted, x="depth_bucket", y="accuracy", hue="pipeline", marker="o", errorbar=None)
    plt.title("Acurácia vs Profundidade no Documento")
    plt.ylabel("Acurácia")
    plt.xlabel("Profundidade da Agulha (%)")
    plt.xticks(range(0, 101, 10))
    plt.ylim(0, 1.1)
    plt.tight_layout()
    plt.savefig("grafico_profundidade.png")
    plt.show()


def plotar_metricas_globais(df):

    # Filtra dados desconhecidos por segurança
    df_validos = df[df["cenario"] != "unknown"].copy()

    if df_validos.empty:
        print("Nenhum dado válido para análise global.")
        return

    sns.set_theme(style="whitegrid")

    # --- 1. Gráfico de Acurácia Geral (Média de Todos os Casos) ---
    acuracia_geral = df_validos[["rag_accuracy", "agentic_accuracy"]].mean()
    df_geral = pd.DataFrame(
        {
            "Estratégia": ["RAG Tradicional", "Agentic RAG"],
            "Acurácia Média": [acuracia_geral["rag_accuracy"], acuracia_geral["agentic_accuracy"]],
        }
    )

    plt.figure(figsize=(6, 5))
    ax_geral = sns.barplot(data=df_geral, x="Estratégia", y="Acurácia Média")
    plt.title("Acurácia Global do Experimento")
    plt.ylabel("Taxa de Acerto Média (Proporção)")
    plt.ylim(0, 1.1)

    # Rótulo de porcentagem nas barras
    for p in ax_geral.patches:
        height = p.get_height()
        ax_geral.annotate(
            f"{height * 100:.1f}%",
            (p.get_x() + p.get_width() / 2.0, height),
            ha="center",
            va="bottom",
            fontsize=11,
            color="black",
            xytext=(0, 5),
            textcoords="offset points",
        )

    plt.tight_layout()
    plt.savefig("grafico_acuracia_geral.png", dpi=300)
    plt.show()


# Como executar:
df_resultados = extrair_dados_experimento("resources/data/results")
print(df_resultados.groupby("cenario")[["rag_accuracy", "agentic_accuracy"]].mean())
plotar_resultados(df_resultados)
plotar_metricas_globais(df_resultados)
