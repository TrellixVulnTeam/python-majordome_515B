# -*- coding: utf-8 -*-
from argparse import ArgumentParser
from pathlib import Path
import json
from .manager import Manager
from .manager import __doc__

def main():
    """ Main function. """
    print(__doc__)

    parser = ArgumentParser('Create minimal Python embeddings')
    parser.add_argument('--config', action='store', dest='config',
                        help='path to JSON configuration file')
    args = parser.parse_args()

    config = {}
    if args.config is not None:
        if not Path(args.config).exists():
            print(f'Invalid configuration file: {args.config}')
            return 1

        with open(args.config) as fp:
            config = json.load(fp)

    Manager(config).build()
    return 0


if __name__ == '__main__':
    main()