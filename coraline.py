#!/usr/bin/python3

import struct
import random
import string
import itertools
import os
import binascii
import subprocess


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
    mutated  -  a bytearray containing mutated data
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
                 mutationrule=default_rule, workingdirectory="/tmp",
                 reportdirectory="./", timeout=10):
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

        # Create the working directories
        self.mutationrule = mutationrule
        self.workingdirectory = os.path.join(workingdirectory, "coraline")
        self.workingin = os.path.join(self.workingdirectory, "input")
        self.workingout = os.path.join(self.workingdirectory, "output")
        if not os.path.exists(self.workingdirectory):
            os.makedirs(self.workingdirectory)
        if not os.path.exists(self.workingin):
            os.makedirs(self.workingin)
        if not os.path.exists(self.workingout):
            os.makedirs(self.workingout)

        # Set the timeout
        self.timeout = timeout

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

    def handle_hang(self, index):
        print(index, "Hang")

    def handle_crash(self, index, result, pid):
        print(index, result, pid)

    def fuzz(self, fuzz_range=(0, None)):
        for i in self.build_range(fuzz_range):
            self.fuzz_step(i)

    def fuzz_step(self, index):
        mutated = self.mutationrule(self.seed, index, self.sample, self.scores)
        uniq = binascii.hexlify(bytes(self.seed, "ascii")).decode("ascii") + "_"
        working_filein = os.path.join(self.workingin, uniq + str(index))
        # working_fileout = os.path.join(self.workingout, uniq + str(index))
        with open(working_filein, 'wb') as working_file:
            working_file.write(mutated)
        try:
            process = subprocess.Popen(["./samples/crashable", working_filein],
                                       stdout=subprocess.DEVNULL,
                                       stderr=subprocess.DEVNULL)
            pid = process.pid
            result = process.wait(self.timeout)
        except subprocess.TimeoutExpired:
            result = None

        if result is None:
            self.handle_hang(index)
        elif result < 0:
            self.handle_crash(index, result, pid)

        os.unlink(working_filein)

    def cleanup(self):
        if os.listdir(self.workingin):
            for i in os.listdir(self.workingin):
                os.unlink(os.path.join(self.workingin, i))
        if os.listdir(self.workingout):
            for i in os.listdir(self.workingout):
                os.unlink(i)
        os.rmdir(self.workingin)
        os.rmdir(self.workingout)
        os.rmdir(self.workingdirectory)


def main():
    cora = Coraline("./samples/good.txt", "./samples/crashable_score.zl",
                    "seed", timeout=2)
    cora.fuzz((0, 255))
    cora.cleanup()

if __name__ == "__main__":
    main()
