from    numpy                   import  array, concatenate, full, mean, median, percentile, std
import  plotly.graph_objects    as      go
from    plotly.subplots         import  make_subplots
from    prop_2                  import  sim_runs, get_metric, get_rr_metric
from    sys                     import  argv
from    time                    import  time


PARAMS = {
    "runs":                         100, 
    "days":                         256,
    "mu":                           0.0004,
    "sigma":                        0.0009,
    "discretionary_buffer":         0,
    "max_resets":                   3,
    "leverage":                     1.0,
    "trades_per_day":               5,
    "withdrawal_frequency_days":    21,
    "withdrawal_amount_dollars":    2000,
    "transaction_costs_per_trade":  16.5,
    "show_runs":                    0,
    "mode":                         "tradeday_50k"
}


def pad_runs(run_list: array, days: int):

    for i in range(len(run_list)):

        run_i   = run_list[i]
        to_fill = days - len(run_i)

        if to_fill:

            tail        = full(to_fill, run_i[-1])
            run_list[i] = concatenate((run_i, tail))


def v_percentile(x: array, p: float):
    
    lim = len(x[0])

    y = [
        percentile([ x_[i] for x_ in x ], p)
        for i in range(lim)
    ]

    return y


def print_header(title):

    print(f"\n{title}\n\n-----\n")
    
    for k, v in PARAMS.items():

        print(f"{k + ':':<32}{v}")

    print("\n")


def fig_1():

    title = "p50 equity curve, tradeday 50k vs personal 2k, no withdrawals, 10k runs"

    PARAMS["runs"]                      = 10_000
    mu, _, sigma, _                     = get_rr_metric("0.6:2", "0.4:2", 5)
    PARAMS["mu"]                        = mu
    PARAMS["sigma"]                     = sigma
    PARAMS["withdrawal_frequency_days"] = 0
    fig                                 = go.Figure()

    res_tradeday_50k    = sim_runs(**PARAMS)
    tradeday_runs       = res_tradeday_50k["runs"]

    PARAMS["mode"]      = "personal_2k"

    res_personal_2k     = sim_runs(**PARAMS)
    personal_runs       = res_personal_2k["runs"]

    pad_runs(tradeday_runs, PARAMS["days"])
    pad_runs(personal_runs, PARAMS["days"])

    median_tradeday_run = v_percentile(tradeday_runs, 50)
    median_personal_run = v_percentile(personal_runs, 50)

    traces = [ 
        ( median_tradeday_run, "p50 tradeday", "#FF0000" ),
        ( median_personal_run, "p50 personal", "#0000FF")
    ]
    x       = [ i for i in range(PARAMS["days"]) ]

    for trace in traces:
    
        fig.add_trace(
            go.Scattergl(
                {
                    "x":        x,
                    "y":        trace[0],
                    "name":     trace[1],
                    "marker":   { "color": trace[2] }
                }
            )
        )

    del PARAMS["mu"]
    del PARAMS["sigma"]
    del PARAMS["discretionary_buffer"]
    del PARAMS["withdrawal_frequency_dollars"]
    del PARAMS["withdrawal_amount_dollars"]
    del PARAMS["show_runs"]
    del PARAMS["mode"]

    PARAMS["reward"]    = "60% +2pts"
    PARAMS["risk"]      = "40% -2pts"

    print_header(title)

    fig.update_layout(title_text = title)

    fig.show()


def test_fig():

    res = sim_runs(**PARAMS)

    res["fig"].show()

    PARAMS["reward"]    = PARAMS["mu"]
    PARAMS["risk"]      = PARAMS["sigma"]

    del PARAMS["mu"]
    del PARAMS["sigma"]

    print_header("test")

    pass


FIGS = {
    "test_fig": test_fig,
    "fig_1":    fig_1
}


if __name__ == "__main__":

    t0 = time()

    FIGS[argv[1]]()

    print(f"{time() - t0:0.2f}s\n")