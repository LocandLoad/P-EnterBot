import multiprocessing
import dataclasses
import argparse
import time
import os
import re

import pyautogui
import keyboard

import MirrorDungeonRunner

QUEUE_PATTERN = r'(\d+)[hnHN]'

parser = argparse.ArgumentParser(
    prog="(L.C.M.D.D.S.) : Limbus Company Mirror Dungeon Do-er Script"
)
parser.add_argument('-q', '--queue', type=str)
parser.add_argument('-r', '--runs', type=int)
parser.add_argument('-t', '--team', type=int)
parser.add_argument('-m', '--hardMode', type=bool)
parser.add_argument('-b', '--oneBonusPerRun', type=bool)

pyautogui.FAILSAFE = False

script_path = os.path.abspath(__file__)
script_directory = os.path.dirname(script_path)
os.chdir(script_directory)

args = parser.parse_args()

@dataclasses.dataclass
class Run:
    is_hard: bool
    count: int

def parse_queue(q: str) -> list[Run]:
    runs = []

    matches = re.finditer(QUEUE_PATTERN, q)

    for match in matches:
        is_hard = q[match.span()[1] - 1].lower() == 'h'
        runs.append(
            Run(
                is_hard=is_hard,
                count=int(match.groups()[0])
            )
        )

    return runs

def do_queued_runs(queue: list[Run], team_id: int | None, individualWeeklyBonus: bool | None) -> None:
    mirror_dungeon_runner = MirrorDungeonRunner.MirrorDungeonRunner(team_id, individualWeeklyBonus)

    run_count = 1
    for run in queue:
        for run_n in range(run.count):
            mirror_dungeon_runner.hardMode = run.is_hard

            print(f"Starting run {run_count}, {run.is_hard=}")
            mirror_dungeon_runner.run_md()

            run_count += 1

def main():
    team_id: int | None = None
    if args.team:
        team_id = args.team

    individualWeeklyBonus: bool | None = None
    if args.oneBonusPerRun:
        individualWeeklyBonus = args.oneBonusPerRun

    if args.queue:
        queue: list[Run] = parse_queue(args.queue)
        do_queued_runs(queue, team_id, individualWeeklyBonus)
        return

    runs = 0
    if not args.runs:
        user_input: str = pyautogui.prompt(text = "Enter number of MD runs", title = "StartMenu", default = 1)
        if not user_input:
            return 0
        if not user_input.isnumeric():
            print("Number of runs must be integer")
            exit(1)
        runs = int(user_input)
    else:
        runs = args.runs

    hard: bool = False
    if args.hardMode:
        hard = args.hardMode

    mirror_dungeon_runner = MirrorDungeonRunner.MirrorDungeonRunner(team_id, individualWeeklyBonus)
    mirror_dungeon_runner.hardMode = hard
    for i in range(runs):
        print(f"Doing run {i}")
        mirror_dungeon_runner.run_md()

if __name__ == '__main__':
    multiprocessing.freeze_support()
    process = multiprocessing.Process(target=main)#multiprocess with main function so failsafe key can be detected whenever
    process.start()
    while process.is_alive():
        time.sleep(0.1)
        if keyboard.is_pressed('q'): #failsafe
            process.terminate()
            break
