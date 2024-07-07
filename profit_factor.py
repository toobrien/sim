from    bisect                  import  bisect_left
from    numpy                   import  mean, percentile, std
import  plotly.graph_objects    as      go
from    polars                  import  col, read_csv
from    random                  import  choices
from    sys                     import  argv
from    time                    import  time


def profit_factor(sample):

    profits = [ i for i in sample if i > 0 ]
    losses  = [ abs(i) for i in sample if i < 0 ]
    pf      = sum(profits) / sum(losses)

    return pf


if __name__ == "__main__":

    t0          = time()
    start       = argv[1]
    df          = read_csv("~/trading/index_data/SPX/SPX_daily.csv").filter(col("datetime") > start)
    closes      = df["close"]
    trader_pf   = float(argv[2]) if len(argv) > 2 else None
    chgs        = [ closes[i] - closes[i - 1] for i in range(1, len(closes)) ]
    obs_pf      = profit_factor(chgs)
    
    sampling_distribution = sorted([
        profit_factor(choices(population = chgs, k = len(chgs)))
        for i in range(10_000)
    ])

    p_05    = percentile(sampling_distribution, 5)
    p_95    = percentile(sampling_distribution, 95)
    mu      = mean(sampling_distribution)
    sigma   = std(sampling_distribution)

    if trader_pf:

        x           = bisect_left(sampling_distribution, trader_pf)
        p_trader    = x / len(sampling_distribution)
        fig         = go.Figure()

        fig.add_trace(go.Histogram(x = sampling_distribution, histnorm = "probability density"))
        fig.add_vline(x=trader_pf, line_color="red")

        fig.show()

        print(f"p_trader: {p_trader:0.2f}")

    print(f"obs_pf:   {obs_pf:0.2f}")
    print(f"p05_pf:   {p_05:0.2f}")
    print(f"p95_pf:   {p_95:0.2f}")
    print(f"mu:       {mu:0.2f}")
    print(f"sigma:    {sigma:0.2f}")
    print(f"\n{time() - t0:0.1f}s")