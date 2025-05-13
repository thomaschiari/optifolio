#!/usr/bin/env python3
# backtest_q1_2025.py
# --------------------------------------------------------------
# Avalia, no 1º tri­mestre 2025, a carteira que saiu vencedora
# da simulação (Q4 2024) e compara as métricas.

import pandas as pd
import numpy as np
from pathlib import Path
import sys

# ----------------------------------------------------------------
# CONFIGURAÇÃO – ajuste se seus caminhos forem diferentes
PORTFOLIO_CSV   = Path("../src/portfolio_results.csv")   # carteira “ótima”
BACKTEST_DIR    = Path("../src/data/backtest")           # CSVs de 2025‑Q1
OUTPUT_CSV      = Path("backtesting_results.csv")        # sai aqui

PERIOD_START    = "2025-01-01"
PERIOD_END      = "2025-03-31"

# ----------------------------------------------------------------
def calculate_portfolio_metrics(returns: pd.DataFrame, weights: np.ndarray):
    """
    Retorno anualizado, volatilidade anualizada e Sharpe ratio.
    """
    port_ret = np.sum(returns.mean() * weights) * 252      # retorno
    port_vol = np.sqrt(weights.T @ (returns.cov() * 252) @ weights)  # vol
    sharpe   = port_ret / port_vol if port_vol != 0 else np.nan
    return port_ret, port_vol, sharpe

# ----------------------------------------------------------------
def main():
    if not PORTFOLIO_CSV.exists():
        sys.exit(f"❌ Arquivo {PORTFOLIO_CSV} não encontrado")

    best = pd.read_csv(PORTFOLIO_CSV).iloc[0]

    # -------- parse tickers & pesos (corrige vírgula decimal) ----
    tickers = best["Tickers"].split('-')
    weights = np.array([
        float(w.replace(',', '.'))  # garante . como separador decimal
        for w in best["Weights"].split('-')
    ])

    # -------- lê preços de Q1‑2025 --------------------------------
    good_tickers = []
    good_weights = []
    price_series = []

    for tkr, w in zip(tickers, weights):
        fp = BACKTEST_DIR / f"{tkr}.csv"
        if not fp.exists():
            print(f"[WARN] dados de {tkr} ausentes em {fp}, removendo da carteira")
            continue

        df = pd.read_csv(fp)
        # supõe colunas ['Date', <ticker>]  (igual ao DataLoader)
        price_col = [c for c in df.columns if c != "Date"][0]
        ser = (
            df.assign(Date=pd.to_datetime(df["Date"]))
              .set_index("Date")[price_col]
              .loc[PERIOD_START:PERIOD_END]
        )

        # apenas se houver dados suficientes
        if ser.empty or ser.isna().all():
            print(f"[WARN] série vazia para {tkr} em Q1‑2025, removendo")
            continue

        good_tickers.append(tkr)
        good_weights.append(w)
        price_series.append(ser)

    if not good_tickers:
        sys.exit("❌ Nenhum ativo com dados válidos para Q1‑2025.")

    # normaliza pesos para somar 1, caso algo tenha sido removido
    good_weights = np.array(good_weights)
    good_weights = good_weights / good_weights.sum()

    # -------- monta DataFrame combinado e calcula retornos --------
    combined = pd.concat(price_series, axis=1)
    combined.columns = good_tickers              # garante mesma ordem
    returns  = combined.pct_change().dropna()

    # -------- métricas Q1‑2025 ------------------------------------
    q1_ret, q1_vol, q1_sharpe = calculate_portfolio_metrics(returns, good_weights)

    # -------- print comparativo -----------------------------------
    print("\n🔎  Q1‑2025 Performance:")
    print(f"  • Annual Return    : {q1_ret:.4f}")
    print(f"  • Annual Volatility: {q1_vol:.4f}")
    print(f"  • Sharpe Ratio     : {q1_sharpe:.4f}")

    print("\n🔄  Comparação c/ Q4‑2024 (training):")
    print(f"  • Return  Q4‑24    : {best['AnnualReturn']:.4f}")
    print(f"  • Vol     Q4‑24    : {best['AnnualVol']:.4f}")
    print(f"  • Sharpe  Q4‑24    : {best['Sharpe']:.4f}")

    # -------- salva CSV de resultados -----------------------------
    out = pd.DataFrame({
        "Period"       : ["Q4‑2024", "Q1‑2025"],
        "AnnualReturn" : [best['AnnualReturn'], q1_ret],
        "AnnualVol"    : [best['AnnualVol'],    q1_vol],
        "Sharpe"       : [best['Sharpe'],       q1_sharpe],
        "Tickers"      : ['-'.join(good_tickers)]*2,
        "Weights"      : ['-'.join(map(str, good_weights))]*2
    })

    out.to_csv(OUTPUT_CSV, index=False)
    print(f"\n✅ Resultados gravados em {OUTPUT_CSV.resolve()}")

# ----------------------------------------------------------------
if __name__ == "__main__":
    main()
