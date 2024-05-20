from    numpy                   import  array, concatenate, full, mean, median, percentile
import  plotly.graph_objects    as      go
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
                    "max_resets":                   2,
                    "leverage":                     1.0,
                    "performance_post_costs":       0,
                    "trades_per_day":               5,
                    "withdrawal_frequency_days":    0,
                    "withdrawal_amount_dollars":    0,
                    "transaction_costs_per_trade":  16.5,
                    "show_runs":                    0,
                    "mode":                         "tradeday_50k"
                }


def get_performance_profiles():

    mu_naive, _, sigma_naive, _         = get_rr_metric("0.6:2", "0.4:2", PARAMS["trades_per_day"])
    mu_novice, sigma_novice             = get_metric("$9.74", 0)[0], get_metric("$400", 0)[0]
    mu_experienced, sigma_experienced   = get_metric("$25.49", 0)[0], get_metric("$400", 0)[0]

    profiles = [
        ( mu_novice, sigma_novice, 1, "novice" ),
        ( mu_experienced, sigma_experienced, 1, "experienced" ),
        ( mu_naive, sigma_naive, 0, "naive" )
    ]

    return profiles


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


def fig_1():

    text = [
        "median equity curve by day",
        "tradeday 50k vs personal 2k",
        "naive:         sharpe = 7.30, reward = 60% +2pt, risk = 40% -2pt",
        "novice:        sharpe = 0.39, reward = $9.74,    risk = $400,",
        "experienced:   sharpe = 1.02, reward = $25.49,   risk = $400",
        "5 trades per day",
        "no withdrawals",
        "2 resets maximum"
        "1 year",
        f"{PARAMS['runs']} runs"
    ]

    for line in text:

        print(line)

    for profile in get_performance_profiles():

        fig_1_plot(*profile)


def fig_1_plot(mu: float, sigma: float, performance_post_costs: int, profile: str):

    PARAMS["mu"]                        = mu
    PARAMS["sigma"]                     = sigma
    PARAMS["performance_post_costs"]    = performance_post_costs
    fig                                 = go.Figure()

    PARAMS["mode"]      = "tradeday_50k"
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
        ( median_tradeday_run, f"median tradeday {profile}", FUNDED_COLOR   ),
        ( median_personal_run, f"median personal {profile}", PERSONAL_COLOR )
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

    fig.show()


def fig_2():

    text = [
            "percentiles, returns (total and after fees)"
            "tradeday 50k vs personal 2k",
            "60% win rate, 2pt risk and reward, 5 trades daily",
            "0 withdrawals",
            "1 year",
            "2 resets, maximum",
            f"{PARAMS['runs']} runs\n"
        ]
    
    for line in text:

        print(line)

    for profile in get_performance_profiles():

        fig_2_plot(*profile)


def fig_2_plot(mu: float, sigma: float, performance_post_costs: int, profile: str):

    PARAMS["mu"]                        = mu
    PARAMS["sigma"]                     = sigma
    PARAMS["performance_post_costs"]    = performance_post_costs
    fig                                 = go.Figure()

    PARAMS["mode"]  = "tradeday_50k"
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
        ( funded_total_y,   f"{profile} tradeday total returns",       FUNDED_COLOR,   0.3 ),
        ( funded_after_y,   f"{profile} tradeday after cost returns",  FUNDED_COLOR,   1.0 ),
        ( personal_total_y, f"{profile} personal total returns",       PERSONAL_COLOR, 0.3 ),
        ( personal_after_y, f"{profile} personal after cost returns",  PERSONAL_COLOR, 1.0 )
    ]

    for trace in traces:

        fig.add_trace(
            go.Scatter(
                {
                    "x":        x,
                    "y":        trace[0],
                    "name":     trace[1],
                    "marker":   { "color": trace[2] },
                    "opacity":  trace[3]
                }
            )
        )

    fig.show()


def fig_3():

    fig = go.Figure()

    traces = [ 
            #( "0.60:2", "0.40:2", "naive" ), 
            #( "0.5055:2", "0.4945:2", "novice" ),
            #( "0.51425:2", "0.48575:2", "experienced" )
            ( 0.0004,       0.000876,   "naive", 0 ),
            #( 0.000024375,  0.001,      "novice", 1 ),          # $250, $6.09
            #( 0.000064,     0.001,      "experienced", 1),      # $250, $16
            ( 0.000038976,  0.001599,   "novice", 1 ),          #  $400, $9.74
            ( 0.00010194,   0.001599,   "experienced", 1 ),      #  $400, $25.49
        ]
    
        #sigma = 0.001,      $250  mu = 0.000024375, $6.09
        #sigma = 0.001599,   $400  mu = 0.000038976, $9.74
    

    counts                  = {}
    PARAMS["runs"]          = 10_000
    
    x = [ 10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 99, 100 ]

    results = {}

    for trace in traces:

        PARAMS["mu"]                        = trace[0]
        PARAMS["sigma"]                     = trace[1]
        PARAMS["performance_post_costs"]    = trace[3]

        runs                = sim_runs(**PARAMS)
        eval_fees           = runs["eval_fees"]
        counts[trace[2]]    = runs["eval_counts"]
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

    text = [
        "\nevals costs per pass",
        "tradeday 50k",
        "5 trades daily",
        "2 resets, maximum"
        f"{PARAMS['runs']} runs",
        "\n-----\n",
        f"{'':20}{'sharpe':12}{'win rate':12}{'risk':12}{'reward':12}\n",
        f"{'naive':20}{7.30:<12.2f}{'60%':12}{'2 points':12}{'2 points':12}",
        f"{'novice (<2yr)':20}{0.39:<12.2f}{'50.55%':12}{'$400':12}{'$9.74':12}",
        f"{'experienced (>2yr)':20}{1.02:<12.2f}{'51.425%':12}{'$400':12}{'$25.49':12}",
        "\n-----\n",
        f"{'':20}{'mean':12}{'median':12}\n",
        f"{'naive':20}${mean(results['naive']):<11.2f}${median(results['naive']):<11.2f}",
        f"{'novice':20}${mean(results['novice']):<11.2f}${median(results['novice']):<11.2f}",
        f"{'experienced':20}${mean(results['experienced']):<11.2f}${median(results['experienced']):<11.2f}\n"
        "\n-----\n",
        "evals per pass\n",
        f"{'':20}{'mean':12}{'median':12}",
        f"{'naive':20}{mean(counts['naive']):<12.1f}{median(counts['naive']):<12.1f}",
        f"{'novice':20}{mean(counts['novice']):<12.1f}{median(counts['novice']):<12.1f}",
        f"{'experienced':20}{mean(counts['experienced']):<12.1f}{median(counts['experienced']):<12.1f}\n"
    ]

    for line in text:

        print(line)

    fig.show()


FIGS = {
    "fig_1":    fig_1,
    "fig_2":    fig_2,
    "fig_3":    fig_3
}


if __name__ == "__main__":

    t0 = time()

    PARAMS["runs"] = int(argv[2])

    FIGS[argv[1]]()

    print(f"{time() - t0:0.2f}s\n")