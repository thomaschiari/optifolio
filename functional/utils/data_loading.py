# functional/utils/data_loading.py
from pathlib import Path
from datetime import datetime
import time, random
import yfinance as yf
import pandas as pd
from yfinance.exceptions import YFRateLimitError

# --------- constants ---------
DOW_30 = [
    "MSFT","AAPL","NVDA","AMZN","WMT","JPM","V","HD","PG","JNJ",
    "UNH","KO","CRM","CVX","CSCO","IBM","MCD","AXP","MRK","DIS",
    "VZ","GS","CAT","BA","AMGN","HON","NKE","SHW","MMM","TRV",
]

DATA_DIR = (
    Path(__file__).resolve()        
    .parents[1]                     
    / "src" / "data"
)

# Create data directories
SIMULATION_DIR = DATA_DIR

BACKTEST_DIR = DATA_DIR / "backtest"

for directory in [SIMULATION_DIR, BACKTEST_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# --------- helpers ------------
def _download_batch(tickers, start, end, interval, max_retries=5):
    for attempt in range(max_retries):
        try:
            df = yf.download(
                tickers=tickers,
                start=start,
                end=end,
                interval=interval,
                group_by="ticker",
                progress=False,
                threads=False,
                auto_adjust=False,
            )
            return df
        except YFRateLimitError:
            wait = 2 ** attempt + random.uniform(0, 1)
            print(f"Rate‑limited. Retry in {wait:.1f}s …")
            time.sleep(wait)
    raise RuntimeError(f"Unable to fetch {tickers} after {max_retries} retries")

def fetch_dow30(start, end, output_dir, interval="1d", batch_size=5) -> None:
    """Download Dow‑30 history and dump each Close series to CSV."""
    dfs = []
    for i in range(0, len(DOW_30), batch_size):
        batch = DOW_30[i : i + batch_size]
        dfs.append(_download_batch(batch, start, end, interval))

    panel = pd.concat(dfs, axis=1).loc[:, pd.IndexSlice[:, "Close"]]
    panel.columns = panel.columns.get_level_values(0)

    for tkr in panel:
        outfile = output_dir / f"{tkr}.csv"
        panel[[tkr]].dropna().to_csv(outfile)
        print(f"Saved {outfile.relative_to(DATA_DIR.parent.parent)}")  # neat log

# --------- CLI usage ----------
if __name__ == "__main__":
    # Download 2024 data (Aug-Dec) for simulation
    print("\nDownloading 2024 data (Aug-Dec) for simulation...")
    fetch_dow30("2024-08-01", "2024-12-31", SIMULATION_DIR)

    print("\nDownloading 2025 data (Jan-Mar) for backtest...")
    fetch_dow30("2025-01-01", "2025-03-31", BACKTEST_DIR)
