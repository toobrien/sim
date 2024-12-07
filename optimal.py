import  plotly.graph_objects    as      go
from    plotly.subplots         import  make_subplots
from    math                    import  sqrt
from    numpy                   import  array, concatenate, cumsum, percentile, tile
from    numpy.random            import  normal
from    sys                     import  argv
from    time                    import  time
from    typing                  import  List


MPD     = 390
DPY     = 256
IDX_STD = 0.02 * sqrt(1 / MPD)
SIGNAL  = 0.0001 / MPD


def check_dist(x: List):

    fig = go.Figure()

    fig.add_trace(go.Histogram(x = sorted(x)))

    print(percentile(x, [ 2.5, 15, 50, 85, 97.5 ]))

    fig.show()


def fig_a(params: List):
    
    fig             = go.Figure()
    N               = MPD * DPY
    half            = int(MPD / 2)
    noise           = normal(0, IDX_STD, N)
    idx_returns     = array(noise)
    signal          = tile(concatenate((array([ -SIGNAL for _ in range(half)]), array([ SIGNAL for _ in range(half) ]))), DPY)
    idx_returns     = noise + signal
    optimal_weights = tile(concatenate((array([ -1 for _ in range(half)]), array([ 1 for _ in range(half) ]))), DPY)
    optimal_returns = idx_returns * optimal_weights

    for trace in [ 
        ( idx_returns,      "idx_returns"       ),
        ( noise,            "noise"             ),
        ( signal,           "signal"            ),
        ( optimal_returns,  "optimal_returns"   )
    ]:

        fig.add_trace(
            {
                "x":    [ i for i in range(len(idx_returns)) ],
                "y":    cumsum(trace[0]),
                "name": trace[1]
            }
        )

    fig.show()

    pass


if __name__ == "__main__":

    t0          = time()
    selection   = argv[1]
    params      = argv[2:]
    figures     = {
                    "a": fig_a
                }

    figures[selection](params)

    print(f"{time() - t0:0.1f}s")