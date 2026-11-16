"""
YELLOW BITER  -  built from our game storyboard.

Scene order:
  Intro video -> Loading screen -> Title menu (Start Game / Settings / Quit)
  -> Main gameplay (tutorial -> Level 1 -> Level 2 -> Level 3 boss) -> Victory + credits -> Title menu.
  Run out of lives in ANY gameplay scene -> GAME OVER (then retry).
Every scene fades out and fades in.

Keep chomper.py, the .png files, the "intro" folder and the "sounds" folder together in the SAME folder.
Run:  pip install pygame   then   python chomper.py
Controls: WASD / arrow keys move (and choose in menus), SPACE or ENTER select/skip, + / - volume, M mute,
          F11 (or F) full screen on/off, Esc = PAUSE during the game (Esc again = resume).
The selected menu text turns yellow - only one at a time.
"""
import math
import os
import random
import sys
from array import array

import pygame

GAME_NAME = "Yellow Biter"

# ---------------- CREDITS (Victory scene): put EVERY member's name and what they did ----------------
CREDITS = [
    ("Arthur Jake Abad", "Game Artist, Music, SFX"),
    ("Ramces Marc Padilla", "Game Developer, Game Designer, Programmer, Graphic Designer, VFX"),
    ("Jose Raphael Ramos", "Leader, Graphic Designer Assistant"),
]
SPECIAL_THANKS = "Canva and Claude AI for help."
DISCLAIMER = ("This game is a remake of Pac-Man by 1st year BSIT Students Group. "
              "We are not associated with Bandai Namco Entertainment. "
              "\u00a9 2026 Group 3 Disney All Rights Reserved.")

BOSS_TEXT = ("An Invisible ghost is here to chase you, try eating all as much as you can "
             "to disappear the invisible ghost.")

# ---------------- MAZES: # wall, . dot, o power star, - ghost door, G ghost house, P start ----------------
MAP = [
    "###################",
    "#........#........#",
    "#o##.###.#.###.##o#",
    "#.................#",
    "#.##.#.#####.#.##.#",
    "#....#...#...#....#",
    "####.###.#.###.####",
    "####.#       #.####",
    "####.# ##-## #.####",
    "    .  #GGG#  .    ",
    "####.# ##### #.####",
    "####.#       #.####",
    "####.# ##### #.####",
    "#........#........#",
    "#.##.###.#.###.##.#",
    "#o.#.....P.....#.o#",
    "##.#.#.#####.#.#.##",
    "#....#...#...#....#",
    "#.######.#.######.#",
    "#.................#",
    "###################",
]
MAP_CURSED = [      # the Cursed Maze (Level 3)
    "###################",
    "#o.......#.......o#",
    "#.###.##.#.##.###.#",
    "#.................#",
    "#.#..#.#####.#..#.#",
    "#.#..#...#...#..#.#",
    "####.###.#.###.####",
    "####.#       #.####",
    "####.# ##-## #.####",
    "    .  #GGG#  .    ",
    "####.# ##### #.####",
    "####.#       #.####",
    "####.# ##### #.####",
    "#..#.....#.....#..#",
    "#.#.###.#.#.###.#.#",
    "#.....#..P..#.....#",
    "#.###.#.....#.###.#",
    "#.#...#.###.#...#.#",
    "#.#.###.....###.#.#",
    "#o...............o#",
    "###################",
]
LEVELS = {
    0: dict(map=MAP, line=(66, 99, 255), fill=(14, 18, 56), boss=False),            # tutorial
    1: dict(map=MAP, line=(66, 99, 255), fill=(14, 18, 56), boss=False),
    2: dict(map=MAP, line=(60, 220, 140), fill=(8, 40, 30), boss=False),
    3: dict(map=MAP_CURSED, line=(190, 80, 255), fill=(34, 8, 52), boss=True),
}

# ---------------- SCREEN SIZES ----------------
COLS, ROWS = 19, 21
T = 42                              # tile size in pixels  (BIG map: 19 x 42 = 798 wide, 21 x 42 = 882 tall)
SPR = 48                            # sprites are drawn at 48 x 48 (the art is 32 x 32)
MW, MH = COLS * T, ROWS * T
SW, SH = 1920, 1080                 # the game is drawn at 1920 x 1080, then fitted to your screen
OX, OY = (SW - MW) // 2, (SH - MH) // 2     # where the maze sits
CX = SW // 2
WINDOW_SIZE = (1280, 720)           # size when you leave full screen (F11)
FADE_TIME = 0.45                    # seconds to fade out, and again to fade in

# ---------------- PICTURES ----------------
IMG_LOADING = "Loading_Screen_Yellow_Bitter.png"
IMG_FRAME = "Main_Gameplay_Preview_Yellow_Biter.png"
IMG_OVER = "Game_Over_Yellow_Biter.png"
IMG_LOGO = "Title_Logo.png"
MENU_IMAGES = {"main": "MENU.png", "pause": "PAUSE_MENU.png",
               "tabs": "PAUSE_MENU_SCREEN.png", "tabs_y": "PAUSE_MENU_SCREEN_SELECT_EACH.png"}
# where each menu word sits inside those 1920x1080 pictures: (x, y, width, height)
MAIN_LABELS = [(820, 570, 277, 24), (848, 659, 221, 24), (904, 748, 109, 24)]       # START GAME, SETTINGS, QUIT
PAUSE_LABELS = [(876, 347, 165, 24), (848, 436, 221, 24), (862, 525, 193, 24),      # RESUME, SETTINGS, RESTART,
                (778, 615, 361, 24), (834, 704, 249, 24)]                           # QUIT TO TITLE, QUIT GAME
TAB_LABELS = [(160, 110, 189, 21), (547, 110, 189, 21), (943, 110, 117, 21), (1265, 110, 141, 21),
              (1597, 110, 165, 21)]  # GAMEPLAY, CONTROLS, AUDIO, RETURN, CREDITS
MENU_YELLOW = (255, 225, 56)        # the selected word turns yellow (only one at a time)
TAB_ROWS = {0: 3, 2: 4}             # how many choices each settings tab has (CONTROLS, RETURN and CREDITS have none)

BG = (11, 12, 22)
YELLOW = (255, 208, 52)
WHITE = (244, 244, 244)
PINK = (244, 166, 212)
GREEN = (167, 240, 112)
RED = (230, 80, 100)
INK = (20, 24, 60)                  # dark text on the white panel
BLUE = (44, 112, 230)
GRAY = (120, 130, 160)
GOLD = (214, 140, 0)
DIRS = [(1, 0), (-1, 0), (0, 1), (0, -1)]
HOME = {0: (9, 9), 1: (8, 9), 2: (9, 9), 3: (10, 9), 4: (9, 9)}   # ghost house tiles

# the 4 ghosts drawn by our teammate (each sheet: 4 frames = down, up, left, right)
GHOST_FILES = ["ghost_direction_revised_1_png.png", "ghost_direction_revised_2.png",
               "ghost_direction_revised_3_png.png", "ghost_direction_revised_4_png.png"]

# sound effects and music made by our teammate (files are in the "sounds" folder).
# name used in the game -> file.  To swap a sound, just replace the file or change the name here.
SOUND_FILES = {
    "press": "press_button.wav",        # pressing a button / menu choice / volume change
    "quit": "quit.wav",                 # leaving the game
    "power": "acquire.wav",             # eating a power star
    "fruit": "acquire.wav",             # picking up the bonus fruit
    "clear": "round_complete.wav",      # level clear
    "lose": "game_over.wav",            # GAME OVER screen
    "victory": "game_win.ogg",          # boss defeated + Victory page
    "win_music": "win_game.ogg",        # credits music
    "title": "title_music.ogg",         # title menu music (8-bit)
    "music0": "music_tutorial.ogg",     # background music while playing: tutorial
    "music1": "music_level1.ogg",       #                                  level 1
    "music2": "music_level2.ogg",       #                                  level 2
    "music3": "music_level3.ogg",       #                                  level 3 (boss)
}
MUSIC_SOUNDS = {"title", "music0", "music1", "music2", "music3", "win_music", "victory"}   # the MUSIC slider; everything else is SOUND EFFECTS
LEVEL_MUSIC = {0: "music0", 1: "music1", 2: "music2", 3: "music3"}
VICTORY_PAGE = 8.5                  # seconds the "VICTORY!" page stays before the credits start
CREDITS_SPEED = 34.5                # how fast the credits scroll (pixels per second)
CREDITS_Y0 = SH - 90                # where the credits start

# ---------------- SETTINGS (tiles per second) - lower = slower, higher = faster ----------------
PAC_SPEED = 4.5             # Yellow-Biter
GHOST_SPEED = 3.6           # ghosts at level 1 (+0.3 faster every level)
GHOST_MAX = 5.0             # ghosts never go faster than this
SCARED_SPEED = 2.2          # scared ghosts (bats)
PHANTOM_SPEED = 3.8         # the invisible boss ghost
POWER_TIME = 10.0           # "Eat the ghosts under 10 seconds!"
START_VOLUME = 0.5          # 0.0 (silent) to 1.0 (loudest)
SPEED_NAMES = ("EASY", "NORMAL", "HARD")      # the GAME SPEED (difficulty) choice in Settings
PAC_MULT = (1.35, 1.25, 1.15)       # Yellow-Biter is always FASTER than the ghosts ...
GHOST_MULT = (0.65, 0.8, 0.95)      # ... and the ghosts are slower (EASY = slowest ghosts)
LIVES_OPTIONS = (3, 5, 7)                     # the LIVES choice in Settings
HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------- PIXEL LETTERS for the big VICTORY! text ----------------
FONT5 = {
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "I": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "C": (".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
}


# ---------------- IMAGES AND SPRITES ----------------
def load_image(name, alpha=True):
    path = os.path.join(HERE, name)
    if not os.path.exists(path):
        sys.exit(f"Missing image: {name}\nPut all the .png files in the same folder as chomper.py")
    img = pygame.image.load(path)
    return img.convert_alpha() if alpha else img.convert()


def frames(sheet, w, h, n):
    """Cut a sprite sheet (frames side by side) into a list of images."""
    return [sheet.subsurface((i * w, 0, w, h)).copy() for i in range(n)]


def tint(img, color):
    s = img.copy()
    s.fill((*color, 255), special_flags=pygame.BLEND_RGBA_MULT)
    return s


def fade(img, alpha):
    s = img.copy()
    s.fill((255, 255, 255, alpha), special_flags=pygame.BLEND_RGBA_MULT)
    return s


def lighten(img):
    s = img.copy()
    s.fill((90, 90, 90, 0), special_flags=pygame.BLEND_RGB_ADD)
    return s


class Sprites:
    def __init__(self):
        big = lambda f: pygame.transform.scale(f, (SPR, SPR))      # 32 -> 48 (the map is big now)
        # pacman_directions.png frame order: down, up, left, right
        d = frames(load_image("pacman_directions.png"), 32, 32, 4)
        self.pac_dir = {"down": big(d[0]), "up": big(d[1]), "left": big(d[2]), "right": big(d[3])}
        # pacman_chomp.png: 4 frames facing right (flip them for left)
        cr = frames(load_image("pacman_chomp.png"), 32, 32, 4)
        self.chomp = {"right": [big(f) for f in cr],
                      "left": [big(pygame.transform.flip(f, True, False)) for f in cr]}
        # the 4 ghosts drawn by our teammate. Frame order in each sheet: down, up, left, right
        ghost32 = [frames(load_image(n), 32, 32, 4) for n in GHOST_FILES]
        self.ghost_dir = [[big(f) for f in fr] for fr in ghost32]
        self.ghost_icon = [pygame.transform.scale(fr[0], (96, 96)) for fr in ghost32]
        self.ghost_icon_gone = [fade(i, 55) for i in self.ghost_icon]
        # the invisible boss ghost: the plain white ghost, tinted purple and drawn see-through
        plain = frames(load_image("ghost_directions.png"), 32, 32, 4)
        purple = [tint(f, (190, 120, 255)) for f in plain]
        self.phantom = {a: [big(fade(f, a)) for f in purple] for a in (30, 95, 175)}
        # scared ghosts turn into bats
        bat = frames(load_image("bat_flap.png"), 32, 32, 5)
        self.bat = [big(f) for f in bat]
        self.bat_light = [big(lighten(f)) for f in bat]
        # bonus fruit: 3 animation frames
        fr = load_image("fruits.png")
        self.fruit = [pygame.transform.smoothscale(fr.subsurface((i * 119, 0, 119, 120)).copy(), (54, 54))
                      for i in range(3)]
        # power stars: the first star of each of the 4 glow frames
        st = load_image("stars_glow.png")
        self.star = [pygame.transform.smoothscale(st.subsurface((i * 200 + 22, 23, 56, 54)).copy(), (33, 33))
                     for i in range(4)]
        self.life_big = pygame.transform.smoothscale(d[3], (66, 66))


# ---------------- SOUND: the sounds we did not get from the teammate are made in code ----------------
RATE = 22050


def hz(m):
    """MIDI note number -> frequency (A4 = 69 = 440 Hz)."""
    return 440.0 * 2 ** ((m - 69) / 12)


def render(parts):
    """parts: list of (freq, seconds, end_freq, wave, volume, hold). freq 0 = silence. Returns samples."""
    buf = []
    phase = 0.0
    for freq, dur, end, wave, vol, hold in parts:
        n = int(RATE * dur)
        if freq == 0:
            buf.extend([0.0] * n)
            continue
        end = end or freq
        for i in range(n):
            phase += (freq + (end - freq) * i / n) / RATE
            x = phase % 1
            if wave == "saw":
                s = 2 * x - 1
            elif wave == "tri":
                s = 4 * abs(x - .5) - 1
            else:
                s = 1.0 if x < .5 else -1.0
            env = min(1.0, i / 200, (n - i) / 400) if hold else 1 - i / n
            buf.append(s * env * vol)
    return buf


def sound(*tracks):
    """Mix one or more tracks into a pygame Sound."""
    n = max(len(t) for t in tracks)
    tracks = [t + [0.0] * (n - len(t)) for t in tracks]
    buf = array("h", (max(-32767, min(32767, int(sum(v) * 32767))) for v in zip(*tracks)))
    return pygame.mixer.Sound(buffer=buf.tobytes())


def blip(freq, dur, end=None, vol=0.3, wave="square"):
    return render([(freq, dur, end, wave, vol, False)])


def tune(notes, wave="square", vol=0.25):
    """notes: list of (midi_note, seconds); midi_note 0 = rest."""
    return render([(0 if m == 0 else hz(m), d, None, wave, vol, True) for m, d in notes])


def build_intro_sounds():   # built first, so the intro can play right away
    return {"start": sound(tune([(72, .1), (76, .1), (79, .1), (84, .1), (79, .1), (84, .35)]))}


def build_sounds():         # built while the loading screen is showing
    S = {}
    S["waka1"] = sound(blip(330, .05))                          # "Wak"
    S["waka2"] = sound(blip(250, .05))                          # "Wak"
    S["eat"] = sound(blip(500, .2, 1000))                       # eating a ghost
    S["death"] = sound(blip(500, .9, 60, .3, "saw"))
    S["siren"] = sound(render([(300, .6, 520, "tri", .07, True), (520, .6, 300, "tri", .07, True)]))  # Ghost Siren
    S["chase"] = sound(render([(180, .1, None, "square", .06, True), (230, .1, None, "square", .06, True)] * 3))
    return S


def load_sound_files():
    """The sound effects and music made by our teammate (SOUND_FILES above)."""
    S, cache = {}, {}
    for name, fname in SOUND_FILES.items():
        try:
            if fname not in cache:
                cache[fname] = pygame.mixer.Sound(os.path.join(HERE, "sounds", fname))
            S[name] = cache[fname]
        except (pygame.error, OSError):
            print(f"Could not load sounds/{fname} - using a beep instead")
            S[name] = sound(blip(440, .25))
    return S


# ---------------- CHARACTERS ----------------
class Actor:
    """Sits on tile (tx, ty) and slides toward the next tile (dx, dy). p = progress 0..1."""

    def __init__(self, tx, ty):
        self.tx, self.ty = tx, ty
        self.dx = self.dy = 0
        self.p = 0.0

    def pos(self):
        return self.tx + self.dx * self.p, self.ty + self.dy * self.p

    def flip(self):
        if self.dx or self.dy:
            self.tx = (self.tx + self.dx) % COLS
            self.ty += self.dy
            self.p = 1 - self.p
            self.dx, self.dy = -self.dx, -self.dy


class Ghost(Actor):
    def __init__(self, kind, state, wait):
        hx, hy = HOME[kind]
        super().__init__(hx, hy)
        self.hx, self.hy = hx, hy
        self.kind = kind            # 0..3 the four ghosts, 4 = invisible boss ghost
        self.state = state          # "house" or "out"
        self.wait = wait
        self.scared = False
        if state == "out":
            self.ty = 7


def detect_tabs(img):
    """Find where each tab word sits in the settings picture -> list of (x, y, w, h)."""
    w, h = img.get_size()
    band = [x for x in range(w) if any(sum(img.get_at((x, y))[:3]) > 300 for y in range(95, 150, 2))]
    groups, start, prev = [], None, None
    for x in band:
        if start is None:
            start = prev = x
        elif x - prev > 40:
            groups.append((start, prev))
            start = x
        prev = x
    if start is not None:
        groups.append((start, prev))
    return [(a, 110, b - a + 1, 21) for a, b in groups]


TAB_NAMES = ("GAMEPLAY", "CONTROLS", "AUDIO", "RETURN", "CREDITS")


def wrap(text, font, maxw):
    lines, cur = [], ""
    for word in text.split():
        t = (cur + " " + word).strip()
        if font.size(t)[0] <= maxw:
            cur = t
        else:
            lines.append(cur)
            cur = word
    lines.append(cur)
    return lines


# ---------------- THE GAME ----------------
class Game:
    def __init__(self):
        pygame.mixer.pre_init(22050, -16, 1, 512)
        pygame.init()
        pygame.display.set_caption(GAME_NAME)
        self.screen = pygame.Surface((SW, SH))   # the stage: everything is drawn here at 1920x1080
        self.k, self.off = 1.0, (0, 0)           # scale and position of the stage inside the window
        self.button = None                       # the clickable button (when visible)
        self.full = True
        self.set_fullscreen(True)
        self.clock = pygame.time.Clock()
        self.small = pygame.font.Font(None, 33)
        self.font = pygame.font.Font(None, 42)
        self.mid = pygame.font.Font(None, 60)
        self.big = pygame.font.Font(None, 84)
        # fade transition: alpha 255 = black. We start black and fade the first scene in.
        self._fade_win = None
        self.fade_alpha, self.fade_dir, self.pending = 255.0, -1, None
        # sound
        self.music = self.fx = None              # the two looping sound slots
        self.volume, self.muted = START_VOLUME, False
        self.music_vol, self.sfx_vol = 1.0, 1.0      # MUSIC and SOUND EFFECTS sliders (multiply the master volume)
        self.sounds = build_intro_sounds() if pygame.mixer.get_init() else {}
        self.apply_volume()
        # things loaded later, during the loading screen
        self.sp = self.frame = self.over_full = self.logo = self.menu_img = None
        self.loading_full = load_image(IMG_LOADING, False)
        self._ycache = {}
        self.menu_idx, self.pause_idx = 0, 0
        self.menu_rects = [pygame.Rect(r).inflate(80, 40) for r in MAIN_LABELS]
        self.pause_rects = [pygame.Rect(r).inflate(80, 40) for r in PAUSE_LABELS]
        self.tab_labels, self.tabs_from_image = list(TAB_LABELS), True
        self.tab_rects = [pygame.Rect(r).inflate(70, 50) for r in TAB_LABELS]
        self.row_rects, self.vol_rects = [], []
        self.paused = False
        # settings screen (opened from the title menu or the pause menu)
        self.settings_open = False
        self.set_tab, self.set_row, self.set_focus = 0, 0, "tabs"
        self.speed_idx, self.start_lives = 1, 3
        # intro video = a folder of frames (made from the intro video)
        self.intro_fps, self.intro_n = 24, 0
        try:
            with open(os.path.join(HERE, "intro", "meta.txt")) as f:
                a, b = f.read().split()
                self.intro_fps, self.intro_n = int(a), int(b)
        except (OSError, ValueError):
            pass
        self.intro_t, self._intro_idx, self._intro_img = 0.0, -1, None
        self.load_t, self.load_ticks, self.loaded = 0.0, 0, False
        self.hi = self.load_hi()
        self.score, self.lives, self.level_start_score = 0, 3, 0
        self.death_msg = ""
        self.end_t = 0.0
        self.credit_lines = []
        self.credits_started = False
        self.waka = 0
        self.setup_level(0)
        self.enter_intro()

    # ----- window, fades and sound helpers -----
    def set_fullscreen(self, on):
        self.full = on
        if on:
            self.window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)   # whole monitor
        else:
            self.window = pygame.display.set_mode(WINDOW_SIZE)

    def present(self):
        """Fit the 1920x1080 stage into the window (keeping its shape) and show it."""
        ww, wh = self.window.get_size()
        self.k = min(ww / SW, wh / SH)
        size = (int(SW * self.k), int(SH * self.k))
        self.off = ((ww - size[0]) // 2, (wh - size[1]) // 2)
        self.window.fill((0, 0, 0))
        if size == (SW, SH):
            img = self.screen
        elif self.k < 1:
            img = pygame.transform.smoothscale(self.screen, size)
        else:
            img = pygame.transform.scale(self.screen, size)
        self.window.blit(img, self.off)
        if self.fade_alpha > 0:                     # fade to / from black
            if self._fade_win is None or self._fade_win.get_size() != (ww, wh):
                self._fade_win = pygame.Surface((ww, wh))
                self._fade_win.fill((0, 0, 0))
            self._fade_win.set_alpha(int(self.fade_alpha))
            self.window.blit(self._fade_win, (0, 0))
        pygame.display.flip()

    def change_scene(self, fn):
        """Fade to black, run fn() (which sets up the next scene), then fade back in."""
        if self.fade_dir == 1:
            return
        self.pending = fn
        self.fade_dir = 1

    def update_fade(self, dt):
        if self.fade_dir == 1:
            self.fade_alpha += 255 / FADE_TIME * dt
            if self.fade_alpha >= 255:
                self.fade_alpha = 255.0
                fn, self.pending = self.pending, None
                self.fade_dir = -1
                self.settings_open = False
                if self.paused:                 # leaving the pause menu for another scene
                    self.paused = False
                    if pygame.mixer.get_init():
                        pygame.mixer.unpause()
                if fn:
                    fn()
        elif self.fade_dir == -1:
            self.fade_alpha -= 255 / FADE_TIME * dt
            if self.fade_alpha <= 0:
                self.fade_alpha, self.fade_dir = 0.0, 0

    def play(self, name):
        if name in self.sounds:
            self.sounds[name].play()

    def loop_sound(self, slot, name):
        """slot 'music' or 'fx' keeps ONE looping sound at a time. name None = silence."""
        cur = getattr(self, slot)
        if cur == name:
            return
        if cur in self.sounds:
            self.sounds[cur].stop()
        setattr(self, slot, name)
        if name in self.sounds:
            self.sounds[name].play(-1)

    def silence(self):
        """Stop every sound."""
        if pygame.mixer.get_init():
            pygame.mixer.stop()
        self.music = self.fx = None

    def apply_volume(self):
        master = 0.0 if self.muted else self.volume
        for name, snd in self.sounds.items():
            snd.set_volume(master * (self.music_vol if name in MUSIC_SOUNDS else self.sfx_vol))

    def set_volume(self, v):
        self.volume = min(1.0, max(0.0, round(v, 1)))
        self.muted = False
        self.apply_volume()

    def set_channel_volume(self, which, v):
        """which: 'music' or 'sfx' (the two extra sliders in Settings > AUDIO)."""
        v = min(1.0, max(0.0, round(v, 1)))
        if which == "music":
            self.music_vol = v
        else:
            self.sfx_vol = v
        self.apply_volume()

    def change_volume(self, delta):
        self.set_volume(self.volume + delta)
        self.play("press")

    def toggle_mute(self):
        self.muted = not self.muted
        self.apply_volume()

    def load_hi(self):
        try:
            with open(os.path.join(HERE, "chomper_hi.txt")) as f:
                return int(f.read())
        except (OSError, ValueError):
            return 0

    def save_hi(self):
        if self.score > self.hi:
            self.hi = self.score
            try:
                with open(os.path.join(HERE, "chomper_hi.txt"), "w") as f:
                    f.write(str(self.hi))
            except OSError:
                pass

    # ----- scenes: intro -> loading -> title -> gameplay -> over / ending -----
    def enter_intro(self):
        self.silence()
        if self.intro_n == 0:               # no video frames found: go straight to loading
            self.enter_loading()
            return
        self.state = "intro"
        self.intro_t, self._intro_idx, self._intro_img = 0.0, -1, None
        self.play("start")

    def enter_loading(self):
        self.silence()
        self.state = "loading"
        self.load_t, self.load_ticks = 0.0, 0
        self.loaded = self.sp is not None

    def load_assets(self):
        """Runs while the loading screen is showing."""
        self.sp = Sprites()
        self.frame = load_image(IMG_FRAME, False)
        self.over_full = load_image(IMG_OVER, False)            # your 1920x1080 Game Over picture
        self.menu_img = {k: load_image(f, False) for k, f in MENU_IMAGES.items()}
        found = detect_tabs(self.menu_img["tabs"])
        if len(found) == len(TAB_NAMES):                # the picture has all 5 tabs: use its words
            self.tab_labels, self.tabs_from_image = found, True
        else:                                           # older 4-tab picture: draw the 5 tabs in code
            self.tabs_from_image = False
            self.tab_labels = []
            for (x, y, w, h), name in zip(TAB_LABELS, TAB_NAMES):
                tw = self.mid.size(name)[0]
                self.tab_labels.append((x + w // 2 - tw // 2, 110, tw, 21))
        self.tab_rects = [pygame.Rect(r).inflate(70, 50) for r in self.tab_labels]
        logo = load_image(IMG_LOGO, False)
        self.logo = pygame.transform.smoothscale(logo, (904, 368))
        if pygame.mixer.get_init():
            self.sounds.update(build_sounds())
            self.sounds.update(load_sound_files())
            self.apply_volume()

    def enter_title(self):
        self.silence()
        self.state = "title"
        self.score = 0
        self.menu_idx = 0
        self.loop_sound("music", "title")   # upbeat music

    def activate_menu(self):
        if self.fade_dir != 0:
            return
        if self.menu_idx == 0:              # START GAME
            self.play("press")
            self.change_scene(self.start_tutorial)
        elif self.menu_idx == 1:            # SETTINGS
            self.play("press")
            self.open_settings()
        else:                               # QUIT
            self.request_quit()

    def request_quit(self):
        """Play the quit sound, fade out, then close the game."""
        if self.fade_dir != 0:
            return
        self.play("quit")
        self.change_scene(self.quit_game)

    def quit_game(self):
        snd = self.sounds.get("quit")
        if snd is not None:
            pygame.time.wait(min(1500, int(snd.get_length() * 1000)))
        pygame.quit()
        sys.exit()

    # ----- pause (ESC) -----
    def escape(self):
        if self.settings_open:
            self.settings_input("back")
        elif self.paused:
            self.set_pause(False)
        elif self.state in ("play", "ready", "dead", "win"):
            if self.fade_dir == 0:
                self.set_pause(True)
        else:                               # title, game over, intro, loading, credits: Esc quits
            self.request_quit()

    def set_pause(self, on):
        self.paused = on
        self.pause_idx = 0
        if pygame.mixer.get_init():
            (pygame.mixer.pause if on else pygame.mixer.unpause)()
        self.play("press")

    def activate_pause(self):
        i = self.pause_idx
        if i == 0:                          # RESUME
            self.set_pause(False)
        elif i == 1:                        # SETTINGS
            self.play("press")
            self.open_settings()
        elif i == 2:                        # RESTART (this level again)
            if self.fade_dir == 0:
                self.play("press")
                self.change_scene(self.restart_level)
        elif i == 3:                        # QUIT TO TITLE
            if self.fade_dir == 0:
                self.play("press")
                self.change_scene(self.enter_title)
        else:                               # QUIT GAME
            self.request_quit()

    def restart_level(self):
        self.score, self.lives = self.level_start_score, self.start_lives
        self.begin_level(self.level)

    # ----- settings screen -----
    def open_settings(self):
        self.settings_open = True
        self.set_tab, self.set_row, self.set_focus = 0, 0, "tabs"

    def settings_input(self, action):
        """action: left / right / up / down / enter / back"""
        tab, nrows = self.set_tab, TAB_ROWS.get(self.set_tab, 0)
        if action == "back":
            if self.set_focus == "rows":
                self.set_focus = "tabs"
            else:
                self.settings_open = False
            self.play("press")
        elif self.set_focus == "tabs":
            if action in ("left", "right"):
                self.set_tab = (tab + (1 if action == "right" else -1)) % 5
                self.play("press")
            elif action == "down" and nrows:
                self.set_focus, self.set_row = "rows", 0
                self.play("press")
            elif action == "enter":
                if tab == 3:                # RETURN
                    self.settings_open = False
                    self.play("press")
                elif nrows:
                    self.set_focus, self.set_row = "rows", 0
                    self.play("press")
        else:
            if action == "up":
                if self.set_row == 0:
                    self.set_focus = "tabs"
                else:
                    self.set_row -= 1
                self.play("press")
            elif action == "down":
                self.set_row = min(nrows - 1, self.set_row + 1)
                self.play("press")
            elif action == "left":
                self.change_row(-1)
            elif action == "right":
                self.change_row(1)
            elif action == "enter":
                self.activate_row()

    def change_row(self, delta):
        t, r = self.set_tab, self.set_row
        if t == 0:
            if r == 0:                      # GAME SPEED
                self.speed_idx = (self.speed_idx + delta) % 3
            elif r == 1:                    # LIVES
                i = (LIVES_OPTIONS.index(self.start_lives) + delta) % 3
                self.start_lives = LIVES_OPTIONS[i]
            else:                           # FULL SCREEN
                self.set_fullscreen(not self.full)
        elif t == 2:
            if r == 0:                      # MASTER VOLUME
                self.set_volume(self.volume + 0.1 * delta)
            elif r == 1:                    # MUSIC
                self.set_channel_volume("music", self.music_vol + 0.1 * delta)
            elif r == 2:                    # SOUND EFFECTS
                self.set_channel_volume("sfx", self.sfx_vol + 0.1 * delta)
            else:                           # MUTE
                self.toggle_mute()
        self.play("press")

    def activate_row(self):
        if self.set_tab == 2 and self.set_row <= 2:     # a volume bar: ENTER goes up, then back to 0
            cur = (self.volume, self.music_vol, self.sfx_vol)[self.set_row]
            new = 0.0 if cur >= 0.99 else cur + 0.1
            if self.set_row == 0:
                self.set_volume(new)
            else:
                self.set_channel_volume("music" if self.set_row == 1 else "sfx", new)
            self.play("press")
        else:
            self.change_row(1)

    # ----- starting / ending games -----
    def start_tutorial(self):
        self.score, self.lives = 0, self.start_lives
        self.begin_level(0)

    def retry(self):                    # Game Over -> play again from level 1
        self.score, self.lives = 0, self.start_lives
        self.begin_level(1)

    def skip_tutorial(self):
        self.score = 0
        self.change_scene(lambda: self.begin_level(1))

    def enter_over(self):
        self.state = "over"
        self.silence()
        self.play("lose")
        self.loop_sound("fx", "chase")

    def begin_ending(self):             # Victory
        self.loop_sound("music", None)      # (the victory fanfare keeps playing from the boss fight)
        self.loop_sound("fx", None)
        self.save_hi()
        self.state = "ending"
        self.end_t = 0.0
        self.credits_started = False
        lines = [("CREDITS", GOLD, self.big, 105)]
        for name, role in CREDITS:
            lines += [(name, BLUE, self.mid, 51)]
            lines += [(r, INK, self.font, 45) for r in wrap(role, self.font, 1500)]
            lines += [("", INK, self.font, 36)]
        lines += [("Special thanks to", GOLD, self.mid, 60), (SPECIAL_THANKS, INK, self.font, 90)]
        lines += [(r, GRAY, self.small, 39) for r in wrap(DISCLAIMER, self.small, 1300)]
        lines += [("", INK, self.font, 30), ("Thanks for playing!", BLUE, self.mid, 90),
                  (f"HIGH SCORE {self.hi}", GOLD, self.font, 60)]
        self.credit_lines = lines

    def press_start(self):
        """SPACE / ENTER / clicking the button."""
        if self.settings_open:
            self.settings_input("enter")
            return
        if self.paused:
            self.activate_pause()
            return
        if self.fade_dir != 0:
            return
        if self.state == "title":
            self.activate_menu()
        elif self.state == "intro":
            self.play("press")
            self.change_scene(self.enter_loading)
        elif self.state == "over":
            self.play("press")
            self.change_scene(self.retry)
        elif self.state == "ending":
            self.play("press")
            self.change_scene(self.enter_title)
        elif self.state == "play" and self.level == 0:
            self.play("press")
            self.skip_tutorial()

    # ----- levels -----
    def fresh_map(self):
        m = [list(row) for row in self.theme["map"]]
        n = 0
        for row in m:
            for x, c in enumerate(row):
                if c in ".o":
                    n += 1
                elif c in "PG":
                    row[x] = " "
        return m, n

    def setup_level(self, n):
        self.level = n
        self.theme = LEVELS[n]
        self.map, self.pellets = self.fresh_map()
        self.eaten = 0                  # dots eaten this level
        self.eaten_kinds = set()        # ghosts bitten for good (levels 1-2)
        self.fruit_t = 0.0              # >0 means a bonus fruit is on the board
        self.fruits_spawned = self.fruits_got = 0
        self.tut_moved = self.tut_power = False
        self.reset_positions()

    def reset_positions(self):
        self.pac = Actor(9, 11 if self.level == 0 else 15)     # tutorial: spawn in the middle
        self.pac.nx, self.pac.ny = (0, 0) if self.level == 0 else (-1, 0)
        self.face = (-1, 0)
        self.combo = 0
        self.fright = 0.0
        if self.level == 0:
            cfg = [(0, "out", 0), (2, "house", 3)]                       # two harmless practice ghosts
        else:
            cfg = [(0, "out", 0), (1, "house", 2), (2, "house", 5), (3, "house", 8)]
        self.ghosts = [Ghost(k, st, w) for k, st, w in cfg if k not in self.eaten_kinds]
        if self.theme["boss"]:
            self.ghosts.append(Ghost(4, "house", 8))                     # the invisible ghost

    def begin_level(self, n):
        self.setup_level(n)
        self.silence()
        self.level_start_score = self.score
        if n == 0:
            self.state = "play"
            self.timer = 0.0
        else:
            self.state = "ready"
            self.timer = 6.0 if self.theme["boss"] else 1.8
            self.play("start")

    def is_open(self, x, y):
        x %= COLS
        if y < 0 or y >= ROWS:
            return False
        return self.map[y][x] not in "#-"

    def pac_mult(self):
        return PAC_MULT[self.speed_idx]

    def ghost_mult(self):
        return GHOST_MULT[self.speed_idx]

    def ghost_speed(self):
        if self.level == 0:
            return 3.0 * self.ghost_mult()
        return min(GHOST_MAX, GHOST_SPEED + 0.3 * (self.level - 1)) * self.ghost_mult()

    # ----- movement -----
    def move(self, a, dt, speed, choose):
        step = speed * dt
        while step > 0:
            if not a.dx and not a.dy:
                choose(a)
                if not a.dx and not a.dy:
                    return
                a.p = 0.0
            need = 1 - a.p
            if step < need:
                a.p += step
                return
            step -= need
            a.tx = (a.tx + a.dx) % COLS
            a.ty += a.dy
            a.p = 0.0
            choose(a)
            if not a.dx and not a.dy:
                return

    def pac_choose(self, a):
        if (a.nx or a.ny) and self.is_open(a.tx + a.nx, a.ty + a.ny):
            a.dx, a.dy = a.nx, a.ny
        elif not self.is_open(a.tx + a.dx, a.ty + a.dy):
            a.dx = a.dy = 0
        if a.dx or a.dy:
            self.face = (a.dx, a.dy)

    def ghost_choose(self, g):
        opts = [d for d in DIRS if self.is_open(g.tx + d[0], g.ty + d[1])
                and not (d[0] == -g.dx and d[1] == -g.dy)]
        if not opts:
            opts = [d for d in DIRS if self.is_open(g.tx + d[0], g.ty + d[1])]
        if not opts:
            g.dx = g.dy = 0
            return
        wander = g.kind != 4 and (g.scared or (g.kind == 2 and random.random() < .4) or random.random() < .08)
        if wander:
            pick = random.choice(opts)
        else:
            tx, ty = self.pac.tx, self.pac.ty
            if g.kind == 1:         # ghost 2 aims 4 tiles ahead of Yellow-Biter
                tx += self.face[0] * 4
                ty += self.face[1] * 4
            if g.kind == 3 and math.hypot(g.tx - self.pac.tx, g.ty - self.pac.ty) < 6:
                tx, ty = 1, 19      # ghost 4 runs to a corner when close
            pick = min(opts, key=lambda d: math.hypot(g.tx + d[0] - tx, g.ty + d[1] - ty))
        g.dx, g.dy = pick

    def set_dir(self, x, y):
        p = self.pac
        p.nx, p.ny = x, y
        if self.state == "play" and (p.dx or p.dy) and p.dx == -x and p.dy == -y:
            p.flip()

    # ----- update -----
    def update(self, dt):
        self.update_fade(dt)
        if self.paused:                 # the game is frozen while the pause menu is open
            return
        st = self.state
        if st == "loading":
            self.update_loading(dt)
            return
        if self.fade_dir != 0:          # scenes wait while the screen fades
            return
        if st == "intro":
            self.intro_t += dt
            if self.intro_t >= self.intro_n / self.intro_fps + 0.8:
                self.change_scene(self.enter_loading)
        elif st == "ready":
            self.timer -= dt
            if self.timer <= 0:
                self.state = "play"
        elif st == "dead":
            self.timer -= dt
            if self.timer <= 0:
                self.lives -= 1
                if self.lives <= 0:
                    self.save_hi()
                    self.change_scene(self.enter_over)          # GAME OVER
                else:
                    self.reset_positions()
                    self.state, self.timer = "ready", 1.5
        elif st == "win":
            self.timer -= dt
            if self.timer <= 0:
                if self.theme["boss"]:
                    self.change_scene(self.begin_ending)        # VICTORY
                else:
                    self.change_scene(lambda: self.begin_level(self.level + 1))
        elif st == "ending":
            self.end_t += dt
            if self.end_t >= VICTORY_PAGE:
                if not self.credits_started:            # credits music starts with the credits
                    self.credits_started = True
                    self.play("win_music")
                total = sum(h for _, _, _, h in self.credit_lines)
                if CREDITS_Y0 - (self.end_t - VICTORY_PAGE) * CREDITS_SPEED + total < 90:
                    self.change_scene(self.enter_title)
        elif st == "play":
            self.update_play(dt)

    def update_loading(self, dt):
        self.load_t += dt
        self.load_ticks += 1
        if not self.loaded and self.load_ticks >= 3:    # let the loading picture appear first
            self.load_assets()
            self.loaded = True
        if self.loaded and self.load_t >= 3.0:
            self.change_scene(self.enter_title)

    def sync_audio(self):
        self.loop_sound("music", LEVEL_MUSIC[self.level])
        scared = self.fright > 0 and any(g.scared for g in self.ghosts)
        self.loop_sound("fx", "chase" if scared else "siren")

    def kill(self, msg):
        self.state, self.timer = "dead", 1.4
        self.death_msg = msg
        self.loop_sound("fx", None)
        self.play("death")
        self.save_hi()

    def level_clear(self):
        self.state, self.timer = "win", 2.0
        self.silence()
        self.play("victory" if self.theme["boss"] else "clear")
        self.save_hi()

    def update_play(self, dt):
        boss = self.theme["boss"]
        pm, gm = self.pac_mult(), self.ghost_mult()
        self.sync_audio()
        self.move(self.pac, dt, PAC_SPEED * pm, self.pac_choose)
        if self.pac.dx or self.pac.dy:
            self.tut_moved = True

        # --- eat dots / stars on the tile Yellow-Biter is closest to
        px, py = self.pac.pos()
        ex, ey = round(px) % COLS, round(py)
        c = self.map[ey][ex] if 0 <= ey < ROWS else " "
        if c in ".o":
            self.map[ey][ex] = " "
            self.pellets -= 1
            self.eaten += 1
            if c == ".":
                self.score += 10
                self.waka ^= 1
                self.play("waka1" if self.waka else "waka2")
            else:
                self.score += 50
                self.fright = POWER_TIME
                self.combo = 0
                self.tut_power = True
                for g in self.ghosts:
                    if g.state == "out" and g.kind != 4:
                        g.scared = True
                        g.flip()
                self.play("power")
            if self.level > 0 and not boss and self.eaten in (40, 100):
                self.fruit_t = 9.0
            if self.level == 0 and (self.eaten >= 45 or (self.tut_power and self.eaten >= 30)):
                self.skip_tutorial()                    # tutorial finished
                return
            if self.pellets <= 0 and self.level > 0 and not boss:
                self.map, self.pellets = self.fresh_map()   # maze refills until all 4 ghosts are bitten
                self.eaten = 0

        # --- bonus fruit
        if self.level > 0:
            if boss:                                    # boss level: 2 fruits that wait for you
                want = 2 if (self.pellets <= 0 or self.eaten >= 100) else (1 if self.eaten >= 40 else 0)
                if self.fruit_t <= 0 and self.fruits_spawned < want:
                    self.fruits_spawned += 1
                    self.fruit_t = 1e9
            elif self.fruit_t > 0:
                self.fruit_t -= dt
            if self.fruit_t > 0 and ex == 9 and ey == 11:
                self.score += 500
                self.fruit_t = 0
                self.fruits_got += 1
                self.play("fruit")
        if boss and self.pellets <= 0 and self.fruits_got >= 2:
            self.level_clear()                          # all dots, stars and fruit eaten: ghost disappears
            return

        # --- ghosts
        self.fright = max(0.0, self.fright - dt)
        gone = []
        for g in self.ghosts:
            if g.state == "house":
                g.wait -= dt
                if g.wait <= 0:
                    g.state = "out"
                    g.tx, g.ty, g.dx, g.dy, g.p = 9, 7, 0, 0, 0.0
                continue
            if g.kind == 4:
                speed = (2.0 if self.fright > 0 else PHANTOM_SPEED) * gm
            else:
                if self.fright <= 0:
                    g.scared = False
                speed = SCARED_SPEED * gm if g.scared else self.ghost_speed()
            self.move(g, dt, speed, self.ghost_choose)
            ax, ay = self.pac.pos()
            bx, by = g.pos()
            if abs(ax - bx) < .6 and abs(ay - by) < .6:
                if g.scared:                            # Yellow-Biter bites a scared ghost
                    self.score += 200 * 2 ** self.combo
                    self.combo = min(self.combo + 1, 3)
                    self.play("eat")
                    if self.level > 0 and not boss:     # eaten ghosts do NOT come back...
                        gone.append(g)
                        self.eaten_kinds.add(g.kind)
                    else:                               # ...except in the boss fight (and tutorial)
                        g.state, g.wait, g.scared = "house", 2.5, False
                        g.tx, g.ty, g.dx, g.dy, g.p = g.hx, 9, 0, 0, 0.0
                elif self.level > 0:                    # bit a ghost by accident
                    self.kill("The invisible ghost got you!" if g.kind == 4
                              else "Oops! You bit a ghost by accident!")
                    return
        if gone:
            self.ghosts = [g for g in self.ghosts if g not in gone]
            if len(self.eaten_kinds) >= 4:
                self.level_clear()                      # all 4 ghosts bitten = level up

    # ----- drawing helpers -----
    def center(self, a):
        x, y = a.pos()
        return int(OX + x * T + T / 2), int(OY + y * T + T / 2)

    def pac_image(self, ts):
        fx, fy = self.face
        moving = self.pac.dx or self.pac.dy
        if fx:
            side = "right" if fx > 0 else "left"
            return self.sp.chomp[side][(ts // 80) % 4] if moving else self.sp.pac_dir[side]
        return self.sp.pac_dir["up" if fy < 0 else "down"]

    def ghost_dir_idx(self, g):
        """Which frame of the ghost sheet: 0 down/front, 1 up, 2 left, 3 right."""
        if g.state == "house" or (not g.dx and not g.dy):
            return 0
        return 0 if g.dy > 0 else 1 if g.dy < 0 else 2 if g.dx < 0 else 3

    def ghost_image(self, g, ts):
        if g.scared:
            i = (ts // 100) % 5
            flash = self.fright < 2 and (ts // 200) % 2
            return (self.sp.bat_light if flash else self.sp.bat)[i]
        return self.sp.ghost_dir[g.kind][self.ghost_dir_idx(g)]

    def text(self, msg, x, y, color, font=None, center=False, right=False):
        img = (font or self.font).render(msg, True, color)
        r = img.get_rect()
        if center:
            r.midtop = (x, y)
        elif right:
            r.topright = (x, y)
        else:
            r.topleft = (x, y)
        self.screen.blit(img, r)

    def pixel_text(self, msg, cx, y, scale, color, shadow=None):
        x0 = cx - (len(msg) * 6 * scale - scale) // 2
        for col, off in ((shadow, scale // 2), (color, 0)):
            if col is None:
                continue
            for i, ch in enumerate(msg):
                for r, row in enumerate(FONT5.get(ch, ())):
                    for c, bit in enumerate(row):
                        if bit == "#":
                            pygame.draw.rect(self.screen, col, (x0 + i * 6 * scale + c * scale + off,
                                                                y + r * scale + off, scale, scale))

    def banner(self, msg, row, color=WHITE):
        """One line of text on the top or bottom wall row of the maze (no gameplay happens there)."""
        y = OY + row * T
        pygame.draw.rect(self.screen, BG, (OX, y, MW, T))
        img = self.small.render(msg, True, color)
        self.screen.blit(img, img.get_rect(center=(CX, y + T // 2)))

    def message(self, lines, cy, width=600):
        """A boxed message in the maze. lines = list of (text, color, font, line_height)."""
        h = sum(l[3] for l in lines) + 33
        box = (CX - width // 2, cy - h // 2, width, h)
        pygame.draw.rect(self.screen, BG, box)
        pygame.draw.rect(self.screen, PINK, box, 4)
        y = box[1] + 18
        for msg, color, font, lh in lines:
            self.text(msg, CX, y, color, font, center=True)
            y += lh

    def draw_button(self, rect, label, ts, font=None):
        pygame.draw.rect(self.screen, (41, 54, 111), rect)
        pygame.draw.rect(self.screen, YELLOW if (ts // 450) % 2 else PINK, rect, 4)
        img = (font or self.big).render(label, True, WHITE)
        self.screen.blit(img, img.get_rect(center=rect.center))

    def yellow(self, key, labels, idx, source=None):
        """Paint ONE menu word yellow (the selected one) on top of the white picture."""
        k = (key, idx)
        if k not in self._ycache:
            r = pygame.Rect(labels[idx]).inflate(10, 10)
            if source is None:                      # take the white word and tint it yellow
                crop = self.menu_img[key].subsurface(r).copy()
                crop.fill(MENU_YELLOW, special_flags=pygame.BLEND_RGB_MULT)
            else:                                   # the settings tabs come in a ready-made yellow picture
                crop = source.subsurface(r).copy()
            self._ycache[k] = (crop, r.topleft)
        crop, pos = self._ycache[k]
        self.screen.blit(crop, pos)

    def draw_maze(self, ts):
        s = self.screen
        fill, line = self.theme["fill"], self.theme["line"]
        for y in range(ROWS):
            for x in range(COLS):
                c = self.map[y][x]
                px, py = OX + x * T, OY + y * T
                if c == "#":
                    pygame.draw.rect(s, fill, (px, py, T, T))
                    for dx, dy, rect in ((0, -1, (px, py, T, 5)), (0, 1, (px, py + T - 5, T, 5)),
                                         (-1, 0, (px, py, 5, T)), (1, 0, (px + T - 5, py, 5, T))):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < COLS and 0 <= ny < ROWS and self.map[ny][nx] != "#":
                            pygame.draw.rect(s, line, rect)
                elif c == "-":
                    pygame.draw.rect(s, PINK, (px, py + T // 2 - 3, T, 6))
                elif c == ".":
                    pygame.draw.circle(s, YELLOW, (px + T // 2, py + T // 2), 5)
                elif c == "o":
                    s.blit(self.sp.star[(ts // 150) % 4], (px + T // 2 - 16, py + T // 2 - 16))

    def draw_actors(self, ts):
        s = self.screen
        if self.fruit_t > 0:
            bob = round(math.sin(ts / 200) * 3)
            s.blit(self.sp.fruit[(ts // 250) % 3], (OX + 9 * T + T // 2 - 27, OY + 11 * T + T // 2 - 27 + bob))
        for g in self.ghosts:
            cx, cy = self.center(g)
            bob = round(math.sin(ts / 150 + g.kind) * 3)
            if g.kind == 4:                                  # the invisible ghost: faint, flickers, shows during power-up
                if self.state == "win":
                    continue
                a = 175 if self.fright > 0 else 95 if (ts // 700) % 5 == 0 else 30
                s.blit(self.sp.phantom[a][self.ghost_dir_idx(g)], (cx - 24, cy - 26 + bob))
            else:
                s.blit(self.ghost_image(g, ts), (cx - 24, cy - 26 + bob))
        cx, cy = self.center(self.pac)
        if self.state == "dead":
            k = max(0.0, self.timer / 1.4)                   # spin and shrink the surprised face
            rot = pygame.transform.rotozoom(self.sp.pac_dir["down"], (1 - k) * 720, max(0.05, k))
            s.blit(rot, rot.get_rect(center=(cx, cy - 6)))
        else:
            bob = 2 * ((ts // 90) % 2) if (self.pac.dx or self.pac.dy) and not self.face[0] else 0
            s.blit(self.pac_image(ts), (cx - 24, cy - 30 + bob))

    def draw_hud(self):
        """Score on the left of the maze, level info and controls on the right."""
        s = self.screen
        L, R = 311, 1608                                     # centres of the two side columns
        boss = self.theme["boss"]
        self.text("SCORE", L, 165, GRAY, self.small, center=True)
        self.text(str(self.score), L, 201, INK, self.big, center=True)
        self.text("HIGH SCORE", L, 321, GRAY, self.small, center=True)
        self.text(str(max(self.hi, self.score)), L, 357, GOLD, self.big, center=True)
        self.text("LIVES", L, 477, GRAY, self.small, center=True)
        gap = min(78, 430 // max(1, self.lives))
        x0 = L - gap * self.lives // 2 + (gap - 66) // 2
        for i in range(self.lives):
            s.blit(self.sp.life_big, (x0 + i * gap, 516))

        if self.level == 0:
            self.text("TUTORIAL", R, 165, BLUE, self.mid, center=True)
            self.text("Nothing can hurt you here", R, 240, GRAY, self.small, center=True)
        else:
            self.text(f"LEVEL {self.level}", R, 165, BLUE, self.mid, center=True)
            if boss:
                self.text("CURSED MAZE", R, 225, (150, 60, 220), self.font, center=True)
                self.text("DOTS LEFT", R, 315, GRAY, self.small, center=True)
                self.text(str(self.pellets), R, 348, INK, self.big, center=True)
                self.text("FRUIT", R, 450, GRAY, self.small, center=True)
                self.text(f"{self.fruits_got} / 2", R, 483, INK, self.mid, center=True)
            else:
                self.text("GHOSTS BITTEN", R, 285, GRAY, self.small, center=True)
                for k in range(4):
                    icon = self.sp.ghost_icon_gone[k] if k in self.eaten_kinds else self.sp.ghost_icon[k]
                    s.blit(icon, (R - 216 + k * 108 + 6, 321))
                self.text(f"{len(self.eaten_kinds)} / 4", R, 438, INK, self.mid, center=True)

        self.text("VOLUME", R, 615, GRAY, self.small, center=True)
        filled = 0 if self.muted else round(self.volume * 10)
        for i in range(10):
            pygame.draw.rect(s, BLUE if i < filled else (210, 218, 235), (R - 195 + i * 39, 654, 33, 30))
        hints = ["WASD / Arrows  move", "+ / -  volume     M  mute", "F11  full screen     Esc  pause"]
        if self.level == 0:
            hints.insert(0, "ENTER  skip tutorial")
        for i, h in enumerate(hints):
            self.text(h, R, 732 + i * 36, GRAY, self.small, center=True)

    def tutorial_text(self):
        if not self.tut_moved:
            return "Press WASD or Arrow Keys to move."
        if self.fright > 0:
            return "Scared ghosts turn into bats - bite them!"
        if self.eaten < 12:
            return "Eat the dots to score points."
        if not self.tut_power:
            return "Big stars give you power. Eat one to bite the ghosts!"
        return "Nice! Eat a few more dots - the real game is next."

    def draw_scene(self, ts):
        """Main gameplay: the BIG maze sits inside the blue-and-white frame picture."""
        st = self.state
        self.screen.blit(self.frame, (0, 0))
        pygame.draw.rect(self.screen, BLUE, (OX - 10, OY - 10, MW + 20, MH + 20))
        pygame.draw.rect(self.screen, BG, (OX, OY, MW, MH))
        self.draw_maze(ts)
        self.draw_actors(ts)
        self.draw_hud()
        mid_y = OY + 11 * T
        if st == "ready":
            if self.theme["boss"]:
                lines = [("FINAL LEVEL: CURSED MAZE", PINK, self.mid, 62)]
                lines += [(t, WHITE, self.small, 34) for t in wrap(BOSS_TEXT, self.small, 700)]
                lines += [("READY!", YELLOW, self.big, 78)]
                self.message(lines, mid_y, 760)
            else:
                self.message([("READY!", YELLOW, self.big, 78),
                              ("(Try not to lose this level)", WHITE, self.small, 36)], mid_y, 600)
        elif st == "win":
            if self.theme["boss"]:
                self.message([("BOSS DEFEATED!", GREEN, self.big, 78),
                              ("The invisible ghost vanished!", WHITE, self.small, 36)], mid_y, 640)
            else:
                self.message([("LEVEL CLEAR!", GREEN, self.big, 78),
                              ("All 4 ghosts bitten!", WHITE, self.small, 36)], mid_y, 600)
        elif st == "dead":
            self.banner(self.death_msg, 20, RED)
        elif st == "play":
            if self.level == 0:
                self.banner("Welcome to " + GAME_NAME + "!", 0, YELLOW)
                self.banner(self.tutorial_text(), 20, GREEN)
            elif self.fright > 0:
                self.banner(f"Eat the ghosts under 10 seconds!   {math.ceil(self.fright)}", 20, PINK)

    def draw_intro(self, ts):
        idx = min(self.intro_n - 1, int(self.intro_t * self.intro_fps))
        if idx != self._intro_idx:                           # load the next video frame from disk
            try:
                img = pygame.image.load(os.path.join(HERE, "intro", f"f{idx + 1:04d}.jpg")).convert()
                self._intro_img = pygame.transform.smoothscale(img, (SW, SH))
            except (pygame.error, OSError):
                pass
            self._intro_idx = idx
        self.screen.fill((0, 0, 0))
        if self._intro_img is not None:
            self.screen.blit(self._intro_img, (0, 0))
        self.text("Press SPACE or ENTER to skip", CX, SH - 60, GRAY, self.small, center=True)

    def draw_loading(self, ts):
        self.screen.blit(self.loading_full, (0, 0))
        p = min(1.0, self.load_t / 3.0)                      # little progress bar under "LOADING"
        pygame.draw.rect(self.screen, (255, 205, 60), (685, 918, int(450 * p), 12))
        pygame.draw.rect(self.screen, (255, 255, 255), (685, 918, 450, 12), 3)

    def draw_title(self, ts):
        """Your MENU picture (white words on black) + the logo. The selected word turns yellow."""
        self.screen.blit(self.menu_img["main"], (0, 0))
        self.screen.blit(self.logo, self.logo.get_rect(center=(CX, 305)))
        self.yellow("main", MAIN_LABELS, self.menu_idx)
        self.text("UP / DOWN  choose     ENTER  select     + / -  volume     M  mute     F11  full screen",
                  CX, 1020, GRAY, self.small, center=True)

    def draw_pause(self, ts):
        self.screen.blit(self.menu_img["pause"], (0, 0))
        self.yellow("pause", PAUSE_LABELS, self.pause_idx)
        self.text("ESC  resume     UP / DOWN  choose     ENTER  select", CX, 1020, GRAY, self.small, center=True)

    def draw_row(self, y, label, value, selected, arrows=True):
        color = YELLOW if selected else WHITE                # only the selected row is yellow
        self.text(label, 520, y, color, self.mid)
        shown = f"<  {value}  >" if (selected and arrows) else value
        self.text(shown, 1400, y, color, self.mid, right=True)
        self.row_rects.append(pygame.Rect(420, y - 20, 1080, 90))

    def draw_settings(self, ts):
        s = self.screen
        s.blit(self.menu_img["tabs"], (0, 0))
        tab, focus = self.set_tab, self.set_focus
        if not self.tabs_from_image:                         # tabs drawn in code (picture has fewer tabs)
            pygame.draw.rect(s, (0, 0, 0), (0, 85, SW, 75))
            for i, name in enumerate(TAB_NAMES):
                x, y, w, h = self.tab_labels[i]
                img = self.mid.render(name, True, MENU_YELLOW if (focus == "tabs" and i == tab) else WHITE)
                s.blit(img, img.get_rect(center=(x + w // 2, 120)))
        elif focus == "tabs":                                # selected tab = yellow
            self.yellow("tabs", self.tab_labels, tab, source=self.menu_img["tabs_y"])
        if focus != "tabs":                                  # focus is below: just underline the open tab
            x, y, w, h = self.tab_labels[tab]
            pygame.draw.rect(s, WHITE, (x, y + h + 12, w, 4))
        self.row_rects, self.vol_rects = [], []
        sel = lambda i: focus == "rows" and self.set_row == i
        if tab == 0:                                         # GAMEPLAY
            self.draw_row(330, "GAME SPEED", SPEED_NAMES[self.speed_idx], sel(0))
            self.draw_row(460, "LIVES", str(self.start_lives), sel(1))
            self.draw_row(590, "FULL SCREEN", "ON" if self.full else "OFF", sel(2))
            self.text("Changes apply the next time you start or restart a level.", CX, 780, GRAY, self.font, center=True)
        elif tab == 1:                                       # CONTROLS (just a list)
            rows = [("MOVE", "W A S D  /  ARROW KEYS"), ("SELECT", "ENTER  /  SPACE"), ("PAUSE", "ESC"),
                    ("VOLUME", "+  /  -"), ("MUTE", "M"), ("FULL SCREEN", "F11  /  F")]
            for i, (k, v) in enumerate(rows):
                y = 290 + i * 100
                self.text(k, 520, y, WHITE, self.mid)
                self.text(v, 1400, y, WHITE, self.mid, right=True)
        elif tab == 2:                                       # AUDIO
            bars = (("VOLUME", self.volume), ("MUSIC", self.music_vol), ("SOUND EFFECTS", self.sfx_vol))
            for n, (label, val) in enumerate(bars):
                y = 330 + n * 130
                color = YELLOW if sel(n) else WHITE
                self.text(label, 520, y, color, self.mid)
                filled = 0 if self.muted else round(val * 10)
                for i in range(10):                          # 10 blocks, click one to set the volume
                    r = pygame.Rect(908 + i * 50, y + 6, 42, 46)
                    self.vol_rects.append((n, r))
                    pygame.draw.rect(s, color if i < filled else (60, 60, 60), r)
                self.row_rects.append(pygame.Rect(420, y - 20, 1080, 90))
            self.draw_row(720, "MUTE", "ON" if self.muted else "OFF", sel(3))
        elif tab == 4:                                       # CREDITS (names, thanks, disclaimer)
            y = 230
            for name, role in CREDITS:
                self.text(name, CX, y, YELLOW, self.mid, center=True)
                y += 52
                for line in wrap(role, self.font, 1500):
                    self.text(line, CX, y, WHITE, self.font, center=True)
                    y += 42
                y += 36
            self.text("Special thanks to", CX, y + 10, YELLOW, self.mid, center=True)
            self.text(SPECIAL_THANKS, CX, y + 62, WHITE, self.font, center=True)
            y += 140
            for line in wrap(DISCLAIMER, self.small, 1300):
                self.text(line, CX, y, GRAY, self.small, center=True)
                y += 38
        else:                                                # RETURN
            self.text("Press ENTER to go back.", CX, 480, WHITE, self.mid, center=True)
        self.text("LEFT / RIGHT  change tab or value     UP / DOWN  choose     ENTER  select     ESC  back",
                  CX, 1020, GRAY, self.small, center=True)

    def draw_gameover(self, ts):            # your 1920x1080 picture is shown full screen; we add the score and buttons
        self.screen.blit(self.over_full, (0, 0))
        self.text(f"SCORE {self.score}", CX, 648, INK, self.big, center=True)
        self.text(f"HIGH SCORE {self.hi}", CX, 735, GOLD, self.mid, center=True)
        self.button = pygame.Rect(CX - 315, 822, 630, 78)
        self.draw_button(self.button, "RETRY: SPACE / ENTER", ts, self.mid)
        self.text("QUIT: ESC", CX, 933, INK, self.font, center=True)

    def draw_ending(self, ts):
        s = self.screen
        s.blit(self.frame, (0, 0))
        t = self.end_t
        if t < VICTORY_PAGE:                                 # VICTORY page
            self.pixel_text("VICTORY!", CX, 150, 21, (240, 170, 20), INK)
            bob = round(abs(math.sin(ts / 250)) * 21)
            hero = pygame.transform.scale(self.sp.chomp["right"][(ts // 120) % 4], (144, 144))
            s.blit(hero, (CX - 72, 393 - bob))
            self.text("Yellow-Biter finally won!", CX, 588, INK, self.mid, center=True)
            self.text("THE END.", CX, 657, BLUE, self.big, center=True)
            self.text(f"HIGH SCORE {self.hi}", CX, 756, GOLD, self.mid, center=True)
        else:                                                # credits scroll up inside the white panel
            s.set_clip(pygame.Rect(90, 90, SW - 180, 825))
            y = CREDITS_Y0 - (t - VICTORY_PAGE) * CREDITS_SPEED
            for msg, color, font, lh in self.credit_lines:
                if 0 < y + lh and y < SH:
                    self.text(msg, CX, y, color, font, center=True)
                y += lh
            s.set_clip(None)
        self.text("Press SPACE or ENTER to skip credits", CX, SH - 138, GRAY, self.small, center=True)

    def draw(self):
        ts = pygame.time.get_ticks()
        self.button = None
        st = self.state
        if self.settings_open:
            self.draw_settings(ts)
        elif self.paused:
            self.draw_pause(ts)
        elif st == "intro":
            self.draw_intro(ts)
        elif st == "loading":
            self.draw_loading(ts)
        elif st == "title":
            self.draw_title(ts)
        elif st == "over":
            self.draw_gameover(ts)
        elif st == "ending":
            self.draw_ending(ts)
        else:
            self.draw_scene(ts)
        self.present()

    # ----- mouse and keyboard -----
    def to_stage(self, pos):
        return (pos[0] - self.off[0]) / self.k, (pos[1] - self.off[1]) / self.k

    def mouse_move(self, pos):
        gx, gy = self.to_stage(pos)
        if self.settings_open:
            for i, r in enumerate(self.tab_rects):
                if r.collidepoint(gx, gy):
                    self.set_tab, self.set_focus = i, "tabs"
            for i, r in enumerate(self.row_rects):
                if r.collidepoint(gx, gy):
                    self.set_focus, self.set_row = "rows", i
        elif self.paused:
            for i, r in enumerate(self.pause_rects):
                if r.collidepoint(gx, gy):
                    self.pause_idx = i
        elif self.state == "title":
            for i, r in enumerate(self.menu_rects):
                if r.collidepoint(gx, gy):
                    self.menu_idx = i

    def mouse_click(self, pos):
        gx, gy = self.to_stage(pos)
        if self.settings_open:
            for i, r in enumerate(self.tab_rects):
                if r.collidepoint(gx, gy):
                    self.set_tab, self.set_focus = i, "tabs"
                    if i == 3:
                        self.settings_open = False
                        self.play("press")
                    return
            for i, r in enumerate(self.row_rects):
                if r.collidepoint(gx, gy):
                    self.set_focus, self.set_row = "rows", i
                    for j, (n, vr) in enumerate(self.vol_rects):  # clicking a volume block sets that volume
                        if vr.collidepoint(gx, gy):
                            v = (j % 10 + 1) / 10
                            if n == 0:
                                self.set_volume(v)
                            else:
                                self.set_channel_volume("music" if n == 1 else "sfx", v)
                            self.play("press")
                            return
                    self.activate_row()
                    return
        elif self.paused:
            for i, r in enumerate(self.pause_rects):
                if r.collidepoint(gx, gy):
                    self.pause_idx = i
                    self.activate_pause()
        elif self.state == "over" and self.button and self.button.collidepoint(gx, gy):
            self.press_start()
        elif self.state == "title":
            for i, r in enumerate(self.menu_rects):
                if r.collidepoint(gx, gy):
                    self.menu_idx = i
                    self.activate_menu()

    def nav_key(self, action, dx, dy):
        if self.settings_open:
            self.settings_input(action)
        elif self.paused:
            if dy:
                self.pause_idx = (self.pause_idx + dy) % 5
                self.play("press")
        elif self.state == "title":
            if dy and self.fade_dir == 0:
                self.menu_idx = (self.menu_idx + dy) % 3
                self.play("press")
        elif self.state in ("play", "ready", "dead"):
            self.set_dir(dx, dy)

    # ----- main loop -----
    def run(self):
        nav = {pygame.K_UP: ("up", 0, -1), pygame.K_w: ("up", 0, -1), pygame.K_DOWN: ("down", 0, 1),
               pygame.K_s: ("down", 0, 1), pygame.K_LEFT: ("left", -1, 0), pygame.K_a: ("left", -1, 0),
               pygame.K_RIGHT: ("right", 1, 0), pygame.K_d: ("right", 1, 0)}
        while True:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                    self.escape()
                elif e.type == pygame.KEYDOWN and e.key in (pygame.K_EQUALS, pygame.K_PLUS, pygame.K_KP_PLUS):
                    self.change_volume(0.1)
                elif e.type == pygame.KEYDOWN and e.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    self.change_volume(-0.1)
                elif e.type == pygame.KEYDOWN and e.key == pygame.K_m:
                    self.toggle_mute()
                elif e.type == pygame.KEYDOWN and e.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                    self.press_start()
                elif e.type == pygame.KEYDOWN and e.key in (pygame.K_F11, pygame.K_f):
                    self.set_fullscreen(not self.full)
                elif e.type == pygame.MOUSEMOTION:
                    self.mouse_move(e.pos)
                elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    self.mouse_click(e.pos)
                elif e.type == pygame.KEYDOWN and e.key in nav:
                    self.nav_key(*nav[e.key])
            dt = min(0.05, self.clock.tick(60) / 1000)
            self.update(dt)
            self.draw()


if __name__ == "__main__":
    Game().run()