import os

for seed in range(1, 5 + 1):
    os.system(
        'java -jar SquareRemoverVis.jar -exec "python sol.py" '
        '-novis -seed {}'.format(seed))
