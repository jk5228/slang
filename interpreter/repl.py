# The Slang REPL                                             Jason Kim, 7/7/2016
# The Slang REPL (read-evaluate-print loop) does exactly that. To exit, enter
# "exit"

import sys
import env
import copy
import slang
import colors
import execute

# The help string
help_str = '''Commands:
exit    : Exit from the REPL.
locals  : Print all of the bindings in the environment.
reset   : Reset the environment to its initial set of bindings.
help    : Print this list of commands.
'''

# Launch the RELP.
def launch():
    fresh_env = copy.deepcopy(env.env)
    in_prompt = '%s%s%s' % (colors.color('In  [', colors.OKGREEN), '%s', colors.color(']: ', colors.OKGREEN))
    out_prompt = '%s%s%s%s' % (colors.color('Out [', colors.FAIL), '%s', colors.color(']: ', colors.FAIL), '%s')
    cnt = 0
    print('Slang REPL')
    print('Enter "exit" to quit.')
    print('Enter "help" for more commands.')
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
        elif line == 'locals':
            print('Environment:')
            for (key, val) in env.env.items():
                print('%s\t=\t%s' % (key, val))
            print()
        elif line == 'reset':
            env.env = fresh_env
            print('Environment reset.\n')
        elif line == 'help':
            print(help_str)
        else:
            try:
                res = slang.run(line)
                res = res.res
                print(out_prompt % (cnt, str(res)))
            except Exception as err:
                print(colors.color('Error: %s', colors.FAIL) % err)

        cnt += 1
        sys.stdout.write(in_prompt % cnt)
        sys.stdout.flush()