from    math                    import  sqrt
from    numpy                   import  cumsum
from    numpy.random            import  normal
import  plotly.figure_factory   as      ff
import  plotly.graph_objects    as      go
from    plotly.subplots         import  make_subplots
from    time                    import  time
from    utils.performance       import  summarize


if __name__ == "__main__":

    t0          = time()
    n_trials    = 1080
    n_charts    = 30
    n_steps     = 390
    sigma       = 4.8e-4
    drift       = 1.67e-5
    a           = []
    b           = []
    b_0j        = []
    b_jn        = []
    j           = 60
    x           = list(range(n_steps))
    locs        = [ 0. for i in x ]
    fig         = make_subplots(
                    rows                = n_charts,
                    cols                = 1,
                    subplot_titles      = tuple( x + 1 for x in range(n_charts) ),
                    vertical_spacing    = 0.0025
                )
    
    fig.update_layout(autosize = True, height = n_charts * 600)
    

    for i in range(0, j):

        locs[i] = drift

    for i in range(n_trials):

        a_ = cumsum([ normal(loc = 0, scale = sigma) for i in x ])
        b_ = cumsum([ normal(loc = locs[i], scale = sigma) for i in x ])

        a.append(a_[-1])
        b.append(b_[-1])
        b_0j.append(b_[j - 1])
        b_jn.append(b_[-1] - b_[j])

        if i < n_charts:

            for trace in [ 
                ( a_, "a", "#FF0000" ), 
                ( b_, "b", "#0000FF" )
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

    r           = 0.05/252
    a_perf      = summarize(a, rfr = r)
    b_perf      = summarize(b, rfr = r)
    b_0j_perf   = summarize(b_0j, rfr = r)
    b_jn_perf   = summarize(b_jn, rfr = r)

    print(f"{'':10}{'mu':>10}{'sigma':>10}{'total':>10}{'sharpe':>10}")
    print(f"{'r:':>10}{a_perf[0]:10.4f}{a_perf[1]:10.4f}{a_perf[2]:10.2f}{a_perf[3]*sqrt(252):10.2f}")
    print(f"{'b:':>10}{b_perf[0]:10.4f}{b_perf[1]:10.4f}{b_perf[2]:10.2f}{b_perf[3]*sqrt(252):10.2f}")
    print(f"{'b_sig:':>10}{b_0j_perf[0]:10.4f}{b_0j_perf[1]:10.4f}{b_0j_perf[2]:10.2f}{b_0j_perf[3]*sqrt(252):10.2f}")
    print(f"{'b_noise:':>10}{b_jn_perf[0]:10.4f}{b_jn_perf[1]:10.4f}{b_jn_perf[2]:10.2f}{b_jn_perf[3]*sqrt(252):10.2f}")

    fig = ff.create_distplot(
        [ a, b, b_0j, b_jn ],
        [ "r", "b", "b_sig", "b_noise" ],
        curve_type  = "normal",
        bin_size    = 1e-3,
        show_hist   = False
    )

    fig.show()

    fig = go.Figure()

    for trace in [
        ( cumsum(b_0j), f"pnl_b_sig_only, sharpe = {b_0j_perf[3]*sqrt(252):0.2f}", "#FF00FF" ),
        ( cumsum(b), f"pnl_b, sharpe = {b_perf[3]*sqrt(252):0.2f}", "#0000FF" ),
        ( cumsum(a), f"pnl_a, sharpe = {a_perf[3]*sqrt(252):0.2f}", "#FF0000")
    ]:
        
        fig.add_trace(
            go.Scatter(
                {
                    "x":    [ i for i in range(n_trials) ],
                    "y":    trace[0],
                    "name": trace[1],
                    "marker":   { "color": trace[2] }
                }
            )
        )

    fig.show()

    print(f"{time() - t0:0.1f}s")