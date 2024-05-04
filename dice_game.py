from    random                  import  choices
from    numpy                   import  cumsum, mean, std
import  plotly.figure_factory   as      ff
import  plotly.graph_objects    as      go
from    plotly.subplots         import  make_subplots
from    time                    import  time


def example_a():

    t0      = time()
    rolls   = 100_000
    sides   = [ -3, -2, -1, 1, 2, 3 ]
    probs   = [ 0.05, 0.20, 0.25, 0.25, 0.20, 0.05 ]
    sample  = choices(population = sides, weights = probs, k = rolls)
    total   = cumsum(sample)
    avg     = [ total[i] / (i + 1) for i in range(0, rolls) ]
    fig     = make_subplots(specs = [ [ {"secondary_y": True } ] ])

    fig.add_trace(
        go.Scattergl(
            {
                "x":            list(range(len(avg))),
                "y":            avg,
                "name":         "average",
                "mode":         "lines",
                "marker":       { "color": "#0000FF" }
            }
        ),
        secondary_y = False
    )

    fig.add_trace(
        go.Scattergl(
            {
                "x":            list(range(len(total))),
                "y":            total,
                "name":         "total",
                "mode":         "lines",
                "marker":       { "color": "#FF00FF" }
            }
        ),
        secondary_y = True
    )

    fig.show()

    print(f"average (fair): ${avg[-1]:0.2f}")
    print(f"total (fair):   ${total[-1]:0.2f}")

    sides   = [ -3, -2, -1, 1.25, 2, 3 ]
    sample  = sample  = choices(population = sides, weights = probs, k = rolls)
    total   = cumsum(sample)
    avg     = [ total[i] / (i + 1) for i in range(0, rolls) ]
    fig     = make_subplots(specs = [ [ {"secondary_y": True } ] ])

    fig.add_trace(
        go.Scattergl(
            {
                "x":            list(range(len(avg))),
                "y":            avg,
                "name":         "average (edge)",
                "mode":         "lines",
                "marker":       { "color": "#0000FF" }
            }
        ),
        secondary_y = False
    )

    fig.add_trace(
        go.Scattergl(
            {
                "x":            list(range(len(total))),
                "y":            total,
                "name":         "total (edge)",
                "mode":         "lines",
                "marker":       { "color": "#FF00FF" }
            }
        ),
        secondary_y = True
    )

    fig.show()

    print(f"average (edge): ${avg[-1]:0.2f}")
    print(f"total (edge):   ${total[-1]:0.2f}")
    print(f"{time() - t0:0.1f}s")


def example_b():

    t0 = time()
    rolls           = 10_000
    traders         = 10_000
    fair_sides      = [ -3, -2, -1, 1, 2, 3 ]
    edge_sides      = [ -3, -2, -1, 1.25, 2, 3 ]
    probs           = [ 0.05, 0.20, 0.25, 0.25, 0.20, 0.05 ]
    fair_sample     = [ 
                        sum(choices(population = fair_sides, weights = probs, k = rolls))
                        for i in range(traders)
                    ]
    edge_sample     = [
                        sum(choices(population = edge_sides, weights = probs, k = rolls))
                        for i in range(traders)
                    ]
    
    fig = ff.create_distplot(
        [ fair_sample, edge_sample ],
        [ "fair die", "edge die" ],
        curve_type  = "normal",
        show_hist   = True,
        show_rug    = False
    )

    fig.show()
    
    print(f"average (fair): {mean(fair_sample):0.2f}")
    print(f"stdev (fair):   {std(fair_sample):0.2f}")
    print(f"average (edge): {mean(edge_sample):0.2f}")
    print(f"stdev (edge):   {std(edge_sample):0.2f}")
    print(f"{time() - t0:0.1f}s")



if __name__ == "__main__":

    #example_a()

    example_b()