from    random                  import  choice
from    numpy                   import  mean, std
from    time                    import  time
import  plotly.graph_objects    as      go


CONFIG      = {
    "eval": {
        "target":       3000,
        "drawdown":     2500,
        "cost_win":     -34,
        "cost_lose":    -34
    },
    "pa": {
        "target":       2600,
        "drawdown":     2500,
        "cost_win":     2000 - 85,
        "cost_lose":    -85
    }
}
CONTRACTS   = 6
TICK_VAL    = 5
POPULATION  = [ 1, -1 ]
TRIALS      = 10_000


def run(mode: str):

    results     = []
    cost        = []
    #fig         = go.Figure()

    for i in range(TRIALS):

        curve               = []
        dd                  = []
        equity              = 0
        target              = CONFIG[mode]["target"]
        drawdown            = CONFIG[mode]["drawdown"]
        trailing_drawdown   = -drawdown

        while(True):

            pnl_tick            =   choice(POPULATION) * CONTRACTS * TICK_VAL
            equity              +=  pnl_tick
            trailing_drawdown   =   max(trailing_drawdown, -drawdown + equity)

            curve.append(equity)
            dd.append(trailing_drawdown)

            if (equity >= target):

                results.append(1)
                cost.append(CONFIG[mode]["cost_win"])
                
                break

            elif (equity <= trailing_drawdown):

                results.append(0)
                cost.append(CONFIG[mode]["cost_lose"])

                break
        
        '''
        fig.add_trace(
            go.Scattergl(
                {
                    "x": [ i for i in range(len(curve))],
                    "y": curve,
                    "name": "pnl",
                    "marker": { "color": "#0000FF" }
                }
            )
        )

        fig.add_trace(
            go.Scattergl(
                {
                    "x": [ i for i in range(len(dd))],
                    "y": dd,
                    "name": "drawdown",
                    "marker": { "color": "#FF0000" }
                }
            )
        )
        '''

    #fig.show()

    pass_rate   = mean(results)
    ev          = mean(cost)

    print(f"{mode} pass_rate:    {pass_rate * 100:0.2f}%")
    print(f"{mode} ev:          ${ev:0.2f}")


    pass


if __name__ == "__main__":

    t0 = time()

    run("eval")
    run("pa")

    print(f"\n{time() - t0:0.1f}s")