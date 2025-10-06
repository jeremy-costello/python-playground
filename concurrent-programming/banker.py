# https://begriffs.com/posts/2020-03-23-concurrent-programming.html

from dataclasses import dataclass
from random import randrange
from threading import Thread


N_ACCOUNTS: int = 10
N_THREADS: int = 20
N_ROUNDS: int = 10000
INIT_BALANCE: int = 100


@dataclass
class Account:
    balance: int


accts: list[Account] = [Account(balance=0) for _ in range(N_ACCOUNTS)]


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
                
        if accts[from_account].balance > 0:
            payment = 1 + randrange(accts[from_account].balance)
            accts[from_account].balance -= payment
            accts[to_account].balance += payment


def main() -> None:
    for acct in accts:
        acct.balance = INIT_BALANCE
    
    print(f"Initial money in system: {N_ACCOUNTS * INIT_BALANCE}")

    # https://docs.python.org/3/library/threading.html#introduction

    threads: list[Thread] = []
    for _ in range(N_THREADS):
        t = Thread(
            target=disburse
        )
        threads.append(t)
    
    for t in threads:
        t.start()
    
    for t in threads:
        t.join()
    
    total: int = 0
    for acct in accts:
        total += acct.balance
    
    print(f"Final money in system: {total}")


if __name__ == "__main__":
    main()
