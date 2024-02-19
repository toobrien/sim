from    math                    import  e, log, sqrt
from    numpy                   import  cumsum
from    numpy.random            import  normal
import  plotly.graph_objects    as      go
from    plotly.subplots         import  make_subplots


if __name__ == "__main__":
    
    dpy             = 252
    es_price        = 5000 * 50
    rfr             = 0.0392
    
    reward          = 200
    risk            = 500 / 2
    max_dd          = 2000
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

    print(f"{'':<10}{'mean':>10}{'stdev':>10}")
    print(f"{spx_sharpe:<10.2f}{spx_mu / dpy:>10.4f}{spx_sigma * sqrt(1 / dpy):>10.4f}")

    for i in range(len(sharpes)):

        print(f"{sharpes[i]:<10.2f}{strat_mu:>10.4f}{sigmas[i]:>10.4f}")

    print()
    print(f"{'sharpe':>15}{'failed (%)':>15}")

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
    n_trials        = 10
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
        sharpe  = sharpes[i]
        sigma   = sigmas[i]

        for i in range(n_trials):

            color   = colors[sharpe]
            y       = list(cumsum(normal(loc = strat_mu, scale = sigma, size = dpy)))
            x_      = x

            for j in range(len(y)):

                if y[j] <= max_dd_log:

                    failed  +=  1
                    color   =   "#FF0000"
                    y       =   y[:j + 1]
                    x_      =   x[:j + 1]

                    break


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

        row += 1
        
        print(f"{sharpe:>15.2f}{(failed / n_trials)*100:>15.2f}")
        
    fig.show()

    pass

