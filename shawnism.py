from numpy                  import mean, std
from polars                 import read_csv
from plotly.graph_objects   import Figure, Histogram, Scatter
from random                 import randint
from scipy.stats            import binom
from sys                    import argv
from time                   import time


# python shawnism.py 6E.c.0_ohlcv-1m 0.0005


if __name__ == "__main__":

    t0          = time()
    fn          = argv[1]
    df          = read_csv(f"../databento/csvs/{fn}.csv")
    o           = list(df["open"])
    h           = list(df["high"])
    l           = list(df["low"])
    ts          = list(df["ts_event"])
    start       = ts[0].split("T")[0]
    end         = ts[-1].split("T")[0]
    n_obs       = len(o) - 1000
    n_trades    = 100
    n_samples   = 10_000
    limit       = float(argv[2])
    results     = []
    theo_p      = [ binom.pmf(i, n_trades, 0.50) for i in range(n_trades) ]

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

        results.append(wins)

    fig = Figure()

    fig.add_trace(Scatter({ "x": [ i for i in range(n_trades)], "y": theo_p, "name": "theo" }))
    fig.add_trace(Histogram(x = results, histnorm = "probability density"))
    fig.add_vline(x = 50, line_color = "#FF00FF")

    fig.show()

    print(f"period:  {start} - {end}")
    print(f"mean:    {mean(results):0.2f}")
    print(f"stdev:   {std(results):0.2f}")
    print(f"\n{time() - t0:0.2f}s")