import random
from pprint import pprint
from typing import Dict

from casino import Player, Card, Game
from env import CardsGuessing
from utils import Inteleaving
# from misha import MishaBotV1, MishaBotV2
# from ilariia import B1V1, B1V2, B1V3, BlackBot
from bots import *


def versus(p1, p2):
    winners: Dict[Player, int] = {p1: 0, p2: 0}
    games = 1000
    rounds = 1000
    print("Start battle %s vs %s\n" % (p1.name, p2.name))
    for i in range(games):
        game = Game(p1, 100, p2, 100, rounds=rounds, debug=False)
        winner = game.run()
        if winner is not None:
            winners[winner] += 1
            # print("%s winning rate: %f" % (p1.name, float(winners[p1]) / ( i + 1)))
            # print("%s winning rate: %f" % (p2.name, float(winners[p2]) / ( i + 1)))

    print("Battle result:\n")
    print("After %s games %s won %d times and %s won %d times" % (games,
                                                                  p1.name, winners[p1],
                                                                  p2.name, winners[p2]))
    print("%s winning rate: %f" % (p1.name, float(winners[p1])/games))
    print("%s winning rate: %f" % (p2.name, float(winners[p2])/games))
    print("\n")


def main():
    # versus(B1V2(100), B1V1())
    # versus(B1V3(100), B1V1())
    # versus(B1V2(100), SmarterBaseline("MishaSmarter"))
    # versus(B1V2(100), BaselinePlayer("MishaBaseline"))
    # versus(B1V3(100), SmarterBaseline("MishaSmarter"))
    # versus(B1V3(100), BaselinePlayer("MishaBaseline"))
    # versus(B1V2(100), B1V3(100))
    # versus(MishaBotV1(10), BaselinePlayer("MishaBaseline"))
    # versus(MishaBotV1(10), BaselinePlayer("MishaSmarter"))
    # versus(MishaBotV1(10), B1V3(500))
    # versus(SmarterBaseline("MishaSmarter"), B1V3(100))
    # versus(BaselinePlayer("MishaBaseline"), B1V3(100))
    # versus(MishaBotV1(10), B1V3(100))
    # versus(B1V1(), B1V3(100))
    # versus(BlackBot(), B1V3(100))
    # versus(B1V1(), B1V3(500))

    # versus(MishaBotV1(10), MishaBotV2())
    # versus(MishaBotV1(10), B1V3(100))
    # versus(MishaBotV2(), BaselinePlayer("Baseline"))
    # versus(MishaBotV1(), SmarterBaseline("Smarter"))

    opponent = SmarterBaselineBot()
    env = CardsGuessing(starting_money=100, opponent=opponent)
    player = IlariiaRandomUltimatumBot(100, debug=True)
    player.set_env(env)
    player.run(1)

if __name__ == "__main__":
    main()
