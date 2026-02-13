"""
Ultra-fast prescreener using bulk price data
Cuts 12k → ~2–4k in minutes
"""

import yfinance as yf
import pandas as pd
from pathlib import Path
import math

INPUT_TICKERS = "/Users/jazzhashzzz/Documents/Market_Analysis_files/ticker.txt"
OUTPUT_TICKERS = "/Users/jazzhashzzz/Documents/Market_Analysis_files/ticker_filtered.txt"

BATCH_SIZE = 100
MIN_PRICE = 5
MIN_AVG_VOL = 8_000_000


def load_tickers(path):
    with open(path) as f:
        return [line.split("\t")[0].strip().upper() for line in f if line.strip()]


def chunk(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def main():
    tickers = load_tickers(INPUT_TICKERS)
    print(f"Loaded {len(tickers)} tickers")

    passed = []

    for i, batch in enumerate(chunk(tickers, BATCH_SIZE), 1):
        print(f"Batch {i} / {math.ceil(len(tickers)/BATCH_SIZE)}")

        try:
            data = yf.download(
                batch,
                period="30d",
                group_by="ticker",
                auto_adjust=True,
                threads=False,
                progress=False
            )
        except:
            continue

        for ticker in batch:
            try:
                df = data[ticker]
                if len(df) < 10:
                    continue

                price = df["Close"].iloc[-1]
                avg_vol = df["Volume"].mean()

                if price >= MIN_PRICE and avg_vol >= MIN_AVG_VOL:
                    passed.append(ticker)

            except:
                continue

    with open(OUTPUT_TICKERS, "w") as f:
        for t in passed:
            f.write(f"{t}\n")

    print("\n" + "=" * 60)
    print(f"Filtered universe: {len(passed)}")
    print(f"Saved to: {OUTPUT_TICKERS}")
    print("=" * 60)


if __name__ == "__main__":
    main()
