from    random                  import  choice
from    numpy                   import  mean, std
from    time                    import  time
from    sys                     import  argv


class ftt_gt:

    def __init__(self):

        self.day    = 0
        self.equity = 0
        self.tp     = 7500
        self.dd     = 7500
        self.trail  = "daily"
        self.state  = None
        self.alive  = True

    def get_next_trade_params(self):

        pass


POPULATION  = [ 1, -1 ]
MODES       = {
                "ftt_gt":  ftt_gt
            }


def trial(mode: dict):

    account = MODES[mode]()

    while (account.alive):

        account.get_next_trade_params()

    pass


def run(
    mode:   dict, 
    runs:   int
):

    costs           = []
    terminal_states = []

    for _ in range(runs):

        cost, terminal_state = trial(mode)

        costs.append(cost)
        terminal_states.append(terminal_state)


if __name__ == "__main__":

    t0      = time()
    mode    = argv[1]
    runs    = int(argv[2])

    run(MODES[mode])

    print(f"{time() - t0:0.1f}s")