import multiprocessing
import dataclasses
import argparse
import time
import os
import re
import sys

import pyautogui
import keyboard

import MirrorDungeonRunner

from tkinter import *
from tkinter import ttk

QUEUE_PATTERN = r'(\d+)[hnHN]'

parser = argparse.ArgumentParser(
    prog="(L.C.M.D.D.S.) : Limbus Company Mirror Dungeon Do-er Script"
)
parser.add_argument('-q', '--queue', type=str)
parser.add_argument('-l', '--loadLast', type=bool)
parser.add_argument('-r', '--runs', type=int)
parser.add_argument('-t', '--team', type=int)
parser.add_argument('-m', '--hardMode', type=bool)
parser.add_argument('-b', '--oneBonusPerRun', type=bool)
parser.add_argument('--multiprocessing-fork', type=str)
parser.add_argument('pipe_handle=', type=str, default="", nargs="?")

pyautogui.FAILSAFE = False

script_path = os.path.abspath(__file__)
script_directory = os.path.dirname(script_path)
os.chdir(script_directory)

args = parser.parse_args()
@dataclasses.dataclass
class GUIResult:
    runs: str
    hard: bool
    bonus: bool
    load: bool
    team: str
    queueBool: bool
    queue: str

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

def do_queued_runs(queue: list[Run], load_last: bool, team_id: int | None, individualWeeklyBonus: bool | None) -> None:
    mirror_dungeon_runner = MirrorDungeonRunner.MirrorDungeonRunner(team_id, individualWeeklyBonus)
    if load_last:
        mirror_dungeon_runner.loadLastSelectedTeam()

    run_count = 1
    for run in queue:
        for run_n in range(run.count):
            mirror_dungeon_runner.hardMode = run.is_hard

            print(f"Starting run {run_count}, {run.is_hard=}")
            mirror_dungeon_runner.run_md()

            run_count += 1

def makeGUI() -> GUIResult:
    root = Tk()
    root.title ("P-EnterBot")
    frm = ttk.Frame(root, padding=10)
    frm.grid()

    ttk.Label(frm, text="Settings").grid(column=0, row=0)
    ttk.Label(frm, text="Runs").grid(column=1, row=1)
    ttk.Label(frm, text="Hard").grid(column=1,row=2)
    ttk.Label(frm, text="OneWeeklyBonus").grid(column=1,row=3)
    ttk.Label(frm, text="LoadLast").grid(column=1,row=4)
    ttk.Label(frm, text="Team").grid(column=1,row=5)
    ttk.Label(frm, text="QueueMode").grid(column=1,row=6)
    ttk.Label(frm, text="Queue").grid(column=1,row=7)

    runsEntry = ttk.Entry(frm, width=4)
    runsEntry.grid(column=0,row=1)
    runsEntry.insert(0,1)

    hardBool = BooleanVar(value=False)
    hardBox = ttk.Checkbutton(frm, variable = hardBool)
    hardBox.grid(column=0,row=2)

    bonusBool = BooleanVar(value=False)
    bonusBox = ttk.Checkbutton(frm,variable = bonusBool)
    bonusBox.grid(column=0,row=3)

    loadBool = BooleanVar(value=False)
    loadBox = ttk.Checkbutton(frm,variable = loadBool)
    loadBox.grid(column=0,row=4)

    teamEntry = ttk.Entry(frm, width=4)
    teamEntry.grid(column=0,row=5)

    queueBool = BooleanVar(value=False)
    queueBox = ttk.Checkbutton(frm,variable= queueBool)
    queueBox.grid(column=0,row=6)

    queueEntry = ttk.Entry(frm, width=6)
    queueEntry.insert(0,"1n")
    queueEntry.grid(column=0,row=7)

    def enterButton():
        global returnVar
        returnVar = GUIResult(hard=hardBool.get(),
                            runs=runsEntry.get(),
                            team=teamEntry.get(),
                            queue=queueEntry.get(),
                            bonus=bonusBool.get(),
                            load=loadBool.get(),
                            queueBool=queueBool.get())
        root.destroy()
        

    ttk.Button(frm, text="Enter", command=enterButton).grid(column=2,row=8)
    global returnVar
    returnVar = None
    root.mainloop()
    
    return returnVar

def main():

    os.makedirs('.cache/', exist_ok=True)

    load_last: bool = False
    team_id: int | None = None
    individualWeeklyBonus: bool | None = None
    hard: bool = False
    runs: int = 0
    result: GUIResult | None = None
    if len(sys.argv) == 1:
            result = makeGUI()

    #GUI loads variables

    if (result is not None):
        if result.team:
            if result.team.isnumeric():
                team_id = int(result.team)
            else:
                print("Team should be an integer")
        if result.runs:
            if result.runs.isnumeric():
                runs = int(result.runs)
            else:
                print("Runs should be an integer")
                exit(1)
        individualWeeklyBonus = result.bonus
        hard = result.hard
        load_last = result.load

    #Arguments load variables
    if args.loadLast:
        load_last = args.loadLast
    if args.team:
        team_id = args.team
    if args.oneBonusPerRun:
        individualWeeklyBonus = args.oneBonusPerRun
    if args.hardMode:
            hard = args.hardMode
    if args.runs:
        runs = args.runs

    if args.queue:
        queue: list[Run] = parse_queue(args.queue)
        do_queued_runs(queue, load_last, team_id, individualWeeklyBonus)
        return
    
    if (result is not None):
        if result.queueBool:
            queue: list[Run] = parse_queue(result.queue)
            do_queued_runs(queue, load_last, team_id, individualWeeklyBonus)
            return
    
    mirror_dungeon_runner = MirrorDungeonRunner.MirrorDungeonRunner(team_id, individualWeeklyBonus)
    mirror_dungeon_runner.hardMode = hard
    if load_last:
        mirror_dungeon_runner.loadLastSelectedTeam()

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
