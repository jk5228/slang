# The Slang REPL                                             Jason Kim, 7/7/2016
# The Slang REPL (read-evaluate-print loop) does exactly that. To exit, enter
# "exit"

import sys
import slang
import execute
import colors

# Launch the RELP.
def launch():
    in_prompt = '%s%s%s' % (colors.color('In  [', colors.OKGREEN), '%s', colors.color(']: ', colors.OKGREEN))
    out_prompt = '%s%s%s%s' % (colors.color('Out [', colors.FAIL), '%s', colors.color(']: ', colors.FAIL), '%s')
    cnt = 0
    print('Slang REPL')
    print('Enter "exit" to quit.')
    print()
    sys.stdout.write(in_prompt % cnt)
    sys.stdout.flush()
    for line in sys.stdin:
        line = line.strip()
        if not line:
            sys.stdout.write(in_prompt % cnt)
            sys.stdout.flush()
            continue
        if line == 'exit': break

        try:
            res = slang.run(line)
            res = res.res
            print(out_prompt % (cnt, str(res)))
        except Exception as err:
            print(colors.color('Error: %s', colors.FAIL) % err)

        cnt += 1
        sys.stdout.write(in_prompt % cnt)
        sys.stdout.flush()