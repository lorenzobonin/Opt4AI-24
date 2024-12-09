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
            m = max(self.test_list)

            d = {'test_list': self.test_list}

            try:
                exec(p, d)
                guess = d['max_val']
                fitness += len(p)

                if guess not in self.test_list:
                    fitness += 10000

                v = int(abs(m - guess))
                if v <= 10e6:
                    fitness += v
                else:
                    fitness = self.default_fitness

            except:
                fitness = self.default_fitness

            t1 = time.time()

            if t1 - t0 > 10:
                fitness = self.default_fitness
                break

        return fitness

def generate_list():
    return [random.randint(50) for _ in range(10)]