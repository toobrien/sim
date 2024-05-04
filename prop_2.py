from    math                    import  ceil, e, log, sqrt
from    numpy                   import  cumsum, mean
from    numpy.random            import  normal
from    typing                  import  List, Tuple

DPY                     = 256
DPM                     = 21
T_BILL                  = 0.05
T_BILL_DAILY            = log(1 + T_BILL) / DPY
ES                      = 5000 * 50
ES_MU                   = 0.10
ES_SIGMA                = 0.15
ES_MU_DAILY             = log(1 + ES_MU) / 256
ES_SIGMA_DAILY          = log(1 + ES_SIGMA) * sqrt(1 / DPY)
ES_SHARPE               = (ES_MU_DAILY - T_BILL_DAILY) / ES_SIGMA_DAILY * sqrt(DPY)
ACCOUNT_SIZE            = 50_000
DRAWDOWN                = 2000
DRAWDOWN_PERCENT        = log((ES - DRAWDOWN) / ES)
PROFIT_TARGET           = 3000
PROFIT_TARGET_PERCENT   = log((ES + PROFIT_TARGET) / ES)
EVAL_MONTHLY_FEE        = 50
ACTIVATION_FEE          = 100
PA_MONTHLY_FEE          = 135
LEVERAGE_MINI           = 1.0
LEVERAGE_MICRO          = 0.1
RUNS                    = 1000
RUN_YEARS               = 1

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
    fees                = []

    for i in range(runs):

        total_return        = 0
        total_fees          = 0
        trailing_drawdown   = DRAWDOWN_PERCENT
        high_watermark      = 0
        run                 = list(leverage * cumsum(normal(loc = mu, scale = sigma, size = days)))

        for j in range(len(run)):

            equity = run[j]

            if equity > high_watermark:

                trailing_drawdown = min(equity + DRAWDOWN_PERCENT, 0)
            
            elif equity <= trailing_drawdown:

                failed  += 1
                run     =  run[0:j]

                break

        target_met_index = len(run)

        for j in range(len(run)):

            equity = run[j]

            if equity >= PROFIT_TARGET_PERCENT:

                passed              += 1
                target_met_index    = j
                total_fees          += ACTIVATION_FEE

                break

        months_in_eval  = ceil(target_met_index / DPM)
        months_in_pa    = ceil((len(run) - target_met_index) / DPM)
        total_fees      = total_fees + (months_in_eval * EVAL_MONTHLY_FEE) + (months_in_pa * PA_MONTHLY_FEE)
        total_return    = run[-1]
        
        returns.append(total_return)
        fees.append(total_fees)

    failure_rate        = failed / runs
    passed_eval_rate    = passed / runs
    average_return      = mean(returns)
    average_fees        = mean(fees)

    return failure_rate, passed_eval_rate, average_return, average_fees


if __name__ == "__main__":

    print(f"t_bill:                 {T_BILL:0.4f}")
    print(f"t_bill_daily:           {T_BILL_DAILY:0.4f}")
    print(f"es_mu:                  {ES_MU:0.4f}")
    print(f"es_mu_daily:            {ES_MU_DAILY:0.4f}")
    print(f"es_sigma:               {ES_SIGMA:0.4f}")
    print(f"es_sigma_daily:         {ES_SIGMA_DAILY:0.4f}")
    print(f"es_sharpe:              {ES_SHARPE:0.4f}")
    print(f"profit_target:          {PROFIT_TARGET}")
    print(f"profit_target_percent:  {PROFIT_TARGET_PERCENT:0.4f}")
    print(f"drawdown:               {DRAWDOWN}")
    print(f"drawdown_percent:       {DRAWDOWN_PERCENT:0.4f}")

    risks           = [ 1, 1/2, 1/3, 1/4, 1/5 ]
    rewards         = [ 1, 2, 3, 4, 5 ] 
    risk_header     = "         " + "".join([ f"{risk:<10.2f}" for risk in risks ])

    # DISPLAY SHARPE RATIOS

    print("\n\n", "-----", "\n\n", "sharpe", "\n\n", risk_header)

    for reward in rewards:

        mu = reward * ES_MU_DAILY

        line = f"{reward:<10}"

        for risk in risks:

            sigma = risk * ES_SIGMA_DAILY

            sharpe = (mu - T_BILL_DAILY) / sigma
            sharpe = sharpe * sqrt(DPY)

            line += f"{sharpe:<10.1f}"

        print(line)

    # DISPLAY PASS RATES
        
    print("\n\n", "-----", "\n\n", "pass rate (1 micro)", "\n\n", risk_header)
        
    for reward in rewards:

        mu = reward * ES_MU_DAILY

        line = f"{reward:<10}"

        for risk in risks:

            sigma = risk * ES_SIGMA_DAILY

            pass_rate = sim_runs(RUNS, RUN_YEARS * DPY, mu, sigma, LEVERAGE_MICRO)

            pass

        print(line)

    pass