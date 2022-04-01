#-----------------------------------------------------------------------
# runserver.py
# Author: Ryan Clare and Mateo Godoy
#-----------------------------------------------------------------------

import argparse
from sys import argv, exit, stderr
from flask_app import app

# --------------------------------------------------------------------

# adds an argument parser to this program and returns the arguments in
# a dictionary format
def get_args():
    # initialize an argument parser
    parser = argparse.ArgumentParser(
        description='The registrar application', allow_abbrev=False)

    # add arguments to the parser
    parser.add_argument(
        'port',
        help='the port at which the server should listen', type=int)

    # return a dictionary of the arguments
    return vars(parser.parse_args())

# --------------------------------------------------------------------
def main():
    try:
        # get the port number from the command line input
        args = dict(get_args())
        port = int(args['port'])
    except Exception as ex:
        print(argv[0] + ': ' + str(ex), file=stderr)
        exit(2)

    try:
        app.run(host='0.0.0.0', port=port, debug=True)
    except Exception as ex:
        print(ex, file=stderr)
        exit(1)

if __name__ == '__main__':
    main()
