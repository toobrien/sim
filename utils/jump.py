from    math                    import  log
from    numpy                   import  cumsum, mean, std
from    numpy.random            import  normal
import  plotly.graph_objects    as      go
from    plotly.subplots         import  make_subplots
from    random                  import  randint
from    utils.rtools            import  get_random_spx_days

'''
dates, dfs  = get_random_spx_days(1, 1500)
closes      = list(dfs[0]["close"])
closes      = [ log(closes[i] / closes[i - 1]) for i in range(len(closes)) ]

sigma       = std(closes)
mu          = mean(closes)
'''

def jump_walk(
    length:     float,
    sigma:      float,
    jump_scale: float,
    decay:      float,
    max_shocks: float,
    mu:         float = 0.
):
    
    n_shocks    = randint(0, max_shocks)
    arrival     = [ randint(0, length - 1) for i in range(n_shocks) ]
    vols        = []
    jump        = 0

    for i in range(length):

        if i in arrival:

            jump += sigma * abs(normal(loc = 0, scale = jump_scale))

        vols.append(sigma + jump)

        jump *= decay

    y = list(cumsum([ normal(loc = mu, scale = i) for i in vols ]))

    return [ y, vols ]


if __name__ == "__main__":

    length      = 120
    sigma       = 0.0005
    jump_scale  = 2
    decay       = 0.9
    max_shocks  = 5
    x           = [ i for i in range(length) ]
    sig, vols   = jump_walk(length, sigma, jump_scale, decay, max_shocks)

    fig = make_subplots(2, 1)

    fig.add_trace(
        go.Scatter(
            {
                "x":        x,
                "y":        sig,
                "marker":   { "color": "#FF0000" },
                "name":     "walk"
            }
        ),
        row = 1,
        col = 1
    )

    fig.add_trace(
        go.Scatter(
            {
                "x":        x,
                "y":        vols,
                "marker":   { "color": "#0000FF" },
                "name":     "vol"
            }
        ),
        row = 2,
        col = 1
    )

    fig.show()

    pass