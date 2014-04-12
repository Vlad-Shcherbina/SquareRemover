import subprocess
import re

p = subprocess.Popen('xsel --clipboard --input', shell=True, stdin=subprocess.PIPE)

text = open('cc/sol.cc').read()
text = text.replace('int main(', 'int main1(')

def replacer(m):
  return open('cc/' + m.group(1)).read()
text = re.sub(r'#include "(.+\.h)"', replacer, text)

p.communicate(text)
ret = p.wait()
assert ret == 0
print('solution copied to clipboard')
