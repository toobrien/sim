from    json                    import  loads
import  plotly.graph_objects    as      go
from    plotly.subplots         import  make_subplots
from    math                    import  ceil, e, log, sqrt
from    numpy                   import  array, cumsum, mean, percentile
from    numpy.random            import  normal
from    sys                     import  argv
from    time                    import  time
from    typing                  import  List, Tuple


# python prop_2.py '{ "risk": "0.60:2", "reward": "0.40:2", "leverage": 1.0, "runs": 100, "trades_per_day": 5, "withdrawal_frequency_days": 21, "withdrawal_amount_dollars": 2000, "run_years": 1, "eval": 1, "max_resets": 3, "show_dists": 0, "show_runs": 1, "mode": "tradeday_50k" }'
# python prop_2.py '{ "risk": "$100",   "reward": "$250",   "leverage": 1.0, "runs": 100, "trades_per_day": 5, "withdrawal_frequency_days": 21, "withdrawal_amount_dollars": 2000, "run_years": 1, "eval": 1, "max_resets": 3, "show_dists": 0, "show_runs": 1, "mode": "tradeday_50k" }'
# python prop_2.py '{ "risk": "0.0004", "reward": "0.01",   "leverage": 1.0, "runs": 100, "trades_per_day": 5, "withdrawal_frequency_days": 21, "withdrawal_amount_dollars": 2000, "run_years": 1, "eval": 1, "max_resets": 3, "show_dists": 0, "show_runs": 1, "mode": "tradeday_50k" }'
# python prop_2.py '{ "risk": "1x",     "reward": "0.37x",  "leverage": 1.0, "runs": 100, "trades_per_day": 5, "withdrawal_frequency_days": 21, "withdrawal_amount_dollars": 2000, "run_years": 1, "eval": 1, "max_resets": 3, "show_dists": 0, "show_runs": 1, "mode": "tradeday_50k" }'


t0                          = time()
args                        = loads(argv[1])
reward                      = args["risk"]
risk                        = args["reward"]
leverage                    = args["leverage"]
runs                        = args["runs"]
trades_per_day              = args["trades_per_day"]
withdrawal_frequency_days   = args["withdrawal_frequency_days"]
withdrawal_amount_dollars   = args["withdrawal_amount_dollars"]
run_years                   = args["run_years"]
eval                        = args["eval"]
max_resets                  = args["max_resets"]
show_dists                  = args["show_dists"]
show_runs                   = args["show_runs"]
mode                        = args["mode"]


#               size    eval ($/mo)     eval (min days) pa ($/mo)   activation fee  trailing dd     eval target
# apex:         50,000  35              0               85          n/a             2,500           3,000
# tradeday:     50,000  85              7               135         140             2,000           2,500
# topstep:      50,000  50              ?               135         150             2,000           3,000


MODES = {
    "personal_2k": {
        "account_size":         2_000,
        "drawdown":             2_000,
        "profit_target":        2_500,
        "buffer":               0,
        "profit_share_rate":    0,
        "profit_share_limit":   0,
        "min_trading_days":     0,
        "activation_fee":       0,
        "pa_monthly_fee":       0,
        "eval":                 False,
        "eval_min_days":        0,
        "eval_monthly_fee":     0,
        "eval_reset_fee":       0
    },
    "tradeday_50k": {
        "account_size":         50_000,
        "drawdown":             2_000,
        "profit_target":        2_500,
        "buffer":               0,
        "profit_share_rate":    0.10,
        "profit_share_limit":   10_000,
        "min_trading_days":     10,
        "activation_fee":       139,
        "pa_monthly_fee":       135,
        "eval":                 True,
        "eval_min_days":        7,
        "eval_monthly_fee":     85,
        "eval_reset_fee":       99
    },
    "apex_50k": {
        "account_size":         50_000,
        "drawdown":             2_500,
        "profit_target":        3_000,
        "buffer":               100,
        "profit_share_rate":    0.10,
        "profit_share_limit":   25_000,
        "min_trading_days":     10,
        "activation_fee":       0,
        "pa_monthly_fee":       85,
        "eval":                 True,
        "eval_min_days":        0,
        "eval_monthly_fee":     35,
        "eval_reset_fee":       90
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
ACCOUNT_SIZE                = MODES[mode]["account_size"]
DRAWDOWN                    = MODES[mode]["drawdown"]
MINIMUM_TRADING_DAYS        = MODES[mode]["min_trading_days"]
PROFIT_TARGET               = MODES[mode]["profit_target"]
ACTIVATION_FEE              = 100
PA_MONTHLY_FEE              = 135
COMMISSIONS_ALL_IN          = 4.0  if leverage >= 1.0 else 1.2
SPREAD                      = 12.5 if leverage >= 1.0 else 1.25
TRANSACTION_COSTS           = COMMISSIONS_ALL_IN + SPREAD
BUFFER                      = MODES[mode]["buffer"]
PROFIT_SHARE_RATE           = MODES[mode]["profit_share_rate"]
PROFIT_SHARE_LIMIT          = MODES[mode]["profit_share_limit"]


def sim_eval(mu, sigma, max_resets, min_days, monthly_fees, reset_fee):

    count = 1
    fees  = monthly_fees
    pnl   = 0
    days  = 0

    while(True):

        pnl += ES * (e**normal(loc = mu, scale = sigma) - 1) - TRANSACTION_COSTS

        if pnl >= PROFIT_TARGET and days >= min_days:

            break

        elif pnl <= -DRAWDOWN:

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
    runs:                       int,
    days:                       int,
    mu:                         float,
    sigma:                      float,
    max_resets:                 int,
    leverage:                   float,
    trades_per_day:             int,
    withdrawal_frequency_days:  int,
    withdrawal_amount_dollars:  float,
    show_runs:                  bool
) -> List[Tuple]:

    eval_min_days       = MODES[mode]["eval_min_days"]
    eval_monthly_fee    = MODES[mode]["eval_monthly_fee"]
    eval_reset_fee      = MODES[mode]["eval_reset_fee"]

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

    fig.update_layout(title_text = mode)

    for _ in range(runs):

        num_evals, eval_costs   = sim_eval(mu, sigma, max_resets, eval_min_days, eval_monthly_fee, eval_reset_fee) if eval else ( 0, 0 )
        total_prop_fees         = ACTIVATION_FEE
        total_transaction_costs = 0
        run                     = array([ ES * (e**i - 1) for i in (leverage * cumsum(normal(loc = mu, scale = sigma, size = days))) ])
        costs                   = [ (TRANSACTION_COSTS * trades_per_day) * i for i in range(1, len(run) + 1) ]
        run                     = run - costs
        trailing_drawdown       = [ max(min(max(run[:i + 1]) - DRAWDOWN, 0), -DRAWDOWN) for i in range(len(run)) ] if "personal" not in mode else [ -DRAWDOWN for _ in range(len(run))]
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

            elif equity >= PROFIT_TARGET and \
                 equity - withdrawal_amount_dollars >= BUFFER and \
                 j >= MINIMUM_TRADING_DAYS:

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
                        "marker":   { "color": "#FF0000" if blown else "#00FF00" if equity >= PROFIT_TARGET else "#0000FF" }
                    }
                ),
                row = 1,
                col = 1
            )
        
        if withdrawn > PROFIT_SHARE_LIMIT and "personal" not in mode:

            profit_share    =   (withdrawn - PROFIT_SHARE_LIMIT) * PROFIT_SHARE_RATE
            withdrawn       -=  profit_share

        days_survived           = len(run)
        months                  = ceil(days_survived / DPM)
        total_prop_fees         = total_prop_fees + months * PA_MONTHLY_FEE + costs
        total_transaction_costs = (TRANSACTION_COSTS * trades_per_day * days_survived)
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

    if show_runs:

        fig.add_trace(go.Histogram(y = [ i for i in raw_returns if i > 0 ], marker_color = "#00FF00"), row = 1, col = 2)
        fig.add_trace(go.Histogram(y = [ i for i in raw_returns if i == trail ], marker_color = "#FF0000"), row = 1, col = 2)

    failure_rate        = failed / runs
    hit_rate            = hit / runs
    withdrawal_rate     = total_withdrawals / runs

    return (
        failure_rate, 
        hit_rate, 
        withdrawal_rate,
        array(eval_counts),
        array(eval_fees),
        array(raw_returns),
        array(ending_equities),
        array(prop_fees), 
        array(transaction_costs), 
        array(run_days), 
        array(profits_shared), 
        array(withdrawals),
        fig
    )


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

    print(f"t_bill:                         {T_BILL:0.4f}")
    print(f"t_bill_daily:                   {T_BILL_DAILY:0.4f}")
    print(f"es_price:                       {ES / 50:0.2f}")
    print(f"es_average_annual:              {ES_MU:0.4f}")
    print(f"es_avg_daily:                   {ES_MU_DAILY:0.4f}")
    print(f"es_stdev_annual:                {ES_SIGMA:0.4f}")
    print(f"es_stdev_daily:                 {ES_SIGMA_DAILY:0.4f}")
    print(f"es_sharpe (rfr = {T_BILL*100:0.2f}):         {ES_SHARPE:0.2f}")
    print(f"es_sharpe (rfr = 0):            {ES_SHARPE_0:0.2f}")
    print(f"profit_target:                  ${PROFIT_TARGET}")
    print(f"drawdown:                       ${DRAWDOWN}")
    print(f"commissions (rt):               {COMMISSIONS_ALL_IN:0.2f}")
    print(f"spread:                         ${SPREAD:0.2f}")
    
    if withdrawal_frequency_days:
    
        print(f"withdrawal_frequency_days:      {withdrawal_frequency_days}")
        print(f"withdrawal_amount_dollars:      ${withdrawal_amount_dollars:0.2f}")
        print(f"profit_share_limit:             ${PROFIT_SHARE_LIMIT}")
        print(f"profit_share_rate:              {PROFIT_SHARE_RATE * 100:0.2f}%")
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

    (
        failure_rate, 
        hit_rate,
        withdrawal_rate,
        eval_counts,
        eval_fees,
        raw_returns,
        ending_equities,
        prop_fees,
        transaction_costs,
        run_days,
        profit_share,
        withdrawals,
        fig_runs
    ) = sim_runs(
        runs, 
        run_years * DPY,
        mu_bp, 
        sigma_bp,
        max_resets,
        leverage, 
        trades_per_day, 
        withdrawal_frequency_days,
        withdrawal_amount_dollars,
        show_runs
    )

    evals_per_account       = mean(eval_counts)
    average_days_survived   = int(ceil(mean(run_days)))

    print(f"mode:                           {mode}")
    print(f"evals per account:              {evals_per_account:0.2f}")
    print(f"survival rate:                  {(1 - failure_rate) * 100:0.2f}%")
    print(f"target hit:                     {hit_rate * 100:0.2f}%") if "personal" not in mode else None
    print(f"withdrawals per account:        {withdrawal_rate:0.2f}")
    print(f"average days survived:          {average_days_survived}")

    total_returns       = ending_equities + transaction_costs + profit_share + withdrawals
    return_after_costs  = total_returns - transaction_costs - profit_share - prop_fees

    print("\n-----\n")

    print(f"{'':32}{'mean':<15}{'10%':<10}{'20%':<10}{'30%':<10}{'40%':<10}{'50%':<10}{'60%':<10}{'70%':<10}{'80%':<10}{'90%':<10}{'95%':<10}{'99%':<10}{'100%':<10}\n")
    
    total_return_lines          = format_stats("total return", total_returns)
    eval_fees_lines             = format_stats("eval_fees", eval_fees) if eval else None
    prop_fees_lines             = format_stats("prop fees", prop_fees) if "personal" not in mode else None
    transaction_costs_lines     = format_stats("transaction costs", transaction_costs)
    profit_share_lines          = format_stats("profit share", profit_share) if "personal" not in mode else None
    return_after_costs_lines    = format_stats("return after costs", return_after_costs)
    ending_equity_lines         = format_stats("ending equity", ending_equities)
    withdrawn_lines             = format_stats("amount withdrawn", withdrawals)

    print(total_return_lines[0])
    print(prop_fees_lines[0])               if "personal" not in mode else None
    print(transaction_costs_lines[0])
    print(profit_share_lines[0])            if (withdrawal_frequency_days and "personal" not in mode) else None

    print("\n")

    print(return_after_costs_lines[0])
    print(ending_equity_lines[0])           if withdrawal_frequency_days else None
    print(withdrawn_lines[0])               if withdrawal_frequency_days else None

    print("\n-----\n")

    print(total_return_lines[1])
    print(prop_fees_lines[1])               if "personal" not in mode else None
    print(transaction_costs_lines[1])
    print(profit_share_lines[1])            if (withdrawal_frequency_days and "personal" not in mode) else None

    print("\n")

    print(return_after_costs_lines[1])
    print(ending_equity_lines[1])           if withdrawal_frequency_days else None
    print(withdrawn_lines[1])               if withdrawal_frequency_days else None

    print("\n")

    if show_runs:
    
        fig_runs.show()

    if show_dists:
        
        fig_dists = get_dist_figure(ending_equities, withdrawals, run_days)

        fig_dists.show()

    print(f"elapsed: {time() - t0:0.1f}s")