import  plotly.graph_objects    as      go
from    numpy                   import  array, cumsum, max, min, mean
from    random                  import  choices
from    sys                     import  argv
from    time                    import  time



if __name__ == "__main__":

    t0          = time()
    n           = 10_000
    trades      = 1000
    tp          = float(argv[1])
    sl          = float(argv[2])
    equity      = 2500
    p_win       = abs(sl) / (tp + sl)
    p_lose      = 1 - p_win
    costs       = 15
    X           = [ i for i in range(1, trades + 1) ]
    no_costs    = array([ cumsum(choices([tp, -sl], [ p_win, p_lose ], k = trades )) for _ in range(n) ])
    with_costs  = array([ cumsum(choices([tp - costs, -sl - costs], [ p_win, p_lose ], k = trades)) for _ in range(n) ])

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
    
    # pnl

    fig = go.Figure()

    for trace in traces:

        fig.add_trace(
            go.Scatter(
                {
                    "x":        X,
                    "y":        trace[0],
                    "name":     trace[1],
                    "marker":   { "color": trace[2] }
                }
            )
        )
        
    fig.show()

    # survival rate

    no_costs_survival   = array([ 0. for i in range(n) ])
    with_costs_survival = array([ 0. for i in range(n) ])

    for arrs in [ 
        ( no_costs, no_costs_survival ),
        ( with_costs, with_costs_survival )
    ]:

        in_arr  = arrs[0]
        out_arr = arrs[1]

        for i in range(n):

            for j in range(trades):

                if in_arr[i][j] <= -equity:

                    break

                else:

                    out_arr[j] += 1

    no_costs_survival /= n
    with_costs_survival /= n

    fig     = go.Figure()
    traces  = [
                ( no_costs_survival, "survival rate, without costs", "#0000FF" ),
                ( with_costs_survival, "survival rate, with costs", "#FF0000" )
            ]

    for trace in traces:

        fig.add_trace(
            go.Scatter(
                {
                    "x":        X,
                    "y":        trace[0],
                    "name":     trace[1],
                    "marker":   { "color": trace[2] }
                }
            )
        )

    fig.show()

    print(f"{time() - t0:0.1f}s")