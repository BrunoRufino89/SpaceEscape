import pygame
import random
import os
import json
import math
import time

pygame.init()

# ----------------------------------------------------------
# CONFIG
# ----------------------------------------------------------
WIDTH, HEIGHT = 800, 600
FPS = 60
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Escape - Alpha")
clock = pygame.time.Clock()



# ----------------------------------------------------------
#                   ASSETS
# ----------------------------------------------------------

ASSETS = {
    "player1": "player1.png",
    "player2": "player2.png",
    "bullet": "bullet.png",
    "meteoro_normal": "meteoro_normal.png",
    "meteoro_amarelo": "meteoro_amarelo.png",
    "meteoro_verde": "meteoro_verde.png",
    "meteoro_teleport": "meteoro_teleport.png",
    "boss_sprite": "boss_sprite.png",
    "boss_engine": "boss_engine.png",
    "shield": "shield.png",
    "bg_phase1": "bg_phase1.png",
    "bg_phase2": "bg_phase2.png",
    "bg_phase3": "bg_phase3.png",
    "bg_phase4": "bg_phase4.png",
    "bg_boss": "bg_boss.png"
}

AUDIO_ASSETS = {
    "intro": "intro.mp3",
    "shoot": "shoot.WAV",
    "hit": "hit.WAV",
    "powerup_life": "powerup_life.WAV",
    "powerup_shot": "powerup_shot.WAV",
    "powerup_tp": "powerup_teleport.WAV",
    "point": "point.wav",
    "bg_phase1": "bg_phase1.mp3",
    "bg_phase2": "bg_phase2.mp3",
    "bg_phase3": "bg_phase3.mp3",
    "bg_phase4": "bg_phase4.mp3",
    "bg_boss": "bg_boss.mp3"
}

# COLORS & FONTS
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 220, 0)
RED = (255, 60, 60)
GREEN = (60, 255, 100)
BLUE = (60, 100, 255)

font = pygame.font.Font(None, 36)
big_font = pygame.font.Font(None, 48)

# GAME CONFIG
PHASE_TARGETS = {1: 50, 2: 75, 3: 100, 4: 125}
MAX_PHASE = 5
MAX_METEORS_BASE = 5
MAX_METEORS_INCREMENT = 3
METEOR_MAX_SPEED = 12
BULLET_LIMIT = 9
INVULN_DURATION = 2000
TP_SHIELD_DURATION = 5000
PHASE_START_DELAY = 3000
PLAYER_START_LIVES = 5
SAVE_FILE = "savegame.json"
HIGHSCORE_FILE = "highscores.json"
TOP_SCORES = 10

BOSS_W = 256
BOSS_H = 128
ENGINE_FRAMES = 10

# ----------------------------------------------------------
# HELPERS: IMAGEM/SOM/FALLBACK
# ----------------------------------------------------------
def load_image(filename, fallback_color=(100,100,100,0), size=None):
    if filename and os.path.exists(filename):
        try:
            img = pygame.image.load(filename).convert_alpha()
            if size:
                img = pygame.transform.scale(img, size)
            return img
        except Exception:
            pass
    w, h = size if size else (50,50)
    surf = pygame.Surface((w,h), pygame.SRCALPHA)
    surf.fill(fallback_color)
    return surf

def load_sound(filename):
    if filename and os.path.exists(filename):
        try:
            return pygame.mixer.Sound(filename)
        except Exception:
            return None
    return None

# Load images
IMAGES = {
    "player1": load_image(ASSETS.get("player1",""), size=(80,60)),
    "player2": load_image(ASSETS.get("player2",""), size=(80,60)),
    "bullet": pygame.transform.scale(load_image(ASSETS.get("bullet","")), (24,24)),
    "meteoro_normal": load_image(ASSETS.get("meteoro_normal",""), size=(40,40)),
    "meteoro_amarelo": load_image(ASSETS.get("meteoro_amarelo",""), size=(40,40)),
    "meteoro_verde": load_image(ASSETS.get("meteoro_verde",""), size=(40,40)),
    "meteoro_teleport": load_image(ASSETS.get("meteoro_teleport",""), size=(40,40)),
    "boss_sprite": load_image(ASSETS.get("boss_sprite","")),
    "boss_engine": load_image(ASSETS.get("boss_engine","")),
    "shield": load_image(ASSETS.get("shield",""), size=(90,90)),
    "bg_phase1": load_image(ASSETS.get("bg_phase1",""), size=(WIDTH,HEIGHT)),
    "bg_phase2": load_image(ASSETS.get("bg_phase2",""), size=(WIDTH,HEIGHT)),
    "bg_phase3": load_image(ASSETS.get("bg_phase3",""), size=(WIDTH,HEIGHT)),
    "bg_phase4": load_image(ASSETS.get("bg_phase4",""), size=(WIDTH,HEIGHT)),
    "bg_boss": load_image(ASSETS.get("bg_boss",""), size=(WIDTH,HEIGHT))
}

SOUNDS = {k: load_sound(v) for k,v in AUDIO_ASSETS.items()}

# ----------------------------------------------------------
# CONTROLE MUSICAS
# ----------------------------------------------------------
def play_music_for_phase(phase):
    key = None
    if phase == 1: key = "bg_phase1"
    elif phase == 2: key = "bg_phase2"
    elif phase == 3: key = "bg_phase3"
    elif phase == 4: key = "bg_phase4"
    elif phase == 5: key = "bg_boss"
    path = AUDIO_ASSETS.get(key,"")
    if path and os.path.exists(path):
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(0.3)
            pygame.mixer.music.play(-1)
        except Exception:
            pass
    else:
        try:
            pygame.mixer.music.stop()
        except:
            pass

def play_intro_music():
    path = AUDIO_ASSETS.get("intro","")
    if path and os.path.exists(path):
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(0.35)
            pygame.mixer.music.play(-1)
        except:
            pass
    else:
        try:
            pygame.mixer.music.stop()
        except:
            pass

def stop_music():
    try:
        pygame.mixer.music.stop()
    except:
        pass

# ----------------------------------------------------------
# SAVE
# ----------------------------------------------------------
def clamp(n, a, b):
    return max(a, min(b, n))

def save_json(filepath, data):
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print("Erro ao salvar JSON:", e)
        return False

def load_json(filepath):
    if not os.path.exists(filepath):
        return None
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print("Erro ao ler JSON:", e)
        return None

# ----------------------------------------------------------
# SPRITESHEET
# ----------------------------------------------------------
class SpriteAnimation:
    def __init__(self, spritesheet_surf, frame_w, frame_h, frame_time=100, frames_count=None):
        self.frames = []
        self.frame_w = frame_w
        self.frame_h = frame_h
        self.frame_time = frame_time
        self.last_update = pygame.time.get_ticks()
        self.current_frame = 0

        if spritesheet_surf:
            sheet_w = spritesheet_surf.get_width()
            total = frames_count if frames_count else max(1, sheet_w // frame_w)
            for i in range(total):
                rect = pygame.Rect(i * frame_w, 0, frame_w, frame_h)
                try:
                    frame = spritesheet_surf.subsurface(rect).copy()
                except Exception:
                    frame = pygame.Surface((frame_w, frame_h), pygame.SRCALPHA)
                self.frames.append(frame)

    def update(self):
        if len(self.frames) <= 1:
            return
        now = pygame.time.get_ticks()
        if now - self.last_update >= self.frame_time:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.frames)

    def get_frame(self):
        if not self.frames:
            return None
        return self.frames[self.current_frame]

# ----------------------------------------------------------
# CLASSES: Projectile, Player, Meteor, Boss
# ----------------------------------------------------------

class Powerup:
    def __init__(self, x, y, image_key, speed=3):
        self.rect = pygame.Rect(int(x), int(y), 40, 40)
        self.image = IMAGES.get(image_key)
        self.speed = speed

    def update(self):
        self.rect.y += self.speed

    def draw(self, surf):
        if self.image:
            surf.blit(self.image, self.rect)
        else:
            pygame.draw.rect(surf, YELLOW, self.rect)

class PowerupLife(Powerup):
    def __init__(self, x, y):
        super().__init__(x, y, "meteoro_verde", speed=3)

class PowerupShot(Powerup):
    def __init__(self, x, y):
        super().__init__(x, y, "meteoro_amarelo", speed=3)

class PowerupTeleport(Powerup):
    def __init__(self, x, y):
        super().__init__(x, y, "meteoro_teleport", speed=3)

class Projectile:
    def __init__(self, x, y, vx, vy, owner, speed=12):
        self.rect = pygame.Rect(int(x), int(y), 6, 12)
        self.vx = vx
        self.vy = vy
        self.owner = owner
        self.speed = speed

    def update(self):
        self.rect.x += int(self.vx)
        self.rect.y += int(self.vy)

    def draw(self, surf):
        try:
            surf.blit(IMAGES["bullet"], self.rect)
        except:
            pygame.draw.rect(surf, YELLOW, self.rect)

class Player:
    def __init__(self, number, x, y):
        self.number = number
        self.image = IMAGES["player1"] if number == 1 else IMAGES["player2"]
        self.rect = self.image.get_rect(center=(x,y))
        self.speed = 7
        self.lives = PLAYER_START_LIVES
        self.invulnerable_until = 0
        self.shot_level = 1
        self.bullets = []
        self.max_bullets = BULLET_LIMIT
        self.width = self.rect.width
        self.height = self.rect.height

    def can_shoot(self):
        return len(self.bullets) < self.max_bullets

    def take_damage(self):
        now = pygame.time.get_ticks()
        if now < self.invulnerable_until:
            return False
        self.lives -= 1
        self.invulnerable_until = now + INVULN_DURATION
        if SOUNDS.get("hit"):
            try:
                SOUNDS["hit"].play()
            except:
                pass
        return True

    def draw(self, surf):
        now = pygame.time.get_ticks()
        if now < self.invulnerable_until:
            if (now // 120) % 2 == 0:
                return
        surf.blit(self.image, self.rect)

class Meteor:
    def __init__(self, x, y, w=40, h=40, typ="normal", speed=4):
        self.rect = pygame.Rect(int(x), int(y), w, h)
        self.type = typ
        self.speed = speed
        self.image = IMAGES.get("meteoro_normal")

    def update(self):
        self.rect.y += self.speed

    def draw(self, surf):
        if self.image:
            surf.blit(self.image, self.rect)
        else:
            pygame.draw.rect(surf, RED, self.rect)

class Boss:
    def __init__(self, center_x, center_y):
        self.w, self.h = BOSS_W, BOSS_H
        raw = IMAGES.get("boss_sprite")
        self.sprite = pygame.transform.scale(raw, (self.w, self.h)) if raw else None
        self.rect = pygame.Rect(center_x - self.w//2, center_y - self.h//2, self.w, self.h)

        self.hp_left = 100
        self.hp_core = 300
        self.hp_right = 100
        self.max_left = 100
        self.max_core = 300
        self.max_right = 100

        self.projectiles = []
        self.shoot_delay = 1200
        self.last_shot = pygame.time.get_ticks()

        # ANIMAÇÃO DOS MOTORES
        sheet = IMAGES.get("boss_engine")
        if sheet and sheet.get_width() > 0 and sheet.get_height() > 0:
            orig_w = sheet.get_width()
            orig_h = sheet.get_height()
            frames_count = max(2, orig_w // max(1, orig_h))
            frame_w = orig_w // frames_count

            scaled_sheet = pygame.Surface((self.w * frames_count, self.h), pygame.SRCALPHA)
            for i in range(frames_count):
                try:
                    src_rect = pygame.Rect(i * frame_w, 0, frame_w, orig_h)
                    frame = sheet.subsurface(src_rect)
                    scaled = pygame.transform.scale(frame, (self.w, self.h))
                    scaled_sheet.blit(scaled, (i * self.w, 0))
                except:
                    pass
            self.engine_anim = SpriteAnimation(scaled_sheet, self.w, self.h, frame_time=90, frames_count=frames_count)
        else:
            self.engine_anim = None

        self.engine_offset_y = self.h // 2 + 25

    def total_hp(self): return max(0,self.hp_left) + max(0,self.hp_core) + max(0,self.hp_right)
    def max_total_hp(self): return self.max_left + self.max_core + self.max_right
    def is_defeated(self): return self.total_hp() <= 0

    def take_damage_to_part(self, part, dmg):
        if part == "left": self.hp_left = max(0, self.hp_left - dmg)
        elif part == "core": self.hp_core = max(0, self.hp_core - dmg)
        elif part == "right": self.hp_right = max(0, self.hp_right - dmg)

    def update(self, players):
        if self.engine_anim: self.engine_anim.update()
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            targets = [p for p in players if p and p.lives > 0]
            if targets:
                alive = []
                if self.hp_left > 0: alive.append("left")
                if self.hp_core > 0: alive.append("core")
                if self.hp_right > 0: alive.append("right")
                if alive:
                    part = random.choice(alive)
                    offset = -self.w//3 if part == "left" else self.w//3 if part == "right" else 0
                    shooter_x = self.rect.centerx + offset
                    target = random.choice(targets)
                    dx = target.rect.centerx - shooter_x
                    dy = target.rect.centery - self.rect.centery
                    dist = math.hypot(dx, dy) or 1
                    speed = 4.5
                    proj = Projectile(shooter_x, self.rect.centery, dx/dist*speed, dy/dist*speed, "boss")
                    self.projectiles.append(proj)
            self.last_shot = now

        for p in list(self.projectiles):
            p.update()
            if not (0 <= p.rect.centerx <= WIDTH and 0 <= p.rect.centery <= HEIGHT):
                self.projectiles.remove(p)

    def draw(self, surf):
        if self.sprite:
            surf.blit(self.sprite, self.rect)
        else:
            pygame.draw.rect(surf, (180,180,180), self.rect)

        if self.engine_anim:
            frame = self.engine_anim.get_frame()
            if frame:
                r = frame.get_rect(center=(self.rect.centerx, self.rect.centery + self.engine_offset_y))
                surf.blit(frame, r)

        total, max_t = self.total_hp(), self.max_total_hp()
        bar_w, bar_h = 340, 16
        x = self.rect.centerx - bar_w//2
        y = self.rect.top - 40
        pygame.draw.rect(surf, (80,0,0), (x, y, bar_w, bar_h))
        if max_t > 0:
            pygame.draw.rect(surf, (0,255,0), (x, y, int(bar_w * total / max_t), bar_h))

        for proj in self.projectiles:
            pygame.draw.circle(surf, (255,80,80), proj.rect.center, 9)
# ----------------------------------------------------------
# UI / HUD
# ----------------------------------------------------------
def draw_text_center(text, y, size=36, color=WHITE):
    f = pygame.font.Font(None, size)
    surf = f.render(text, True, color)
    rect = surf.get_rect(center=(WIDTH//2, y))
    screen.blit(surf, rect)

def draw_hud(players, phase_score, phase, phase_target, credits=0):
    y = 8
    for p in players:
        if p:
            text = f"P{p.number} Vidas:{p.lives} Tiros:{p.shot_level} BalasTela:{len(p.bullets)}"
            surf = font.render(text, True, WHITE)
            screen.blit(surf, (10, y))
            y += 24
    info = f"Fase: {phase}"
    surf = font.render(info, True, WHITE)
    screen.blit(surf, (WIDTH - 150, 8))
    target_text = f"Pontos: {phase_score} / {phase_target if phase < 5 else 'BOSS'}"
    surf2 = font.render(target_text, True, WHITE)
    screen.blit(surf2, (WIDTH - 320, 35))
    credit_text = f"CREDIT(S): {credits}"
    surf3 = font.render(credit_text, True, WHITE)
    screen.blit(surf3, (WIDTH//2 - 60, HEIGHT - 30))

# ----------------------------------------------------------
# SPAWN DE METEOROS E POWERUPS
# ----------------------------------------------------------
def spawn_meteors_for_phase(phase):
    max_count = MAX_METEORS_BASE + (phase - 1) * MAX_METEORS_INCREMENT
    lst = []
    for _ in range(max_count):
        x = random.randint(0, WIDTH - 40)
        y = random.randint(-500, -40)
        speed = random.randint(3 + (phase - 1), min(METEOR_MAX_SPEED, 5 + (phase - 1) * 2))
        meteor = Meteor(x, y, 40, 40, typ="normal", speed=speed)
        lst.append(meteor)
    return lst

def spawn_powerups_for_phase(phase):
    lst = []
    base_count = 3 + phase
    extra = random.randint(3, 8)
    for _ in range(base_count + extra):
        x = random.randint(0, WIDTH - 40)
        y = random.randint(-1200, -100)
        r = random.random()
        if r < 0.35:
            lst.append(PowerupLife(x, y))
        elif r < 0.70:
            lst.append(PowerupShot(x, y))
        else:
            lst.append(PowerupTeleport(x, y))
    return lst

# ----------------------------------------------------------
# SAVE/LOAD/HIGHSCORES
# ----------------------------------------------------------
def make_save_state(phase, phase_score, players, meteors, powerups, boss, phase_timer_start, player2_active, mouse_control):
    state = {
        "phase": phase,
        "phase_score": phase_score,
        "player2_active": player2_active,
        "mouse_control": mouse_control,
        "phase_timer_start": phase_timer_start,
        "players": [],
        "meteors": [],
        "powerups": [],
        "boss": None
    }
    for p in players:
        if p:
            pl = {
                "number": p.number,
                "x": p.rect.x,
                "y": p.rect.y,
                "lives": p.lives,
                "shot_level": p.shot_level,
                "inv_rem": max(0, p.invulnerable_until - pygame.time.get_ticks())
            }
            state["players"].append(pl)
    for m in meteors:
        state["meteors"].append({"x": m.rect.x, "y": m.rect.y, "speed": m.speed})
    for pu in powerups:
        typ = "life" if isinstance(pu, PowerupLife) else "shot" if isinstance(pu, PowerupShot) else "tp"
        state["powerups"].append({"x": pu.rect.x, "y": pu.rect.y, "type": typ})
    if boss:
        state["boss"] = {
            "hp_left": boss.hp_left,
            "hp_core": boss.hp_core,
            "hp_right": boss.hp_right
        }
    return state

def restore_save_state(s):
    phase = s.get("phase", 1)
    phase_score = s.get("phase_score", 0)
    player_objs = [None, None]
    for pd in s.get("players", []):
        num = pd.get("number", 1)
        p = Player(num, pd.get("x", WIDTH//2), pd.get("y", HEIGHT-60))
        p.lives = pd.get("lives", PLAYER_START_LIVES)
        p.shot_level = pd.get("shot_level", 1)
        inv_rem = pd.get("inv_rem", 0)
        if inv_rem > 0:
            p.invulnerable_until = pygame.time.get_ticks() + inv_rem
        player_objs[num-1] = p
    meteors = []
    for md in s.get("meteors", []):
        m = Meteor(md.get("x",0), md.get("y",-50), 40, 40, typ="normal", speed=md.get("speed",4))
        meteors.append(m)
    powerups = []
    for pud in s.get("powerups", []):
        x, y = pud.get("x",0), pud.get("y",-100)
        typ = pud.get("type","life")
        if typ == "life": powerups.append(PowerupLife(x,y))
        elif typ == "shot": powerups.append(PowerupShot(x,y))
        else: powerups.append(PowerupTeleport(x,y))
    boss = None
    if s.get("boss"):
        boss = Boss(WIDTH//2, HEIGHT//3)
        boss.hp_left = s["boss"].get("hp_left", boss.max_left)
        boss.hp_core = s["boss"].get("hp_core", boss.max_core)
        boss.hp_right = s["boss"].get("hp_right", boss.max_right)
    return phase, phase_score, player_objs, meteors, powerups, boss, s.get("phase_timer_start", None), s.get("player2_active", False), s.get("mouse_control", False)

def load_highscores():
    data = load_json(HIGHSCORE_FILE)
    if not data:
        return []
    return data

def save_highscores(lst):
    save_json(HIGHSCORE_FILE, lst)

def add_highscore(name, score):
    scores = load_highscores()
    scores.append({"name": name, "score": score})
    scores = sorted(scores, key=lambda s: s["score"], reverse=True)[:TOP_SCORES]
    save_highscores(scores)

# ----------------------------------------------------------
# EXIT/MENU
# ----------------------------------------------------------
def confirm_quit_sequence():
    while True:
        screen.fill((10,10,20))
        draw_text_center("Pressione ESC para confirmar saída, ou qualquer outra tecla para cancelar.", HEIGHT//2, size=24)
        pygame.display.flip()
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return False
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    return True
                else:
                    return False
        clock.tick(FPS)

def start_menu():
    credits = 0
    show_highscores = False
    enable_player2 = False
    mouse_control = False
    scores = load_highscores()

    play_intro_music()

    while True:
        screen.fill((18,18,30))
        draw_text_center("SPACE ESCAPE", HEIGHT//4, size=64)
        draw_text_center("Pressione C para inserir ficha (Insert Coin).", HEIGHT//4 + 60, size=24)
        draw_text_center("Pressione ENTER para iniciar (requer 1 ficha).", HEIGHT//4 + 90, size=22)
        draw_text_center("Pressione H para ver High Scores. M ativa mouse para P1. 2 ativa P2.", HEIGHT//4 + 120, size=20)
        draw_text_center("Pressione L para carregar jogo salvo. Pressione Q para sair.", HEIGHT//4 + 150, size=20)

        credit_surf = font.render(f"CREDIT(S): {credits}", True, WHITE)
        screen.blit(credit_surf, (WIDTH//2 - 60, HEIGHT//2 + 80))

        if show_highscores:
            y = HEIGHT//2 - 20
            draw_text_center("Top Scores:", y, size=32)
            y += 40
            for s in scores[:TOP_SCORES]:
                surf = font.render(f"{s['name']} - {s['score']}", True, WHITE)
                screen.blit(surf, (WIDTH//2 - 100, y))
                y += 24

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                stop_music()
                if confirm_quit_sequence():
                    pygame.quit()
                    raise SystemExit
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    credits += 1
                if event.key == pygame.K_h:
                    show_highscores = not show_highscores
                if event.key == pygame.K_2:
                    enable_player2 = not enable_player2
                if event.key == pygame.K_m:
                    mouse_control = not mouse_control
                if event.key == pygame.K_l:
                    stop_music()
                    return {"start": True, "player2": enable_player2, "mouse": mouse_control, "load": True, "credits": credits}
                if event.key == pygame.K_q:
                    stop_music()
                    if confirm_quit_sequence():
                        pygame.quit()
                        raise SystemExit
                if event.key == pygame.K_RETURN:
                    if credits >= 1:
                        credits -= 1
                        stop_music()
                        return {"start": True, "player2": enable_player2, "mouse": mouse_control, "load": False, "credits": credits}
                    else:
                        try:
                            if SOUNDS.get("hit"):
                                SOUNDS["hit"].play()
                        except:
                            pass
        clock.tick(FPS)

def end_screen(win, phase_score):
    try:
        pygame.mixer.music.stop()
    except:
        pass
    name = ""
    entering = True
    while entering:
        screen.fill((10,10,20))
        if win:
            draw_text_center("Você venceu! Parabéns!", HEIGHT//3, size=48)
        else:
            draw_text_center("Fim de jogo!", HEIGHT//3, size=48)
        draw_text_center(f"Pontuação final: {phase_score}", HEIGHT//3 + 60, size=32)
        draw_text_center("Digite seu nome e pressione ENTER para salvar no High Score:", HEIGHT//3 + 120, size=20)
        name_surf = font.render(name, True, WHITE)
        screen.blit(name_surf, (WIDTH//2 - 100, HEIGHT//3 + 160))
        pygame.display.flip()
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                if confirm_quit_sequence():
                    pygame.quit()
                    raise SystemExit
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_RETURN:
                    if name.strip() == "":
                        name = "ANÔNIMO"
                    add_highscore(name, phase_score)
                    entering = False
                    break
                elif ev.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    if len(name) < 16 and ev.unicode.isprintable():
                        name += ev.unicode
    showing = True
    while showing:
        screen.fill((10,10,20))
        draw_text_center("Jogo encerrado.", HEIGHT//2 - 40)
        draw_text_center("Pressione C para voltar ao menu inicial ou Q para sair.", HEIGHT//2 + 10)
        pygame.display.flip()
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                if confirm_quit_sequence():
                    pygame.quit()
                    raise SystemExit
            if ev.type == pygame.KEYDOWN:
                if ev.key019 == pygame.K_c:
                    showing = False
                    return
                if ev.key == pygame.K_q:
                    if confirm_quit_sequence():
                        pygame.quit()
                        raise SystemExit

# ----------------------------------------------------------
# GAME LOOP
# ----------------------------------------------------------
def game_loop(start_args):
    phase = 1
    phase_score = 0
    phase_target = PHASE_TARGETS.get(phase, None)
    meteors = spawn_meteors_for_phase(phase)
    powerups = spawn_powerups_for_phase(phase)
    boss = None
    players = [None, None]
    players[0] = Player(1, WIDTH//2, HEIGHT-80)
    if start_args.get("player2"):
        players[1] = Player(2, WIDTH//2 - 120, HEIGHT-80)
    mouse_control = start_args.get("mouse", False)
    player2_active = bool(start_args.get("player2", False))
    phase_start_time = pygame.time.get_ticks()
    in_phase_countdown = True
    countdown_start = pygame.time.get_ticks()
    stop_music()
    play_music_for_phase(phase)
    running = True
    paused = False
    credits_remaining = start_args.get("credits", 0)

    while running:
        dt = clock.tick(FPS)
        now = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if confirm_quit_sequence():
                    pygame.quit()
                    raise SystemExit

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = not paused
                if event.key == pygame.K_F1:
                    state = make_save_state(phase, phase_score, players, meteors, powerups, boss, phase_start_time, player2_active, mouse_control)
                    save_json(SAVE_FILE, state)
                if event.key == pygame.K_F2:
                    s = load_json(SAVE_FILE)
                    if s:
                        phase, phase_score, restored_players, meteors, powerups, boss, pst, player2_active, mouse_control = restore_save_state(s)
                        if restored_players[0]: players[0] = restored_players[0]
                        if len(restored_players) > 1 and restored_players[1]: players[1] = restored_players[1]
                        phase_start_time = pygame.time.get_ticks()
                        in_phase_countdown = True
                        countdown_start = pygame.time.get_ticks()
                        play_music_for_phase(phase)
                if event.key == pygame.K_2:
                    if not players[1]:
                        players[1] = Player(2, WIDTH//2 - 120, HEIGHT-80)
                        player2_active = True
                if event.key == pygame.K_m:
                    mouse_control = not mouse_control
                if event.key == pygame.K_ESCAPE:
                    if confirm_quit_sequence():
                        pygame.quit()
                        raise SystemExit

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and mouse_control and players[0]:
                    p1 = players[0]
                    if p1.can_shoot():
                        spacing = int(p1.width * 0.55)
                        levels = p1.shot_level
                        offsets = []
                        if levels == 1:
                            offsets = [0]
                        elif levels == 2:
                            offsets = [-spacing//2, spacing//2]
                        else:
                            offsets = [-spacing, 0, spacing]
                        for off in offsets:
                            bullet_w = IMAGES["bullet"].get_width()
                            bullet_h = IMAGES["bullet"].get_height()
                            ship_center = p1.rect.centerx
                            ship_top = p1.rect.top
                            bx = ship_center - bullet_w//2 + off
                            by = ship_top - bullet_h//2
                            proj = Projectile(bx, by, 0, -12, 1)
                            p1.bullets.append(proj)
                            if SOUNDS.get("shoot"):
                                try:
                                    SOUNDS["shoot"].play()
                                except:
                                    pass

        if paused:
            draw_text_center("PAUSADO - pressione P para continuar", HEIGHT//2)
            pygame.display.flip()
            continue

        if in_phase_countdown:
            elapsed = now - countdown_start
            screen.fill((10,10,30))
            seconds_left = max(0, PHASE_START_DELAY - elapsed)
            if seconds_left > 0:
                sleft = int(math.ceil(seconds_left / 1000.0))
                draw_text_center(f"Prontos? {sleft}", HEIGHT//2, size=64)
                pygame.display.flip()
            else:
                in_phase_countdown = False
            if in_phase_countdown:
                continue

        keys = pygame.key.get_pressed()

        #PLAYER 1
        p1 = players[0]
        if p1:
            if mouse_control:
                mx, my = pygame.mouse.get_pos()
                p1.rect.centerx = clamp(mx, p1.rect.width//2, WIDTH - p1.rect.width//2)
                p1.rect.centery = clamp(my, p1.rect.height//2, HEIGHT - p1.rect.height//2)
            else:
                if keys[pygame.K_LEFT] and p1.rect.left > 0:
                    p1.rect.x -= p1.speed
                if keys[pygame.K_RIGHT] and p1.rect.right < WIDTH:
                    p1.rect.x += p1.speed
                if keys[pygame.K_UP] and p1.rect.top > 0:
                    p1.rect.y -= p1.speed
                if keys[pygame.K_DOWN] and p1.rect.bottom < HEIGHT:
                    p1.rect.y += p1.speed
                if keys[pygame.K_SPACE]:
                    if p1.can_shoot():
                        spacing = int(p1.width * 0.55)
                        levels = p1.shot_level
                        offsets = []
                        if levels == 1: offsets = [0]
                        elif levels == 2: offsets = [-spacing//2, spacing//2]
                        else: offsets = [-spacing, 0, spacing]
                        for off in offsets:
                            bullet_w = IMAGES["bullet"].get_width()
                            bullet_h = IMAGES["bullet"].get_height()
                            ship_center = p1.rect.centerx
                            ship_top = p1.rect.top
                            bx = ship_center - bullet_w//2 + off
                            by = ship_top - bullet_h//2
                            proj = Projectile(bx, by, 0, -12, 1)
                            p1.bullets.append(proj)
                            if SOUNDS.get("shoot"):
                                try: SOUNDS["shoot"].play()
                                except: pass

        #PLAYER 2
        p2 = players[1]
        if p2:
            if keys[pygame.K_a] and p2.rect.left > 0: p2.rect.x -= p2.speed
            if keys[pygame.K_d] and p2.rect.right < WIDTH: p2.rect.x += p2.speed
            if keys[pygame.K_w] and p2.rect.top > 0: p2.rect.y -= p2.speed
            if keys[pygame.K_s] and p2.rect.bottom < HEIGHT: p2.rect.y += p2.speed
            if keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
                if p2.can_shoot():
                    spacing = int(p2.width * 0.55)
                    levels = p2.shot_level
                    offsets = []
                    if levels == 1: offsets = [0]
                    elif levels == 2: offsets = [-spacing//2, spacing//2]
                    else: offsets = [-spacing, 0, spacing]
                    for off in offsets:
                        bullet_w = IMAGES["bullet"].get_width()
                        bullet_h = IMAGES["bullet"].get_height()
                        ship_center = p2.rect.centerx
                        ship_top = p2.rect.top
                        bx = ship_center - bullet_w//2 + off
                        by = ship_top - bullet_h//2
                        proj = Projectile(bx, by, 0, -12, 2)
                        p2.bullets.append(proj)
                        if SOUNDS.get("shoot"):
                            try: SOUNDS["shoot"].play()
                            except: pass

        for p in players:
            if p:
                for b in list(p.bullets):
                    b.update()
                    if b.rect.bottom < 0 or b.rect.top > HEIGHT or b.rect.left > WIDTH or b.rect.right < 0:
                        try: p.bullets.remove(b)
                        except: pass

        #METEOROS
        for m in list(meteors):
            m.update()
            if m.rect.top > HEIGHT:
                m.rect.y = random.randint(-200, -40)
                m.rect.x = random.randint(0, WIDTH - m.rect.width)
                m.speed = random.randint(3 + (phase - 1), min(METEOR_MAX_SPEED, 5 + (phase - 1) * 2))

            for p in players:
                if p and m.rect.colliderect(p.rect):
                    if p.take_damage():
                        m.rect.y = random.randint(-200, -40)
                        m.rect.x = random.randint(0, WIDTH - m.rect.width)

            for p in players:
                if p:
                    for b in list(p.bullets):
                        if m.rect.colliderect(b.rect):
                            if SOUNDS.get("point"):
                                try: SOUNDS["point"].play()
                                except: pass
                            try: p.bullets.remove(b)
                            except: pass
                            m.rect.y = random.randint(-200, -40)
                            m.rect.x = random.randint(0, WIDTH - m.rect.width)
                            phase_score += 2
                            break

        #POWERUPS
        for pu in list(powerups):
            pu.update()
            if pu.rect.top > HEIGHT:
                powerups.remove(pu)
                continue

            for p in players:
                if p and pu.rect.colliderect(p.rect):
                    if isinstance(pu, PowerupLife):
                        p.lives += 1
                        if SOUNDS.get("powerup_life"): SOUNDS["powerup_life"].play()
                    elif isinstance(pu, PowerupShot):
                        p.shot_level = clamp(p.shot_level + 1, 1, 3)
                        if SOUNDS.get("powerup_shot"): SOUNDS["powerup_shot"].play()
                    elif isinstance(pu, PowerupTeleport):
                        p.rect.centerx = WIDTH//2
                        p.rect.centery = HEIGHT - 120
                        p.invulnerable_until = pygame.time.get_ticks() + TP_SHIELD_DURATION
                        if SOUNDS.get("powerup_tp"): SOUNDS["powerup_tp"].play()
                    try: powerups.remove(pu)
                    except: pass
                    newm = Meteor(random.randint(0, WIDTH-40), random.randint(-300,-40),
                                  typ="normal",
                                  speed=random.randint(3 + (phase - 1), min(METEOR_MAX_SPEED, 5 + (phase - 1) * 2)))
                    meteors.append(newm)
                    break

        #BOSS
        if phase == 5:
            if boss is not None:
                meteors = []
                powerups = []
            if not boss:
                boss = Boss(WIDTH//2, HEIGHT//3)
            boss.update(players)

            for proj in list(boss.projectiles):
                for p in players:
                    if p and proj.rect.colliderect(p.rect):
                        if p.take_damage():
                            if SOUNDS.get("hit"): SOUNDS["hit"].play()
                        try: boss.projectiles.remove(proj)
                        except: pass

            for p in players:
                if p:
                    for b in list(p.bullets):
                        if boss.rect.colliderect(b.rect):
                            rel_x = b.rect.centerx - boss.rect.left
                            third = boss.rect.width / 3.0
                            if rel_x < third:
                                boss.take_damage_to_part("left", 10)
                            elif rel_x < 2*third:
                                boss.take_damage_to_part("core", 10)
                            else:
                                boss.take_damage_to_part("right", 10)
                            phase_score += 10
                            try: p.bullets.remove(b)
                            except: pass

            if boss.is_defeated():
                end_screen(win=True, phase_score=phase_score + sum([p.lives * 5 for p in players if p]))
                return

        #INCREMENTO FASES
        if phase < 5:
            if phase_score >= PHASE_TARGETS[phase]:
                phase += 1
                phase_score = 0
                if phase == 5:
                    meteors = []
                    powerups = []
                else:
                    meteors = spawn_meteors_for_phase(phase)
                    powerups = spawn_powerups_for_phase(phase)
                in_phase_countdown = True
                countdown_start = pygame.time.get_ticks()
                play_music_for_phase(phase)
                continue

        active_players = [p for p in players if p and p.lives > 0]
        if not active_players:
            end_screen(win=False, phase_score=phase_score)
            return

        # DESENHOS
        bg_key = {1:"bg_phase1",2:"bg_phase2",3:"bg_phase3",4:"bg_phase4",5:"bg_boss"}.get(phase)
        screen.fill((5,5,20))
        if bg_key and os.path.exists(ASSETS.get(bg_key,"")):
            try: screen.blit(IMAGES[bg_key], (0,0))
            except: pass

        for m in meteors: m.draw(screen)
        for pu in powerups: pu.draw(screen)

        for p in players:
            if p:
                p.draw(screen)
                if p.invulnerable_until > pygame.time.get_ticks():
                    try:
                        shield_img = IMAGES["shield"]
                        extra = 24
                        shield_scaled = pygame.transform.scale(shield_img, (p.rect.width + extra, p.rect.height + extra))
                        shield_rect = shield_scaled.get_rect(center=p.rect.center)
                        screen.blit(shield_scaled, shield_rect)
                    except:
                        pygame.draw.circle(screen, (100,200,255), p.rect.center, max(p.rect.width,p.rect.height)//2 + 8, 3)

        for p in players:
            if p:
                for b in p.bullets:
                    b.draw(screen)

        if boss: boss.draw(screen)
        draw_hud(players, phase_score, phase, PHASE_TARGETS.get(phase, None) or "BOSS", start_args.get("credits", 0))

        pygame.display.flip()

# ----------------------------------------------------------
# MAIN
# ----------------------------------------------------------
def main():
    try:
        args = start_menu()
        if not args:
            return
        if args.get("load"):
            s = load_json(SAVE_FILE)
            if s:
                phase, phase_score, players, meteors, powerups, boss, pst, player2_active, mouse_control = restore_save_state(s)
                game_loop({"player2": player2_active, "mouse": mouse_control, "credits": args.get("credits", 0)})
            else:
                game_loop(args)
        else:
            game_loop({"player2": args.get("player2", False), "mouse": args.get("mouse", False), "credits": args.get("credits", 0)})
    except SystemExit:
        pass
    except Exception as e:
        print("Erro no jogo:", e)
        pygame.quit()

if __name__ == "__main__":
    main()
