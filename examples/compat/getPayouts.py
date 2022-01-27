#!/usr/bin/env python3

from synack.compat.v1 import synack
import psycopg2
import subprocess
import os
import sys

s1 = synack()
s1.getSessionToken()

payouts = s1.getTransactions()
for i in range(len(payouts)):
    print(payouts[i])
