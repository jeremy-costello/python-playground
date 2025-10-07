# https://begriffs.com/posts/2020-03-23-concurrent-programming.html
### this adds a condition for printing the highest number of threads in the locked section at once

from dataclasses import dataclass
from random import randrange
from threading import Thread, RLock, Condition
from timeit import timeit


N_ACCOUNTS: int = 50
N_THREADS: int = 100
N_ROUNDS: int = 10000
INIT_BALANCE: int = 100
N_TIMEIT_RUNS = 10


@dataclass
class Account:
    balance: int
    lock: RLock | None


accts: list[Account] = [
    Account(
        balance=0,
        lock=None
    ) for _ in range(N_ACCOUNTS)
]

stats_cond = Condition()
stats_curr: int = 0
stats_best: int = 0


def stats_change(
        delta: int
) -> None:
    global stats_best
    global stats_curr

    with stats_cond:
        stats_curr += delta
        if stats_curr > stats_best:
            stats_best = stats_curr
            stats_cond.notify()


def stats_print() -> None:
    global stats_best
    prev_best: int

    while True:
        with stats_cond:
            prev_best = stats_best
            while prev_best == stats_best:
                stats_cond.wait()
            
            print(stats_best, flush=True)


def disburse() -> None:
    from_account: int
    payment: int
    to_account: int

    for _ in range(N_ROUNDS):
        from_account = randrange(N_ACCOUNTS)
        while True:
            to_account = randrange(N_ACCOUNTS)
            if to_account != from_account:
                break
        
        with accts[min(from_account, to_account)].lock:
            with accts[max(from_account, to_account)].lock:
                stats_change(1)
                if accts[from_account].balance > 0:
                    payment = 1 + randrange(accts[from_account].balance)
                    accts[from_account].balance -= payment
                    accts[to_account].balance += payment
                stats_change(-1)


def main(
        print_outputs=False
) -> None:
    for acct in accts:
        acct.balance = INIT_BALANCE
        acct.lock = RLock()
    
    if print_outputs:
        print(f"Initial money in system: {N_ACCOUNTS * INIT_BALANCE}")

    # https://docs.python.org/3/library/threading.html#introduction

    threads: list[Thread] = []
    for _ in range(N_THREADS):
        t = Thread(
            target=disburse
        )
        threads.append(t)
    
    stats_thread = Thread(
        target=stats_print,
        daemon=True
    )
    stats_thread.start()
    
    for t in threads:
        t.start()
    
    for t in threads:
        t.join()
    
    total: int = 0
    for acct in accts:
        total += acct.balance
    
    if print_outputs:
        print(f"Final money in system: {total}")


if __name__ == "__main__":
    total_time = timeit("main()", globals=globals(), number=N_TIMEIT_RUNS)
    avg_time = total_time / N_TIMEIT_RUNS

    print(f"Total time for {N_TIMEIT_RUNS} runs: {total_time:.6f} seconds")
    print(f"Average time per run: {avg_time:.6f} seconds")
