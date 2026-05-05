import argparse

from ceremony.runtime import run


def main():
    parser = argparse.ArgumentParser(
        prog="ceremony",
        description="A small lattice ceremony with unnecessary machinery.",
    )
    parser.add_argument("--first", default="human", help="driver spec")
    parser.add_argument("--second", default="human", help="driver spec")
    parser.add_argument("--quiet", action="store_true", help="suppress intermediate projections")
    args = parser.parse_args()

    result = run(args.first, args.second, chorus=not args.quiet)
    if args.quiet:
        print(result["glyph"])
    print(result["utterance"])


if __name__ == "__main__":
    main()
