import  plotly.graph_objects    as      go
from    math                    import  ceil, e, log, sqrt
from    numpy                   import  cumsum, mean
from    numpy.random            import  normal
from    sys                     import  argv
from    typing                  import  List, Tuple


#                  reward risk   leverage runs  trades_per_day withdrawal_frequency_days withdrawal_amount_dollars run_years show_chart
# python prop_2.py 1.0x   1.0x   1.0      10000 1              0                         0                         1         0
# python prop_2.py \$100  \$200  1.0      10000 1              0                         0                         1         0
# python prop_2.py 2p     5p     1.0      1000  1              21                        2000                      2         1
# python prop_2.py 0.0003 0.0125 1.0      1000  1              63                        2000                      2         1

# risk/reward can be ES multiplier, $, ES points, or basis points


reward                      = argv[1]
risk                        = argv[2]
leverage                    = float(argv[3])
runs                        = int(argv[4])
trades_per_day              = int(argv[5])
withdrawal_frequency_days   = int(argv[6])
withdrawal_amount_dollars   = float(argv[7])
run_years                   = int(argv[8])
show_chart                  = int(argv[9])


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
ACCOUNT_SIZE                = 50_000
DRAWDOWN                    = 2_000
MINIMUM_TRADING_DAYS        = 10
DRAWDOWN_PERCENT            = log(1 - DRAWDOWN / ES)
PROFIT_TARGET               = 3_000
PROFIT_TARGET_PERCENT       = log(1 + PROFIT_TARGET / ES)
ACTIVATION_FEE              = 100
PA_MONTHLY_FEE              = 135
COMMISSIONS_ALL_IN          = 4.0 if leverage >= 1.0 else 1.2
SPREAD                      = 12.5 if leverage >= 1.0 else 1.25
TRANSACTION_COSTS           = COMMISSIONS_ALL_IN + SPREAD
TRANSACTION_COSTS_PERCENT   = log(1 + TRANSACTION_COSTS / ES)
WITHDRAWAL_AMOUNT_PCT       = log(1 + withdrawal_amount_dollars / ES)
PROFIT_SHARE_RATE           = 0.1
PROFIT_SHARE_LIMIT          = 10_000


#               size    eval ($/mo)     pa ($/mo)   activation fee  trailing dd     eval target
# apex:         50,000  35              85          n/a             2,500           3,000
# tradeday:     50,000  85              135         140             2,000           2,500
# topstep:      50,000  50              135         150             2,000           3,000


def sim_runs(
    runs:                       int,
    days:                       int,
    mu:                         float,
    sigma:                      float,
    leverage:                   float,
    trades_per_day:             int,
    withdrawal_frequency_days:  int,
    withdrawal_amount_dollars:  float,
    show_chart:                 bool
) -> List[Tuple]:
    
    fig                 = go.Figure()
    failed              = 0
    passed              = 0
    total_withdraws     = 0
    returns             = []
    prop_fees           = []
    transaction_costs   = []
    withdraws           = []
    profits_shared      = []
    run_days            = []

    for i in range(runs):

        total_return            = 0
        total_prop_fees         = ACTIVATION_FEE
        total_transaction_costs = 0
        run                     = leverage * cumsum(normal(loc = mu, scale = sigma, size = days)) - TRANSACTION_COSTS_PERCENT * trades_per_day
        trailing_drawdown       = [ max(min(max(run[:i + 1]) + DRAWDOWN_PERCENT, 0), DRAWDOWN_PERCENT) for i in range(len(run)) ]
        profit_share            = 0
        withdrawn               = 0
        blown                   = False
        pt_hit                  = False

        for j in range(len(run)):

            equity  = run[j]
            trail   = trailing_drawdown[j]
            
            if equity <= trail:

                blown               =   True
                failed              +=  1
                run                 =   run[0:j + 1]
                trailing_drawdown   =   run[0:j + 1]

                break

            elif equity >= PROFIT_TARGET_PERCENT and j > MINIMUM_TRADING_DAYS:

                pt_hit = True

                if withdrawal_frequency_days and j % withdrawal_frequency_days == 0:

                    total_withdraws += 1
                    withdrawn       += withdrawal_amount_dollars
                    run[j + 1:]     -= WITHDRAWAL_AMOUNT_PCT

        if pt_hit:

            passed += 1

        if show_chart:

            fig.add_trace(
                go.Scattergl(
                    {
                        "x":        [ i for i in range(len(run)) ],
                        "y":        [ ES * e**(run[i]) for i in range(len(run)) ],
                        "text":     [ f"{ES * e**trailing_drawdown[i]:0.2f}" for i in range(len(trailing_drawdown)) ],
                        "marker":   { "color": "#FF0000" if blown else "#00FF00" if equity >= PROFIT_TARGET_PERCENT else "#0000FF" }
                    }
                )
            )
        
        if withdrawn > PROFIT_SHARE_LIMIT:

            profit_share    =   (withdrawn - PROFIT_SHARE_LIMIT) * PROFIT_SHARE_RATE
            withdrawn       -=  profit_share

        months                  = ceil(len(run) / DPM)
        total_prop_fees         = total_prop_fees + months * PA_MONTHLY_FEE
        total_transaction_costs = (TRANSACTION_COSTS * trades_per_day * len(run))
        total_return            = equity if not blown and equity > PROFIT_TARGET_PERCENT else 0
        total_return            = total_return + log(1 + total_transaction_costs / ES)
        total_return            = total_return + log(1 + withdrawn / ES)

        run_days.append(len(run))
        returns.append(total_return)
        prop_fees.append(total_prop_fees)
        transaction_costs.append(total_transaction_costs)
        profits_shared.append(profit_share)
        withdraws.append(withdrawn)

    failure_rate                    = failed / runs
    passed_eval_rate                = passed / runs
    withdrawal_rate                 = total_withdraws / runs
    average_return                  = mean(returns)
    average_prop_fees               = log(1 + mean(prop_fees) / ES)
    average_transaction_costs       = log(1 + mean(transaction_costs) / ES)
    average_trading_days            = mean(run_days)
    average_profit_share            = log(1 + mean(profits_shared) / ES)
    average_withdrawn               = log(1 + mean(withdraws) / ES)

    return failure_rate, passed_eval_rate, withdrawal_rate, average_return, average_prop_fees, average_transaction_costs, average_trading_days, average_profit_share, average_withdrawn, fig


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
        average_return, 
        average_prop_fees,
        average_transaction_costs,
        average_trading_days,
        average_profit_share,
        average_withdrawn,
        fig
    ) = sim_runs(
        runs, 
        run_years * DPY,
        mu_bp, 
        sigma_bp, 
        leverage, 
        trades_per_day, 
        withdrawal_frequency_days,
        withdrawal_amount_dollars,
        show_chart
    )

    print(f"survival rate:                  {(1 - failure_rate) * 100:0.2f}%")
    print(f"withdrawal eligible:            {pass_rate * 100:0.2f}%")
    print(f"withdraws per account:          {withdrawal_rate:0.2f}")
    print(f"average days survived:          {int(ceil(average_trading_days))}\n")
    print(f"expected return before costs:   {average_return * 100:0.2f}%\t${ES * (e**average_return - 1):0.2f}")
    print(f"average prop fees:              {average_prop_fees * 100:0.2f}%\t${ES * (e**average_prop_fees - 1):0.2f}")
    print(f"average transaction costs:      {average_transaction_costs * 100:0.2f}%\t${ES * (e**average_transaction_costs - 1):0.2f}")

    if withdrawal_frequency_days:
    
        print(f"average_profit_share:           {average_profit_share * 100:0.2f}%\t${ES * (e**average_profit_share - 1):0.2f}\n")

    return_after_costs      = average_return - average_prop_fees - average_transaction_costs - average_profit_share
    average_ending_equity   = average_return - average_transaction_costs - average_profit_share - average_withdrawn

    print(f"expected return after costs:    {return_after_costs * 100:0.2f}%\t${ES * (e**return_after_costs - 1):0.2f}")
    
    if withdrawal_frequency_days:

        print(f"average ending equity:          {average_ending_equity * 100:0.2f}%\t${ES * (e**average_ending_equity - 1):0.2f}")
        print(f"average_withdrawn:              {average_withdrawn * 100:0.2f}%\t${ES * (e**(average_withdrawn) - 1):0.2f}")

    print("\n\n")

    if show_chart:
    
        fig.show()

    pass