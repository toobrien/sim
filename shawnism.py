from numpy                  import mean, std
from polars                 import read_csv
from plotly.graph_objects   import Figure, Histogram
from random                 import randint
from time                   import time


if __name__ == "__main__":

    t0          = time()
    eurusd      = read_csv("../databento/csvs/6E.c.0_ohlcv-1m.csv")
    o           = list(eurusd["open"])
    h           = list(eurusd["high"])
    l           = list(eurusd["low"])
    h           = list(eurusd["close"])
    n_obs       = len(o) - 1000
    n_trades    = 1_000
    n_samples   = 10_000
    limit       = 0.0005
    results     = []

    for i in range(n_samples):

        wins    = 0

        for j in range(n_trades):

            k = randint(0, n_obs)

            entry   = o[k]
            tp      = entry + limit
            sl      = entry - limit 

            while(k <= n_obs):

                high = max(h[k], l[k])
                low  = min(h[k], l[k])

                if high >= tp:

                    wins += 1

                    break
                
                elif low <= sl:

                    break

                k += 1

        results.append(wins / n_trades)

    fig = Figure()

    fig.add_trace(Histogram(x = results, name = f"trades: {n_trades}<br>samples: {n_samples}<br>tp, sl = {limit}"))
    fig.add_vline(x = n_trades / 2, line_color = "#FF00FF")

    fig.show()

    print(f"mean:  {mean(results):0.2f}")
    print(f"stdev: {std(results):0.2f}")
    print(f"\n{time() - t0:0.2f}s")

    pass