import logging
import random
import time
import math
import csv
import os

from dataclasses import dataclass
from typing import Self

import pyautogui
import numpy as np
import pyscreeze

from PIL import Image

logging.basicConfig(format='%(levelname)s:%(funcName)s - %(message)s', level=logging.DEBUG)

IMAGE_DIR = 'Images/'

@dataclass
class GameElement:
    id: int
    image: str
    region: tuple[int, int, int, int] | None = None
    confidence: float = 0.8
    grayscale: bool = True

    def __str__(self) -> str:
        return f'{self.id=} {self.image=} {self.region=} {self.confidence=} {self.grayscale=}'

REST_BONUS_REGION = (1750,780,60,60)

NODE1PATHPIXELS = ((825,430),(829,326),(815,526))
NODE2PATHPIXELS = ((1220,111),(1220,226))
NODE3PATHPIXELS = ((1247,433),(1214,323),(1201,529))
NODE4PATHPIXELS = ((1229,754),(1267,635))
NODEPATHSEARCHNEAR = (825,430)
NODEPATHSEARCHFAR = (1247,433)
NODE2REGION = (990,70,250,250)
NODE3REGION = (992,368,250,250)
NODE4REGION = (990,716,250,250)
NODE5REGION = (1385,70,250,250)
NODE6REGION = (1385,368,250,250)
NODE7REGION = (1385,716,250,250)

GAME_ELEMENTS = {
    "ClearAllCaches" : GameElement(0, "ClearAllCaches.png", (285, 950, 250, 100)),
    "Drive" : GameElement(1, "Drive.png", (1236, 907, 150, 150), 0.75),
    "MD6Button" : GameElement(2, "MD6Button.png", (520,351,300,250)),
    "MD6StartButton" : GameElement(3, "MD6StartButton.png", (715,255,550,650), 0.6),
    "EnterMD" : GameElement(4, "EnterMD.png", (960,690,400,100)),
    "LowLevelCheck" : GameElement(27, "LowLevelCheck.png", (641,351,650,150)),
    "StarlightBonus" : GameElement(5, "StarlightBonus.png", (1600,770,300,250), 0.75),
    "DungeonProgress" : GameElement(6, "DungeonProgress.png", (812,325,300,100), 0.75),
    "Starlight_Guidance" : GameElement(7, "Starlight_Guidance.png", (828,579,350,200), 0.75),
    "Will_You_Buff" : GameElement(8, "Will_You_Buff.png", (750,280,550,100), 0.75),
    "Starting_Gift" : GameElement(9, "Starting_Gift.png", (1100,150,600,300)),
    "EGO_GIFT_GET" : GameElement(10, "EGO_GIFT_GET.png", (817,249,350,100)),
    "Theme_Pack" : GameElement(11, "Theme_Pack.png", (967,150,250,100)),
    "SelectEventEffect" : GameElement(26, "SelectEventEffect.png", (564,200,900,300)), #rare occurence of multiple event status effects
    "NodeSelect" : GameElement(12, "NodeSelect.png", (1802,115,100,100), 0.9),
    "Event_Skip" : GameElement(13, "Event_Skip.png"),
    "Team_Total_Participants" : GameElement(14, "Team_TotalParticipants.png", (1595,750,150,100)),
    "Battle_Winrate" : GameElement(15, "Battle_Winrate.png", (800,750,1120,200)),
    "Shop_Refresh" : GameElement(16, "Shop_Refresh.png", (1385,147,250,100)),
    "Select_Encounter_Reward" : GameElement(17, "Select_Encounter_Reward.png", (383, 148,850,150)),
    "RefuseGift" : GameElement(18, "RefuseGift.png", (1285,816,300,150)),
    "End_Passlvlup" : GameElement(19, "End_Passlvlup.png", (818,347,350,100)),
    "End_Victory" : GameElement(20, "End_Victory.png", (1375,150,500,500)),
    "End_ClaimTheRewards" : GameElement(21, "End_ClaimTheRewards.png", (750,450,450,200), 0.7),
    "End_ClaimTheRewards1" : GameElement(22, "End_ClaimTheRewards1.png", (750,450,450,200), 0.7),
    "End_ExplorationReward" : GameElement(23, "End_ExplorationReward.png", (725,126,400,100)),
    "End_ExplorationComplete" : GameElement(24, "End_ExplorationComplete.png", (179,112,300,200)),
    "End_Defeat" : GameElement(25, "End_Defeat.png", (1475,192,300,150)),
    "Team_TwelveOfTwelve" : GameElement(-2, "Team_TwelveOfTwelve.png", (1595,750,300,200)),
    "RestBonus_0" : GameElement(-2, "RestBonus_0.png", REST_BONUS_REGION, 0.95, False),
    "RestBonus_1" : GameElement(-2, "RestBonus_1.png", REST_BONUS_REGION, 0.9, False),
    "RestBonus_2" : GameElement(-2, "RestBonus_2.png", REST_BONUS_REGION, 0.9, False),
    "RestBonus_3" : GameElement(-2, "RestBonus_3.png", REST_BONUS_REGION, 0.9, False),
    "RestBonus_4" : GameElement(-2, "RestBonus_4.png", REST_BONUS_REGION, 0.9, False),
    "RestBonus_5" : GameElement(-2, "RestBonus_5.png", REST_BONUS_REGION, 0.925, False),
    "RestBonus_6" : GameElement(-2, "RestBonus_6.png", REST_BONUS_REGION, 0.9, False),
    "RestBonus_7" : GameElement(-2, "RestBonus_7.png", REST_BONUS_REGION, 0.925),
    "RestBonus_8" : GameElement(-2, "RestBonus_8.png", REST_BONUS_REGION, 0.95, False),
    "RestBonus_9" : GameElement(-2, "RestBonus_9.png", REST_BONUS_REGION, 0.9, False),
    "ResumeMD5" : GameElement(-2, "ResumeMD5.png", (781,566,400,100)),
    "Teams" : GameElement(-2, "Teams.png", (143,411,200,100)),
    "ConfirmTeam" : GameElement(-2, "ConfirmTeam.png"),
    "ConfirmBuff" : GameElement(-2, "ConfirmBuff.png"),
    "EGOGift_Confirm" : GameElement(-2, "EGOGift_Confirm.png", grayscale=False),
    "Pack_Hard" : GameElement(-2, "Pack_Hard.png", grayscale=False),
    "Pack_Hanger" : GameElement(-2, "Pack_Hanger.png", grayscale=False),
    "Clock_Face" : GameElement(-2, "Clock_Face.png", confidence=0.7, grayscale=False),
    "Enter_Node" : GameElement(-2, "Enter_Node.png", confidence=0.9, grayscale=False),
    "Event_Choices" : GameElement(-2, "Event_Choices.png", grayscale=False),
    "Event_EGOGIFT" : GameElement(-2, "Event_EGOGIFT.png", confidence=0.7, grayscale=False),
    "Event_Predicted" : GameElement(-2, "Event_Predicted.png", grayscale=False),
    "Event_VeryHigh" : GameElement(-2, "Event_VeryHigh.png", confidence=0.7, grayscale=False),
    "Event_High" : GameElement(-2, "Event_High.png", confidence=0.7, grayscale=False),
    "Event_Normal" : GameElement(-2, "Event_Normal.png", confidence=0.7, grayscale=False),
    "Event_Low" : GameElement(-2, "Event_Low.png", confidence=0.7, grayscale=False),
    "Event_VeryLow" : GameElement(-2, "Event_VeryLow.png", confidence=0.7, grayscale=False),
    "Event_Commence" : GameElement(-2, "Event_Commence.png", grayscale=False),
    "Event_Continue" : GameElement(-2, "Event_Continue.png", grayscale=False),
    "Event_Proceed" : GameElement(-2, "Event_Proceed.png", grayscale=False),
    "Event_CommenceBattle" : GameElement(-2, "Event_CommenceBattle.png", grayscale=False),
    "Team_ClearSelection" : GameElement(-2, "Team_ClearSelection.png", (1592,692,300,100), confidence=0.925, grayscale=False),
    "Shop_Item" : GameElement(-2, "Shop_Item.png", (1051,325,850,700), confidence=0.935),
    "Shop_Leave" : GameElement(16, "Shop_Leave.png", grayscale=False, confidence=0.7),
    "Reward_EGOGIFT" : GameElement(-2, "Reward_EGOGIFT.png", grayscale=False),
    "Reward_Cost" : GameElement(-2, "Reward_Cost.png", grayscale=False),
    "Reward_Starlight" : GameElement(-2, "Reward_Starlight.png", grayscale=False),
    "AcquireEGOGIFT" : GameElement(-2, "AcquireEGOGIFT.png", confidence=0.9, grayscale=False),
    "Plus1" : GameElement(-2, "Plus1.png", confidence=0.95, grayscale=False),
    "End_NoRewards" : GameElement(-2, "End_NoRewards.png", grayscale=False),
    "Shop_Item1" : GameElement(-2, "Shop_Item.png", (1051,325,850,700), confidence=0.935),
    "Shop_Item2" : GameElement(-2, "Shop_Item.png", (821,563,1150,500), confidence=0.935),
    "Rest1" : GameElement(-2, "Rest1.png", confidence=0.97, grayscale=False),
    "Rest2" : GameElement(-2, "Rest2.png", confidence=0.97, grayscale=False),
    "Rest3" : GameElement(-2, "Rest3.png", confidence=0.97, grayscale=False),
    "Rest4" : GameElement(-2, "Rest4.png", confidence=0.97, grayscale=False),
    "Rest5" : GameElement(-2, "Rest5.png", confidence=0.955, grayscale=False),
    "Relief" : GameElement(-2, "Relief.png", confidence = 0.9, grayscale = False),
    "ConfirmEventEffect" : GameElement(-2, "ConfirmEventEffect.png", confidence = 0.9, grayscale = False),
    "LowLevelConfirm" : GameElement(-2, "LowLevelConfirm.png", (974,700,400,150), confidence = 0.8, grayscale = False)
}


BASE_STATES = [
    "ClearAllCaches",
    "Drive",
    "MD6StartButton",
    "EnterMD",
    "LowLevelCheck",
    "StarlightBonus",
    "DungeonProgress",
    "Starlight_Guidance",
    "Will_You_Buff",
    "Starting_Gift",
    "EGO_GIFT_GET",
    "Theme_Pack",
    "SelectEventEffect",
    "NodeSelect",
    "Event_Skip",
    "Team_Total_Participants",
    "Battle_Winrate",
    "Shop_Refresh",
    "Select_Encounter_Reward",
    "RefuseGift",
    "End_Passlvlup",
    "End_Victory",
    "End_ClaimTheRewards",
    "End_ClaimTheRewards1",
    "End_ExplorationReward",
    "End_ExplorationComplete",
    "End_Defeat"
]

DEFAULT_TEAMS = [
    [1, "Charge","YiSang", "Faust", "Don", "Ryoshu", "Meursault", "HongLu", "Heathcliff", "Ishmael", "Rodya", "Sinclair", "Outis", "Gregor"],
    [2, "Sinking","YiSang", "Faust", "Don", "Ryoshu", "Meursault", "HongLu", "Heathcliff", "Ishmael", "Rodya", "Sinclair", "Outis", "Gregor"],
    [3, "Bleed","YiSang", "Faust", "Don", "Ryoshu", "Meursault", "HongLu", "Heathcliff", "Ishmael", "Rodya",  "Sinclair", "Outis", "Gregor"],
    [4, "Burn","YiSang", "Faust", "Don", "Ryoshu", "Meursault", "HongLu", "Heathcliff", "Ishmael", "Rodya", "Sinclair", "Outis", "Gregor"],
    [5, "Rupture","YiSang", "Faust", "Don", "Ryoshu", "Meursault", "HongLu", "Heathcliff", "Ishmael", "Rodya", "Sinclair", "Outis", "Gregor"],
    [6, "Tremor","YiSang", "Faust", "Don", "Ryoshu", "Meursault", "HongLu", "Heathcliff", "Ishmael", "Rodya", "Sinclair", "Outis", "Gregor"]
]


SINNER_COORDINATES = {
    "yisang": (435, 339),
    "faust": (637, 331),
    "don": (838, 340),
    "ryoshu": (1026, 343),
    "meursault": (1238, 345),
    "honglu": (1429, 352),
    "heathcliff": (436, 647),
    "ishmael": (634, 640),
    "rodya": (842, 636),
    "sinclair": (1041, 628),
    "outis": (1232, 639),
    "gregor": (1432, 646),
}

class MirrorDungeonRunner:
    width: int
    height: int
    curTeam: list
    teams: list

    resizing_needed: bool = False
    image_dir: str = IMAGE_DIR

    curState: int = -1

    teamSelected: bool = False

    reselectNodePathColors: bool = True
    nodePathColorNear: tuple
    nodePathColorFar: tuple

    def __init__(self, team_id: int | None = None) -> Self:
        self._get_screen_size()
        self._loadTeamConfigs()

        if team_id:
            self.curTeam = self.teams[team_id]

    def _get_screen_size(self) -> None:
        self.width, self.height = pyautogui.size()

        self.resizing_needed = (self.width, self.height) != (1920, 1080)

        if self.resizing_needed:

            logging.info(f'Alternative screen size ({self.height}, {self.width}) detected.')

            aspect_ratio: float = self.width / self.height
            if aspect_ratio != 16 / 9:
                logging.warning(f'Aspect ratio is not 16:9, the program might not work very well. {aspect_ratio=}')

            self.scale_images()

    def scale_images(self) -> None:
        logging.info("Scaling assets for new screen size.")

        # Make scaled images dir and wipe it
        os.makedirs('Scaled_Images/', exist_ok=True)

        for filename in os.listdir('Scaled_Images/'):
            file_path: str = os.path.join('Scaled_Images/', filename)
            if os.path.isfile(file_path):
                os.remove(file_path)

        # Scale all images for new screen size
        for filename in os.listdir(self.image_dir):
            image: Image.Image = Image.open(filename)

            # There are a couple of resampling algorithms that could be used here, LANCZOS is highest quality according to the docs
            # https://pillow.readthedocs.io/en/stable/handbook/concepts.html#concept-filters
            resized_image = image.resize(
                self.scale_coordinate(image.size),
                resample=Image.Resampling.LANCZOS
            )

            resized_image_path: str = os.path.join('Scaled_Images/', filename)
            resized_image.save(resized_image_path)

        # Set image dir to resized images
        self.image_dir = 'Scaled_Images/'

    def _makeConfig(self) -> None:
        with open("Config/TeamConfig.csv", 'w', newline='') as file:
            csv_writer = csv.writer(file)
            header = ["TeamRow","Type","Sinner1", "Sinner2", "Sinner3", "Sinner4", "Sinner5", "Sinner6", "Sinner7", "Sinner8", "Sinner9", "Sinner10", "Sinner11", "Sinner12"]
            csv_writer.writerows([header].extend(DEFAULT_TEAMS))

    def _loadTeamConfigs(self) -> None:
        if not os.path.exists("Config/"):
            os.makedirs("Config")
            self._makeConfig()
        elif not os.path.exists("Config/TeamConfig.csv"):
            self._makeConfig()

        with open('Config/TeamConfig.csv', 'r') as file:
            csv_reader = csv.reader(file)
            self.teams = []

            # TODO : test self.teams = csv_reader[1:] (idk if csv_reader is an iteratable, i think i can tho)
            for i, row in enumerate(csv_reader):
                if i > 0:
                    self.teams.append(row)

        self.curTeam = self.teams[0]

    def scale_coordinate(self, coord: tuple[int, int]) -> tuple[int, int]:
        x, y = coord

        return (self.scale_x(x), self.scale_y(y))

    def scale_region(self, coords: tuple [int, int, int, int]) -> tuple[int, int, int, int]:
        # Idk if this order is right, docs don't say!
        x2, y2, x1, y1 = coords

        return (
            self.scale_x(x2), self.scale_y(y2),
            self.scale_x(x1), self.scale_y(y1)
        )

    def scale_x(self, x: int) -> int:
        return (x / 1920) * self.width

    def scale_y(self, y: int) -> int:
        return (y / 1080) * self.height

    def on_screen(self, game_element: GameElement | str) -> bool:
        if type(game_element) == str:
            game_element: GameElement = GAME_ELEMENTS[game_element]

        image_path: str = os.path.join(self.image_dir, game_element.image)
        try:
            pyautogui.locateOnScreen(
                image_path,
                confidence=game_element.confidence,
                grayscale=game_element.grayscale,
                region=game_element.region
            )
            return True
        except:
            return False

    # Pylance say's it's return a "Box" but i can't find what lib that's from, so i'm calling it a tuple
    def locate_on_screen(self, game_element: GameElement | str) -> tuple | None:
        if type(game_element) == str:
            game_element: GameElement = GAME_ELEMENTS[game_element]

        image_path: str = os.path.join(self.image_dir, game_element.image)

        region = game_element.region
        if self.resizing_needed:
            region = self.scale_region(region)

        try:
            return pyautogui.locateOnScreen(
                image_path,
                confidence=game_element.confidence,
                grayscale=game_element.grayscale,
                region=region
            )
        except:
            return

    def locate_all_on_screen(self, game_element: GameElement | str) -> list:
        if type(game_element) == str:
            game_element: GameElement = GAME_ELEMENTS[game_element]

        image_path: str = os.path.join(self.image_dir, game_element.image)

        region = game_element.region
        if self.resizing_needed:
            region = self.scale_region(region)

        try:
            things = list(pyautogui.locateAllOnScreen(
                image_path,
                confidence=game_element.confidence,
                grayscale=game_element.grayscale,
                region=region
            ))
            return things
        except:
            return None

    # Disgusting method, but it needs all these types to match normal pyautogui.click() functionality
    def human_click(self, x: GameElement | str | tuple | pyscreeze.Point | int | None = None, y: int | None = None) -> bool:
        if type(x) == str:
            x = GAME_ELEMENTS[x]

        location = None
        if type(x) == GameElement:
            location = self.locate_on_screen(x)
            if not location:
                return False
        elif type(x) == tuple:
            location = x
        elif type(x) == pyscreeze.Point:
            location = x

        if type(x) == int or type(x) == np.int64:
            if type(y) != int and type(y) != np.int64:
                logging.error(f'Type of argument y should be int, not {type(y)}')
                return False

            logging.debug(f'moving mouse to {x=} {y=}')

            pyautogui.mouseDown(x, y)
        else:
            pyautogui.mouseDown(location)

        # Average human click duration is 85ms, or 0.085s
        time.sleep(min(max(random.gauss(0.085, 0.5), 0.05), 0.1))
        pyautogui.mouseUp()

        return True

    def move_to_element(self, game_element: GameElement | str) -> bool:
        if type(game_element) == str:
            game_element: GameElement = GAME_ELEMENTS[game_element]

        try:
            pyautogui.moveTo(self.locate_on_screen(game_element))
            return True
        except:
            return False

    def _neutralizeMousePos(self) -> None:
        pyautogui.moveTo(self.width/2, 0)

    def find_state(self) -> int:
        for state_name in BASE_STATES:
            game_element: GameElement = GAME_ELEMENTS[state_name]

            if self.on_screen(game_element):
                if game_element.id == 1: # aka it's the drive button
                    if self.on_screen('MD6Button'):
                        return 2

                return game_element.id

        return -1

    def get_to_mirror_dungeon(self) -> None:
        while True:
            time.sleep(random.uniform(1.0, 5.0))

            state: int = self.find_state()

            logging.debug(f'{state=}')

            match state:
                case 0:
                    self.human_click(self.width/2, self.height/2)
                case 1:
                    self.human_click('Drive')
                case 2:
                    self.human_click('MD6Button')
                case 3:
                    self.human_click(GameElement(3, "MD6StartButton.png", (715,255,550,650), 0.2))
                case 4:
                    self.human_click('EnterMD')
                case 6:
                    self.human_click('ResumeMD5')
                case -1:
                    pass
                case _:
                    return

    def selectBuffs(self):
        self.human_click(963,727)
        self.human_click(682,725)
        self.human_click(1250,280)
        self.human_click(400,400)
        self.human_click(700,400)
        self.human_click(1756,991)

    def get_rest_bonus(self) -> int:
        rest_bonus = 0

        # TODO : Add rest bonuses beyond 5 xD
        for i in range(1, 6):
            temp = self.locate_all_on_screen(f'Rest{i}')
            if temp:
                logging.debug(f'{len(temp)}, {i} rest bonuses')
                rest_bonus += min(len(temp), 12) * i

        return rest_bonus

    def scrollTo(self, dest: int, cur: int) -> int:
        diff: int = cur - dest
        if diff == 0:
            return cur
        baseDrag = 86

        move = baseDrag * diff / abs(diff)

        for i in range(abs(diff)):
            pyautogui.mouseDown()
            pyautogui.moveRel(0, move, duration=0.3, tween=pyautogui.easeOutQuad)
            time.sleep(random.uniform(0.3, 0.5))
            pyautogui.mouseUp()
            pyautogui.moveRel(0, -move)

        return dest

    def selectTeam(self) -> None:
        self.move_to_element('Teams')
        pyautogui.moveRel(0, 50)

        for i in range(30):
            pyautogui.scroll(clicks=100)

        curRow = 1
        maxBonus = 0
        maxTeamRow = 1

        for team in self.teams:
            curRow = self.scrollTo(int(team[0]), curRow)
            time.sleep(random.uniform(0.3, 2.0))
            self.human_click()

            time.sleep(random.uniform(0.1, 0.7))

            rest_bonus: int = self.get_rest_bonus()
            logging.debug(f'{curRow=} {rest_bonus=}')

            if rest_bonus > maxBonus:
                maxBonus = rest_bonus

                maxTeamRow = int(team[0])
                self.curTeam = team

        curRow = self.scrollTo(maxTeamRow, curRow)
        time.sleep(random.uniform(0.1, 0.7))
        self.human_click()

        while not self.human_click('ConfirmTeam'):
            pass

        time.sleep(1)

    def selectStartingGifts(self) -> None:
        giftType: str = self.curTeam[1].lower()
        match giftType:
            case "charge":
                self.human_click(758,667)
            case "sinking":
                self.human_click(307,680)
            case "poise":
                self.human_click(522,669)
            case "rupture":
                self.human_click(975,359)
            case "tremor":
                self.human_click(748,362)
            case "bleed":
                self.human_click(520,360)
            case "burn":
                self.human_click(312,365)
            case "slash":
                self.human_click(980,685)
            case "blunt":
                self.human_click(533,844)
            case "pierce":
                self.human_click(313,846)

        time.sleep(random.uniform(0.1, 0.6))
        #select gifts from top to bottom
        self.human_click(1463,392)
        self.human_click(1463,550)
        self.human_click(1463,713)
        #end selection
        self.human_click(1620,870)

    def run_md(self) -> None:
        self.teamSelected = False
        while True:
            self._neutralizeMousePos()

            time.sleep(0.1)

            if self.curState == -1:
                self.get_to_mirror_dungeon()

            self.curState = self.find_state()

            logging.debug(f'{self.curState=}')

            if not self.process_state():
                break

            time.sleep(0.1)

    def do_event(self) -> None:
        if self.on_screen('Event_Choices'):
            if not self.human_click('Event_EGOGIFT'):
                self.human_click(1366, 350)
                self.human_click(1366, 600)
                self.human_click(1366, 750)

        # Try to click best chances
        if self.on_screen("Event_Predicted"):
            for chance in ['VeryHigh', 'High', 'Normal', 'Low', 'VeryLow']:
                if self.human_click(f'Event_{chance}'):
                    break

        for event_state in ['Commence', 'Continue', 'Proceed', 'CommenceBattle']:
            element_name = f'Event_{event_state}'

            if self.on_screen(element_name):
                if not self.human_click(element_name):
                    self.human_click(1707, 950)
                break

        if self.human_click('Event_Skip'):
            for i in range(6):
                self.human_click()
                time.sleep(random.uniform(0.1, 0.5))


    def do_shop(self) -> None:
        for shop_name in ["Shop_Item1", "Shop_Item2"]:
            shopItems = self.locate_all_on_screen(shop_name)
            if not shopItems:
                continue

            for i in shopItems:
                pyautogui.click(i) # because i is probably a Box?
                time.sleep(random.uniform(0.75, 3.0))
                self.human_click(1120,712)
                time.sleep(random.uniform(0.75, 1.75))
                self.human_click(945,800)
                time.sleep(random.uniform(0.5, 1.5))

        self.human_click('Shop_Leave')
        time.sleep(random.uniform(0.5, 2.0))
        self.human_click(1171,743)
    
    def node_pathfind(self) -> bool:
        nodeScores = [0,0,0]
        tempScore = 0
        maxScore = 0
        maxScoreNode = 0
        if pyautogui.pixelMatchesColor(NODE1PATHPIXELS[0][0],NODE1PATHPIXELS[0][1],self.nodePathColorNear, tolerance = 10):
            nodeScores[0] = self.get_node_rating(NODE3REGION)
            tempScore = nodeScores[0]
            if pyautogui.pixelMatchesColor(NODE3PATHPIXELS[0][0],NODE3PATHPIXELS[0][1],self.nodePathColorFar, tolerance = 10):
                if tempScore < nodeScores[0] + self.get_node_rating(NODE6REGION):
                    tempScore = nodeScores[0] + self.get_node_rating(NODE6REGION)
            if pyautogui.pixelMatchesColor(NODE3PATHPIXELS[1][0],NODE3PATHPIXELS[1][1],self.nodePathColorFar, tolerance = 10):
                if tempScore < nodeScores[0] + self.get_node_rating(NODE5REGION):
                    tempScore = nodeScores[0] + self.get_node_rating(NODE5REGION)
            if pyautogui.pixelMatchesColor(NODE3PATHPIXELS[2][0],NODE3PATHPIXELS[2][1],self.nodePathColorFar, tolerance = 10):
                if tempScore < nodeScores[0] + self.get_node_rating(NODE7REGION):
                    tempScore = nodeScores[0] + self.get_node_rating(NODE7REGION)
            nodeScores[0] = tempScore
            if maxScore < nodeScores[0]:
                maxScore = nodeScores[0]
                maxScoreNode = 3
        
        if pyautogui.pixelMatchesColor(NODE1PATHPIXELS[1][0],NODE1PATHPIXELS[1][1],self.nodePathColorNear, tolerance = 10):
            nodeScores[1] = self.get_node_rating(NODE2REGION)
            tempScore = nodeScores[1]
            if pyautogui.pixelMatchesColor(NODE2PATHPIXELS[0][0],NODE2PATHPIXELS[0][1],self.nodePathColorFar, tolerance = 10):
                if tempScore < nodeScores[1] + self.get_node_rating(NODE5REGION):
                    tempScore = nodeScores[1] + self.get_node_rating(NODE5REGION)
            if pyautogui.pixelMatchesColor(NODE2PATHPIXELS[1][0],NODE2PATHPIXELS[1][1],self.nodePathColorFar, tolerance = 10):
                if tempScore < nodeScores[1] + self.get_node_rating(NODE6REGION):
                    tempScore = nodeScores[1] + self.get_node_rating(NODE6REGION)
            nodeScores[1] = tempScore
            if maxScore < nodeScores[1]:
                maxScore = nodeScores[1]
                maxScoreNode = 2
        
        if pyautogui.pixelMatchesColor(NODE1PATHPIXELS[2][0],NODE1PATHPIXELS[2][1],self.nodePathColorNear, tolerance = 10):
            nodeScores[2] = self.get_node_rating(NODE4REGION)
            tempScore = nodeScores[2]
            if pyautogui.pixelMatchesColor(NODE4PATHPIXELS[0][0],NODE4PATHPIXELS[0][1],self.nodePathColorFar, tolerance = 10):
                if tempScore < nodeScores[2] + self.get_node_rating(NODE6REGION):
                    tempScore = nodeScores[2] + self.get_node_rating(NODE6REGION)
            if pyautogui.pixelMatchesColor(NODE4PATHPIXELS[1][0],NODE4PATHPIXELS[1][1],self.nodePathColorFar, tolerance = 10):
                if tempScore < nodeScores[2] + self.get_node_rating(NODE7REGION):
                    tempScore = nodeScores[2] + self.get_node_rating(NODE7REGION)
            nodeScores[2] = tempScore
            if maxScore < nodeScores[2]:
                maxScore = nodeScores[2]
                maxScoreNode = 4
        print(maxScoreNode)

        match maxScoreNode:
            case 3:
                self.human_click(pyautogui.center(NODE3REGION))
                return True
            case 2:
                self.human_click(pyautogui.center(NODE2REGION))
                return True
            case 4:
                self.human_click(pyautogui.center(NODE4REGION))
                return True

        
        return False

    
    def get_node_rating(self, region: tuple) -> int:
        if self.on_screen(GameElement(-2, "Node_Event.png", region, grayscale = True)):
            return 4
        if self.on_screen(GameElement(-2, "Node_EventFar.png", region, grayscale = True)):
            return 4
        if self.on_screen(GameElement(-2, "Node_Midboss.png", region, grayscale = True)):
            return 3
        if self.on_screen(GameElement(-2, "Node_MidbossFar.png", region, grayscale = True)):
            return 3
        if self.on_screen(GameElement(-2, "Node_Combat.png", region, grayscale = True)):
            return 2
        if self.on_screen(GameElement(-2, "Node_CombatFar.png", region, grayscale = True)):
            return 2
        return 1

    # Main MD Logic Loop
    def process_state(self) -> bool:
        match self.curState:
            case 5: # Team Selection
                if self.on_screen('Teams'):
                    self.selectTeam()

            case 7: # MD6 Buff Selection
                if self.on_screen('Starlight_Guidance'):
                    self.selectBuffs()

            case 8: # End Buff Selection
                if self.on_screen('Will_You_Buff'):
                    self.human_click('ConfirmBuff')

            case 9: # Starting Gift Selection
                if self.on_screen('Starting_Gift'):
                    self.selectStartingGifts()

            case 10:
                if self.on_screen('EGO_GIFT_GET'):
                    self.human_click('EGOGift_Confirm')

            case 11: # Pack Selection
                if self.on_screen('Pack_Hard'):
                    self.human_click(1363, 100)
                self.move_to_element('Pack_Hanger')
                pyautogui.dragRel(0, 500, 1)
                reselectNodePathColors = True

            case 12: # Node Selection
                if (self.reselectNodePathColors):
                    self.nodePathColorNear = pyautogui.pixel(NODEPATHSEARCHNEAR[0],NODEPATHSEARCHNEAR[1])
                    self.nodePathColorFar = pyautogui.pixel(NODEPATHSEARCHFAR[0],NODEPATHSEARCHFAR[1])
                    self.reselectNodePathColors = False
                if (not self.node_pathfind()):
                    located = False
                    if self.on_screen('Clock_Face'):
                        time.sleep(random.uniform(0.5, 1.5))
                        coords: tuple = self.locate_on_screen('Clock_Face')
                        if coords:
                            x, y = pyautogui.center(coords)
                            pyautogui.moveTo(x, y)
                            time.sleep(random.uniform(0.1, 0.5))
                            x += 330
                            y -= 280
                            self.human_click(x, y)
                            time.sleep(random.uniform(0.2, 0.5))
                            located = True

                    failCounter = 0
                    if located:
                        while not self.on_screen('Enter_Node'):
                            logging.debug(f'trying to enter node {x=} {y=}')
                            y += 300
                            self.human_click(x, y)
                            time.sleep(random.uniform(0.25, 1.5))
                            failCounter += 1
                            if failCounter > 3:
                                break
                        time.sleep(random.uniform(0.35, 1.0))
                        pyautogui.press('enter')

                if self.on_screen('Enter_Node'):
                    pyautogui.press('enter')

            case 13: # Event
                self.do_event()

            case 14: # Pre-fight Sinner Selection
                if not self.teamSelected or not self.on_screen("Team_TwelveOfTwelve"):
                    if self.on_screen("Team_ClearSelection"):
                        self.human_click(1715, 720)
                        time.sleep(random.uniform(0.5, 1.0))
                        self.human_click(1145, 740)
                        time.sleep(random.uniform(0.5, 1.0))

                    for i in range(12):
                        self.human_click(SINNER_COORDINATES[self.curTeam[i+2].lower()])
                        time.sleep(random.uniform(0.3, 1.5))
                    
                    self.teamSelected = True

                time.sleep(random.uniform(0.25, 0.75))
                self.human_click(1720,880)
                time.sleep(random.uniform(0.5, 2))

            case 15: # OMG P-ENTER!!!
                self.human_click(self.width / 2, self.height / 6)
                time.sleep(random.uniform(0.05, 0.25))
                pyautogui.press('p')
                time.sleep(random.uniform(0.05, 0.25))
                pyautogui.press('enter')

            case 16: # Shop
                self.do_shop()
                self.human_click('Shop_Leave')

            case 17: # Ego Gift Reward 1
                if not self.human_click('Reward_EGOGIFT'):
                    if not self.human_click('Reward_Cost'):
                        self.human_click('Reward_Starlight')
                time.sleep(random.uniform(0.5, 1.0))
                self.human_click(1200, 800)

            case 18: # Ego Gift Reward 2 (Acquire)
                if not self.human_click('AcquireEGOGIFT'):
                    self.human_click('Plus1')
                time.sleep(random.uniform(0.2, 1.5))
                self.human_click(1705, 870)

            case 19: # Collect Rewards Confirm (pass level up)
                self.human_click(963, 700)
                return False

            case 20: # End Victory
                self.human_click(1671, 839)

            case 21: # End Claim rewards 1
                self.human_click(1150, 750)

            case 22: # End claim rewards 2
                self.human_click(1150, 750)

            case 23: # End exploration reward
                self.human_click(1330, 810)

            case 24: # End exploration complete
                self.human_click(1700, 900)

            case 25: # Defeat Failsafe
                while True:
                    if self.on_screen('End_Defeat'):
                        self.human_click(1673, 840)
                    if self.on_screen('End_NoRewards'):
                        time.sleep(random.uniform(1.0, 2.5))
                        self.human_click(1153, 740)
                        break
                    elif self.on_screen('End_ExplorationReward'):
                        self.human_click(587, 814)
                    elif self.on_screen('End_ExplorationComplete'):
                        self.human_click(1700, 900)
                    time.sleep(random.uniform(0.1, 0.5))
            case 26:
                self.human_click("Relief");
                time.sleep(random.uniform(0.1,0.5))
                self.human_click("ConfirmEventEffect")
            case 27:
                self.human_click("LowLevelConfirm")
                time.sleep(1)
        return True


