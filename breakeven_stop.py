import  random
import  numpy                   as      np
import  plotly.graph_objects    as      go
from    plotly.subplots         import  make_subplots


if __name__ == "__main__":

    steps       =   100
    trials      =   1000
    p           =   0.55
    stop        =   -5
    target      =   5
    fig         =   make_subplots(
                    rows            = 3,
                    cols            = 2,
                    column_widths   = [ 0.7, 0.3 ],
                )
    breakeven   = []
    normal      = []
    be_culled   = []
    cull_stop   = 0
    cull_loss   = 0

    for i in range(trials):

        raw_sample  = random.choices([ 1, -1 ], weights = [ p, 1 - p ], k = steps)
        raw_sample  = list(np.cumsum(raw_sample))
        be_y        = raw_sample
        norm_y      = raw_sample
        be_color    = "#0000FF"
        norm_color  = "#0000FF"
        target_hit  = False
        stop_hit    = False
        culled      = False

        for j in range(len(raw_sample)):

            cur = raw_sample[j]

            if cur == target:

                target_hit = True

            elif target_hit and cur == 0:

                be_y        = raw_sample[:j + 1]
                be_color    = "#FF00FF"
                stop_hit    = True
                culled      = True

                break

            elif cur == stop:

                be_y        = raw_sample[:j + 1]
                be_color    = "#FF0000" 
                stop_hit    = True

                break

        breakeven.append(be_y[-1] if stop_hit else raw_sample[-1])

        stop_hit = False

        for j in range(len(raw_sample)):

            cur = raw_sample[j]

            if cur == stop:

                norm_y      = raw_sample[:j + 1]
                norm_color  = "#FF0000"
                stop_hit    = True

                break

        normal.append(norm_y[-1] if stop_hit else raw_sample[-1])
        
        norm_trace = {
            "x":        [ j for j in range(len(norm_y)) ],
            "y":        norm_y,
            "name":     f"{i} norm",
            "marker":   {
                "color": norm_color
            }
        }

        fig.add_trace(
            go.Scattergl(norm_trace),
            row = 1,
            col = 1
        )

        be_trace = {
            "x":        [ j for j in range(len(be_y)) ],
            "y":        be_y,
            "name":     f"{i} breakeven",
            "marker":   {
                "color": be_color
            }
        }

        fig.add_trace(
            go.Scattergl(be_trace),
            row = 2,
            col = 1
        )

        if culled:

            if stop_hit:

                cull_stop += 1

            be_culled.append(normal[-1])

            if normal[-1] < 0:

                cull_loss += 1

            norm_trace["name"] = f"{i} norm_"

            fig.add_trace(
                go.Scattergl(norm_trace),
                row = 3, 
                col = 1
            )

    fig.add_trace(
        go.Histogram(
            {
                "x":        normal,
                "name":     "no trailing stop",
            }
        ),
        row = 1,
        col = 2
    )

    fig.add_trace(
        go.Histogram(
            {
                "x":        breakeven,
                "name":     "with trailing stop",
            }
        ),
        row = 2,
        col = 2
    )

    fig.add_trace(
        go.Histogram(
            {
                "x":    be_culled,
                "name": "stopped at breakeven"
                "nbinsx"
            }
        ),
        row = 3,
        col = 2
    )

    fig.show()

    print(f"avg (no trail): {np.mean(normal):0.1f}")
    print(f"25% (no trail): {np.percentile(normal, 25)}")
    print(f"50% (no trail): {np.percentile(normal, 50)}")
    print(f"75% (no trail): {np.percentile(normal, 75)}")

    print("\n")

    print(f"avg (w/ trail): {np.mean(breakeven):0.1f}")
    print(f"25% (w/ trail): {np.percentile(breakeven, 25)}")
    print(f"50% (w/ trail): {np.percentile(breakeven, 50)}")
    print(f"75% (w/ trail): {np.percentile(breakeven, 75)}")

    print("\n")

    print(f"avg    (culled): {np.mean(be_culled):0.1f}")
    print(f"stop % (culled): {cull_stop / len(be_culled) * 100:0.1f}%")