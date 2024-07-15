from bisect import bisect_left
from numpy  import cumsum, mean
from random import choices
from sys    import argv


if __name__ == "__main__":

    add_costs   = int(argv[1])
    costs       = 0.33 if add_costs else 0
    n_traders   = 10_000
    n_trades    = 1_000
    max_loss    = 20
    risks       = [ i for i in range(1, max_loss + 1) ]

    print(f"\nnum traders:    {n_traders}")
    print(f"cost per trade: {costs:0.2f}")
    print(f"num trades:     {n_trades}")
    print(f"max loss:       {max_loss}\n")

    print(f"{'reward:risk':20}{'survival rate':20}{'avg trades survived'}\n")

    for r in risks:

        p_w     = r / (1 + r)
        p_l     = 1 - p_w
        results = []
        lens    = []

        for i in range(n_traders):        
            
            sample = cumsum(choices([ 1 - costs, -r - costs ], [ p_w, p_l], k = n_trades))

            if min(sample) <= -max_loss:

                lens.append(bisect_left(sample, -max_loss))
                results.append(0)

            else:

                lens.append(n_trades)
                results.append(1)


        print(f"{f'1:{r}':20}{mean(results):<20.2f}{mean(lens):<20.1f}")
            

