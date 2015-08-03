#!/usr/bin/python3

import struct
import random
import string
import itertools


def default_rule(seed, index, sample, scores):
    """The default mutation rule simply randomises each byte with
    a score. The check for a score more than zero is to demonstrate
    the capability for the rule to include logic.

    Arguments:
    seed     -  a random or user specified string to induce
                unpredictability
    index    -  index provided during fuzzing for deterministic states
    sample   -  sample input data
    scores   -  offset/score pairs

    Returns:
    mutated  -  a string containing mutated data
    """
    rand_seed = seed + str(index)
    rand = random.Random(rand_seed)
    mutable = list(sample)
    for offset, score in scores:
        # if out of sample range, drop the mutation for this byte
        if offset >= len(mutable):
            continue
        # if the score is more than zero, mutate the byte
        if score > 0:
            mutable[offset] = rand.randrange(0x00, 0xff+1)
    mutated = bytearray(mutable)
    return mutated


class Coraline:

    def __init__(self, sample_file, offset_file, seed=None,
                 mutationrule=default_rule):
        # Load the sample into memory
        with open(sample_file, 'rb') as sample:
            self.sample = sample.read()

        # Load scores from zl file
        with open(offset_file, 'rb') as offset:
            self.scores = self.parse_scores(offset.read())

        # Prevents overly predictable mutations between fuzzing sessions
        if seed is None:
            self.seed = ''.join(random.SystemRandom().choice(
                string.ascii_letters + string.digits) for i in range(16))
        else:
            self.seed = seed

        self.mutationrule = mutationrule

    def parse_scores(self, data):
        if len(data) % 8 != 0:
            e = "Score data must contain only pairs of 32 bit integers"
            raise Exception(e)
        scores = []
        for i in range(0, len(data), 8):
            scores.append(struct.unpack("II", data[i:i+8]))
        return scores

    def build_range(self, fuzz_range):
        start, end = fuzz_range
        if end is None:
            return itertools.count(start=start, step=1)
        else:
            return range(start, end)

    def fuzz(self, fuzz_range=(0, None)):
        for i in self.build_range(fuzz_range):
            self.fuzz_step(i)

    def fuzz_step(self, index):
        self.mutationrule(self.seed, index, self.sample, self.scores)


def main():
    cora = Coraline("./samples/test.wav", "./samples/range_score.zl", "seed")
    cora.fuzz((0, 5))

if __name__ == "__main__":
    main()
