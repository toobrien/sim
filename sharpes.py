from    numpy                   import  cumsum, mean
from    numpy.random            import  normal
from    math                    import  sqrt
import  plotly.graph_objects    as      go
from    sys                     import  argv


DPY  = 256
RUNS = 1000 


if __name__ == "__main__":

    fig         = go.Figure()
    x           = [ i for i in range(DPY) ]
    reward_mult = float(argv[1])
    risk_mult   = float(argv[2])
    arr         = [ 
                    ( 0.0003, 0.0123, "A" ),
                    ( 0.0003, 0.0100, "B" ),
                    ( 0.0003, 0.0075, "C" ),
                    ( 0.0003, 0.0050, "D" ),
                    ( 0.0003, 0.0035, "E" ),
                    ( 0.0003, 0.0025, "F" ),
                    ( 0.0003, 0.0020, "G" ),
                    ( 0.0003, 0.0010, "H" )
                ]

    if len(argv) > 3:

        i = int(argv[3])

        mu      = arr[i][0] * reward_mult
        sigma   = arr[i][1] * risk_mult 
        sharpe  = mu / sigma * sqrt(DPY)
        ys      = []

        for j in range(RUNS):

            y = cumsum(normal(loc = mu, scale = sigma, size = DPY))

            fig.add_trace(
                go.Scattergl(
                    {
                        "x":    x,
                        "y":    y,
                        "name": f"{sharpe:0.2f} {j}",
                        "marker": { "color": "#0000FF" }
                    }
                )
            )

            ys.append(y)

        avg = [ 
            mean([ ys[l][k] for l in range(RUNS)])
            for k in range(DPY) 
        ]

        fig.add_trace(
            go.Scattergl(
                {
                    "x":    x,
                    "y":    avg,
                    "name": f"{sharpe:0.2f} avg",
                    "marker": { "color": "#FF0000" }
                }
            )
        )

        fig.show()

    else:

        for mu, sigma, name in arr:
            mu      = mu * reward_mult
            sigma   = sigma * risk_mult
            sharpe  = mu / sigma * sqrt(DPY)
            returns = normal(loc = mu, scale = sigma, size = DPY)
            y       = cumsum(returns)

            print(f"{name}: {sharpe:0.2f}")

            fig.add_trace(
                go.Scattergl(
                    {
                        "x":    x,
                        "y":    y,
                        "name": name
                    }
                )
            )
        
        fig.show()