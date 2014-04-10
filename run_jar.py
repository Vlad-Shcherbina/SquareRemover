import os

seed = 2
os.system(
    'java -jar SquareRemoverVis.jar -exec "python sol.py" '
    '-novis -seed {}'.format(seed))
