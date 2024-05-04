from    random                  import  choices
from    numpy                   import  cumsum
import  plotly.graph_objects    as      go
from    time                    import  time


if __name__ == "__main__":

    t0      = time()
    rolls   = 100_000
    sides   = [ -3, -2, -1, 1, 2, 3 ]
    probs   = [ 0.05, 0.20, 0.25, 0.25, 0.20, 0.05 ]
    sample  = choices(population = sides, weights = probs, k = rolls)
    total   = cumsum(sample)
    avg     = [ total[i] / (i + 1) for i in range(0, rolls) ]
    fig     = go.Figure()

    fig.add_trace(
        go.Scattergl(
            {
                "x":        list(range(len(avg))),
                "y":        avg,
                "name":     "average (fair)",
                "mode":     "lines",
                "marker":   { "color": "#0000FF" }
            }
        )
    )

    fig.add_trace(
        go.Scattergl(
            {
                "x":        list(range(len(total))),
                "y":        total,
                "name":     "total (fair)",
                "mode":     "lines",
                "marker":   { "color": "#FF00FF" }
            }
        )
    )

    fig.show()


    print(f"average (fair): ${avg[-1]:0.2f}")
    print(f"total (fair):   ${total[-1]:0.2f}")

    sides   = [ -3, -2, -1, 1.25, 2, 3 ]
    sample  = sample  = choices(population = sides, weights = probs, k = rolls)
    total   = cumsum(sample)
    avg     = [ total[i] / (i + 1) for i in range(0, rolls) ]
    fig     = go.Figure()

    fig.add_trace(
        go.Scattergl(
            {
                "x":        list(range(len(avg))),
                "y":        avg,
                "name":     "average",
                "mode":     "lines",
                "marker":   { "color": "#0000FF" }
            }
        )
    )

    fig.add_trace(
        go.Scattergl(
            {
                "x":        list(range(len(total))),
                "y":        total,
                "name":     "total",
                "mode":     "lines",
                "marker":   { "color": "#FF00FF" }
            }
        )
    )

    fig.show()

    print(f"average (edge): ${avg[-1]:0.2f}")
    print(f"total (edge):   ${total[-1]:0.2f}")
    print(f"{time() - t0:0.1}s")