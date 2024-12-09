from fitness.base_ff_classes.base_ff import base_ff
import random
import time

class max_in_list(base_ff):

    def __init__(self):
        super().__init__()

    def evaluate(self, ind, **kwargs):
        p = ind.phenotype

        print("\n" + p)

        fitness = 0
        for _ in range(50):
            t0 = time.time()
            self.test_list = generate_list()
            d = {'test_list': self.test_list}
            # CODE HERE

            try:
                exec(p, d)

                guess = d['max_val']
                # CODE HERE

            except:
                fitness = self.default_fitness

            t1 = time.time()

            # CODE HERE

        return fitness

def generate_list():
    # CODE HERE
    pass