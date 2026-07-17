from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats
from statsmodels.stats.contingency_tables import mcnemar

np.random.seed(42)

df = pd.read_csv("../../resources/data/results_csv/results_experiment.csv")

df["rag_correct"] = df.apply(
    lambda row: int(pd.notna(row["result_rag"]) and row["selected_character"].lower() in row["result_rag"].lower()),
    axis=1,
)

df["agenticrag_correct"] = df.apply(
    lambda row: int(
        pd.notna(row["result_agenticrag"]) and row["selected_character"].lower() in row["result_agenticrag"].lower()
    ),
    axis=1,
)


def bootstrap_ci(data, func=np.mean, n_bootstrap=10000, ci=95):
    """Calcula o intervalo de confiança via bootstrapping."""
    if len(data) == 0:
        return np.nan, np.nan

    bootstrapped_scores = []
    for _ in range(n_bootstrap):
        sample = np.random.choice(data, size=len(data), replace=True)
        bootstrapped_scores.append(func(sample))

    alpha = (100 - ci) / 2
    lower_bound = np.percentile(bootstrapped_scores, alpha)
    upper_bound = np.percentile(bootstrapped_scores, 100 - alpha)
    return lower_bound, upper_bound


def bootstrap_diff_ci(data1, data2, func=np.mean, n_bootstrap=10000, ci=95):
    """Calcula o intervalo de confiança para a diferença pareada via bootstrapping."""
    if len(data1) == 0 or len(data2) == 0:
        return np.nan, np.nan

    bootstrapped_diffs = []
    n = len(data1)
    indices = np.arange(n)
    for _ in range(n_bootstrap):
        sample_indices = np.random.choice(indices, size=n, replace=True)
        sample1 = data1[sample_indices]
        sample2 = data2[sample_indices]
        bootstrapped_diffs.append(func(sample1) - func(sample2))

    alpha = (100 - ci) / 2
    lower_bound = np.percentile(bootstrapped_diffs, alpha)
    upper_bound = np.percentile(bootstrapped_diffs, 100 - alpha)
    return lower_bound, upper_bound


def run_analysis(df):
    results = []

    if df.empty:
        print("DataFrame está vazio.")
        return

    print("Iniciando análises estatísticas via Bootstrapping. Isso pode levar alguns segundos...")

    rag_acc = df["rag_correct"].values
    agentic_acc = df["agenticrag_correct"].values

    mean_rag = np.mean(rag_acc)
    mean_agentic = np.mean(agentic_acc)

    ci_rag = bootstrap_ci(rag_acc, np.mean)
    ci_agentic = bootstrap_ci(agentic_acc, np.mean)
    ci_diff = bootstrap_diff_ci(agentic_acc, rag_acc, np.mean)

    results.append(
        {
            "Analise": "Acuracia Global",
            "Metrica": "RAG Accuracy",
            "Valor": mean_rag,
            "IC_Lower": ci_rag[0],
            "IC_Upper": ci_rag[1],
        }
    )
    results.append(
        {
            "Analise": "Acuracia Global",
            "Metrica": "AgenticRAG Accuracy",
            "Valor": mean_agentic,
            "IC_Lower": ci_agentic[0],
            "IC_Upper": ci_agentic[1],
        }
    )
    results.append(
        {
            "Analise": "Acuracia Global",
            "Metrica": "Diferenca (Agentic - RAG)",
            "Valor": mean_agentic - mean_rag,
            "IC_Lower": ci_diff[0],
            "IC_Upper": ci_diff[1],
        }
    )

    a = sum((rag_acc == 0) & (agentic_acc == 0))
    b = sum((rag_acc == 0) & (agentic_acc == 1))
    c = sum((rag_acc == 1) & (agentic_acc == 0))
    d = sum((rag_acc == 1) & (agentic_acc == 1))

    table = [[a, b], [c, d]]
    mcnemar_res = mcnemar(table, exact=False, correction=True)

    results.append(
        {
            "Analise": "Teste de Hipotese (Global)",
            "Metrica": "McNemar p-value",
            "Valor": mcnemar_res.pvalue,
            "IC_Lower": None,
            "IC_Upper": None,
        }
    )

    iter_count = pd.to_numeric(df["iterations_count"], errors="coerce").dropna()
    depth_val = pd.to_numeric(df["depth"], errors="coerce").dropna()

    if len(iter_count) > 0:
        mean_iters = np.mean(iter_count)
        std_iters = np.std(iter_count, ddof=1)
        q1 = np.percentile(iter_count, 25)
        q3 = np.percentile(iter_count, 75)
        iqr_iters = q3 - q1

        results.append(
            {
                "Analise": "Estatistica Descritiva",
                "Metrica": "iterations_count (Média)",
                "Valor": mean_iters,
                "IC_Lower": None,
                "IC_Upper": None,
            }
        )
        results.append(
            {
                "Analise": "Estatistica Descritiva",
                "Metrica": "iterations_count (Desvio Padrão)",
                "Valor": std_iters,
                "IC_Lower": None,
                "IC_Upper": None,
            }
        )
        results.append(
            {
                "Analise": "Estatistica Descritiva",
                "Metrica": "iterations_count (IQR)",
                "Valor": iqr_iters,
                "IC_Lower": None,
                "IC_Upper": None,
            }
        )

    if len(iter_count) >= 3:
        stat, p_iter = stats.shapiro(iter_count)
        results.append(
            {
                "Analise": "Normalidade (Shapiro-Wilk)",
                "Metrica": "iterations_count p-value",
                "Valor": p_iter,
                "IC_Lower": None,
                "IC_Upper": None,
            }
        )

    if len(depth_val) >= 3:
        stat, p_depth = stats.shapiro(depth_val)
        results.append(
            {
                "Analise": "Normalidade (Shapiro-Wilk)",
                "Metrica": "depth p-value",
                "Valor": p_depth,
                "IC_Lower": None,
                "IC_Upper": None,
            }
        )

    df_corr = df.dropna(subset=["iterations_count", "agenticrag_correct"]).copy()
    if not df_corr.empty:
        iters = pd.to_numeric(df_corr["iterations_count"], errors="coerce")
        accs = pd.to_numeric(df_corr["agenticrag_correct"], errors="coerce")

        valid_idx = ~(iters.isna() | accs.isna())
        iters = iters[valid_idx]
        accs = accs[valid_idx]

        if len(iters) > 1:
            corr, p_corr = stats.pointbiserialr(iters, accs)
            results.append(
                {
                    "Analise": "Correlacao (Ponto-Bisserial)",
                    "Metrica": "iterations_count vs agenticrag_correct (corr)",
                    "Valor": corr,
                    "IC_Lower": None,
                    "IC_Upper": None,
                }
            )
            results.append(
                {
                    "Analise": "Correlacao (Ponto-Bisserial)",
                    "Metrica": "iterations_count vs agenticrag_correct (p-value)",
                    "Valor": p_corr,
                    "IC_Lower": None,
                    "IC_Upper": None,
                }
            )

    if "scenario" in df.columns:
        for scenario in df["scenario"].unique():
            if pd.isna(scenario):
                continue
            df_sc = df[df["scenario"] == scenario]
            rag_acc_sc = df_sc["rag_correct"].values
            agentic_acc_sc = df_sc["agenticrag_correct"].values

            ci_rag_sc = bootstrap_ci(rag_acc_sc, np.mean)
            ci_agentic_sc = bootstrap_ci(agentic_acc_sc, np.mean)
            ci_diff_sc = bootstrap_diff_ci(agentic_acc_sc, rag_acc_sc, np.mean)

            results.append(
                {
                    "Analise": f"Cenario: {scenario}",
                    "Metrica": "RAG Accuracy",
                    "Valor": np.mean(rag_acc_sc),
                    "IC_Lower": ci_rag_sc[0],
                    "IC_Upper": ci_rag_sc[1],
                }
            )
            results.append(
                {
                    "Analise": f"Cenario: {scenario}",
                    "Metrica": "AgenticRAG Accuracy",
                    "Valor": np.mean(agentic_acc_sc),
                    "IC_Lower": ci_agentic_sc[0],
                    "IC_Upper": ci_agentic_sc[1],
                }
            )
            results.append(
                {
                    "Analise": f"Cenario: {scenario}",
                    "Metrica": "Diferenca (Agentic - RAG)",
                    "Valor": np.mean(agentic_acc_sc) - np.mean(rag_acc_sc),
                    "IC_Lower": ci_diff_sc[0],
                    "IC_Upper": ci_diff_sc[1],
                }
            )

    results_df = pd.DataFrame(results)

    # Criar pasta se não existir
    out_dir = Path("resources/data/results")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "statistical_results.csv"

    results_df.to_csv(out_path, index=False)
    print(f"\nResultados estatísticos exportados para {out_path}\n")

    pd.set_option("display.max_rows", None)
    print(results_df.to_string())

    generate_plots(df, results_df)


def generate_plots(df, results_df):
    print("\nGerando gráficos...")
    out_dir = Path("resources/data/results/plots")
    out_dir.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid")

    global_acc = results_df[results_df["Analise"] == "Acuracia Global"].copy()
    global_acc = global_acc[global_acc["Metrica"].isin(["RAG Accuracy", "AgenticRAG Accuracy"])]
    global_acc["Estratégia"] = global_acc["Metrica"].map(
        {"RAG Accuracy": "RAG Tradicional", "AgenticRAG Accuracy": "Agentic RAG"}
    )

    plt.figure(figsize=(6, 5))
    ax_geral = sns.barplot(data=global_acc, x="Estratégia", y="Valor", color="steelblue")

    yerr = []
    for idx, row in global_acc.iterrows():
        err_lower = row["Valor"] - row["IC_Lower"]
        err_upper = row["IC_Upper"] - row["Valor"]
        yerr.append([err_lower, err_upper])

    yerr = np.array(yerr).T
    plt.errorbar(x=range(len(global_acc)), y=global_acc["Valor"], yerr=yerr, fmt="none", c="black", capsize=5)

    plt.title("Acurácia Global do Experimento (com IC 95%)")
    plt.ylabel("Taxa de Acerto Média (Proporção)")
    plt.ylim(0, 1.1)

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
    plt.savefig(out_dir / "accuracy_global_ic.png", dpi=300)
    plt.close()

    scenario_df = results_df[results_df["Analise"].str.startswith("Cenario:")].copy()
    scenario_df = scenario_df[scenario_df["Metrica"].isin(["RAG Accuracy", "AgenticRAG Accuracy"])]
    scenario_df["Cenario"] = scenario_df["Analise"].apply(lambda x: x.split(": ")[1])
    scenario_df["Estratégia"] = scenario_df["Metrica"].map(
        {"RAG Accuracy": "RAG", "AgenticRAG Accuracy": "Agentic RAG"}
    )

    plt.figure(figsize=(10, 6))
    ax_scen = sns.barplot(data=scenario_df, x="Cenario", y="Valor", hue="Estratégia")
    plt.title("Comparativo de Acurácia: RAG vs Agentic RAG por Cenário")
    plt.ylabel("Acurácia (Proporção de Acertos)")
    plt.xlabel("Cenário de Teste")
    plt.ylim(0, 1.1)

    for p in ax_scen.patches:
        height = p.get_height()
        if height > 0:
            ax_scen.annotate(
                f"{height:.2f}",
                (p.get_x() + p.get_width() / 2.0, height),
                ha="center",
                va="bottom",
                fontsize=10,
                color="black",
                xytext=(0, 5),
                textcoords="offset points",
            )

    plt.legend(title="Estratégia")
    plt.tight_layout()
    plt.savefig(out_dir / "accuracy_por_cenario.png", dpi=300)
    plt.close()

    plt.figure(figsize=(8, 5))
    ax_iter = sns.countplot(data=df, x="iterations_count", color="steelblue")
    plt.title("Distribuição de Chamadas de Ferramentas (Agentic RAG)")
    plt.ylabel("Frequência (Qtd de Testes)")
    plt.xlabel("Número de Iterações")

    for p in ax_iter.patches:
        ax_iter.annotate(
            f"{int(p.get_height())}",
            (p.get_x() + p.get_width() / 2.0, p.get_height()),
            ha="center",
            va="bottom",
            fontsize=10,
        )
    plt.tight_layout()
    plt.savefig(out_dir / "distribuicao_iteracoes.png", dpi=300)
    plt.close()

    plt.figure(figsize=(8, 5))
    ax_iter_acc = sns.barplot(data=df, x="iterations_count", y="agenticrag_correct", errorbar=None, color="steelblue")
    plt.title("Acurácia do Agentic RAG por Quantidade de Iterações")
    plt.ylabel("Taxa de Acurácia")
    plt.xlabel("Número de Iterações Utilizadas")
    plt.ylim(0, 1.1)

    for p in ax_iter_acc.patches:
        height = p.get_height()
        if height > 0:
            ax_iter_acc.annotate(
                f"{height:.2f}",
                (p.get_x() + p.get_width() / 2.0, height),
                ha="center",
                va="bottom",
                fontsize=10,
                color="black",
                xytext=(0, 5),
                textcoords="offset points",
            )

    plt.tight_layout()
    plt.savefig(out_dir / "iteracoes_vs_acuracia.png", dpi=300)
    plt.close()

    df_depth_melted = df.melt(
        id_vars=["depth"],
        value_vars=["rag_correct", "agenticrag_correct"],
        var_name="Estratégia",
        value_name="accuracy",
    )
    df_depth_melted["Estratégia"] = df_depth_melted["Estratégia"].map(
        {"rag_correct": "RAG Tradicional", "agenticrag_correct": "Agentic RAG"}
    )

    df_depth_melted["depth_bucket"] = (pd.to_numeric(df_depth_melted["depth"], errors="coerce") * 10).round() * 10

    plt.figure(figsize=(12, 6))
    sns.lineplot(data=df_depth_melted, x="depth_bucket", y="accuracy", hue="Estratégia", marker="o", errorbar=None)
    plt.title("Acurácia vs Profundidade no Documento")
    plt.ylabel("Acurácia (Proporção de Acertos)")
    plt.xlabel("Profundidade da Agulha (%)")
    plt.xticks(range(0, 101, 10))
    plt.ylim(0, 1.1)
    plt.tight_layout()
    plt.savefig(out_dir / "grafico_profundidade.png", dpi=300)
    plt.close()

    matrix = pd.crosstab(
        df["rag_correct"],
        df["agenticrag_correct"],
        rownames=["RAG (0=Erro, 1=Acerto)"],
        colnames=["AgenticRAG (0=Erro, 1=Acerto)"],
    )
    plt.figure(figsize=(6, 5))
    sns.heatmap(matrix, annot=True, fmt="d", cmap="Blues", cbar=False)
    plt.title("Matriz de Discordância (RAG vs AgenticRAG)")
    plt.tight_layout()
    plt.savefig(out_dir / "matriz_discordancia.png", dpi=300)
    plt.close()

    print(f"Gráficos salvos com sucesso na pasta: {out_dir}")


if __name__ == "__main__":
    run_analysis(df)
