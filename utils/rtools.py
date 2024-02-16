from    random  import  randint
from    time    import  time
import  polars  as      pl


SPX_DF      = pl.DataFrame()
SPX_DATES   = None

def get_random_spx_days(
        n:              int = 1,
        max_days_back:  int = 0
    ):

    global SPX_DF
    global SPX_DATES

    if SPX_DF.is_empty():

        SPX_DF      = pl.read_csv("/Users/taylor/trading/index_data/SPX/SPX_1m.csv")
        SPX_DF      = SPX_DF.with_columns(pl.col("datetime").apply(lambda dt: dt.split()[0]).alias("date"))
        SPX_DF      = SPX_DF.with_columns(pl.col("datetime").apply(lambda dt: dt.split()[1]).alias("time"))
        SPX_DATES   = sorted(list(set(list(SPX_DF["date"]))))

    i           = -max_days_back if max_days_back else 0
    dates       = SPX_DATES[i:]
    selected    = [ dates[randint(0, len(dates) - 1)] for i in range(n) ]
    dfs         = [ SPX_DF.filter(pl.col("date") == date) for date in selected ]
    res         = [ dates, dfs ]

    return res