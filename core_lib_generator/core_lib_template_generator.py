import argparse

parser = argparse.ArgumentParser(description="Core-Lib Generator")

parser.add_argument("add", nargs='*', metavar="num", type=int,
                    help="All the numbers separated by spaces will be added.")

args = parser.parse_args()

if len(args.add) != 0:
    print(sum(args.add))
