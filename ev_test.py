from    math                    import  sqrt
from    numpy                   import  cumsum, mean, std
from    numpy.random            import  normal
import  plotly.figure_factory   as      ff
import  plotly.graph_objects    as      go
from    plotly.subplots         import  make_subplots
from    time                    import  time
from    utils.performance       import  summarize

if __name__ == "__main__":

    n_trials    = 1000
    n_charts    = 50
    n_steps     = 390
    sigma       = 0.01 * sqrt(1/390)
    drift       = 25e-6
    a_          = []
    b_          = []
    b_km        = []
    k           = 0
    m           = 100
    x           = list(range(n_steps))
    locs        = [ 0. for i in x ]
    fig         = make_subplots(
                    rows                = n_charts,
                    cols                = 1,
                    subplot_titles      = tuple( x + 1 for x in range(n_charts) ),
                    vertical_spacing    = 0.001
                )
    
    fig.update_layout(autosize = True, height = n_charts * 600)
    

    for i in range(k, m):

        locs[i] = drift

    for i in range(n_trials):

        a = [ normal(loc = 0, scale = sigma) for i in x ]
        b = [ normal(loc = locs[i], scale = sigma) for i in x ]

        a_.append(a[-1])
        b_.append(b[-1])
        b_km.append(cumsum(b[k:m])[-1])

        if i < n_charts:

            for trace in [ 
                ( cumsum(a), "a", "#FF0000" ), 
                ( cumsum(b), "b", "#0000FF" )
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

    a_perf  = summarize(a_)
    b_perf  = summarize(b_)
    km_perf = summarize(b_km)

    print(f"a:  {a_perf[0]:0.5f}\t{a_perf[1]:0.5f}")
    print(f"b:  {b_perf[0]:0.5f}\t{b_perf[1]:0.5f}")
    print(f"km: {km_perf[0]:0.5f}\t{km_perf[1]:0.5f}")

    fig = go.Figure()

    for trace in [ 
        ( a_,   "a" ),
        ( b_,   "b" ),
        ( b_km, "b_km" )
    ]:

        fig.add_trace(go.Histogram(x = trace[0], name = trace[1]))

    fig.show()