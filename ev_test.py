from    random                  import  choices
from    numpy                   import  cumsum, mean, std
import  plotly.graph_objects    as      go
from    plotly.subplots         import  make_subplots
from    time                    import  time


if __name__ == "__main__":

    t0          = time()
    n_trials    = 10000
    n_steps     = 100
    p           = 0.51
    fig         = make_subplots(2, 2)
    units       = [ 1, -1 ]
    x           = list(range(n_steps))
    walk        = [ cumsum(choices(population = units, weights = [ 0.5, 0.5 ], k = n_steps)) for i in range(n_trials) ]
    ev_plus     = [ cumsum(choices(population = units, weights = [ p, 1 - p ], k = n_steps)) for i in range(n_trials) ]
    traces      = [
                    ( walk, 1, "#FF0000", "walk" ),
                    ( ev_plus, 2, "#0000FF", "ev+" )
                ]

    for trace in traces:

        ys      = trace[0]
        row     = trace[1]
        color   = trace[2]
        name    = trace[3]
        hist    = [ y[-1] for y in ys ]

        for y in ys:

            fig.add_trace(
                go.Scattergl(
                    {
                        "x":        x,
                        "y":        y,
                        "mode":     "markers",
                        "marker":   { "color": color },
                        "name":     name
                    }
                ),
                row = trace[1],
                col = 1
            )

        fig.add_trace(
            go.Histogram(x = hist, name = name),
            row = row,
            col = 2
        )

        print(f"mu, std {name}:\t{mean(hist):0.2f}\t{std(hist):0.2f}")

    fig.show()

    print(f"{time() - t0:0.2f}s")