import  plotly.graph_objects    as      go
from    math                    import  sqrt
from    random                  import  choices
from    scipy.stats             import  binom


if __name__ == "__main__":

    n       = 100 # number of trades
    risk    = 1
    reward  = 1
    p_win   = risk / (risk + reward)

    mu      = n * p_win
    sigma   = n * p_win * (1 - p_win)
    
    print(f"mean:   {mu:0.2f}")
    print(f"stdev:  {sigma:0.2f}\n")

    wins    = [ i for i in range(n + 1) ]
    probs   = [ binom.pmf(i, n, p_win) for i in wins ]
    total   = sum(probs)

    for i in range(len(wins)):

        print(f"p({wins[i]} wins): {probs[i] * 100:0.2f}%")

    print(f"\ntotal: {total*100:0.2f}%\n")

    for i in range(1, int(n / 2)):

        p_ = binom.cdf(mu + i, n, p_win) - binom.cdf(mu - i, n, p_win)

        print(f"p(+-{i}):  {p_ * 100:0.2f}%")

    r = binom.rvs(n, p_win, size = 10_000)

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            {
                "x": wins,
                "y": probs,
                "name": "p(n wins)"
            }
        )
    )

    fig.add_trace(
        go.Histogram(
            x           = r, 
            name        = f"10,000 simulated groups of {n} trades",
            histnorm    = "probability density"
        )
    )

    fig.show()