import  plotly.graph_objects    as      go
from    plotly.subplots         import  make_subplots
from    math                    import  pi, sin
from    numpy                   import  arange
from    numpy.random            import  normal


N = 1000


if __name__ == "__main__":

    x           = arange(0, 2 * pi, 2 * pi / N)
    y           = [ sin(x_) for x_ in x ]
    noise       = normal(0, 1, N)
    max_weight  = 0.99
    fig         = make_subplots(2, 3)

    params = [
        ( 1, 1, 0.00 ),
        ( 1, 2, 0.10),
        ( 1, 3, 0.20),
        ( 2, 1, 0.50),
        ( 2, 2, 0.99),
        ( 2, 3, 1.00)
    ]

    for p_set in params:

        row         = p_set[0]
        col         = p_set[1]
        w_noise     = p_set[2]
        w_signal    = 1 - w_noise

        y_ = [ w_signal * y[i] + w_noise * noise[i] for i in range(len(y)) ]

        fig.add_trace(
            go.Scatter(
                {
                    "x":        x,
                    "y":        y_,
                    "mode":     "markers",
                    "marker":   { "color": "#0000FF" },
                    "name":     f"signal: {w_signal:0.2f}  noise: {w_noise:0.2f}"
                }
            ),
            row = row,
            col = col
        )

    fig.show()
