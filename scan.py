from Ikariam.scanner import Scanner
from Ikariam.api.session import IkaBot
from argparse import ArgumentParser


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("gf_token", type=str)
    parser.add_argument("nick", type=str)
    parser.add_argument("-c", action="store_true")
    args = parser.parse_args()
    bot = IkaBot(args.gf_token, args.nick)
    scanner = Scanner(bot, f"Ika_Map/{bot.server['number']}.json")
    bugs = scanner.run(args.c)
    scanner.correct(bugs)
