#!/bin/python3

import math
import os
import random
import re
import sys



if __name__ == '__main__':
    e1=[2,3,4,5]
    e2=[6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]
    n = int(input().strip())
    if n%2!=0:
        print("Weird")
    if n%2==0 and n in e1:
        print("Not Weird")
    if n%2==0 and n in e2:
        print("Weird")
    if n%2==0 and n>20:
        print("Not Weird")
