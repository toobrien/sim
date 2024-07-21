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
SPREAD      = 2
COMMISSIONS = 4.64
COSTS       = (SPREAD * TICK_VAL + COMMISSIONS) * CONTRACTS
POPULATION  = [ 1, -1 ]
TP_TICKS    = 20
SL_TICKS    = 80
TP_DOLLARS  = TP_TICKS * CONTRACTS * TICK_VAL
SL_DOLLARS  = SL_TICKS * CONTRACTS * TICK_VAL
TRIALS      = 10_000


def run(mode: str):

    results     = []
    cost        = []
    #fig         = go.Figure()

    for i in range(TRIALS):

        curve               = []
        dd                  = []
        equity              = 0
        tp                  = equity + TP_DOLLARS
        sl                  = equity - SL_DOLLARS
        target              = CONFIG[mode]["target"]
        drawdown            = CONFIG[mode]["drawdown"]
        trailing_drawdown   = -drawdown

        while(True):

            pnl_tick            =   choice(POPULATION) * CONTRACTS * TICK_VAL
            equity              +=  pnl_tick
            trailing_drawdown   =   max(trailing_drawdown, -drawdown + equity)

            if equity >= tp or equity <= sl:

                equity -= COSTS
                tp      = equity + TP_DOLLARS
                sl      = equity - SL_DOLLARS

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

    print(f"{mode + ' pass_rate':30}{pass_rate:<10.2f}")
    print(f"{mode + ' ev':30}{ev:<10.2f}")

    return pass_rate, ev


if __name__ == "__main__":

    t0 = time()

    print(f"{'contracts:':30}{CONTRACTS:<10}")
    print(f"{'tick val ($):':30}{TICK_VAL:<10.2f}")
    print(f"{'spread (ticks):':30}{SPREAD:<10.2f}")
    print(f"{'commissions ($):':30}{COMMISSIONS:<10.2f}")
    print(f"{'trade cost ($):':30}{COSTS:<10.2f}")
    print(f"{'tp (ticks):':30}{TP_TICKS:<10.2f}")
    print(f"{'tp ($):':30}{TP_DOLLARS:<10.2f}")
    print(f"{'sl (ticks):':30}{SL_TICKS:<10.2f}")
    print(f"{'sl ($):':30}{SL_DOLLARS:<10.2f}")
    print(f"{'trials:':30}{TRIALS:<10}\n")

    p_eval_pass, eval_ev    = run("eval")
    p_pa_pass, pa_ev        = run("pa")

    p_eval_fail             = 1 - p_eval_pass
    p_pa_fail               = 1 - p_pa_pass
    c_eval_fail             = CONFIG["eval"]["cost_lose"]
    e_eval_fail             = p_eval_fail * c_eval_fail
    p_eval_pass_pa_fail     = p_eval_pass * p_pa_fail
    c_eval_pass_pa_fail     = CONFIG["eval"]["cost_win"] + CONFIG["pa"]["cost_lose"]
    e_eval_pass_pa_fail     = p_eval_pass_pa_fail * c_eval_pass_pa_fail
    p_eval_pass_pa_pass     = p_eval_pass * p_pa_pass
    c_eval_pass_pa_pass     = CONFIG["eval"]["cost_win"] + CONFIG["pa"]["cost_win"]
    e_eval_pass_pa_pass     = p_eval_pass_pa_pass * c_eval_pass_pa_pass
    p_total                 = p_eval_fail + p_eval_pass_pa_fail + p_eval_pass_pa_pass
    e_total                 = e_eval_fail + e_eval_pass_pa_fail + e_eval_pass_pa_pass

    print("\n")
    print(f"{'case:':30}{'prob':10}{'cost':10}{'ev':10}")
    print(f"{'eval fail:':30}{p_eval_fail:<10.2f}{c_eval_fail:<10.2f}{e_eval_fail:<10.2f}")
    print(f"{'eval pass, pa_fail:':30}{p_eval_pass_pa_fail:<10.2f}{c_eval_pass_pa_fail:<10.2f}{e_eval_pass_pa_fail:<10.2f}")
    print(f"{'eval pass, pa_pass:':30}{p_eval_pass_pa_pass:<10.2f}{c_eval_pass_pa_pass:<10.2f}{e_eval_pass_pa_pass:<10.2f}")
    print(f"{'total:':30}{p_total:<10.2f}{'':10}{e_total:<10.2f}")

    print(f"\n{time() - t0:0.1f}s")