from math           import  log, sqrt
from numpy.random   import  normal


if __name__ == "__main__":

    rfr         = 0.04 / 252
    spx_sigma   = 0.1531 * sqrt(1 / 252)
    spx_mu      = 0.1063 / 252
    spx_sharpe  = ((spx_mu - rfr) / spx_sigma) * sqrt(252)

    strat_sigma     = (250 * 252) / (5000 * 50) * sqrt(1/252)
    strat_mu        = (200 * 252) / (5000 * 50) / 252
    strat_sharpe    = ((strat_mu - rfr) / strat_sigma) * sqrt(252)

    print(f"spx:        {spx_sharpe:0.2f}")
    print(f"strat:      {strat_sharpe:0.2f}")

    pass

