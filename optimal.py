import  plotly.graph_objects    as      go
from    math                    import  sqrt
from    numpy                   import  arange, array, concatenate, cumsum, full, mean, percentile, std, tile
from    numpy.random            import  normal
from    random                  import  randint, choice
from    scipy.stats             import  norm
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

    # 1-year return plot for index, noise, signal, and optimal
    
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


def fig_b(params: List):

    # densities, stats for N samples of M-year index, optimal trader, and random trader cumulative returns

    N               = int(params[0])
    M               = int(params[1]) * DPY
    half            = int(MPD / 2)
    signal          = concatenate((array([ -SIGNAL for _ in range(half)]), array([ SIGNAL for _ in range(half) ])))
    optimal_weights = concatenate((array([ -1 for _ in range(half)]), array([ 1 for _ in range(half) ])))
    population      = [ -1, 1 ]
    idx             = []
    opt             = []
    rnd             = []
    
    for _ in range(N):

        idx_ = []
        opt_ = []
        rnd_ = []

        for _ in range(M):

            idx_return  = normal(0, IDX_STD, MPD) + signal
            opt_return  = optimal_weights * idx_return
            cut         = randint(0, half - 1)
            weight      = choice(population)
            rnd_weight  = concatenate((full(cut, weight), full(half, -weight), full(half - cut, weight)))
            rnd_return  = rnd_weight * idx_return

            idx_.append(cumsum(idx_return)[-1])
            opt_.append(cumsum(opt_return)[-1])
            rnd_.append(cumsum(rnd_return)[-1])

        idx.append(cumsum(idx_)[-1])
        opt.append(cumsum(opt_)[-1])
        rnd.append(cumsum(rnd_)[-1])

    fig = go.Figure()

    traces = [
        ( idx, "idx" ),
        ( opt, "opt" ),
        ( rnd, "rnd" )
    ]

    print(f"{'':8}{'mean':>8}{"std":>8}{'losers':>8}")

    for trace in traces:

        X       = trace[0]
        mu      = mean(X)
        sigma   = std(X)
        X_      = arange(mu - 4 * sigma, mu + 4 * sigma, 0.01)
        nd      = norm(loc = mu, scale = sigma)
        Y_      = nd.pdf(X_)
        p_lose  = nd.cdf(0)
        
        fig.add_trace(
            go.Scatter(
                {
                    "x":    X_,
                    "y":    Y_,
                    "name": trace[1]
                }
            )
        )
        
        print(f"{trace[1]:<8}{mu * 100:>7.2f}%{sigma * 100:>7.2f}%{p_lose * 100:>7.2f}%")

    fig.show()


def fig_c(params: List):

    pass


if __name__ == "__main__":

    t0          = time()
    selection   = argv[1]
    params      = argv[2:]
    figures     = {
                    "a": fig_a,
                    "b": fig_b,
                    "c": fig_c
                }

    figures[selection](params)

    print(f"{time() - t0:0.1f}s")