from    bisect  import  bisect_left, bisect_right
from    random  import  randint
import  polars  as      pl


SPX_DF      = pl.DataFrame()
SPX_DATES   = None


def get_spx():

    global SPX_DF
    global SPX_DATES

    if SPX_DF.is_empty():

        SPX_DF      = pl.read_csv("/Users/taylor/trading/index_data/SPX/SPX_1m.csv")
        SPX_DF      = SPX_DF.with_columns(pl.col("datetime").apply(lambda dt: dt.split()[0]).alias("date"))
        SPX_DF      = SPX_DF.with_columns(pl.col("datetime").apply(lambda dt: dt.split()[1]).alias("time"))
        SPX_DATES   = sorted(list(set(list(SPX_DF["date"]))))

    return SPX_DATES, SPX_DF


def get_random_spx_days(
        n:              int = 1,
        max_days_back:  int = 0
    ):

    SPX_DATES, SPX_DF = get_spx()

    i           = -max_days_back if max_days_back else 0
    dates       = SPX_DATES[i:]
    selected    = [ dates[randint(0, len(dates) - 1)] for i in range(n) ]
    dfs         = [ SPX_DF.filter(pl.col("date") == date) for date in selected ]
    res         = [ dates, dfs ]

    return res


def get_spx_days(
    start:  str = None, 
    end:    str = None
):

    SPX_DATES, SPX_DF = get_spx()

    i       = bisect_left(SPX_DATES, start) if start    else 0
    j       = bisect_right(SPX_DATES, end)  if end      else None
    dates   = SPX_DATES[i:j]
    dfs     = [ SPX_DF.filter(pl.col("date") == date) for date in dates ]
    res     = [ dates, dfs ]

    return res