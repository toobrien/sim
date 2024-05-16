import  plotly.graph_objects    as      go
from    plotly.subplots         import  make_subplots
from    math                    import  ceil, e, log, sqrt
from    numpy                   import  array, cumsum, mean, percentile
from    numpy.random            import  normal
from    sys                     import  argv
from    time                    import  time
from    typing                  import  List, Tuple


#                  reward risk   leverage runs  trades_per_day withdrawal_frequency_days withdrawal_amount_dollars run_years show_dists show_chart mode
# python prop_2.py 1.0x   1.0x   1.0      10000 5              0                         0                         1         1          0          tradeday_50k
# python prop_2.py \$100  \$200  1.0      10000 5              0                         0                         1         1          0          personal_2k
# python prop_2.py 2p     5p     1.0      100   5              21                        2000                      2         1          1          tradeday_50k
# python prop_2.py 0.0003 0.0125 1.0      100   5              63                        2000                      2         1          1          personal_2k

# risk/reward can be ES multiplier, $, ES points, or basis points

t0                          = time()
reward                      = argv[1]
risk                        = argv[2]
leverage                    = float(argv[3])
runs                        = int(argv[4])
trades_per_day              = int(argv[5])
withdrawal_frequency_days   = int(argv[6])
withdrawal_amount_dollars   = float(argv[7])
run_years                   = int(argv[8])
show_dists                  = int(argv[9])
show_runs                   = int(argv[10])
mode                        = argv[11]


#               size    eval ($/mo)     pa ($/mo)   activation fee  trailing dd     eval target
# apex:         50,000  35              85          n/a             2,500           3,000
# tradeday:     50,000  85              135         140             2,000           2,500
# topstep:      50,000  50              135         150             2,000           3,000


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
        "pa_monthly_fee":       0
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
        "pa_monthly_fee":       135
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
        "pa_monthly_fee":       85
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
DRAWDOWN_PERCENT            = log(1 - DRAWDOWN / ES)
PROFIT_TARGET               = MODES[mode]["profit_target"]
PROFIT_TARGET_PERCENT       = log(1 + PROFIT_TARGET / ES)
ACTIVATION_FEE              = 100
PA_MONTHLY_FEE              = 135
COMMISSIONS_ALL_IN          = 4.0 if leverage >= 1.0 else 1.2
SPREAD                      = 12.5 if leverage >= 1.0 else 1.25
TRANSACTION_COSTS           = COMMISSIONS_ALL_IN + SPREAD
TRANSACTION_COSTS_PERCENT   = log(1 + TRANSACTION_COSTS / ES)
WITHDRAWAL_AMOUNT_PCT       = log(1 + withdrawal_amount_dollars / ES)
BUFFER                      = MODES[mode]["buffer"]
BUFFER_PCT                  = log(1 + BUFFER / ES)
PROFIT_SHARE_RATE           = MODES[mode]["profit_share_rate"]
PROFIT_SHARE_LIMIT          = MODES[mode]["profit_share_limit"]


def sim_runs(
    runs:                       int,
    days:                       int,
    mu:                         float,
    sigma:                      float,
    leverage:                   float,
    trades_per_day:             int,
    withdrawal_frequency_days:  int,
    withdrawal_amount_dollars:  float,
    show_runs:                  bool
) -> List[Tuple]:
    
    fig                 = make_subplots(rows = 1, cols = 2, column_widths = [ 0.85, 0.15 ], horizontal_spacing = 0.05)
    failed              = 0
    passed              = 0
    total_withdrawals   = 0
    raw_returns         = []
    ending_equities     = []
    prop_fees           = []
    transaction_costs   = []
    withdrawals         = []
    profits_shared      = []
    run_days            = []

    for _ in range(runs):

        total_prop_fees         = ACTIVATION_FEE
        total_transaction_costs = 0
        run                     = array([ ES * (e**i - 1) for i in (leverage * cumsum(normal(loc = mu, scale = sigma, size = days))) ]) - (TRANSACTION_COSTS * trades_per_day)
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
                trailing_drawdown       =   trailing_drawdown[0:j + 1]
                
                running_withdrawals[j]  =   withdrawn

                break

            elif equity >= PROFIT_TARGET_PERCENT and j >= MINIMUM_TRADING_DAYS:

                pt_hit = True

                if withdrawal_frequency_days and j % withdrawal_frequency_days == 0:

                    total_withdrawals   += 1
                    withdrawn           += withdrawal_amount_dollars
                    run[j + 1:]         -= WITHDRAWAL_AMOUNT_PCT

            running_withdrawals[j] = withdrawn

        if pt_hit:

            passed += 1

        if show_runs:

            fig.add_trace(
                go.Scattergl(
                    {
                        "x":        [ i for i in range(len(run)) ],
                        "y":        run,
                        "text":     [ f"trailing drawdown: {trailing_drawdown[i]:0.2f}<br>withdrawn: ${running_withdrawals[i]:0.2f}" for i in range(len(trailing_drawdown)) ],
                        "marker":   { "color": "#FF0000" if blown else "#00FF00" if equity >= PROFIT_TARGET_PERCENT else "#0000FF" }
                    }
                ),
                row = 1,
                col = 1
            )
        
        if withdrawn > PROFIT_SHARE_LIMIT and "personal" not in mode:

            profit_share    =   (withdrawn - PROFIT_SHARE_LIMIT) * PROFIT_SHARE_RATE
            withdrawn       -=  profit_share

        months                  = ceil(len(run) / DPM)
        total_prop_fees         = total_prop_fees + months * PA_MONTHLY_FEE
        total_transaction_costs = (TRANSACTION_COSTS * trades_per_day * len(run))
        raw_return              = max(equity, -trail)
        ending_equity           = max(equity, 0) if "personal" not in mode else raw_return

        run_days.append(len(run))
        raw_returns.append(raw_return)
        ending_equities.append(ending_equity)
        prop_fees.append(total_prop_fees if "personal" not in mode else 0)
        transaction_costs.append(total_transaction_costs)
        profits_shared.append(profit_share)
        withdrawals.append(withdrawn)

    if show_runs:

        fig.add_trace(go.Histogram(y = [ i for i in raw_returns if i > 0 ], marker_color = "#00FF00"), row = 1, col = 2)
        fig.add_trace(go.Histogram(y = [ i for i in raw_returns if i <= 0 ], marker_color = "#FF0000"), row = 1, col = 2)

    failure_rate        = failed / runs
    passed_eval_rate    = passed / runs
    withdrawal_rate     = total_withdrawals / runs

    return (
        failure_rate, 
        passed_eval_rate, 
        withdrawal_rate,
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
    withdrawals_bins    = ceil((max(withdrawals) - min(withdrawals)) / withdrawal_amount_dollars)
    run_days_bins       = max(run_days) - min(run_days)

    traces = [
        ( raw_returns, "ending equity (hist)", raw_returns_bins, False, "#03396c", 1, 1 ),
        ( raw_returns, "ending equity (cdf)", raw_returns_bins, True, "#03396c", 1, 2 ),
        ( withdrawals, "amount withdrawn (hist)", withdrawals_bins, False, "#005b96", 2, 1 ),
        ( withdrawals, "amount withdrawn (cdf)", withdrawals_bins * 10, True, "#005b96", 2, 2 ),
        ( run_days,  "days survived (hist)", run_days_bins, False, "#6497b1", 3, 1 ),
        ( run_days,  "days survived (cdf)", run_days_bins, True, "#6497b1", 3, 2 ),
    ]

    for trace in traces:

        fig.add_trace(
            go.Histogram(
                x                   = trace[0],
                name                = trace[1],
                nbinsx              = trace[2],
                cumulative_enabled  = trace[3],
                marker_color        = trace[4]

            ),
            row = trace[5],
            col = trace[6]
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
    print(f"profit_target_percent:          {PROFIT_TARGET_PERCENT:0.4f}")
    print(f"drawdown:                       ${DRAWDOWN}")
    print(f"drawdown_percent:               {DRAWDOWN_PERCENT:0.4f}")
    print(f"commissions (rt):               {COMMISSIONS_ALL_IN:0.2f}")
    print(f"spread:                         ${SPREAD:0.2f}")
    print(f"transaction_costs_bp:           {TRANSACTION_COSTS_PERCENT:0.5f}")
    
    if withdrawal_frequency_days:
    
        print(f"withdrawal_frequency_days:      {withdrawal_frequency_days}")
        print(f"withdrawal_amount_dollars:      ${withdrawal_amount_dollars:0.2f}")
        print(f"profit_share_limit:             ${PROFIT_SHARE_LIMIT}")
        print(f"profit_share_rate:              {PROFIT_SHARE_RATE * 100:0.2f}%")
        print("\n-----\n")

    mu_bp, mu_dollars       = get_metric(reward, ES_MU_DAILY)
    sigma_bp, sigma_dollars = get_metric(risk, ES_SIGMA_DAILY)
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
        pass_rate,
        withdrawal_rate,
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
        leverage, 
        trades_per_day, 
        withdrawal_frequency_days,
        withdrawal_amount_dollars,
        show_runs
    )

    average_days_survived = int(ceil(mean(run_days)))

    print(f"mode:                           {mode}")
    print(f"survival rate:                  {(1 - failure_rate) * 100:0.2f}%")
    print(f"withdrawal eligible:            {pass_rate * 100:0.2f}%") if "personal" not in mode else None
    print(f"withdrawals per account:        {withdrawal_rate:0.2f}")
    print(f"average days survived:          {average_days_survived}")

    total_returns       = ending_equities + transaction_costs + profit_share + withdrawals
    return_after_costs  = total_returns - transaction_costs - profit_share - prop_fees

    print("\n-----\n")

    print(f"{'':32}{'mean':<15}{'10%':<10}{'20%':<10}{'30%':<10}{'40%':<10}{'50%':<10}{'60%':<10}{'70%':<10}{'80%':<10}{'90%':<10}{'95%':<10}{'99%':<10}{'100%':<10}\n")
    
    total_return_lines          = format_stats("total return", total_returns)
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
        
        fig_dists = get_dist_figure(raw_returns, withdrawals, run_days)

        fig_dists.show()

    print(f"elapsed: {time() - t0:0.1f}s")