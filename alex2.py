from    numpy                   import  mean, std
from    numpy.random            import  binomial
import  plotly.graph_objects    as      go
from    random                  import  choices
from    sys                     import  argv


# eval pass_rate:   30.86%
# pa pass_rate:     36.40%


EVAL_COST = 34


if __name__ == "__main__":

    n_evals = int(argv[1])

    X = [
            binomial(n_evals, p = 0.3086)
            for i in range(10_000)
        ]

    fig = go.Figure()

    fig.add_trace(
        go.Histogram(
            x           = X,
            histnorm    = "probability density"
        )
    )

    mu      = mean(X)
    sigma   = std(X)

    print(f"cost:   ${n_evals * EVAL_COST:0.2f}")
    print(f"mean:    {mu:5.2f}")
    print(f"std:     {sigma:5.2f}")

    fig.show()