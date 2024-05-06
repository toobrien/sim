from    math                    import  ceil, e, log, sqrt
from    numpy                   import  cumsum, mean
from    numpy.random            import  normal
from    sys                     import  argv
from    typing                  import  List, Tuple


#                  risk reward  leverage
# python prop_2.py 1.0  1.0     1.0


DPY                         = 256
DPM                         = 21
T_BILL                      = 0.05
T_BILL_DAILY                = log(1 + T_BILL) / DPY
ES                          = 5000 * 50
ES_MU                       = 0.0721
ES_SIGMA                    = 0.1961
ES_MU_DAILY                 = ES_MU / DPY
ES_SIGMA_DAILY              = ES_SIGMA * sqrt(1 / DPY)
ES_SHARPE                   = (ES_MU_DAILY - T_BILL_DAILY) / ES_SIGMA_DAILY * sqrt(DPY)
ACCOUNT_SIZE                = 50_000
DRAWDOWN                    = 2000
DRAWDOWN_PERCENT            = log((ES - DRAWDOWN) / ES)
PROFIT_TARGET               = 3000
PROFIT_TARGET_PERCENT       = log((ES + PROFIT_TARGET) / ES)
EVAL_MONTHLY_FEE            = 50
ACTIVATION_FEE              = 100
PA_MONTHLY_FEE              = 135
TRADES_PER_DAY              = 1
COMMISSIONS_ALL_IN          = 4.0
SPREAD                      = 12.5
TRANSACTION_COSTS           = COMMISSIONS_ALL_IN + SPREAD
TRANSACTION_COSTS_PERCENT   = log((ES + TRANSACTION_COSTS) / ES)
RUNS                        = 1000
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
    leverage:           float
) -> List[Tuple]:
    
    failed              = 0
    passed              = 0
    returns             = []
    prop_fees           = []
    transaction_costs   = []

    for i in range(runs):

        total_return            = 0
        total_prop_fees         = 0
        total_transaction_costs = 0
        trailing_drawdown       = DRAWDOWN_PERCENT
        high_watermark          = 0
        run                     = list(leverage * cumsum(normal(loc = mu, scale = sigma, size = days)))

        for j in range(len(run)):

            equity = run[j]

            if equity > high_watermark:

                high_watermark      = equity
                trailing_drawdown   = min(high_watermark + DRAWDOWN_PERCENT, 0)
            
            elif equity <= trailing_drawdown:

                failed  += 1
                run     =  run[0:j]

                break

        target_met_index = len(run)

        for j in range(len(run)):

            equity = run[j]

            if equity >= PROFIT_TARGET_PERCENT:

                passed              +=  1
                target_met_index    =   j
                total_prop_fees     += ACTIVATION_FEE

                break

        months_in_eval          = ceil(target_met_index / DPM)
        months_in_pa            = ceil((len(run) - target_met_index) / DPM)
        total_prop_fees         = total_prop_fees + (months_in_eval * EVAL_MONTHLY_FEE) + (months_in_pa * PA_MONTHLY_FEE)
        total_transaction_costs = (TRANSACTION_COSTS * TRADES_PER_DAY * len(run))
        total_return            = run[-1] if len(run) >= 1 else equity
        
        returns.append(total_return)
        prop_fees.append(total_prop_fees)
        transaction_costs.append(total_transaction_costs)

    failure_rate                = failed / runs
    passed_eval_rate            = passed / runs
    average_return              = mean(returns)
    average_prop_fees           = log(1 + mean(prop_fees) / ES)
    average_transaction_costs   = log(1 + mean(transaction_costs) / ES)
    excess_expected_return      = average_return - average_prop_fees - average_transaction_costs

    return failure_rate, passed_eval_rate, average_return, average_prop_fees, average_transaction_costs, excess_expected_return


if __name__ == "__main__":

    print(f"t_bill:                     {T_BILL:0.4f}")
    print(f"t_bill_daily:               {T_BILL_DAILY:0.4f}")
    print(f"es_price:                   {ES:0.2f}")
    print(f"es_mu:                      {ES_MU:0.4f}")
    print(f"es_mu_daily:                {ES_MU_DAILY:0.4f}")
    print(f"es_sigma:                   {ES_SIGMA:0.4f}")
    print(f"es_sigma_daily:             {ES_SIGMA_DAILY:0.4f}")
    print(f"es_sharpe:                  {ES_SHARPE:0.4f}")
    print(f"profit_target:              {PROFIT_TARGET}")
    print(f"profit_target_percent:      {PROFIT_TARGET_PERCENT:0.4f}")
    print(f"drawdown:                   {DRAWDOWN}")
    print(f"drawdown_percent:           {DRAWDOWN_PERCENT:0.4f}")
    print(f"transaction_costs_percent:  {TRANSACTION_COSTS_PERCENT:0.4f}\n")
    print("-----\n")
    
    reward      = float(argv[1])
    risk        = float(argv[2])
    leverage    = float(argv[3])
    mu          = reward * ES_MU_DAILY
    sigma       = risk * ES_SIGMA_DAILY
    sharpe      = (mu - T_BILL_DAILY) / sigma * sqrt(DPY)

    (
        failure_rate, 
        pass_rate, 
        average_return, 
        average_prop_fees, 
        average_transaction_costs, 
        excess_expected_return 
    ) = sim_runs(RUNS, RUN_YEARS * DPY, mu, sigma, leverage)

    print(f"reward:                     {reward:0.2f}x")
    print(f"risk:                       {risk:0.2f}x")
    print(f"sharpe:                     {sharpe:0.2f}")
    print(f"failure rate:               {failure_rate * 100:0.2f}%")
    print(f"eval pass rate:             {pass_rate * 100:0.2f}%")
    print(f"average return:             {average_return * 100:0.2f}%\t${ES * e**average_return - ES:0.2f}")
    print(f"average prop fees:          {average_prop_fees * 100:0.2f}%\t${ES * e**average_prop_fees - ES:0.2f}")
    print(f"average transaction costs:  {average_transaction_costs * 100:0.2f}%\t${ES * e**average_transaction_costs - ES:0.2f}")
    print(f"return after fees:          {excess_expected_return * 100:0.2f}%\t${ES * e**excess_expected_return - ES:0.2f}")

    print("\n\n")

    pass