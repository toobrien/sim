from    random                  import  choices
from    numpy                   import  cumsum, mean, std
import  plotly.graph_objects    as      go
from    plotly.subplots         import  make_subplots


if __name__ == "__main__":

    n_steps = 100
    p       = 0.55
    fig     = make_subplots(2, 1)
    units   = [ 1, -1 ]
    x       = list(range(n_steps))
    walk    = cumsum(choices(population = units, weights = [ 0.5, 0.5 ], k = n_steps))
    ev_plus = cumsum(choices(population = units, weights = [ p, 1 - p ], k = n_steps))
    traces  = [
                ( walk, 1, 1, "#FF0000", "walk" ),
                ( ev_plus, 2, 1, "#0000FF", "ev+" )
            ]

    for trace in traces:

        fig.add_trace(
            go.Scatter(
                {
                    "x":        x,
                    "y":        trace[0],
                    "marker":   { "color": trace[3] },
                    "name":     trace[4]
                },
                row = trace[1],
                col = trace[2]
            )
        )

    fig.show()