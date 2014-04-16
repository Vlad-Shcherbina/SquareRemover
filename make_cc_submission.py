import subprocess
import re

p = subprocess.Popen('xsel --clipboard --input', shell=True, stdin=subprocess.PIPE)

text = open('cc/sol.cc').read()

def replacer(m):
  return open('cc/' + m.group(1)).read()
text = re.sub(r'#include "(.+\.h)"', replacer, text)

text = '#define SUBMISSION\n\n' + text

p.communicate(text)
ret = p.wait()
assert ret == 0
print('solution copied to clipboard')
