from    math                    import  e, log, sqrt
from    numpy                   import  cumsum
from    numpy.random            import  normal
import  plotly.graph_objects    as      go


if __name__ == "__main__":
    
    dpy             = 252
    reward          = 200
    risk            = 500 / 2
    es_price        = 5000 * 50
    max_dd          = 2000
    max_dd_log      = log(1 - max_dd / es_price)

    rfr             = 0.0392
    spx_sigma       = 0.1425
    spx_mu          = 0.101
    spx_sharpe      = ((spx_mu - rfr) / spx_sigma)

    rfr             = rfr / dpy
    strat_sigma     = log(1 + risk / es_price)
    strat_mu        = log(1 + reward / es_price)
    strat_sharpe    = ((strat_mu - rfr) / strat_sigma) * sqrt(dpy)

    print(f"{'':<10}{'mean':<10}{'stdev':<10}{'sharpe':<10}")
    print(f"{'spx:':<10}{spx_mu / dpy:>10.4f}{spx_sigma * sqrt(1 / dpy):>10.4f}{spx_sharpe:>10.2f}")
    print(f"{'strat:':<10}{strat_mu:>10.4f}{strat_sigma:>10.4f}{strat_sharpe:10.2f}\n")

    n_trials        = 10
    x               = [ i for i in range(dpy) ]
    fig             = go.Figure()

    print(f"{'sharpe':>10}{'failed%':>10}")

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

    for sharpe in [ 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0, strat_sharpe]:

        failed  = 0
        sigma   = ((strat_mu - rfr) * sqrt(dpy)) / sharpe

        for i in range(n_trials):

            color   = colors[sharpe]
            y       = cumsum(normal(loc = strat_mu, scale = sigma, size = dpy))
            
            if min(y) <= max_dd_log:

                failed  +=  1
                color   =   "#FF0000"

            #y = [ es_price * e**y_ for y_ in y ]

            fig.add_trace(
                go.Scattergl(
                    {
                        "x":        x,
                        "y":        y,
                        "marker":   { "color": color },
                        "mode":     "markers",
                        "name":     f"{i} sharpe = {sharpe:0.2f}"
                    }
                )
            )
        
        print(f"{sharpe:>10.2f}{(failed / n_trials)*100:>10.2f}")
        

    fig.show()

    pass

