from    math                    import  sqrt
from    numpy                   import  array, cumsum, mean, std
import  plotly.graph_objects    as      go
from    random                  import  choices


if __name__ == "__main__":

    init        = 250
    rfr         = 0.052
    n_plays     = 1000
    n_players   = 1000
    X           = [ i for i in range(n_plays) ]
    fig         = go.Figure()
    bankrolls   = []

    for player in range(n_players):
        
        bankroll = init + cumsum(choices([ 1, -1 ], [ 18/37, 19/37 ], k = n_plays))

        fig.add_trace(
            go.Scattergl(
                {
                    "x":        X,
                    "y":        bankroll,
                    "name":     f"player {player + 1}",
                    "mode":     "lines",
                    "marker":   { "color": "#FF0000" if bankroll[-1] < init else "#0000FF" }
                }
            )
        )

        bankrolls.append(bankroll)


    ending_pnls         = [ bankroll[-1] - init for bankroll in bankrolls ]
    average_bankroll    = [
                            mean([ bankroll[i] for bankroll in bankrolls ])
                            for i in range(n_plays)
                        ]
    
    fig.add_trace(
        go.Scattergl(
            {
                "x":        X,
                "y":        average_bankroll,
                "name":     "average",
                "mode":     "lines",
                "marker":   { "color": "#FF00FF" }
            }
        )
    )

    fig.show()

    mu_t            = 18/37 - 19/37
    sigma_t         = sqrt((18/37 * (1 - mu_t)**2 + 19/37 * (-1 - mu_t)**2))
    mu_t            = mu_t * n_plays
    sigma_t         = sigma_t * sqrt(n_plays)
    sharpe_t        = (mu_t / init - rfr) / (sigma_t / init)

    ending_pnls     = array([ bankroll[-1] - init for bankroll in bankrolls ])
    ending_returns  = ending_pnls / init * 100
    mu_o            = mean(ending_pnls)
    sigma_o         = std(ending_pnls) 
    sharpe_o        = (mu_o / init - rfr) / (sigma_o / init)

    best_result     = max(ending_pnls)
    worst_result    = min(ending_pnls)
    percent_winners = mean([ 1 if pnl > 0 else 0 for pnl in ending_pnls ]) * 100

    print(f"\ninitial bankroll:                 ${init}")
    print(f"risk free rate:                    {rfr:0.2f}")
    print(f"games per player, per year:        {n_plays}")
    print(f"number of players:                 {n_players}\n")
    
    print(f"theoretical expected return:      ${mu_t:<10.2f}{mu_t / init * 100:>10.2f}%")
    print(f"theoretical standard deviation:   ${sigma_t:<10.2f}{sigma_t / init * 100:>10.2f}%")
    print(f"theoretical sharpe ratio:          {sharpe_t:<10.2f}\n")

    print(f"observed expected return:         ${mu_o:<10.2f}{mu_o / init * 100:>10.2f}%")
    print(f"observed standard deviation:      ${sigma_o:<10.2f}{sigma_t / init * 100:>10.2f}%")
    print(f"observed sharpe ratio:             {sharpe_o:<10.2f}\n")
    
    print(f"percent_winners:                   {percent_winners:<10.2f}")
    print(f"biggest winner:                   ${best_result:<10.2f}{best_result / init * 100:>10.2f}%")
    print(f"biggest loser:                    ${worst_result:<10.2f}{worst_result / init * 100:>10.2f}%\n")