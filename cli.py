from argparse import ArgumentParser, Namespace
from pathlib import Path

import core


def main():
    parser = ArgumentParser()

    parser.add_argument("-i", "--input", help="Input video file path", type=str)
    parser.add_argument("-o", "--output", help="Output file path", type=str)
    parser.add_argument("-s", "--size", help="Target size (MB)", type=int, default=10)

    args: Namespace = parser.parse_args()

    work = core.Work(args.input, args.output, args.size)

    work.run()


if __name__ == "__main__":
    main()
