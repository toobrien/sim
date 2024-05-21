from    json                    import  loads
import  plotly.graph_objects    as      go
from    plotly.subplots         import  make_subplots
from    math                    import  ceil, e, log, sqrt
from    numpy                   import  array, cumsum, mean, percentile
from    numpy.random            import  normal
from    sys                     import  argv
from    time                    import  time
from    typing                  import  List, Tuple


# python prop_2.py '{ "risk": "0.60:2", "reward": "0.40:2", "leverage": 1.0, "runs": 100, "discretionary_buffer": 1000, "performance_post_costs": 1, "trades_per_day": 5, "withdrawal_frequency_days": 21, "withdrawal_amount_dollars": 2000, "run_years": 1, "eval": 1, "max_resets": 3, "show_dists": 0, "show_runs": 1, "mode": "tradeday_50k" }'
# python prop_2.py '{ "risk": "$100",   "reward": "$250",   "leverage": 1.0, "runs": 100, "discretionary_buffer": 1000, "performance_post_costs": 1, "trades_per_day": 5, "withdrawal_frequency_days": 21, "withdrawal_amount_dollars": 2000, "run_years": 1, "eval": 1, "max_resets": 3, "show_dists": 0, "show_runs": 1, "mode": "tradeday_50k" }'
# python prop_2.py '{ "risk": "0.0004", "reward": "0.01",   "leverage": 1.0, "runs": 100, "discretionary_buffer": 1000, "performance_post_costs": 1, "trades_per_day": 5, "withdrawal_frequency_days": 21, "withdrawal_amount_dollars": 2000, "run_years": 1, "eval": 1, "max_resets": 3, "show_dists": 0, "show_runs": 1, "mode": "tradeday_50k" }'
# python prop_2.py '{ "risk": "1x",     "reward": "0.37x",  "leverage": 1.0, "runs": 100, "discretionary_buffer": 1000, "performance_post_costs": 1, "trades_per_day": 5, "withdrawal_frequency_days": 21, "withdrawal_amount_dollars": 2000, "run_years": 1, "eval": 1, "max_resets": 3, "show_dists": 0, "show_runs": 1, "mode": "tradeday_50k" }'


MODES = {
    "personal_2k": {
        "account_size":         2_000,
        "drawdown":             2_000,
        "profit_target":        0,
        "required_buffer":      0,
        "profit_share_rate":    0,
        "profit_share_limit":   0,
        "min_trading_days":     0,
        "activation_fee":       0,
        "pa_monthly_fee":       0,
        "eval":                 False,
        "eval_profit_target":   0,
        "eval_drawdown":        0,
        "eval_min_days":        0,
        "eval_monthly_fee":     0,
        "eval_reset_fee":       0
    },
    "tradeday_50k": {
        # ignored tradeday rules:
        #   - no eval day greater than 30% of profit
        "account_size":         50_000,
        "profit_target":        0,
        "drawdown":             2_000,
        "required_buffer":      0,
        "profit_share_rate":    0.10,
        "profit_share_limit":   10_000,
        "min_trading_days":     0,
        "activation_fee":       139,
        "pa_monthly_fee":       135,
        "eval":                 True,
        "eval_profit_target":   2_500,
        "eval_drawdown":        2_000,
        "eval_min_days":        7,
        "eval_monthly_fee":     132,
        "eval_reset_fee":       99
    },
    "apex_full_rithmic_50k": {
        # ignored apex rules:
        #   - min/max payout for the first three months
        "account_size":         50_000,
        "profit_target":        2_500,
        "drawdown":             2_500,
        "required_buffer":      100,
        "profit_share_rate":    0.10,
        "profit_share_limit":   25_000,
        "min_trading_days":     10,
        "activation_fee":       0,
        "pa_monthly_fee":       85,
        "eval":                 True,
        "eval_profit_target":   3_000,
        "eval_drawdown":        2_500,
        "eval_min_days":        1,
        "eval_monthly_fee":     35,
        "eval_reset_fee":       80
    },
    "topstep_live_50k": {
        # ignored topstep rules: 
        #   - 50% balance withdrawal maximum, 5 winning
        #   - 5 green days per withdrawal
        "account_size":         50_000,
        "profit_target":        3_000,
        "drawdown":             2_000,
        "required_buffer":      0,
        "profit_share_rate":    0.10,
        "profit_share_limit":   25_000,
        "min_trading_days":     5,
        "activation_fee":       149,
        "pa_monthly_fee":       135,
        "eval":                 True,
        "eval_profit_target":   3_000,
        "eval_drawdown":        2_000,
        "eval_min_days":        2,
        "eval_monthly_fee":     49,
        "eval_reset_fee":       49
    }
}


DPY                         = 256
DPM                         = 21
T_BILL                      = log(1 + 0.05)
T_BILL_DAILY                = T_BILL / DPY
ES                          = 5_000 * 50
ES_MU                       = 0.0721
ES_SIGMA                    = 0.1961
ES_MU_DAILY                 = ES_MU / DPY
ES_SIGMA_DAILY              = ES_SIGMA * sqrt(1 / DPY)
ES_SHARPE                   = (ES_MU_DAILY - T_BILL_DAILY) / ES_SIGMA_DAILY * sqrt(DPY)
ES_SHARPE_0                 = ES_MU_DAILY / ES_SIGMA_DAILY * sqrt(DPY)


def sim_eval(
    mu:                     float,
    sigma:                  float,
    performance_post_costs: int,
    profit_target:          float,
    drawdown:               float,
    max_resets:             int,
    min_days:               int,
    monthly_fees:           int,
    reset_fee:              int,
    transaction_costs:      float,
    trades_per_day:         int
):

    count                       = 1
    fees                        = monthly_fees
    pnl                         = 0
    days                        = 0
    transaction_costs_per_day   = transaction_costs * trades_per_day if not performance_post_costs else 0

    while(True):

        pnl += ES * (e**normal(loc = mu, scale = sigma) - 1) - transaction_costs_per_day

        if pnl >= profit_target and days >= min_days:

            break

        elif pnl <= -drawdown:

            days    = 0
            pnl     = 0
            count   = count + 1

            if max_resets > 0:

                max_resets -= 1
                fees       += reset_fee

        days += 1

        if days % 21 == 0:

            fees += monthly_fees

    return count, fees


def sim_runs(
    runs:                           int,
    days:                           int,
    mu:                             float,
    sigma:                          float,
    discretionary_buffer:           float,
    max_resets:                     int,
    leverage:                       float,
    performance_post_costs:         int,
    trades_per_day:                 int,
    withdrawal_frequency_days:      int,
    withdrawal_amount_dollars:      float,
    transaction_costs_per_trade:    float,
    show_runs:                      bool,
    mode:                           str
) -> List[Tuple]:

    profit_target           = MODES[mode]["profit_target"]
    drawdown                = MODES[mode]["drawdown"]
    required_buffer         = MODES[mode]["required_buffer"]
    min_trading_days        = MODES[mode]["min_trading_days"]
    activation_fee          = MODES[mode]["activation_fee"]
    pa_monthly_fee          = MODES[mode]["pa_monthly_fee"]
    profit_share_rate       = MODES[mode]["profit_share_rate"]
    profit_share_limit      = MODES[mode]["profit_share_limit"]
    eval_profit_target      = MODES[mode]["eval_profit_target"]
    eval_drawdown           = MODES[mode]["eval_drawdown"]
    eval_min_days           = MODES[mode]["eval_min_days"]
    eval_monthly_fee        = MODES[mode]["eval_monthly_fee"]
    eval_reset_fee          = MODES[mode]["eval_reset_fee"]

    fig                 = make_subplots(rows = 1, cols = 2, column_widths = [ 0.85, 0.15 ], horizontal_spacing = 0.05)
    failed              = 0
    hit                 = 0
    total_withdrawals   = 0
    eval_counts         = []
    eval_fees           = []
    raw_returns         = []
    ending_equities     = []
    prop_fees           = []
    transaction_costs   = []
    withdrawals         = []
    profits_shared      = []
    run_days            = []
    run_list            = []

    fig.update_layout(title_text = mode)

    for i in range(runs):

        num_evals, eval_costs   = sim_eval(
                                    mu,
                                    sigma,
                                    performance_post_costs,
                                    eval_profit_target,
                                    eval_drawdown,
                                    max_resets,
                                    eval_min_days,
                                    eval_monthly_fee,
                                    eval_reset_fee,
                                    transaction_costs_per_trade,
                                    trades_per_day
                                ) if eval else ( 0, 0 )
        total_prop_fees         = activation_fee
        total_transaction_costs = 0
        run                     = array([ ES * (e**i - 1) for i in (leverage * cumsum(normal(loc = mu, scale = sigma, size = days))) ])
        costs                   = [ (transaction_costs_per_trade * trades_per_day) * i for i in range(1, len(run) + 1) ]
        run                     = run - costs if not performance_post_costs else run
        trailing_drawdown       = [ max(min(max(run[:i + 1]) - drawdown, required_buffer), -drawdown) for i in range(len(run)) ] if "personal" not in mode else [ -drawdown for _ in range(len(run))]
        running_withdrawals     = [ 0 for _ in range(len(trailing_drawdown)) ]
        profit_share            = 0
        withdrawn               = 0
        blown                   = False
        pt_hit                  = False

        for j in range(len(run)):

            equity  = run[j]
            trail   = trailing_drawdown[j]
            
            if equity <= trail:

                blown                   =   True
                failed                  +=  1
                run                     =   run[0:j + 1]
                run[-1]                 =   trail
                trailing_drawdown       =   trailing_drawdown[0:j + 1]
                running_withdrawals[j]  =   withdrawn

                break

            elif equity >= profit_target and \
                 equity - withdrawal_amount_dollars >= max(required_buffer, discretionary_buffer) and \
                 j >= min_trading_days:

                pt_hit = True

                if withdrawal_frequency_days and j % withdrawal_frequency_days == 0:

                    total_withdrawals   += 1
                    withdrawn           += withdrawal_amount_dollars
                    run[j + 1:]         -= withdrawal_amount_dollars

            running_withdrawals[j] = withdrawn

        if pt_hit:

            hit += 1

        if show_runs:

            fig.add_trace(
                go.Scattergl(
                    {
                        "x":        [ i for i in range(len(run)) ],
                        "y":        run,
                        "text":     [ f"trailing drawdown: {trailing_drawdown[i]:0.2f}<br>withdrawn: ${running_withdrawals[i]:0.2f}" for i in range(len(trailing_drawdown)) ],
                        "marker":   { "color": "#FF0000" if blown else "#00FF00" if pt_hit else "#0000FF" },
                        "name":     f"run {i}"
                    }
                ),
                row = 1,
                col = 1
            )
        
        if withdrawn > profit_share_limit and "personal" not in mode:

            profit_share    =   (withdrawn - profit_share_limit) * profit_share_rate
            withdrawn       -=  profit_share

        days_survived           = len(run)
        months                  = ceil(days_survived / DPM)
        total_prop_fees         = total_prop_fees + (months * pa_monthly_fee) + eval_costs + required_buffer
        total_transaction_costs = (transaction_costs_per_trade * trades_per_day * days_survived)
        raw_return              = run[-1]
        ending_equity           = max(run[-1], 0) if "personal" not in mode else raw_return

        eval_counts.append(num_evals)
        eval_fees.append(eval_costs)
        run_days.append(days_survived)
        raw_returns.append(raw_return)
        ending_equities.append(ending_equity)
        prop_fees.append(total_prop_fees if "personal" not in mode else 0)
        transaction_costs.append(total_transaction_costs)
        profits_shared.append(profit_share)
        withdrawals.append(withdrawn)
        run_list.append(run)

    if show_runs:

        fig.add_trace(go.Histogram(y = [ i for i in raw_returns if i > 0 ], marker_color = "#00FF00"), row = 1, col = 2)
        fig.add_trace(go.Histogram(y = [ i for i in raw_returns if i <= 0 ], marker_color = "#FF0000"), row = 1, col = 2)

    failure_rate        = failed / runs
    hit_rate            = hit / runs
    withdrawal_rate     = total_withdrawals / runs

    return {
        "failure_rate":         failure_rate, 
        "hit_rate":             hit_rate, 
        "withdrawal_rate":      withdrawal_rate,
        "eval_counts":          array(eval_counts),
        "eval_fees":            array(eval_fees),
        "raw_returns":          array(raw_returns),
        "ending_equities":      array(ending_equities),
        "prop_fees":            array(prop_fees), 
        "transaction_costs":    array(transaction_costs), 
        "run_days":             array(run_days), 
        "profits_shared":       array(profits_shared), 
        "withdrawals":          array(withdrawals),
        "runs":                 run_list,
        "fig":                  fig
    }


def get_dist_figure(
    raw_returns,
    withdrawals,
    run_days
):

    fig                 = make_subplots(rows = 3, cols = 2, horizontal_spacing = 0.05)
    raw_returns_bins    = 100
    withdrawals_bins    = 100 #ceil((max(withdrawals) - min(withdrawals)) / withdrawal_amount_dollars)
    run_days_bins       = int(max(run_days) - min(run_days))

    traces = [
        ( raw_returns, "ending equity (hist)", raw_returns_bins, False, "#03396c", "", 1, 1 ),
        ( raw_returns, "ending equity (cdf)", raw_returns_bins, True, "#03396c", "probability density", 1, 2 ),
        ( withdrawals, "amount withdrawn (hist)", withdrawals_bins, False, "#005b96", "", 2, 1 ),
        ( withdrawals, "amount withdrawn (cdf)", withdrawals_bins * 10, True, "#005b96", "probability density", 2, 2 ),
        ( run_days,  "days survived (hist)", run_days_bins, False, "#6497b1", "", 3, 1 ),
        ( run_days,  "days survived (cdf)", run_days_bins, True, "#6497b1", "probability density", 3, 2 ),
    ]

    for trace in traces:

        fig.add_trace(
            go.Histogram(
                x                   = trace[0],
                name                = trace[1],
                nbinsx              = trace[2],
                cumulative_enabled  = trace[3],
                marker_color        = trace[4],
                histnorm            = trace[5]

            ),
            row = trace[6],
            col = trace[7]
        )

    return fig


def format_stats(name: str, x: List):

    return_x = x / ES * 100
    dollar_x = x
    
    return_mean = mean(return_x)
    dollar_mean = mean(dollar_x)

    percentiles = [ 10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 99, 100 ]

    return_percentiles = percentile(return_x, percentiles)
    dollar_percentiles = percentile(dollar_x, percentiles)

    return_line = f"{name + ' (%):':<32}{return_mean:<10.2f}|    "
    dollar_line = f"{name + ' ($):':<32}{dollar_mean:<10.2f}|    "

    for i in range(len(percentiles)):

        return_line += f"{return_percentiles[i]:<10.2f}"
        dollar_line += f"{dollar_percentiles[i]:<10.2f}"

    return return_line, dollar_line


def get_metric(x, es_x):

    if "$" in x:

        x_bp = log(1 + float(x[1:]) / ES)

    elif "x" in x:

        # ES multiplier

        x_bp = float(x[:-1]) * es_x
    
    elif "p" in x:

        x_bp = log(1 + 50 * float(x[0:-1]) / ES)

    else:

        # basis points

        x_bp = float(x)

    x_dollars = ES * (e**x_bp - 1)

    return x_bp, x_dollars


def get_rr_metric(reward, risk, trades_per_day):

    reward_parts    = reward.split(":")
    risk_parts      = risk.split(":")

    reward_probability  = float(reward_parts[0])
    reward_points       = float(reward_parts[1])
    risk_probability    = float(risk_parts[0])
    risk_points         = float(risk_parts[1])

    mu_points   = (reward_probability * reward_points - risk_probability * risk_points)
    mu_dollars  = mu_points * trades_per_day * 50
    mu_bp       = log(1 + mu_dollars / ES)

    sigma_points    = sqrt((reward_points - mu_points)**2 * reward_probability + (-risk_points - mu_points)**2 * risk_probability) * sqrt(trades_per_day)
    sigma_dollars   = sigma_points * 50
    sigma_bp        = log(1 + sigma_dollars / ES)

    return mu_bp, mu_dollars, sigma_bp, sigma_dollars


if __name__ == "__main__":

    print()

    t0                          = time()
    args                        = loads(argv[1])
    reward                      = args["reward"]
    risk                        = args["risk"]
    leverage                    = args["leverage"]
    runs                        = args["runs"]
    run_years                   = args["run_years"]
    performance_post_costs      = args["performance_post_costs"]
    trades_per_day              = args["trades_per_day"]
    withdrawal_frequency_days   = args["withdrawal_frequency_days"]
    withdrawal_amount_dollars   = args["withdrawal_amount_dollars"]
    discretionary_buffer        = args["discretionary_buffer"]
    eval                        = args["eval"]
    max_resets                  = args["max_resets"]
    show_dists                  = args["show_dists"]
    show_runs                   = args["show_runs"]
    mode                        = args["mode"]
    commissions_all_in          = 4.0  if leverage >= 1.0 else 1.2
    spread                      = 12.5 if leverage >= 1.0 else 1.25
    transaction_costs           = commissions_all_in + spread

    print(f"t_bill:                         {T_BILL:0.4f}")
    print(f"t_bill_daily:                   {T_BILL_DAILY:0.4f}")
    print(f"es_price:                       {ES / 50:0.2f}")
    print(f"es_average_annual:              {ES_MU:0.4f}")
    print(f"es_avg_daily:                   {ES_MU_DAILY:0.4f}\t${ES * (e**ES_MU_DAILY - 1):0.2f}")
    print(f"es_stdev_annual:                {ES_SIGMA:0.4f}")
    print(f"es_stdev_daily:                 {ES_SIGMA_DAILY:0.4f}\t${ES * (e**ES_SIGMA_DAILY - 1):0.2f}")
    print(f"es_sharpe (rfr = {T_BILL*100:0.2f}):         {ES_SHARPE:0.2f}")
    print(f"es_sharpe (rfr = 0):            {ES_SHARPE_0:0.2f}")
    print(f"profit_target:                  ${MODES[mode]['profit_target']}")
    print(f"drawdown:                       ${-MODES[mode]['drawdown']}")
    print(f"commissions (rt):               {commissions_all_in:0.2f}")
    print(f"spread:                         ${spread:0.2f}")
    
    print("\n-----\n")
    
    for k, v in MODES[mode].items():

        print(f"{k + ':':32}{v}")

    print("\n-----\n")

    if withdrawal_frequency_days:
    
        print(f"withdrawal_frequency_days:      {withdrawal_frequency_days}")
        print(f"withdrawal_amount_dollars:      ${withdrawal_amount_dollars:0.2f}")
        print(f"required_buffer:                ${MODES[mode]['required_buffer']}")
        print(f"discretionary_buffer:           ${discretionary_buffer}")
        print(f"profit_share_limit:             ${MODES[mode]['profit_share_limit']}")
        print(f"profit_share_rate:              {MODES[mode]['profit_share_rate'] * 100:0.2f}%")
        print("\n-----\n")

    if ":" not in reward:

        mu_bp, mu_dollars       = get_metric(reward, ES_MU_DAILY)
        sigma_bp, sigma_dollars = get_metric(risk, ES_SIGMA_DAILY)
    
    else:

        mu_bp, mu_dollars, sigma_bp, sigma_dollars = get_rr_metric(reward, risk, trades_per_day)

        reward_parts = reward.split(":")
        risk_parts   = risk.split(":")
        reward       = f"{int(float(reward_parts[0]) * 100)}% +{reward_parts[1]}p"
        risk         = f"{int(float(risk_parts[0]) * 100)}% -{risk_parts[1]}p"

    sharpe                  = (mu_bp - T_BILL_DAILY) / sigma_bp * sqrt(DPY)
    sharpe_0                = mu_bp / sigma_bp * sqrt(DPY)

    print(f"daily reward:                   {reward}\t{mu_bp * 100:0.2f}%\tw/ leverage: ${mu_dollars * leverage:0.2f}\t{mu_bp * 100 * leverage:0.4f}%")
    print(f"daily risk:                     {risk}\t{sigma_bp * 100:0.2f}%\tw/ leverage: ${sigma_dollars * leverage:0.2f}\t{sigma_bp * 100 * leverage:0.4f}%")
    print(f"leverage:                       {leverage:0.2f}x")
    print(f"runs:                           {runs}")
    print(f"years:                          {run_years}")
    print(f"trades_per_day:                 {trades_per_day}\n")
    print(f"sharpe (rfr = {T_BILL * 100:0.2f}%):           {sharpe:0.2f}")
    print(f"sharpe (rfr = 0):               {sharpe_0:0.2f}\t({sharpe_0 / ES_SHARPE_0:0.2f}x ES risk-adjusted return)")

    print("\n-----\n")
    
    res = sim_runs(
        runs, 
        run_years * DPY,
        mu_bp, 
        sigma_bp,
        discretionary_buffer,
        max_resets,
        leverage,
        performance_post_costs,
        trades_per_day, 
        withdrawal_frequency_days,
        withdrawal_amount_dollars,
        transaction_costs,
        show_runs,
        mode
    )

    evals_per_account       = mean(res["eval_counts"])
    average_eval_costs      = mean(res["eval_fees"])
    average_days_survived   = int(ceil(mean(res["run_days"])))

    print(f"mode:                           {mode}")
    print(f"evals per account:              {evals_per_account:0.2f}") if eval else None
    print(f"survival rate:                  {(1 - res['failure_rate']) * 100:0.2f}%")
    print(f"target hit:                     {res['hit_rate'] * 100:0.2f}%") if "personal" not in mode else None
    print(f"withdrawals per account:        {res['withdrawal_rate']:0.2f}")
    print(f"average days survived:          {average_days_survived}")

    total_returns       = res['ending_equities'] + res['transaction_costs'] + res['profits_shared'] + res['withdrawals']
    return_after_costs  = total_returns - res['transaction_costs'] - res['profits_shared'] - res['prop_fees']

    print("\n-----\n")

    print(f"{'':32}{'mean':<15}{'10%':<10}{'20%':<10}{'30%':<10}{'40%':<10}{'50%':<10}{'60%':<10}{'70%':<10}{'80%':<10}{'90%':<10}{'95%':<10}{'99%':<10}{'100%':<10}\n")
    
    total_return_lines          = format_stats("total return", total_returns)
    eval_fees_lines             = format_stats("eval_fees", res['eval_fees']) if eval else None
    prop_fees_lines             = format_stats("prop fees (inc. eval)" if eval else "prop fees", res['prop_fees']) if "personal" not in mode else None
    transaction_costs_lines     = format_stats("transaction costs", res['transaction_costs'])
    profit_share_lines          = format_stats("profit share", res['profits_shared']) if "personal" not in mode else None
    return_after_costs_lines    = format_stats("return after costs", return_after_costs)
    ending_equity_lines         = format_stats("ending equity", res['ending_equities'])
    withdrawn_lines             = format_stats("amount withdrawn", res['withdrawals'])

    print(total_return_lines[0])
    print(eval_fees_lines[0])               if eval else None
    print(prop_fees_lines[0])               if "personal" not in mode else None
    print(transaction_costs_lines[0])
    print(profit_share_lines[0])            if (withdrawal_frequency_days and "personal" not in mode) else None

    print("\n")

    print(return_after_costs_lines[0])
    print(ending_equity_lines[0])           if withdrawal_frequency_days else None
    print(withdrawn_lines[0])               if withdrawal_frequency_days else None

    print("\n-----\n")

    print(total_return_lines[1])
    print(eval_fees_lines[1])               if eval else None
    print(prop_fees_lines[1])               if "personal" not in mode else None
    print(transaction_costs_lines[1])
    print(profit_share_lines[1])            if (withdrawal_frequency_days and "personal" not in mode) else None

    print("\n")

    print(return_after_costs_lines[1])
    print(ending_equity_lines[1])           if withdrawal_frequency_days else None
    print(withdrawn_lines[1])               if withdrawal_frequency_days else None

    print("\n")

    if show_runs:
    
        res['fig'].show()

    if show_dists:
        
        fig_dists = get_dist_figure(res['ending_equities'], res['withdrawals'], res['run_days'])

        fig_dists.show()

    print(f"elapsed: {time() - t0:0.1f}s")