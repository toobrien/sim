from    numpy                   import  array, concatenate, full, mean, median, percentile, std
import  plotly.graph_objects    as      go
from    plotly.subplots         import  make_subplots
from    prop_2                  import  sim_runs, get_metric, get_rr_metric
from    sys                     import  argv
from    time                    import  time


PERSONAL_COLOR  = "#0000FF"
FUNDED_COLOR    = "#FF00FF"
PARAMS          = {
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


def get_total_and_after_cost_returns(res):

    total_returns       = res['ending_equities'] + res['transaction_costs'] + res['profits_shared'] + res['withdrawals']
    return_after_costs  = total_returns - res['transaction_costs'] - res['profits_shared'] - res['prop_fees']

    return total_returns, return_after_costs


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

    title = "p50 equity curve by day, tradeday 50k vs personal 2k, 60% +2pt, 40% -2pt, 5 trades daily, no withdrawals, 1 year, 10k runs"

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
        ( median_tradeday_run, "p50 tradeday", FUNDED_COLOR   ),
        ( median_personal_run, "p50 personal", PERSONAL_COLOR )
    ]
    
    x = [ i for i in range(PARAMS["days"]) ]

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
    del PARAMS["withdrawal_frequency_days"]
    del PARAMS["withdrawal_amount_dollars"]
    del PARAMS["show_runs"]
    del PARAMS["mode"]

    PARAMS["reward"]    = "60% +2pts"
    PARAMS["risk"]      = "40% -2pts"

    print_header(title)

    fig.update_layout(title_text = title)

    fig.show()


def fig_2():

    title = "percentiles, returns (total and after fees), tradeday 50k vs personal 2k, 60% +2pt, 40% -2pt, 5 trades daily, no withdrawals, 1 year, 10k runs"

    PARAMS["runs"]                      = 10_000
    mu, _, sigma, _                     = get_rr_metric("0.6:2", "0.4:2", 5)
    PARAMS["mu"]                        = mu
    PARAMS["sigma"]                     = sigma
    PARAMS["withdrawal_frequency_days"] = 0
    fig_total                           = go.Figure()
    fig_after                           = go.Figure()

    funded_runs     = sim_runs(**PARAMS)
    PARAMS["mode"]  = "personal_2k"
    personal_runs   = sim_runs(**PARAMS)

    funded_total_returns, funded_after_cost_returns     = get_total_and_after_cost_returns(funded_runs)
    personal_total_returns, personal_after_cost_returns = get_total_and_after_cost_returns(personal_runs)


    x = [ 10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 99, 100 ]
    
    funded_total_y      = [ percentile(funded_total_returns, x_) for x_ in x ]
    funded_after_y      = [ percentile(funded_after_cost_returns, x_) for x_ in x ]
    personal_total_y    = [ percentile(personal_total_returns, x_) for x_ in x ]
    personal_after_y    = [ percentile(personal_after_cost_returns, x_) for x_ in x ]

    traces = [
        ( funded_total_y,   "tradeday total returns",       fig_total, FUNDED_COLOR   ),
        ( personal_total_y, "personal total returns",       fig_total, PERSONAL_COLOR ),
        ( funded_after_y,   "tradeday after cost returns",  fig_after, FUNDED_COLOR   ),
        ( personal_after_y, "personal after cost returns",  fig_after, PERSONAL_COLOR )
    ]

    for trace in traces:

        fig = trace[2]

        fig.add_trace(
            go.Scatter(
                {
                    "x":        x,
                    "y":        trace[0],
                    "name":     trace[1],
                    "marker":   { "color": trace[3] }
                }
            )
        )

    del PARAMS["mu"]
    del PARAMS["sigma"]
    del PARAMS["discretionary_buffer"]
    del PARAMS["withdrawal_frequency_days"]
    del PARAMS["withdrawal_amount_dollars"]
    del PARAMS["show_runs"]
    del PARAMS["mode"]

    PARAMS["reward"]    = "60% +2pts"
    PARAMS["risk"]      = "40% -2pts"

    print_header(title)

    fig_total.show()
    fig_after.show()

    pass


def fig_3():

#sharpe 0.39 = 0.5055 +2, 0.4945 -2
#sharpe 1.02 = 0.51425 +2, 0.48575 -2

    fig = go.Figure()

    traces = [ 
            #( "0.60:2", "0.40:2", "naive" ), 
            #( "0.5055:2", "0.4945:2", "novice" ),
            #( "0.51425:2", "0.48575:2", "experienced" )
            ( 0.0004,       0.000876,   "naive" ),
            #( 0.000024375,  0.001,      "novice" ),          # $250 risk
            #( 0.000064,     0.001,      "experienced"),      # $250 risk
            ( 0.000038976,  0.001599,   "novice" ),          # $400 risk
            ( 0.00010194,   0.001599,   "experienced"),      # $400 risk
        ]
#sigma = 0.001,      $250  mu = 0.000024375, $6.09
#sigma = 0.001599,   $400  mu = 0.000038976, $9.74
    
    PARAMS["runs"]          = 100
    PARAMS["max_resets"]    = 0
    
    x = [ 10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 99, 100 ]

    results = {}

    for trace in traces:

        #mu, _, sigma, _     = get_rr_metric(trace[0], trace[1], 5)

        mu      = trace[0]
        sigma   = trace[1]

        PARAMS["mu"]        = mu
        PARAMS["sigma"]     = sigma

        runs                = sim_runs(**PARAMS)
        eval_fees           = runs["eval_fees"]
        results[trace[2]]   = eval_fees

        fig.add_trace(
            go.Scatter(
                {
                    "x":    x,
                    "y":    [ percentile(eval_fees, x_) for x_ in x ],
                    "name": trace[2]
                }
            )
        )
    
    title = [
                "evals costs per pass",
                "tradeday 50k",
                "5 trades daily",
                "no resets, 10k runs"
                "\n\n-----\n\n",
                "naive (sharpe 7.30):       60%         +2pt, 40%       -2pt",
                "novice (sharpe 0.39):      50.55%      +2pt, 49.45%    -2pt",
                "experienced (sharpe 1.02): 51.425%     +2pt, 48.575    -2pt",
                "\n\n-----\n\n",
                f"{'':20}{'mean':20}{'median':20}",
                f"{'naive':20}${mean(results['naive']):<19.2f}${median(results['naive']):<19.2f}",
                f"{'novice':20}${mean(results['novice']):<19.2f}${median(results['novice']):<19.2f}",
                f"{'experienced':20}${mean(results['experienced']):<19.2f}${median(results['experienced']):<19.2f}"
            ]

    for line in title:

        print(line)

    print()

    fig.show()


FIGS = {
    "fig_1":    fig_1,
    "fig_2":    fig_2,
    "fig_3":    fig_3
}


if __name__ == "__main__":

    t0 = time()

    FIGS[argv[1]]()

    print(f"{time() - t0:0.2f}s\n")