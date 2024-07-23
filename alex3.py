from    random                  import  choices
from    numpy                   import  zeros
from    time                    import  time
import  plotly.graph_objects    as      go


CONTRACTS   = 6
TICK_VAL    = 5
SPREAD      = 2
COMMISSIONS = 4.64
COSTS       = (SPREAD * TICK_VAL + COMMISSIONS) * CONTRACTS
POPULATION  = [ 1 * CONTRACTS * TICK_VAL, -1 * CONTRACTS * TICK_VAL ]
WEIGHTS     = [ 0.5, 0.5 ]
TRIALS      = 10_000
MAX_TICKS   = 10_000
WIN_LVL     = 2500
TDD         = -3000


def params_a(equity: float):

    # flip days

    if equity <= WIN_LVL:

        return 20 * CONTRACTS * TICK_VAL, 80 * CONTRACTS * TICK_VAL
    
    else:

        return 7 * CONTRACTS * TICK_VAL, 7 * CONTRACTS * TICK_VAL


def params_b(equity: float):

    # static

    return 20 * CONTRACTS * TICK_VAL, 80 * CONTRACTS * TICK_VAL


def params_c(equity: float):

    if equity <= 2340:

        return 26 * CONTRACTS * TICK_VAL, 83 * CONTRACTS * TICK_VAL
    
    else:

        return 7 * CONTRACTS * TICK_VAL, 7 * CONTRACTS * TICK_VAL


PARAMS = {
    "A": params_a,
    "B": params_b,
    "C": params_c
}


def run(strategy: str):

    p_win   = zeros(MAX_TICKS)

    for _ in range(TRIALS):

        ticks               = choices(POPULATION, WEIGHTS, k = MAX_TICKS)
        equity              = 0
        get_params          = PARAMS[strategy]
        tp_dlrs, sl_dlrs    = get_params(equity)
        tp                  = equity + tp_dlrs
        sl                  = equity - sl_dlrs
        drawdown            = TDD

        for j in range(MAX_TICKS):

            pnl_tick            =   ticks[j]
            equity              +=  pnl_tick
            trailing_drawdown   =   min(max(drawdown, drawdown + equity), 100)

            if equity >= tp or equity <= sl:

                equity              -=  COSTS
                tp_dlrs, sl_dlrs    =   get_params(equity)
                tp                  =   equity + tp_dlrs
                sl                  =   equity - sl_dlrs

            if (equity >= WIN_LVL):

                p_win[j] += 1

            elif (equity <= trailing_drawdown):

                break
    
    p_win /= TRIALS

    return p_win


if __name__ == "__main__":

    t0      = time()
    fig     = go.Figure()
    X       = [ i for i in range(MAX_TICKS) ]

    p_win_a = run("A")
    p_win_b = run("B")
    p_win_c = run("C")

    for trace in [ 
        ( p_win_a, "flip days" ),
        ( p_win_b, "static" ),
        ( p_win_c, "supian" )
    ]:

        fig.add_trace(
            go.Scattergl(
                {
                    "x":    X,
                    "y":    trace[0],
                    "name": f"p(>{WIN_LVL}) ({trace[1]})"
                }
            )
        )

    fig.show()

    print(f"{time() - t0:0.1f}s")
    