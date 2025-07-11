"""
Course: CSE 351 
Week: 07 Team
File:   team.py
Author: <Add name here>

Purpose: Solve the Dining philosophers problem to practice skills you have learned so far in this course.

Problem Statement:

Five silent philosophers sit at a round table with bowls of spaghetti. Forks
are placed between each pair of adjacent philosophers.

Each philosopher must alternately think and eat. However, a philosopher can
only eat spaghetti when they have both left and right forks. Each fork can be
held by only one philosopher and so a philosopher can use the fork only if it
is not being used by another philosopher. After an individual philosopher
finishes eating, they need to put down both forks so that the forks become
available to others. A philosopher can only take the fork on their right or
the one on their left as they become available and they cannot start eating
before getting both forks.  When a philosopher is finished eating, they think 
for a little while.

Eating is not limited by the remaining amounts of spaghetti or stomach space;
an infinite supply and an infinite demand are assumed.

The problem is how to design a discipline of behavior (a concurrent algorithm)
such that no philosopher will starve

Instructions:

        ****************************************************************
        ** DO NOT search for a solution on the Internet! Your goal is **
        ** not to copy a solution, but to work out this problem using **
        ** the skills you have learned so far in this course.         **
        ****************************************************************

Requirements you must Implement:

- Use threads for this problem.
- Start with the PHILOSOPHERS being set to 5.
- Philosophers need to eat for a random amount of time, between 1 to 3 seconds, when they get both forks.
- Philosophers need to think for a random amount of time, between 1 to 3 seconds, when they are finished eating.
- You want as many philosophers to eat and think concurrently as possible without violating any rules.
- When the number of philosophers has eaten a combined total of MAX_MEALS_EATEN times, stop the
  philosophers from trying to eat; any philosophers already eating will put down their forks when they finish eating.
    - MAX_MEALS_EATEN = PHILOSOPHERS x 5

Suggestions and team Discussion:

- You have Locks and Semaphores that you can use:
    - Remember that lock.acquire() has arguments that may be useful: `blocking` and `timeout`.  
- Design your program to handle N philosophers and N forks after you get it working for 5.
- When you get your program working, how to you prove that no philosopher will starve?
  (Just looking at output from print() statements is not enough!)
- Are the philosophers each eating and thinking the same amount?
    - Modify your code to track how much eat philosopher is eating.
- Using lists for the philosophers and forks will help you in this program. For example:
  philosophers[i] needs forks[i] and forks[(i+1) % PHILOSOPHERS] to eat (the % operator helps).
"""

import time
import random
import threading

PHILOSOPHERS = 5
MAX_MEALS_EATEN = PHILOSOPHERS * 5 # NOTE: Total meals to be eaten, not per philosopher!

def philospher_algrm(forks, id, meals_per_phil):
    meals = 0
    left_fork = forks[id]
    right_fork = forks[(id+1) % PHILOSOPHERS]
    left_acq = False
    right_acq = False
    while meals < 5:
      left_acq = left_fork.acquire(blocking=False)
      right_acq = right_fork.acquire(blocking=False)

      if (left_acq and right_acq):
          print(f"Philospher: {id} ATE")
          meals += 1
          meals_per_phil[id] = meals
          left_fork.release()
          right_fork.release()
      else:
          drop_fork = random.randint(0,1)
          if drop_fork == 1:
              if left_acq:
                left_fork.release()
              elif right_acq:
                right_fork.release()
    print(f"Philospher: {id} FINISHED")
    

def main():
    # TODO - Create the forks.
    # TODO - Create PHILOSOPHERS philosophers.
    forks = []
    philosophers = []
    meals_per_philospher = {}
    for i in range(PHILOSOPHERS):
        fork = threading.Lock()
        philosopher = threading.Thread(target=philospher_algrm, args=(forks, i, meals_per_philospher))
        forks.append(fork)
        philosophers.append(philosopher)

    # TODO - Start them eating and thinking.
    for p in philosophers:
        p.start()
    for p in philosophers:
        p.join()
    # TODO - Display how many times each philosopher ate.
    for i in range(philosophers):
        print(f"Philospher {i} ate: {meals_per_philospher[i]}")
    pass


if __name__ == '__main__':
    main()
