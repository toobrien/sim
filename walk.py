import numpy                as      np
from   math                 import  log, e
import yfinance             as      yf
import plotly.graph_objects as      go


if __name__ == "__main__":

    data        = yf.download("EURUSD=X", start = "2001-01-01", end = "2024-01-01")
    closes      = data["Close"].values.tolist()
    closes      = [ log(closes[i] / closes[i - 1]) for i in range(1, len(closes)) ]
    mu          = np.mean(closes)
    sigma       = np.std(closes)
    init        = closes[2]
    closes_cum  = [ init ]

    for i in range(1, len(closes)):

        closes_cum.append(closes[i] + closes_cum[i - 1])

    fig = go.Figure()

    for name in [ "A", "B", "C", "D" ]:

        if name == "C":

            fig.add_trace(
                go.Scattergl(
                    {
                        "x":    [ i for i in range(len(closes_cum)) ],
                        "y":    [ init * csum for csum in closes_cum ],
                        "name": "C"
                    }
                )
            )

            continue

        chgs        = np.random.normal(mu, sigma, len(closes_cum))
        chgs_cum    = [ 0 ]

        for i in range(1, len(chgs)):

            chgs_cum.append(chgs[i] + chgs_cum[i - 1])    

        fig.add_trace(
            go.Scattergl(
                {
                    "x":    [ i for i in range(len(chgs_cum))],
                    "y":    [ init * csum for csum in chgs_cum ],
                    "name": name
                }
            )
        )



    fig.show()