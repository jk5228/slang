# Run all example Slang scripts in the specified example directory.

import slang
from os import listdir
from os.path import isfile, join

# Example program path
ex_path = 'examples'

# Example dict
ex = dict()

fnames = (f for f in listdir(ex_path) if isfile(join(ex_path, f)))

for fname in fnames:
    ex[fname] = open(join(ex_path, fname), 'r').read()

if __name__ == "__main__":
    for (fname, script) in ex.items():
        print('Executing "%s/%s"' % (ex_path, fname))
        slang.interpret(script)