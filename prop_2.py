import  plotly.graph_objects    as      go
from    math                    import  ceil, e, log, sqrt
from    numpy                   import  cumsum, mean
from    numpy.random            import  normal
from    sys                     import  argv
from    typing                  import  List, Tuple


#                  risk reward  leverage    runs    trades_per_day  show_chart
# python prop_2.py 1.0  1.0     1.0         1000    1               1


reward          = float(argv[1])
risk            = float(argv[2])
leverage        = float(argv[3])
runs            = int(argv[4])
trades_per_day  = int(argv[5])
show_chart      = int(argv[6])

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
DRAWDOWN_PERCENT            = log((ES - DRAWDOWN) / ES)
PROFIT_TARGET               = 3_000
PROFIT_TARGET_PERCENT       = log((ES + PROFIT_TARGET) / ES)
ACTIVATION_FEE              = 100
PA_MONTHLY_FEE              = 135
COMMISSIONS_ALL_IN          = 4.0 if leverage >= 1.0 else 1.2
SPREAD                      = 12.5 if leverage >= 1.0 else 1.25
TRANSACTION_COSTS           = COMMISSIONS_ALL_IN + SPREAD
TRANSACTION_COSTS_PERCENT   = log((ES + TRANSACTION_COSTS) / ES)
RUN_YEARS                   = 1

#               size    eval ($/mo)     pa ($/mo)   activation fee  trailing dd     eval target
# apex:         50,000  35              85          n/a             2,500           3,000
# tradeday:     50,000  85              135         140             2,000           2,500
# topstep:      50,000  50              135         150             2,000           3,000


def sim_runs(
    runs:               int,
    days:               int,
    mu:                 float,
    sigma:              float,
    leverage:           float,
    trades_per_day:     int,
    show_chart:         bool
) -> List[Tuple]:
    
    fig                 = go.Figure()
    failed              = 0
    passed              = 0
    returns             = []
    prop_fees           = []
    transaction_costs   = []
    run_days            = []

    for i in range(runs):

        total_return            = 0
        total_prop_fees         = ACTIVATION_FEE
        total_transaction_costs = 0
        run                     = leverage * cumsum(normal(loc = mu, scale = sigma, size = days)) - TRANSACTION_COSTS_PERCENT * trades_per_day
        trailing_drawdown       = [ max(min(max(run[:i + 1]) + DRAWDOWN_PERCENT, 0), DRAWDOWN_PERCENT) for i in range(len(run)) ]
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
        
        months                  = ceil(len(run) / DPM)
        total_prop_fees         = total_prop_fees + months * PA_MONTHLY_FEE
        total_transaction_costs = (TRANSACTION_COSTS * trades_per_day * len(run))
        total_return            = equity if not blown and equity > PROFIT_TARGET_PERCENT else 0
        
        run_days.append(len(run))
        returns.append(total_return + log((ES + total_transaction_costs) / ES))
        prop_fees.append(total_prop_fees)
        transaction_costs.append(total_transaction_costs)

    failure_rate                    = failed / runs
    passed_eval_rate                = passed / runs
    average_return                  = mean(returns)
    average_prop_fees               = log(1 + mean(prop_fees) / ES)
    average_transaction_costs       = log(1 + mean(transaction_costs) / ES)
    average_trading_days            = mean(run_days)

    return failure_rate, passed_eval_rate, average_return, average_prop_fees, average_transaction_costs, average_trading_days, fig


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
    print(f"transaction_costs_percent:      ${TRANSACTION_COSTS_PERCENT:0.5f}")
    print("\n-----\n")

    mu          = reward * ES_MU_DAILY
    sigma       = risk * ES_SIGMA_DAILY
    sharpe      = (mu - T_BILL_DAILY) / sigma * sqrt(DPY)
    sharpe_0    = mu / sigma * sqrt(DPY)

    print(f"reward:                         {reward:0.2f}x\t{mu * 100:0.2f}%\t${ES * (e**mu - 1) * leverage:0.2f}")
    print(f"risk:                           {risk:0.2f}x\t{sigma * 100:0.2f}%\t${ES * (e**sigma - 1) * leverage:0.2f}")
    print(f"leverage:                       {leverage:0.2f}x")
    print(f"runs:                           {runs}")
    print(f"trades_per_day:                 {trades_per_day}\n")
    print(f"sharpe (rfr = {T_BILL * 100:0.2f}%):           {sharpe:0.2f}")
    print(f"sharpe (rfr = 0):               {sharpe_0:0.2f}")

    print("\n-----\n")

    (
        failure_rate, 
        pass_rate, 
        average_return, 
        average_prop_fees, 
        average_transaction_costs,
        average_trading_days,
        fig
    ) = sim_runs(runs, RUN_YEARS * DPY, mu, sigma, leverage, trades_per_day, show_chart)

    print(f"survival rate:                  {(1 - failure_rate) * 100:0.2f}%")
    print(f"eval pass rate:                 {pass_rate * 100:0.2f}%")
    print(f"average trading days:           {int(ceil(average_trading_days))}")
    print(f"average return:                 {average_return * 100:0.2f}%\t${ES * e**average_return - ES:0.2f}")
    print(f"average prop fees:              {average_prop_fees * 100:0.2f}%\t${ES * e**average_prop_fees - ES:0.2f}")
    print(f"average transaction costs:      {average_transaction_costs * 100:0.2f}%\t${ES * e**average_transaction_costs - ES:0.2f}")

    return_after_costs = (average_return - average_prop_fees - average_transaction_costs)

    print(f"expected return after costs:    {return_after_costs * 100:0.2f}%\t${ES * e**return_after_costs - ES:0.2f}")

    print("\n\n")

    if show_chart:
    
        fig.show()

    pass