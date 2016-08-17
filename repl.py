# The Slang REPL                                             Jason Kim, 7/7/2016
# The Slang REPL (read-evaluate-print loop) does exactly that. To exit, enter
# "exit"

import slang
from interpreter import env, colors, execute
import cmd, copy

class repl(cmd.Cmd):

    intro = 'Slang REPL\nEnter "exit", ctrl+C, or ctrl+D to quit.\nEnter "help" for more commands.'
    fresh_env = copy.deepcopy(env.env)
    in_prompt = '%s%s%s' % (colors.color('In  [', colors.OKBLUE), '%s', colors.color(']: ', colors.OKBLUE))
    out_prompt = '%s%s%s%s' % (colors.color('Out [', colors.OKCYAN), '%s', colors.color(']: ', colors.OKCYAN), '%s')
    prompt = ''
    ret_prompt = ''
    last_run = None
    exec_list = []
    cnt = 0

    # Utility functions

    # Print an error message.
    def error(self, err):
        print(colors.color('Error: %s', colors.FAIL) % err)

    # Update the in_prompt with the count number.
    def update_in_prompt(self):
        self.prompt = self.in_prompt % self.cnt

    # Update the out_prompt with the count number.
    def update_out_prompt(self):
        self.ret_prompt = self.out_prompt % self.cnt

    # Read in Slang line. This is the default action.
    def default(self, line):
        if line == 'EOF': exit(0)
        try:
            res = slang.run(line)
            res = res.res
            print(self.out_prompt % (self.cnt, str(res)))
        except Exception as err:
            self.error(err)
        self.cnt += 1

    # Commands

    def do_exit(self, arg):
        'Exit from the REPL.'
        exit(0)

    def do_run(self, fpath):
        'Run a specified script. If no path is specified, re-run the last run script.'
        if not fpath:
            if self.last_run:
                fpath = self.last_run
                self.last_run = fpath
            else:
                self.error('no script to re-run.')
                return
        try:
            self.last_run = fpath
            script = open(fpath, 'r').read()
            self.default(script)
        except Exception as err:
            self.error('"%s": %s' % (fpath, err))

    def do_add(self, fpath):
        'Add a script to the exec list.'
        if not fpath:
            self.error('no script specified.')
            return
        self.exec_list.append(fpath)
        print('Script "%s" added to exec list.\n' % fpath)

    def do_del(self, fpath):
        ('Remove every instance of the specified script from the exec list. '
         'If not path is specified, remove the last script added, if any.')
        if not fpath and self.exec_list:
            script = self.exec_list.pop()
            print('Script "%s" deleted from exec list.\n' % fpath)
        else:
            old_len = len(self.exec_list)
            self.exec_list = [fp for fp in self.exec_list if fp != fpath]
            if old_len != len(self.exec_list):
                print('Script "%s" deleted from exec list.\n' % fpath)

    def do_clear(self, arg):
        'Clear the exec list.'
        self.exec_list = []
        print('Exec list cleared.\n')

    def do_list(self, arg):
        'Display the exec list.'
        print('Exec list:')
        for fp in self.exec_list:
            print(fp)
        print()

    def do_exec(self, arg):
        'Run all the scripts in the exec list.'
        for fpath in self.exec_list:
            self.do_run(fpath)

    def do_locals(self, arg):
        'Print all of the bindings in the environment.'
        print('Environment:')
        for (key, val) in env.env.items():
            print('%s\t=\t%s' % (key, val))
        print()

    def do_reset(self, arg):    # TODO: somehow broke after using cmd module
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
    try:
        repl().cmdloop()
    except KeyboardInterrupt:
        exit(0)