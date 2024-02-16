import  plotly.graph_objects    as      go
from    plotly.subplots         import  make_subplots
import  random
from    sys                     import  argv
from    time                    import  time


N_TRIALS            = 10000
PT_VALUE            = 20                            # nq
TP                  = 5
SL                  = 5
P_WIN               = SL / (TP + SL)
P_LOSE              = 1 - P_WIN
COMMISSION          = 2.79 * 2                      # ninja trader
AMT_WIN             = (TP * PT_VALUE) - COMMISSION
AMT_LOSE            = -(SL * PT_VALUE) - COMMISSION
ACCT_SIZE           = 50000
BLOWN               = -2000
PASSED              = 2500
TRADES_PER_MONTH    = 100
MAX_TRADES          = TRADES_PER_MONTH * 36
MONTHLY_FEE         = 165
WITHDRAWAL          = 9733 / 12                     # worldwide median income
PROFIT_SHARE        = 0.9
PROFIT_MIN          = -10000


def funding():

    funded = 0
    total_fees = 0

    for i in range(N_TRIALS):
    
        month       = 0
        pnl         = 0
        sample      = random.choices([ AMT_WIN, AMT_LOSE ], weights = [ P_WIN, P_LOSE ], k = MAX_TRADES)
        trail_stop  = BLOWN

        for j in range(MAX_TRADES):

            pnl += sample[j]

            if j % TRADES_PER_MONTH == 0:

                month += 1

            if sample[j] > 0:

                trail_stop = min(0, trail_stop + AMT_WIN)

            if pnl >= PASSED:

                funded      += 1
                total_fees  += month * MONTHLY_FEE

                break
            
            elif pnl <= trail_stop:

                break

    print(f"accounts: {N_TRIALS}")
    print(f"passed:   {funded / N_TRIALS * 100:0.1f}%")
    print(f"avg fee:  ${total_fees / funded:0.2f}")


def survival():

    fig = make_subplots(
        rows                = 1, 
        cols                = 2, 
        column_widths       = [ 0.7, 0.3 ],
        horizontal_spacing  = 0.025
    )

    net_gross_profit    = 0
    winners             = 0
    funded              = 0
    profit_hist         = []

    for i in range(N_TRIALS):

        month           = 0
        pnl             = 0
        sample          = random.choices([ AMT_WIN, AMT_LOSE ], weights = [ P_WIN, P_LOSE ], k = MAX_TRADES)
        trail_stop      = BLOWN
        passed          = False
        gross_profit    = 0 #PROFIT_MIN
        record          = []
        color           = "#CCCCCC"

        for j in range(MAX_TRADES):
                       
            pnl += sample[j]

            record.append(pnl + ACCT_SIZE)

            if j % TRADES_PER_MONTH == 0:

                month += 1
                pnl   -= MONTHLY_FEE
            
                if month >= 2 and pnl - WITHDRAWAL > trail_stop and passed:

                    pnl             -= WITHDRAWAL
                    gross_profit    += WITHDRAWAL * PROFIT_SHARE

            if sample[j] > 0:

                trail_stop = min(0, trail_stop + AMT_WIN)

            if pnl >= PASSED and not passed:

                passed =    True
                funded +=   1
            
            elif pnl <= trail_stop:

                if gross_profit > 0:

                    net_gross_profit += gross_profit
                    winners          += 1
                    color            =  "#0000FF"

                    profit_hist.append(gross_profit)

                break

        fig.add_trace(
            go.Scattergl(
                {
                    "x":        [ k for k in range(len(record)) ],
                    "y":        record,
                    "mode":     "markers",
                    "marker":   { "color": color },
                    "name":     str(i)
                }
            ),
            row = 1,
            col = 1
        )
    
    fig.add_trace(
        go.Histogram(
            x       = profit_hist,
            name    = "profits",
            nbinsx  = 50
        ),
        row = 1,
        col = 2
    )

    fig.show()

    print(f"accounts:               {N_TRIALS}")
    print(f"passed trial:           {funded}")
    print(f"winners:                {winners}")
    print(f"avg months profitable:  {int(net_gross_profit / winners / WITHDRAWAL)}")
    print(f"avg gross profit:       ${net_gross_profit / winners:0.2f}")


if __name__ == "__main__":

    t0 = time()

    mode = argv[1]

    if mode == "funding":

        funding()
    
    elif mode == "survival":

        survival()

    print(f"elapsed: {time() - t0:0.2f}s")