from    math                    import  e, log, sqrt
from    numpy                   import  cumsum, std
from    numpy.random            import  normal
import  plotly.graph_objects    as      go
from    plotly.subplots         import  make_subplots
from    polars                  import  col, Config, DataFrame, Datetime, read_csv
from    random                  import  randint
from    scipy.stats             import  t
from    sys                     import  argv
from    time                    import  time
from    utils.dbn_util          import  strptime


# python rcandle_generic.py NQ.c.0_ohlcv-1m 10 06:30 13:00 5 1000

DOF     = 4
DEBUG   = False
DT_FMT  = "%Y-%m-%dT%H:%M:%S"
MODE    = "abs"

Config.set_tbl_cols(-1)
Config.set_tbl_rows(-1)


def resample(
    df:         DataFrame, 
    interval:   int
):

    # return df.downsample("a", rule="minute", n=5).agg({"b": ["first", "min", "max", "last"]})

    df = df.group_by_dynamic(
            df["ts_event"], 
            every   = f"{interval}m",
            closed  = "right"
        ).agg(
            [
                col("open").first().alias("open"),
                col("high").max().alias("high"),
                col("low").min().alias("low"),
                col("close").last().alias("close")
            ]
        ).with_columns(
            [
                col("ts_event").dt.strftime("%Y-%m-%d").alias("date"),
                col("ts_event").dt.strftime("%H:%M:%S").alias("time")
            ]
        )
    
    df = df.drop("ts_event")
    
    return df


def run(
    df:             DataFrame, 
    n:              int,
    start:          str,
    end:            str,
    interval:       int,
    max_days_back:  int
):

    fig         = make_subplots(
                    rows                = n,
                    cols                = 1,
                    subplot_titles      = tuple( x + 1 for x in range(n) ),
                    vertical_spacing    = 0.005
                )
    fig.update_layout(
        autosize    = True,
        height      = n * 800
    )
    colors      = [
                    ( "#00FF00", "#FF0000" ),
                    ( "#FFFFFF", "#0000FF" )
                ]
    answers     = []
    seen        = []
    i           = 0
    dates       = sorted(list(df["date"].unique()))
    n_rows      = 0

    if max_days_back:

        dates = dates[-max_days_back:]

    while i < n:

        j = randint(0, len(dates) - 1)

        if j in seen:

            continue
        
        else:

            seen.append(j)

        date    = dates[j]
        day     = df.filter(
                    (col("date") == date) &
                    (col("time") >= start) &
                    (col("time") <= end)
                )
        
        X       = list(day["time"])
        o       = list(day["open"])
        h       = list(day["high"])
        l       = list(day["low"])
        c       = list(day["close"])

        if not o:

            continue

        if n_rows == 0:

            n_rows = day.shape[0]
        
        elif day.shape[0] != n_rows:

            # ensure all days are the same length
            
            continue

        open_   = o[0]
        o_s     = [ log(o[j] / open_) for j in range(1, len(o)) ]
        h_s     = [ log(h[j] / open_) for j in range(1, len(h)) ]
        l_s     = [ log(l[j] / open_) for j in range(1, len(l)) ]
        c_s     = [ log(c[j] / open_) for j in range(1, len(c)) ]

        y       = [ log(c[j] / c[j - 1]) for j in range(1, len(c)) ]
        mu      = 0
        agg     = 60 * interval
        sigma   = std(y) * sqrt(1 / agg)
        count   = (len(c) + 1) * agg
        y       = list(cumsum(t.rvs(DOF, loc = mu, scale = sigma, size = count)))
        
        o_n     = []
        h_n     = []
        l_n     = []
        c_n     = []

        prev_k  = 0

        for k in range(agg, len(y), agg):

            candle  = y[prev_k:k]
            o_k     = candle[0]
            h_k     = max(candle)
            l_k     = min(candle)
            c_k     = candle[-1]

            o_n.append(o_k)
            h_n.append(h_k)
            l_n.append(l_k)
            c_n.append(c_k)

            prev_k = k
        
        noise   = randint(0, 1)
        answer  = f"{i + 1}\t{'N' if noise else 'S'}"
        scheme  = colors[0]
        title   = i
        trace   = [ o_n, h_n, l_n, c_n ] if noise else [ o_s, h_s, l_s, c_s ]

        if MODE == "abs":

            trace = [
                [ open_ * (e**(x) - 1) for x in trace[i] ]
                for i in range(len(trace))
            ]

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

        i += 1

    if DEBUG:
    
        for i in range(n):

            fig.layout.annotations[i].update(text = answers[i])

    fig.update_xaxes(rangeslider_visible = False)
    fig.show()

    for answer in answers:

        print(answer)

    pass


if __name__ == "__main__":

    t0              = time()
    df              = read_csv(f"../databento/csvs/{argv[1]}.csv")
    df              = strptime(df, "ts_event", "ts_event", DT_FMT, "America/Los_Angeles").sort("ts_event")
    df              = df.with_columns(col("ts_event").str.strptime(Datetime, DT_FMT).alias("ts_event"))
    n               = int(argv[2])
    start           = argv[3]
    end             = argv[4]
    interval        = 1
    max_days_back   = None

    #print(df.tail(n = 10))

    if len(argv) > 4:

        interval = int(argv[5])

        df = resample(df, interval)

        #print(df.tail(n = 10))

    if len(argv) > 5:

        max_days_back = int(argv[5])

    run(df, n, start, end, interval, max_days_back)

    print(f"{time() - t0:0.1f}s")