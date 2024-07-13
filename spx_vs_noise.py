from    math                    import  log
from    numpy                   import  cumsum, mean, std
from    numpy.random            import  normal
import  plotly.graph_objects    as      go
from    polars                  import  read_csv
from    time                    import  time


if __name__ == "__main__":

    t0      = time()
    df      = read_csv("~/trading/index_data/SPX/SPX_daily.csv")
    closes  = list(df["close"])
    returns = [ log(closes[i] / closes[i - 1]) for i in range(1, len(closes)) ]
    n       = len(returns)
    fig_1   = go.Figure()
    fig_2   = go.Figure()

    mu          = mean(returns)
    sigma       = std(returns)
    daily_noise = normal(loc = 0, scale = sigma, size = n)

    fig_1.add_trace(go.Histogram(x = returns, name = "SPX"))
    fig_1.add_trace(go.Histogram(x = daily_noise, name = "noise"))
    fig_1.add_vline(x = mu, line_color = "#FF00FF")
    fig_1.add_vline(x = mean(daily_noise), line_color = "#FF00FF")
    fig_1.add_vline(x = 0)
    fig_1.show()

    noises = [
        sum(normal(loc = 0, scale = sigma, size = n))
        for _ in range(100_000)
    ]
    mu_noise    = mean(noises)
    sigma_noise = std(noises)
    spx_total   = cumsum(returns)[-1]
    spx_z       = (spx_total - mu_noise) / sigma_noise

    fig_2.add_trace(go.Histogram(x = noises, name = f"noise, total return of {n} days"))
    fig_2.add_vline(x = spx_total, line_color = "#FF00FF")
    fig_2.show()

    print(f"noise mean:   {mu_noise:0.4f}")
    print(f"noise stdev:  {sigma_noise:0.2f}")
    print(f"spx return:   {spx_total:0.2f}")
    print(f"spx z-score:  {spx_z:0.2f}\n")

    print(f"{time() - t0:0.2f}s")

    print(df.head())

    pass