﻿# P-EnterBot! A.K.A. (LCMDDS) : Limbus Company Mirror Dungeon Do-er Script

A program designed to run mirror dungeons in the hit Korean gacha game Limbus Company by Project Moon.

![Danteh](https://github.com/user-attachments/assets/44e90f4a-7d69-4dea-973a-22a62fd7e507)

## Features

 - Designed for Mirror Dungeon 6
 - Picks team with best rest bonus
 - Configurable teams through TeamConfig.csv

## Notes

Only really tested on 1920 x 1080p. There's some code to try and scale images and positions, but it might not work too well.

# Installation

## Windows

Clone the repo with `git clone https://github.com/LocandLoad/P-EnterBot`

Download Python 3.12 or above if needed

Install requirements `python3.12 -m pip install -r requirements.txt`

# Usage

`python3.12 P-EnterBot.py --runs (run count) OR --queue (queue string ex. 1h4n) --team (index of team in TeamConfig.csv) --hardMode (True/False) --oneBonusPerRun (True/False)`

If a run count is not provided through the programs arguments, it will ask for a run count upon launch.

## Runs

You can have the bot do runs in one of two ways.

### Queue'd Runs

Flag: `-q` / `--queue` (queue string)

Pass the flag a queue string that matches into the regular expression `(\d+)[hnHN]`.

Examples:

- `-q 1h3n` Would do one hard and three normals
- `--queue 1h1n1h` Would do one hard, one normal, and one last hard
- `-q 10h2000n` Would do ten hards and two thousand normals

### Mono-typed Runs

Flag: `-r` / `--runs` (run count)

In conjuction with the hard flags this arg will do n runs based on the input number. All of the same type.

## Extra Team Selection

### Select Team

Flag: `-t` / `--team` (team index (starting from zero) in `Config/TeamConfig.csv`)

The `--team` argument is only intended to be used if you have to restart / start the program in the middle of a Mirror Dungeon run. Otherwise, the program will pick the team with the best rest bonus and use that.

### Load Last

Flag: `-l` / `--loadLast`

Alternatively, you can use the `--loadLast` argument. Which will load whatever team was selected last time.

## Hard mode

Flag: `-m` / `--hardMode`

The `--hardMode` argument will run hard mode dungeons when True and normal dungeons when False. If weekly bonus is available and hard mode is on it will claim all bonuses. Otherwise it will claim no bonuses in normal mode.

### One Weekly Bonus Per Run

Flag: `-b` / `--oneBonusPerRun`

The `--oneBonusPerRun` argument will make the bot claim only one weekly bonus per run for optimal enkephalin per BP level.

## Other

Pressing `q` in the terminal window will stop the program.

## Team Configuration

The top of the CSV file should have the headers `TeamRow,Type,Sinner1,Sinner2,Sinner3,Sinner4,Sinner5,Sinner6,Sinner7,Sinner8,Sinner9,Sinner10,Sinner11,Sinner12`.

After that each row should contain, the row number in the game the team is on "Team #n", the status of the team (Burn, Bleed, Slash, etc.), and then the deployment order of the sinners (Gregor, HongLu, YiSang, etc.).

An example configuration would look like this,

```csv
TeamRow,Type,Sinner1,Sinner2,Sinner3,Sinner4,Sinner5,Sinner6,Sinner7,Sinner8,Sinner9,Sinner10,Sinner11,Sinner12
1,Burn,Gregor,Outis,YiSang,Faust,Sinclair,Don,Ishmael,Meursault,HongLu,Ryoshu,Rodya,Heathcliff
2,Bleed,Don,Rodya,Heathcliff,Ishmael,Outis,Gregor,YiSang,Ryoshu,Faust,Sinclair,Meursault,HongLu
3,Charge,Ryoshu,Outis,Don,Heathcliff,Ishmael,Gregor,Sinclair,YiSang,Faust,Meursault,HongLu,Rodya
7,Poise,Meursault,YiSang,HongLu,Faust,Don,Heathcliff,Outis,Sinclair,Gregor,Rodya,Ishmael,Ryoshu
```
