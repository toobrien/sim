from    math                    import  log, sqrt
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


# python rcandle_generic.py NQ.c.0_ohlcv-1m 10 06:30 13:00 5


DT_FMT = "%Y-%m-%dT%H:%M:%S"

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
    df:         DataFrame, 
    n:          int,
    start:      str,
    end:        str,
    interval:   int
):

    dates = sorted(list(df["date"].unique()))

    for i in range(n):

        j       = randint(0, len(dates) - 1)
        date    = dates[j]
        day     = df.filter(
                    (col("date") == date) &
                    (col("time") >= start) &
                    (col("time") <= end)
                )
        
        o       = list(day["open"])
        h       = list(day["high"])
        l       = list(day["low"])
        c       = list(day["close"])

        o_s     = [ log(o[j] / o[0]) for j in range(1, len(o)) ]
        h_s     = [ log(h[j] / o[0]) for j in range(1, len(h)) ]
        l_s     = [ log(l[j] / o[0]) for j in range(1, len(l)) ]
        c_s     = [ log(c[j] / o[0]) for j in range(1, len(c)) ]

        y       = [ log(c[j] / c[j - 1]) for j in range(1, len(c)) ]
        mu      = 0
        agg     = 60 * interval
        sigma   = std(y) * sqrt(1 / agg)
        count   = (len(c) + 1) * agg
        y       = list(cumsum(t.rvs(2.5, loc = mu, scale = sigma, size = count)))
        
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
        
        pass

    pass


if __name__ == "__main__":

    t0          = time()
    df          = read_csv(f"../databento/csvs/{argv[1]}.csv")
    df          = strptime(df, "ts_event", "ts_event", DT_FMT, "America/Los_Angeles").sort("ts_event")
    df          = df.with_columns(col("ts_event").str.strptime(Datetime, DT_FMT).alias("ts_event"))
    n           = int(argv[2])
    start       = argv[3]
    end         = argv[4]
    interval    = 1

    #print(df.tail(n = 10))

    if len(argv) > 4:

        interval = int(argv[5])

        df = resample(df, interval)

        #print(df.tail(n = 10))

    run(df, n, start, end, interval) 

    print(f"{t0 - time():0.1f}s")