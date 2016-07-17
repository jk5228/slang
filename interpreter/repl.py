# The Slang REPL                                             Jason Kim, 7/7/2016
# The Slang REPL (read-evaluate-print loop) does exactly that. To exit, enter
# "exit"

import sys
import env
import cmd
import copy
import slang
import colors
import execute

class repl(cmd.Cmd):

    intro = 'Slang REPL\nEnter "exit" to quit.\nEnter "help" for more commands.'
    fresh_env = copy.deepcopy(env.env)
    in_prompt = '%s%s%s' % (colors.color('In  [', colors.OKGREEN), '%s', colors.color(']: ', colors.OKGREEN))
    out_prompt = '%s%s%s%s' % (colors.color('Out [', colors.FAIL), '%s', colors.color(']: ', colors.FAIL), '%s')
    prompt = ''
    ret_prompt = ''
    cnt = 0

    # Utility functions

    # Update the in_prompt with the count number.
    def update_in_prompt(self):
        self.prompt = self.in_prompt % self.cnt

    # Update the out_prompt with the count number.
    def update_out_prompt(self):
        self.ret_prompt = self.out_prompt % self.cnt

    # Read in Slang line. This is the default action.
    def default(self, line):
        try:
            res = slang.run(line)
            res = res.res
            print(self.out_prompt % (self.cnt, str(res)))
        except Exception as err:
            print(colors.color('Error: %s', colors.FAIL) % err)
        self.cnt += 1

    # Commands

    def do_exit(self, arg):
        'Exit from the REPL.'
        exit(0)

    def do_locals(self, arg):
        'Print all of the bindings in the environment.'
        print('Environment:')
        for (key, val) in env.env.items():
            print('%s\t=\t%s' % (key, val))
        print()

    def do_reset(self, arg):
        'Reset the environment to its initial set of bindings.'
        env.env = self.fresh_env
        print('Environment reset.\n')

    # Other hook methods.

    # Get initial prompt.
    def preloop(self):
        self.update_in_prompt()

    # Ignore empty lines.
    def emptyline(self):
        pass

    # Update the prompt.
    def postcmd(self, stop, line):
        # TODO: update cnt
        self.update_in_prompt()

# Launch the RELP.
def launch():
    repl().cmdloop()