from Ikariam.scanner import Scanner
from Ikariam.api.session import IkaBot
import sys


if __name__ == "__main__":
    bot = IkaBot(sys.argv[1], sys.argv[2])
    scanner = Scanner(bot, f"Ika_Map/{sys.argv[2]}.json")
    bugs = scanner.run()
    scanner.correct(bugs)
