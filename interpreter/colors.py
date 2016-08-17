# Colors                                                     Jason Kim 7/16/2016

HEADER = '\033[95m'
OKBLUE = '\033[34m'
OKCYAN = '\033[36m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'

def color(text, color):
    return '%s%s%s' % (color, text, ENDC)