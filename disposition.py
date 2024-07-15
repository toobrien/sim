from bisect import bisect_left
from numpy  import cumsum, mean, where
from random import choices
from sys    import argv


# python disposition.py 0 20


if __name__ == "__main__":

    costs       = float(argv[1])
    n_traders   = 10_000
    n_trades    = 1_000
    max_loss    = int(argv[2])
    risks       = [ i for i in range(1, max_loss + 1) ]

    print(f"\nnum traders:        {n_traders}")
    print(f"cost per trade:     {costs:0.2f}")
    print(f"num trades:         {n_trades}")
    print(f"max loss:           {max_loss}\n")

    print(f"{'reward:risk':20}{'survival rate (%)':20}{'avg trades survived'}\n")

    for r in risks:

        w       = 1 - costs
        l       = -r - costs
        p_w     = r / (1 + r)
        p_l     = 1 - p_w
        results = []
        lens    = []

        for i in range(n_traders):        
            
            sample  = cumsum(choices([ w, l ], [ p_w, p_l ], k = n_trades))
            locs    = where(sample <= -max_loss)[0]

            if len(locs) > 0:

                lens.append(locs[0])
                results.append(0)

            else:

                lens.append(n_trades)
                results.append(1)


        print(f"{f'1:{r}':20}{mean(results) * 100:<20.2f}{mean(lens):<20.1f}")

    print("\n")
            

