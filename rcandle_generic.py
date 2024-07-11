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
        ).with_columns(col("ts_event").dt.strftime(DT_FMT))
    
    return df


def run(
    df:     DataFrame, 
    n:      int,
    start:  str,
    end:    str
):

    dates = sorted(set([ dt.split("T")[0] for dt in list(df["ts_event"]) ]))

    pass


if __name__ == "__main__":

    t0      = time()
    df      = read_csv(f"../databento/csvs/{argv[1]}.csv")
    df      = strptime(df, "ts_event", "ts_event", DT_FMT, "America/Los_Angeles").sort("ts_event")
    df      = df.with_columns(col("ts_event").str.strptime(Datetime, DT_FMT).alias("ts_event"))
    n       = int(argv[2])
    start   = argv[3]
    end     = argv[4]

    print(df.tail(n = 10))

    if len(argv) > 4:

        df = resample(df, int(argv[5]))

        print(df.tail(n = 10))

    run(df, n, start, end) 

    print(f"{t0 - time():0.1f}s")