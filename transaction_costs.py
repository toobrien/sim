import  plotly.graph_objects    as      go
from    numpy                   import  array, cumsum, max, min, mean
from    random                  import  choices
from    time                    import  time


if __name__ == "__main__":

    t0          = time()
    n           = 10_000
    trades      = 1000
    tp          = 200
    sl          = -200
    costs       = 15
    X           = [ i for i in range(1, trades + 1) ]
    no_costs    = array([ cumsum(choices([tp, sl], [ 0.5, 0.5 ], k = trades )) for _ in range(n) ])
    with_costs  = array([ cumsum(choices([tp - costs, sl - costs], [ 0.5, 0.5 ], k = trades)) for _ in range(n) ])

    no_costs_m      = mean(no_costs, axis = 0)
    no_costs_h      = max(no_costs, axis = 0)
    no_costs_l      = min(no_costs, axis = 0)
    with_costs_m    = mean(with_costs, axis = 0)
    with_costs_h    = max(with_costs, axis = 0)
    with_costs_l    = min(with_costs, axis = 0)
    traces          = [
                        ( no_costs_m, f"mean pnl, without costs", "#0000FF"),
                        ( no_costs_h, f"max pnl, without costs", "#0000FF"),
                        ( no_costs_l, f"min pnl, without costs", "#0000FF"),
                        ( with_costs_m, f"mean pnl, with costs", "#FF0000"),
                        ( with_costs_h, f"max pnl, with costs", "#FF0000"),
                        ( with_costs_l, f"min pnl, with costs", "#FF0000")
                    ]
    
    fig = go.Figure()

    for trace in traces:

        fig.add_trace(
            go.Scatter(
                {
                    "x": X,
                    "y": trace[0],
                    "name": trace[1],
                    "marker": { "color": trace[2] }
                }
            )
        )
        

    fig.show()

    print(f"{time() - t0:0.1f}s")