from    random                  import  choices
from    numpy                   import  cumsum, mean, std
import  plotly.graph_objects    as      go
from    plotly.subplots         import  make_subplots


if __name__ == "__main__":

    steps   = 100
    p       = 0.55
    fig     = make_subplots(2, 1)
    steps   = [ 1, -1 ]
    x       = range(steps)
    walk    = choices(population = steps, weights = [ 0.5, 0.5 ], k = steps)
    ev_plus = choices(population = steps, weights = [ p, 1 - p ], k = steps)
    traces  = [
                ( walk, 1, 1, "#FF0000", "walk" )
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