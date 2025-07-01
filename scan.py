from Ikariam.scanner import Scanner
from Ikariam.api.session import IkaBot
from argparse import ArgumentParser


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("cookie", type=str)
    parser.add_argument("server", type=int)
    parser.add_argument("-c", action="store_true")
    args = parser.parse_args()
    bot = IkaBot(args.cookie, args.server)
    scanner = Scanner(bot, f"Ika_Map/{args.server}.json")
    bugs = scanner.run(args.c)
    scanner.correct(bugs)
