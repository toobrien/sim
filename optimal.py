from    copy                    import  deepcopy
from    math                    import  sqrt
from    numpy                   import  arange, array, concatenate, corrcoef, cumsum, full, histogram, mean, percentile, std, tile
from    numpy.random            import  normal
import  plotly.graph_objects    as      go
from    plotly.subplots         import  make_subplots
from    random                  import  randint, choice, sample
from    scipy.stats             import  norm, linregress
from    sys                     import  argv
from    time                    import  time
from    typing                  import  List


MPD     = 390
DPY     = 256
IDX_STD = 0.02 * sqrt(1 / MPD)
SIGNAL  = 0.0001 / MPD
DEBUG   = False


def get_returns_a(days: int):

    # 1 bp signal, 1-min

    half            = int(MPD / 2)
    signal          = tile(concatenate((array([ -SIGNAL for _ in range(half)]), array([ SIGNAL for _ in range(half) ]))), days)
    noise           = normal(0, IDX_STD, MPD * days)
    optimal_weights = tile(concatenate((array([ -1 for _ in range(half)]), array([ 1 for _ in range(half) ]))), days)
    population      = [ -1, 1 ]
    idx_returns     = noise + signal
    opt_returns     = idx_returns * optimal_weights
    rnd_weights     = []

    for _ in range(days):
    
        cut     = randint(0, half - 1)
        weight  = choice(population)
        weights = concatenate((full(cut, weight), full(half, -weight), full(half - cut, weight)))
        
        rnd_weights.extend(weights)

    rnd_return = rnd_weights * idx_returns

    return idx_returns, opt_returns, rnd_return


def get_returns_b(days: int):

    # 1% corr signal, daily

    sigma           = IDX_STD / sqrt(1 / MPD)       
    idx_returns     = normal(0, sigma, days)
    signal          = normal(0, sigma, days)
    to_sync         = sample(range(days), int(days * 0.01))
    signal[to_sync] = idx_returns[to_sync]
    weights         = signal / abs(signal)
    strat_returns   = weights * idx_returns

    if DEBUG:

        '''
        idx_returns_dly     = idx_returns.reshape(-1, MPD).sum(axis = 1)
        signal_dly          = signal.reshape(-1, MPD).sum(axis = 1)
        strat_returns_dly   = strat_returns.reshape(-1, MPD).sum(axis = 1)

        print(f"{corrcoef(idx_returns, signal)[0, 1]:8.4f}{corrcoef(idx_returns_dly, signal_dly)[0, 1]:8.4f}{corrcoef(idx_returns, strat_returns)[0, 1]:8.4f}{corrcoef(idx_returns_dly, strat_returns_dly)[0, 1]:8.4f}")
        '''

        print(f"{corrcoef(idx_returns, signal)[0, 1]:8.4f}{corrcoef(idx_returns, strat_returns)[0, 1]:8.4f}")

    return idx_returns, strat_returns, signal
    


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

    # p-densities, stats for N samples of M-year index, optimal trader, and random trader cumulative returns

    samples         = int(params[0])
    days            = int(params[1]) * DPY
    MODE            = params[2]
    r_func          = get_returns_a if MODE == "a" else get_returns_b
    idx             = []
    opt             = []
    rnd             = []
    
    for _ in range(samples):

        idx_returns, opt_returns, rnd_returns = r_func(days)

        idx.append(cumsum(idx_returns)[-1])
        opt.append(cumsum(opt_returns)[-1])

        if MODE == "a":
        
            rnd.append(cumsum(rnd_returns)[-1])

    fig = go.Figure()

    traces = [
        ( idx, "idx", "#0000FF", False ),
        ( opt, "opt", "#FF0000", True  )
    ]

    if MODE == "a":

        traces.append(( rnd, "rnd", "#CCCCCC", False ))

    print(f"{'':8}{'mean':>8}{"std":>8}{'losers':>8}")

    for trace in traces:

        X       = trace[0]
        mu      = mean(X)
        sigma   = std(X)
        nd      = norm(loc = mu, scale = sigma)
        X_      = arange(mu - 4 * sigma, mu + 4 * sigma, 0.01)
        Y_      = nd.pdf(X_)
        p_lose  = nd.cdf(0)
        
        fig.add_trace(
            go.Scatter(
                {
                    "x":        X_,
                    "y":        Y_,
                    "name":     trace[1],
                    "marker":   { "color": trace[2] }
                }
            )
        )

        fig.add_shape(
            type = "line",
            x0   = mu,
            x1   = mu,
            y0   = 0,
            y1   = max(Y_),
            line = { "color": trace[2], "dash": "dash" }
        )

        if trace[3]:

            fig.add_annotation(
                x           = mu,
                y           = -0.01,
                text        = f"{mu * 100:0.2f}%",
                showarrow   = False,
                font        = { "color": trace[2] }
            )
        
        print(f"{trace[1]:<8}{mu * 100:>7.2f}%{sigma * 100:>7.2f}%{p_lose * 100:>7.2f}%")

    fig.show()


def fig_c(params: List):

    # signal with 1% correlation, distplot and summary statistics

    N               = int(params[0]) * MPD * DPY
    M               = int(N * 0.01)
    noise           = normal(0, IDX_STD, N)
    beta            = normal(0, IDX_STD, N)
    index           = sample(range(N), M)
    alpha           = deepcopy(beta)
    alpha[index]    = noise[index]

    fig = make_subplots(rows = 2, cols = 1)

    X_beta                                      = arange(alpha.min(), alpha.max(), 0.0001 )
    X_alpha                                     = arange(alpha.min(), alpha.max(), 0.0001 )
    slope_beta, intercept_beta, r_beta, _, _    = linregress(beta, noise)
    slope_alpha, intercept_alpha, r_alpha, _, _ = linregress(alpha, noise)
    Y_beta                                      = intercept_beta + slope_beta * X_beta
    Y_alpha                                     = intercept_alpha + slope_alpha * X_alpha

    traces = [
                ( beta,     noise,     "0%",       1, "markers"    ),
                ( X_beta,   Y_beta,    "0% reg",   1, "lines"      ),
                ( alpha,    noise,     "1%",       2, "markers"    ),
                ( X_alpha,  Y_alpha,   "1% reg",   2, "lines"      )
            ]

    for trace in traces:
    
        fig.add_trace(
            go.Scattergl(
                {
                    "x":        trace[0],
                    "y":        trace[1],
                    "name":     trace[2],
                    "mode":     trace[4],
                    "marker":   { "size": 2 }
                }
            ),
            row = trace[3],
            col = 1
        )

    print(f"{'':10}{'corr':>10}{'r^2':>10}{'alpha':>10}{'beta':>10}")
    print(f"{'0%':10}{corrcoef(beta, noise)[0, 1]:>10.4f}{r_beta**2:>10.4f}{intercept_beta:>10.4f}{slope_beta:>10.4f}")
    print(f"{'1%:':10}{corrcoef(alpha, noise)[0, 1]:>10.4f}{r_alpha**2:>10.4f}{intercept_alpha:>10.4f}{slope_alpha:>10.4f}")

    fig.show()


def fig_d(params):

    # correlation check for 1% signal, daily

    NBINS   = 100
    N       = int(params[0])
    years   = int(params[1])
    corrs   = []

    for _ in range(N):

        idx_returns, strat_returns, signal = get_returns_b(years * DPY)

        corrs.append(corrcoef(idx_returns, signal)[0, 1])

    counts, _   = histogram(corrs, bins = NBINS)
    mu          = mean(corrs)
    sigma       = std(corrs)
    nd          = norm(loc = mu, scale = sigma)
    X           = arange(mu - 4 * sigma, mu + 4 * sigma, 0.001)
    Y           = nd.pdf(X)

    print(f"mu: {mu:8.4f}, std: {sigma:8.4f}")

    fig = go.Figure()

    fig.add_trace(
        go.Histogram(
                        x           = corrs,
                        nbinsx      = NBINS,
                        histnorm    = "probability", 
                        name        = "corrs"
                    )
    )
    
    Y = Y * (max(counts) / len(corrs)) / Y.max() # rescale

    fig.add_trace(
                    go.Scattergl(
                        {
                            "x":    X,
                            "y":    Y,
                            "name": "model"
                        }
                    )
                )

    fig.show()


def fig_e(params: List):

    # 1% corr (daily) equity curves, median and percentiles
    
    samples = params[0]
    years   = params[1]

    pass


if __name__ == "__main__":

    t0          = time()
    selection   = argv[1]
    params      = argv[2:]
    figures     = {
                    "a": fig_a,
                    "b": fig_b,
                    "c": fig_c,
                    "d": fig_d,
                    "e": fig_e
                }

    figures[selection](params)

    print(f"{time() - t0:0.1f}s")