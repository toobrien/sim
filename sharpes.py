from    numpy                   import  cumsum
from    numpy.random            import  normal
from    math                    import  sqrt
import  plotly.graph_objects    as      go
from    sys                     import  argv


DPY = 256


if __name__ == "__main__":

    fig     = go.Figure()
    x       = [ i for i in range(DPY) ]
    mult    = float(argv[1])

    for mean, stdev in [ 
        ( 0.0003, 0.0125 ),
        ( 0.0003, 0.0100 ),
        ( 0.0003, 0.0075 ),
        ( 0.0003, 0.0050 ),
        ( 0.0003, 0.0035 ),
        ( 0.0003, 0.0025 ),
        ( 0.0003, 0.0010 )
    ]:
        mean    = mean * mult
        sharpe  = mean / stdev * sqrt(DPY)
        returns = normal(loc = mean, scale = stdev, size = DPY)
        y       = cumsum(returns)

        fig.add_trace(
            go.Scattergl(
                {
                    "x":    x,
                    "y":    y,
                    "name": f"{sharpe:0.2f}"
                }
            )
        )
    
    fig.show()