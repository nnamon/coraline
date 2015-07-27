#!/usr/bin/python

import struct
import random


class Coraline:
    
    def __init__(self):
	pass
 
    def parse_scores(data):
        if len(data) % 8 != 0:
	    raise Exception("Score data must contain only pairs of 32 bit integers")
        scores = [] 
        for i in range(0, len(data), 8):
	    scores.append(struct.unpack("II", data[i:i+8]))
        return scores	
	


def main():
    print parse_scores(file("/tmp/data").read()) 

if __name__ == "__main__":
    main()
