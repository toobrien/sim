import  plotly.graph_objects    as      go
from    plotly.subplots         import  make_subplots
from    math                    import  sqrt
from    numpy                   import  cumsum, percentile
from    numpy.random            import  normal
from    sys                     import  argv
from    time                    import  time
from    typing                  import  List


MPD     = 390
DPY     = 256
IDX_STD = 0.02 * sqrt(1 / MPD)
SIGNAL  = 0.01
NOISE   = 1 - SIGNAL


def check_dist(x: List):

    fig = go.Figure()

    fig.add_trace(go.Histogram(x = sorted(x)))

    print(percentile(x, [ 2.5, 15, 50, 85, 97.5 ]))

    fig.show()


def fig_a(params: List):
    
    fig             = go.Figure()
    N               = MPD * DPY
    noise           = normal(0, IDX_STD, N) * NOISE
    signal          = abs(normal(0, IDX_STD, N)) * SIGNAL
    half            = int(MPD / 2)
    optimal_weights = [ 1 for i in range(N)]

    for i in range(DPY):

        for j in range(half):

            signal[i * MPD + j] = -signal[i * MPD + j]

    idx_returns = signal + noise

    for i in range(DPY):

        j = i * MPD

        for k in range(half):

            optimal_weights[j + k] = -1

    optimal_returns = idx_returns * optimal_weights

    for trace in [ 
        ( idx_returns,      "idx_returns"       ),
        ( noise,            "noise"             ),
        ( signal,           "signal"            ),
        ( optimal_returns,  "optimal_returns"   )
    ]:

        fig.add_trace(
            {
                "x":    [ i for i in range(MPD) ],
                "y":    cumsum(trace[0][0:MPD]),
                "name": trace[1]
            }
        )

    '''
    x = [
            cumsum(normal(0, IDX_STD, MPD))[-1]
            for i in range(10_000)
        ]
    
    check_dist(x)
    '''

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