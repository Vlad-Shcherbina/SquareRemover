with open('_submission.py', 'w') as fout:
    fout.write(
        open('sol.py').read().replace(
            'from patterns import *',
            open('patterns.py').read().replace('__main__', 'zzz')))
