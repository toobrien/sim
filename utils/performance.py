from numpy import mean, std


def summarize(series: list, difference = False):

    returns = series

    if difference:
        
        returns = [ series[i] - series[i - 1] for i in range(1, len(series)) ]

    mu      = mean(returns)
    sigma   = std(returns)
    total   = sum(returns)

    return ( mu, sigma, total )