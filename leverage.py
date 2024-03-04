from    math                    import  e, log, sqrt
from    numpy                   import  cumsum
from    numpy.random            import  normal
import  plotly.graph_objects    as      go
from    plotly.subplots         import  make_subplots
from    sys                     import  argv


PLOT            = int(argv[1])
DOLLAR_STATS    = int(argv[2])
N_TRIALS        = int(argv[3])


if __name__ == "__main__":
    
    dpy             = 252
    es_price        = 5000 * 50
    rfr             = 0.0392

    leverage        = 0.2
    reward          = 120
    risk            = 605
    max_dd          = 1250
    max_dd_log      = log(1 - max_dd / es_price)

    spx_sigma       = 0.1425
    spx_mu          = 0.101
    spx_sharpe      = ((spx_mu - rfr) / spx_sigma)

    rfr             = rfr / dpy
    strat_sigma     = log(1 + risk / es_price)
    strat_mu        = log(1 + reward / es_price)
    strat_sharpe    = ((strat_mu - rfr) / strat_sigma) * sqrt(dpy)

    sharpes         = [ 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0, strat_sharpe ]
    sigmas          = [ ((strat_mu - rfr) * sqrt(dpy)) / sharpe for sharpe in sharpes ]
    names           = [ str(sharpe) for sharpe in sharpes ]
    names[-1]       = "strategy"


    print(f"{'es_price:':<20}{es_price / 50:<10.2f}")
    print(f"{'leverage:':<20}{leverage:0.2f}")
    print(f"{'reward:':<20}${reward:<10.2f}")
    print(f"{'risk (p98):':<20}${risk * 2:<10.2f}")
    print(f"{'max dd:':<20}${max_dd:<10.2f}")
    print("\n")
    

    if DOLLAR_STATS:
    
        print(f"{'name':<15}{'sharpe':<15}{'mean ($)':<15}{'stdev ($)':<15}{'failure (%)':<15}\n")
        print(f"{'spx':<15}{spx_sharpe:<15.2f}{es_price * (e**(spx_mu / dpy) - 1):<15.2f}{es_price * (e**(spx_sigma * sqrt(1 / dpy)) - 1):<15.2f}{'-':<15}")

    else:

        print(f"{'name':<15}{'sharpe':<15}{'mean (bp)':<15}{'stdev (bp)':<15}{'failure (%)':<15}\n")
        print(f"{'spx':<15}{spx_sharpe:<15.2f}{spx_mu / dpy:<15.4f}{spx_sigma * sqrt(1 / dpy):<15.4f}{'-':<15}")

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

                    y = [ es_price * e**j - es_price for j in y ]

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

            print(f"{name:<15}{sharpe:<15.2f}{es_price * (e**(strat_mu) - 1):<15.2f}{es_price * (e**(sigma) - 1):<15.2f}{failure_rate:<15.1f}")

        else:
            
            print(f"{name:<15}{sharpe:<15.2f}{strat_mu:<15.4f}{sigma:<15.4f}{failure_rate:<15.1f}")
        
    if PLOT:

        fig.show()