from    numpy                   import  mean, median, percentile, std
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


def print_header(title, risk, reward):

    print(f"\n{title}\n-----\n")
    print(f"{'risk:':<32}{risk}")
    print(f"{'reward:':<32}{reward}")

    for k, v in PARAMS.items():

        print(f"{k + ':':<32}{v}")

    print("\n")


def fig_1():

    PARAMS["runs"]                      = 10_000
    mu, _, sigma, _                     = get_rr_metric("0.6:2", "0.4:2", 5)
    PARAMS["mu"]                        = mu
    PARAMS["sigma"]                     = sigma
    PARAMS["withdrawal_frequency_days"] = 0
    fig                                 = go.Figure()

    res_tradeday_50k    = sim_runs(**PARAMS)
    tradeday_runs       = res_tradeday_50k["runs"]

    PARAMS["mode"] = "personal_2k"

    res_personal_2k     = sim_runs(**PARAMS)
    personal_runs       = res_personal_2k["runs"]

    pass


def test_fig():

    res = sim_runs(**PARAMS)

    res["fig"].show()

    del PARAMS["mu"]
    del PARAMS["sigma"]

    print_header("test", "0.0004", "0.0009")

    pass


FIGS = {
    "test_fig": test_fig,
    "fig_1":    fig_1
}


if __name__ == "__main__":

    t0 = time()

    FIGS[argv[1]]()

    print(f"{time() - t0:0.2f}s\n")