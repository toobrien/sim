from    math                    import  log, sqrt
from    numpy                   import  cumsum, std
from    numpy.random            import  normal
import  plotly.graph_objects    as      go
from    plotly.subplots         import  make_subplots
from    random                  import  randint
from    scipy.stats             import  t
from    sys                     import  argv
from    utils.jump              import  jump_walk
from    utils.rtools            import  get_random_spx_days


DEBUG = True


def get_walk(method: str, args: dict):

    if method == "normal":

        y = list(cumsum(normal(**args)))

    elif method == "t":

        y  = list(cumsum(t.rvs(args["degrees"], loc = args["loc"], scale = args["scale"], size = args["size"])))

    elif method == "jump":

        y = jump_walk(**args)[0]

    return y


if __name__ == "__main__":

    num_charts  = int(argv[1])
    method      = "t"
    history     = 2500
    length      = 180
    min_start   = 10
    max_start   = 10
    dates, dfs  = get_random_spx_days(n = num_charts, max_days_back = history)
    fig         = make_subplots(
                    rows                = num_charts,
                    cols                = 1,
                    subplot_titles      = tuple( x + 1 for x in range(num_charts) ),
                    vertical_spacing    = 0.005
                )
    colors      = [
                    ( "#00FF00", "#FF0000" ),
                    ( "#FFFFFF", "#0000FF" )
                ]
    titles      = [ "R", "B" ]
    answers     = []

    fig.update_layout(
        autosize    = True,
        height      = num_charts * 800
    )

    for i in range(num_charts):

        date    = dates[i]
        df      = dfs[i]

        k       = randint(min_start, max_start)
        m       = k + length

        o       = list(df["open"])[k:m]
        h       = list(df["high"])[k:m]
        l       = list(df["low"])[k:m]
        c       = list(df["close"])[k:m]

        o_s     = [ log(o[j] / o[0]) for j in range(1, len(o)) ]
        h_s     = [ log(h[j] / o[0]) for j in range(1, len(h)) ]
        l_s     = [ log(l[j] / o[0]) for j in range(1, len(l)) ]
        c_s     = [ log(c[j] / o[0]) for j in range(1, len(c)) ]

        y       = [ log(c[j] / c[j - 1]) for j in range(1, len(c)) ]
        mu      = 0
        sigma   = std(y) * sqrt(1 / 60)
        count   = (len(c) + 1) * 60
        #y      = get_walk("normal", { "loc": mu, "scale": sigma, "size": count })
        #y      = get_walk("t", { "degrees": 2.75, "loc": mu, "scale": sigma, "size": count })
        y       = get_walk("jump", { "length": count, "sigma": 0.00002, "jump_scale": 3, "decay": 0.9, "max_shocks": 50, "mu": mu })

        o_n     = []
        h_n     = []
        l_n     = []
        c_n     = []

        prev_j  = 0

        for j in range(60, len(y), 60):

            candle  = y[prev_j:j]
            o_j     = candle[0]
            h_j     = max(candle)
            l_j     = min(candle)
            c_j     = candle[-1]

            o_n.append(o_j)
            h_n.append(h_j)
            l_n.append(l_j)
            c_n.append(c_j)

            prev_j = j

        noise   = randint(0, 1)
        answer  = f"{i + 1}\t{'N' if noise else 'S'}"
        trace   = ( o_n, h_n, l_n, c_n ) if noise else ( o_s, h_s, l_s, c_s )
        scheme  = colors[0]
        title   = i

        answers.append(answer)

        fig.add_trace(
            go.Candlestick(
                {
                    "x":        [ j for j in range(len(trace[0])) ],
                    "open":     trace[0],
                    "high":     trace[1],
                    "low":      trace[2],
                    "close":    trace[3],
                    "name":     title,
                    "increasing_line_color": scheme[0],
                    "decreasing_line_color": scheme[1]
                }
            ),
            row = i + 1,
            col = 1
        )

    if DEBUG:
    
        for i in range(num_charts):

            fig.layout.annotations[i].update(text = answers[i])

    fig.update_xaxes(rangeslider_visible = False)
    fig.show()

    for answer in answers:

        print(answer)