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
    "discretionary_buffer":         1000,
    "max_resets":                   3,
    "leverage":                     1.0,
    "trades_per_day":               5,
    "withdrawal_frequency_days":    21,
    "withdrawal_amount_dollars":    2000,
    "transaction_costs_per_trade":  16.5,
    "show_runs":                    1,
    "mode":                         "tradeday_50k"
}


def fig_1():

    res = sim_runs(**PARAMS)

    res["fig"].show()

    pass

if __name__ == "__main__":

    t0 = time()

    if argv[1] == "fig_1":

        fig_1()

    print(f"{time() - t0:0.2f}s")