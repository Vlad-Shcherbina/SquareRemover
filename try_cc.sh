set -o errexit

g++ --std=c++0x cc/sol.cc

java -jar SquareRemoverVis.jar -exec "./a.out" \
    -novis -seed 2
