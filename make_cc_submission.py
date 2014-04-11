import subprocess

p = subprocess.Popen('xsel --clipboard --input', shell=True, stdin=subprocess.PIPE)

text = open('cc/sol.cc').read()
text = text.replace('int main(', 'int main1(')
text = text.replace('#include "pretty_printing.h"', open('cc/pretty_printing.h').read())

p.communicate(text)
ret = p.wait()
assert ret == 0
print('solution copied to clipboard')
