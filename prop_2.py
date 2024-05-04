from    math                    import  e, log, sqrt
from    numpy                   import  cumsum
from    numpy.random            import  normal
import  plotly.graph_objects    as      go
from    plotly.subplots         import  make_subplots
from    time                    import  time


DPY                     = 256
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
EVAL_FEE                = 50
ACTIVATION_FEE          = 100
MONTHLY_DATA_FEE        = 135
LEVERAGE_MINI           = 1.0
LEVERAGE_MICRO          = 0.1


#               size    eval ($/mo)     pa ($/mo)   activation fee  trailing dd     eval target
# apex:         50,000  35              85          n/a             2,500           3,000
# tradeday:     50,000  85              135         140             2,000           2,500
# topstep:      50,000  50              135         150             2,000           3,000


if __name__ == "__main__":

    print(f"T_BILL:                 {T_BILL:0.4f}")
    print(f"T_BILL_DAILY:           {T_BILL_DAILY:0.4f}")
    print(f"ES_MU:                  {ES_MU:0.4f}")
    print(f"ES_MU_DAILY:            {ES_MU_DAILY:0.4f}")
    print(f"ES_SIGMA:               {ES_SIGMA:0.4f}")
    print(f"ES_SIGMA_DAILY:         {ES_SIGMA_DAILY:0.4f}")
    print(f"ES_SHARPE:              {ES_SHARPE:0.4f}")
    print(f"PROFIT_TARGET:          {PROFIT_TARGET}")
    print(f"PROFIT_TARGET_PERCENT:  {PROFIT_TARGET_PERCENT:0.4f}")
    print(f"DRAWDOWN:               {DRAWDOWN}")
    print(f"DRAWDOWN_PERCENT:       {DRAWDOWN_PERCENT:0.4f}")

    risks   = [ 1, 1/2, 1/3, 1/4, 1/5 ]
    rewards = [ 1, 2, 3, 4, 5 ] 
    header  = "         " + "".join([ f"{risk:<10.2f}" for risk in risks ])

    print("\n\n", "-----", "\n\n", "sharpe", "\n\n", header)

    for reward in rewards:

        mu = reward * ES_MU_DAILY

        line = f"{reward:<10}"

        for risk in risks:

            sigma = risk * ES_SIGMA_DAILY

            sharpe = (mu - T_BILL_DAILY) / sigma
            sharpe = sharpe * sqrt(DPY)

            line += f"{sharpe:<10.4f}"

        print(line)

    pass