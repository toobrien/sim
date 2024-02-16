from    math                    import  log
from    numpy                   import  cumsum, mean, std
from    numpy.random            import  normal
import  plotly.graph_objects    as      go
from    plotly.subplots         import  make_subplots
import  polars                  as      pl
from    random                  import  randint
from    sys                     import  argv
from    utils.rtools            import  get_random_spx_days


if __name__ == "__main__":

    num_charts  = int(argv[1])
    dates, dfs  = get_random_spx_days(n = num_charts)
    fig         = make_subplots(
                    rows                = num_charts,
                    cols                = 1,
                    subplot_titles      = tuple( x + 1 for x in range(num_charts) ),
                    vertical_spacing    = 0.005
                )
    answers     = []

    fig.update_layout(
        autosize    = True,
        height      = num_charts * 800,
    )

    for i in range(num_charts):

        date    = dates[i]
        df      = dfs[i]
        x       = list(range(0, len(df)))[:-5]
        y       = list(df["close"])[:-5]
        y       = [ log(y[j] / y[j - 1]) for j in range(1, len(y)) ][:-5]

        mu      = mean(y)
        sigma   = std(y)
        y_      = normal(loc = mu, scale = sigma, size = len(x))[:-6]
        color   = "#FF0000" if randint(0, 1) else "#0000FF"
        rcolor  = "#0000FF" if color == "#FF0000" else "#FF0000"

        for series in (
            ( y,    date,       color ),
            ( y_,   "random",   rcolor )
        ):

            fig.add_trace(
                go.Scatter(
                    {
                        "x":        x,
                        "y":        cumsum(series[0]),
                        "name":     series[1],
                        "marker":   { "color": series[2] }
                    }
                ),
                row = i + 1,
                col = 1
            )

        answers.append(f"{i + 1}.\t{'red' if rcolor == '#FF0000' else 'blue' }\t{date}")

    fig.show()

    for answer in answers:

        print(answer)