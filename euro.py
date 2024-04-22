from    enum                    import  IntEnum
from    math                    import  log
from    numpy                   import  array
from    polars                  import  col
import  plotly.express          as      px
import  plotly.graph_objects    as      go
from    plotly.subplots         import  make_subplots
from    sklearn.linear_model    import  LinearRegression
from    sys                     import  argv
from    utils.rtools            import  get_spx_days


class r(IntEnum):

    datetime    = 0
    open        = 1
    high        = 2
    low         = 3
    close       = 4
    date        = 5
    time        = 6


if __name__ == "__main__":

    start   = argv[1]
    end     = argv[2]

    dates, dfs = get_spx_days(start, end)

    to_ret      = {}
    from_ret    = {}

    for df in dfs:

        df = df.filter((col("time") >= "09:30:00") & (col("time") <= "15:59:00"))

        open_   = log(df.row(0)[r.open])
        close_  = log(df.row(-1)[r.close])

        for row in df.iter_rows():

            time    = row[r.time]
            close   = log(row[r.close])

            #if abs(close - open_) < 0.01:

                #continue

            if time not in to_ret:

                to_ret[time] = []
            
            to_ret[time].append(close - open_)
            
            if time not in from_ret:
                
                from_ret[time] = []

            from_ret[time].append(close_ - close)

model   = LinearRegression()
times   = sorted(list(to_ret.keys()))
b_      = []
r2_     = []

for time in times:

    x = array(to_ret[time]).reshape(-1, 1)
    y = from_ret[time]

    model.fit(x, y)

    b = model.coef_[0]
    a = model.intercept_

    r2 = model.score(x, y)

    '''
    if time == "12:30:00":

        fig = px.scatter(x = to_ret[time], y = y, trendline = "ols")
        fig.show()

    print(f"{time:<15}{b:<8.4f}{a:<8.4f}{r2:<8.4f}")
    '''

    b_.append(b)
    r2_.append(r2)

fig = make_subplots(rows = 2, cols = 1)

fig.add_trace(
    go.Bar(
        {
            "x":    times,
            "y":    b_,
            "name": "beta"
        }
    ),
    row = 1, col = 1
)

fig.add_trace(
    go.Bar(
        {
            "x":    times[:-1],
            "y":    r2_[:-1],
            "name": "r^2"
        }
    ),
    row = 2,
    col = 1
)

fig.show()