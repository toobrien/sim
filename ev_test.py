from    math                    import  sqrt
from    numpy                   import  cumsum, mean, std
from    numpy.random            import  normal
import  plotly.graph_objects    as      go
from    plotly.subplots         import  make_subplots
from    time                    import  time


if __name__ == "__main__":

    n_trials    = 30
    n_steps     = 390
    sigma       = 0.01 * sqrt(1/390)
    drift       = 1e-5
    k           = 0
    m           = 100
    x           = list(range(n_steps))
    locs        = [ 0. for i in x ]
    fig         = make_subplots(
                    rows                = n_trials,
                    cols                = 1,
                    subplot_titles      = tuple( x + 1 for x in range(n_trials) ),
                    vertical_spacing    = 0.005
                )
    
    fig.update_layout(autosize = True, height = n_trials * 800)
    

    for i in range(k, m):

        locs[i] = drift

    for i in range(n_trials):

        a = cumsum([ normal(loc = 0, scale = sigma) for i in x ])
        b = cumsum([ normal(loc = locs[i], scale = sigma) for i in x ])

        for trace in [ 
            ( a, "a", "#FF0000" ), 
            ( b, "b", "#0000FF" )
        ]:

            fig.add_trace(
                go.Scatter(
                    {
                        "x":        x,
                        "y":        trace[0],
                        "name":     f"{trace[1]} {i + 1}",
                        "marker":   { "color": trace[2] }
                    }
                ),
                row = i + 1,
                col = 1
            )

    fig.show()