set -o errexit

g++ --std=c++0x -W -Wall -Wno-sign-compare -O2 -s -pipe -mmmx -msse -msse2 -msse3 \
  cc/sol.cc

time python3 optimize.py "./a.out"
