from    math                    import  e, log, sqrt
from    numpy                   import  cumsum
from    numpy.random            import  normal
import  plotly.graph_objects    as      go
from    plotly.subplots         import  make_subplots
from    sys                     import  argv


PLOT            = int(argv[1])
DOLLAR_STATS    = int(argv[2])
N_TRIALS        = int(argv[3])
MODE            = "NDX"
ASSETS          = {

    "SPX":      ( 5000, 50, 0.1425, 0.101 ),
    "NDX":      ( 17000, 20, 0.1839, 0.2254 )
}


if __name__ == "__main__":
    
    asset           = ASSETS[MODE]
    dpy             = 252
    ul_multiplier   = asset[1]
    ul_price        = asset[0] * ul_multiplier
    rfr             = 0.0392
    #rfr             = 0

    leverage        = 1.0
    reward          = 200
    risk            = 312.5
    max_dd          = 10000
    max_dd_log      = log(1 - max_dd / ul_price)

    ul__sigma       = asset[2]
    ul__mu          = asset[3]
    ul__sharpe      = ((ul__mu - rfr) / ul__sigma)

    rfr             = rfr / dpy
    strat_sigma     = log(1 + risk / ul_price)
    strat_mu        = log(1 + reward / ul_price)
    strat_sharpe    = ((strat_mu - rfr) / strat_sigma) * sqrt(dpy)

    sharpes         = [ 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0, strat_sharpe ]
    sigmas          = [ ((strat_mu - rfr) * sqrt(dpy)) / sharpe for sharpe in sharpes ]
    names           = [ str(sharpe) for sharpe in sharpes ]
    names[-1]       = "strategy"


    print(f"{'ul_price:':<20}{ul_price / ul_multiplier:<10.2f}")
    print(f"{'leverage:':<20}{leverage:0.2f}")
    print(f"{'reward:':<20}${reward:<10.2f}")
    print(f"{'risk (p98):':<20}${risk * 2:<10.2f}")
    print(f"{'max dd:':<20}${max_dd:<10.2f}")
    print("\n")
    

    if DOLLAR_STATS:
    
        print(f"{'name':<15}{'sharpe':<15}{'mean ($)':<15}{'stdev ($)':<15}{'failure (%)':<15}\n")
        print(f"{'ul_':<15}{ul__sharpe:<15.2f}{ul_price * (e**(ul__mu / dpy) - 1):<15.2f}{ul_price * (e**(ul__sigma * sqrt(1 / dpy)) - 1):<15.2f}{'-':<15}")

    else:

        print(f"{'name':<15}{'sharpe':<15}{'mean (bp)':<15}{'stdev (bp)':<15}{'failure (%)':<15}\n")
        print(f"{'ul_':<15}{ul__sharpe:<15.2f}{ul__mu / dpy:<15.4f}{ul__sigma * sqrt(1 / dpy):<15.4f}{'-':<15}")

    colors = {
        0.5:            "#0f112c",
        1.0:            "#171a42",
        1.5:            "#1e2358",
        2.0:            "#262c6e",
        3.0:            "#2d3483",
        4.0:            "#353d99",
        5.0:            "#3c46af",
        strat_sharpe:   "#444ec5"
        
    }

    n_charts        = len(colors) + 1
    x               = [ i for i in range(dpy) ]
    fig             = make_subplots(
                        rows                = n_charts,
                        cols                = 1,
                        subplot_titles      = tuple( f"{key:0.2f}" for key in colors.keys() ),
                        vertical_spacing    = 0.01
                    )
    
    fig.update_layout(
        autosize    = True,
        height      = n_charts * 400
    )

    row = 1

    for i in range(len(sharpes)):

        failed  = 0
        name    = names[i]
        sharpe  = sharpes[i]
        sigma   = sigmas[i]

        if sigma <= 0:

            continue

        for i in range(N_TRIALS):

            color   = colors[sharpe]
            y       = list(leverage * cumsum(normal(loc = strat_mu, scale = sigma, size = dpy)))
            x_      = x

            for j in range(len(y)):

                if y[j] <= max_dd_log:

                    failed  +=  1
                    color   =   "#FF0000"
                    y       =   y[:j + 1]
                    x_      =   x[:j + 1]

                    break

            
            if PLOT:

                if DOLLAR_STATS:

                    y = [ ul_price * e**j - ul_price for j in y ]

                trace = go.Scatter(
                    {
                        "x":        x_,
                        "y":        y,
                        "marker":   { "color": color },
                        "mode":     "markers",
                        "name":     f"{i}<br>sharpe = {sharpe:0.2f}"
                    }
                )

                fig.add_trace(trace, row = row, col = 1)
                fig.add_trace(trace, row = n_charts, col = 1)

        row             += 1
        failure_rate    =  failed / N_TRIALS * 100

        if DOLLAR_STATS:

            print(f"{name:<15}{sharpe:<15.2f}{ul_price * (e**(strat_mu) - 1):<15.2f}{ul_price * (e**(sigma) - 1):<15.2f}{failure_rate:<15.1f}")

        else:
            
            print(f"{name:<15}{sharpe:<15.2f}{strat_mu:<15.4f}{sigma:<15.4f}{failure_rate:<15.1f}")
        
    if PLOT:

        fig.show()