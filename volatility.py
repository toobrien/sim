from    math                    import  e
from    numpy                   import  array, cumsum, max, mean, median, min
from    numpy.random            import  normal
import  plotly.graph_objects    as      go
from    time                    import  time


if __name__ == "__main__":

    t0      = time()
    mu      = 0.0003
    sig_a   = 0.0100
    sig_b   = 0.0200
    n       = 10_000
    balance = 1
    a_rets  = array([ cumsum(normal(loc = mu, scale = sig_a, size = n)) for _ in range(n) ])
    b_rets  = array([ cumsum(normal(loc = mu, scale = sig_b, size = n)) for _ in range(n) ])
    X       = [ i for i in range(n) ]
    a_med   = mean(a_rets, axis = 0)
    a_max   = max(a_rets, axis = 0)
    a_min   = min(a_rets, axis = 0)
    b_med   = mean(b_rets, axis = 0)
    b_max   = max(b_rets, axis = 0)
    b_min   = min(b_rets, axis = 0)
    a_bal_m = balance * e**a_med
    a_bal_h = balance * e**a_max
    a_bal_l = balance * e**a_min
    b_bal_m = balance * e**b_med
    b_bal_h = balance * e**b_max
    b_bal_l = balance * e**b_min

    fig     = go.Figure()
    traces  = [
                ( a_bal_m,  f"a mean {mu:0.4f}, {sig_a:0.4f}", "#0000FF"),
                #( a_bal_h,  f"a max  {mu:0.4f}, {sig_a:0.4f}", "#0000FF"),
                #( a_bal_l,  f"a min  {mu:0.4f}, {sig_a:0.4f}", "#0000FF"),
                ( b_bal_m,  f"b mean {mu:0.4f}, {sig_b:0.4f}", "#FF0000"),
                #( b_bal_h,  f"b max  {mu:0.4f}, {sig_b:0.4f}", "#FF0000"),
                #( b_bal_l,  f"b min  {mu:0.4f}, {sig_b:0.4f}", "#FF0000")
            ]

    for trace in traces:
    
        fig.add_trace(
            go.Scattergl(
                {
                    "x":    X,
                    "y":    trace[0],
                    "name": trace[1]
                }
            )
        )

    fig.show()

    print(f"{time() - t0:0.1f}s")