# The Slang REPL                                             Jason Kim, 7/7/2016
# The Slang REPL (read-evaluate-print loop) does exactly that. To exit, enter
# "exit"

import sys
import slang

# Launch the RELP.
def launch():
    cnt = 0
    print('Slang REPL')
    print('Enter "exit" to quit.')
    print()
    sys.stdout.write('In  [%d]: ' % cnt)
    sys.stdout.flush()
    for line in sys.stdin:
        line = line.strip()
        if not line:
            sys.stdout.write('In  [%d]: ' % cnt)
            sys.stdout.flush()
            continue
        if line == 'exit': break

        try:
            res = slang.run(line)
            print('Out [%d]: %s' % (cnt, str(res)))
        except Exception as err:
            print('Error: %s' % err)

        cnt += 1
        sys.stdout.write('In  [%d]: ' % cnt)
        sys.stdout.flush()