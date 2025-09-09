#!/usr/bin/env python3
"""
Simple Idle Clicker in Pygame
---------------------------------
A tiny Cookie-Clicker-style game with:
- Click the big button to earn cookies
- Buy upgrades to increase cookies per click (CPC)
- Buy autoclickers that generate cookies per second (CPS)
- Save/Load to idle_save.json automatically on exit/start
- Lightweight UI, no external assets

Run:
    pip install pygame
    python idle_clicker.py

Controls:
    Left-click buttons to buy/activate
    S key: Save
    L key: Load
    Esc or window close: Quit (auto-saves)
"""
import json
import math
import os
import sys
import time
from dataclasses import dataclass, field
from typing import Callable, Optional, Tuple

import pygame


# ----------------------------
# Utility helpers
# ----------------------------
def fmt_num(n: float) -> str:
    """Human-friendly number formatting."""
    suffixes = ["", "K", "M", "B", "T", "Qa", "Qi", "Sx", "Sp", "Oc", "No", "De"]
    if n < 1000:
        return f"{n:.0f}"
    k = 0
    while n >= 1000 and k < len(suffixes) - 1:
        n /= 1000.0
        k += 1
    if n >= 100:
        return f"{n:.0f}{suffixes[k]}"
    elif n >= 10:
        return f"{n:.1f}{suffixes[k]}"
    else:
        return f"{n:.2f}{suffixes[k]}"


# ----------------------------
# UI Components
# ----------------------------
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (60, 60, 60)
LIGHT_GRAY = (90, 90, 90)
GREEN = (70, 160, 90)
RED = (190, 70, 70)
BLUE = (80, 120, 200)
YELLOW = (230, 200, 80)


class Button:
    def __init__(self, rect: pygame.Rect, text: str, font: pygame.font.Font,
                 on_click: Optional[Callable] = None, tooltip: str = "",
                 bg=LIGHT_GRAY, bg_hover=(110, 110, 110), fg=WHITE):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.on_click = on_click
        self.tooltip = tooltip
        self.bg = bg
        self.bg_hover = bg_hover
        self.fg = fg
        self.enabled = True

    def draw(self, surf: pygame.Surface, mouse_pos: Tuple[int, int]):
        hovered = self.rect.collidepoint(mouse_pos)
        color = self.bg_hover if (hovered and self.enabled) else self.bg
        if not self.enabled:
            color = (70, 70, 70)
        pygame.draw.rect(surf, color, self.rect, border_radius=8)
        # text
        txt = self.font.render(self.text, True, self.fg if self.enabled else (160, 160, 160))
        # Support multi-line with \n
        if "\n" in self.text:
            lines = self.text.split("\n")
            total_h = sum(self.font.size(line)[1] for line in lines)
            cur_y = self.rect.centery - total_h // 2
            for line in lines:
                line_surf = self.font.render(line, True, self.fg if self.enabled else (160, 160, 160))
                surf.blit(line_surf, line_surf.get_rect(center=(self.rect.centerx, cur_y + line_surf.get_height() // 2)))
                cur_y += line_surf.get_height()
        else:
            surf.blit(txt, txt.get_rect(center=self.rect.center))
        # border
        pygame.draw.rect(surf, (30, 30, 30), self.rect, 2, border_radius=8)

    def handle_event(self, event):
        if not self.enabled:
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.on_click:
                    self.on_click()


@dataclass
class Upgrade:
    name: str
    base_cost: float
    cost_scale: float
    cps: float = 0.0        # cookies per second this upgrade adds (per unit)
    cpc: float = 0.0        # cookies per click this upgrade adds (per unit)
    owned: int = 0
    color: Tuple[int, int, int] = field(default_factory=lambda: BLUE)

    def current_cost(self) -> float:
        return self.base_cost * (self.cost_scale ** self.owned)

    def buy(self, cookies: float, n: int = 1) -> Tuple[bool, float]:
        """Attempt to buy n units. Returns (purchased?, new_cookie_amount)."""
        total_cost = 0.0
        # Geometric series sum for cost over n units
        for i in range(n):
            total_cost += self.base_cost * (self.cost_scale ** (self.owned + i))
        if cookies >= total_cost:
            self.owned += n
            return True, cookies - total_cost
        return False, cookies


# ----------------------------
# Game
# ----------------------------
SAVE_PATH = "idle_save.json"


class Game:
    def __init__(self, width=900, height=600):
        pygame.init()
        pygame.display.set_caption("Tiny Idle Clicker")
        self.W, self.H = width, height
        self.screen = pygame.display.set_mode((self.W, self.H))
        self.clock = pygame.time.Clock()

        # Fonts
        self.title_font = pygame.font.SysFont("arial", 28, bold=True)
        self.ui_font = pygame.font.SysFont("arial", 20)
        self.small_font = pygame.font.SysFont("arial", 16)

        self.cookies = 0.0
        self.cpc_base = 1.0  # base cookies per click
        self.last_time = time.time()

        # Upgrades (feel free to tweak numbers!)
        self.upgrades = [
            Upgrade("Autoclicker", base_cost=15, cost_scale=1.15, cps=0.1, color=GREEN),
            Upgrade("Grandma", base_cost=100, cost_scale=1.15, cps=1.0, color=YELLOW),
            Upgrade("Farm", base_cost=1100, cost_scale=1.15, cps=8.0, color=BLUE),
            Upgrade("Mine", base_cost=12000, cost_scale=1.15, cps=47.0, color=RED),
        ]
        self.click_upgrades = [
            Upgrade("Cursor+", base_cost=20, cost_scale=1.25, cpc=1.0, color=(120, 120, 220)),
            Upgrade("Strong Finger", base_cost=200, cost_scale=1.25, cpc=5.0, color=(160, 120, 220)),
        ]

        # Buttons
        self.buttons = []
        self.make_buttons()

        # Try autoload
        self.load_game(auto=True)

    # ----------------------------
    # Derived stats
    # ----------------------------
    @property
    def cpc(self) -> float:
        """Cookies per click."""
        return self.cpc_base + sum(u.cpc * u.owned for u in self.click_upgrades)

    @property
    def cps(self) -> float:
        """Cookies per second."""
        return sum(u.cps * u.owned for u in self.upgrades)

    # ----------------------------
    # Save/Load
    # ----------------------------
    def save_game(self):
        data = {
            "cookies": self.cookies,
            "upgrades": [{"name": u.name, "owned": u.owned} for u in self.upgrades],
            "click_upgrades": [{"name": u.name, "owned": u.owned} for u in self.click_upgrades],
            "last_time": time.time(),
        }
        try:
            with open(SAVE_PATH, "w") as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print("Save failed:", e)
            return False

    def load_game(self, auto=False):
        if not os.path.exists(SAVE_PATH):
            return False
        try:
            with open(SAVE_PATH, "r") as f:
                data = json.load(f)
            self.cookies = float(data.get("cookies", 0.0))
            u_owned = {d["name"]: int(d["owned"]) for d in data.get("upgrades", [])}
            cu_owned = {d["name"]: int(d["owned"]) for d in data.get("click_upgrades", [])}
            for u in self.upgrades:
                u.owned = u_owned.get(u.name, 0)
            for u in self.click_upgrades:
                u.owned = cu_owned.get(u.name, 0)
            # Offline progress
            last_time = float(data.get("last_time", time.time()))
            offline_secs = max(0.0, time.time() - last_time)
            gained = self.cps * offline_secs
            if gained > 0:
                self.cookies += gained
            if not auto:
                print(f"Loaded. Offline for {offline_secs:.0f}s, gained ~{fmt_num(gained)} cookies.")
            return True
        except Exception as e:
            print("Load failed:", e)
            return False

    # ----------------------------
    # UI
    # ----------------------------
    def make_buttons(self):
        self.buttons = []

        # Big click button
        big_rect = pygame.Rect(40, 200, 240, 240)
        self.big_click_btn = Button(
            big_rect, "CLICK", self.title_font, on_click=self.handle_big_click, bg=(120, 90, 150),
            tooltip="Click to get cookies!"
        )
        self.buttons.append(self.big_click_btn)

        # Save / Load buttons
        self.save_btn = Button(pygame.Rect(40, 470, 115, 40), "Save (S)", self.ui_font, on_click=self.save_game)
        self.load_btn = Button(pygame.Rect(165, 470, 115, 40), "Load (L)", self.ui_font, on_click=self.load_game)
        self.buttons += [self.save_btn, self.load_btn]

        # Upgrade shop panels
        # Auto (left of center)
        self.auto_buttons = []
        x, y = 320, 140
        for i, u in enumerate(self.upgrades):
            rect = pygame.Rect(x, y + i * 70, 260, 60)
            btn = Button(rect, "", self.ui_font, on_click=lambda u=u: self.buy_upgrade(u))
            btn.tooltip = f"+{u.cps} CPS"
            self.auto_buttons.append(btn)
            self.buttons.append(btn)

        # Click upgrades (right side)
        self.click_buttons = []
        x2, y2 = 600, 140
        for i, u in enumerate(self.click_upgrades):
            rect = pygame.Rect(x2, y2 + i * 70, 260, 60)
            btn = Button(rect, "", self.ui_font, on_click=lambda u=u: self.buy_upgrade(u))
            btn.tooltip = f"+{u.cpc} CPC"
            self.click_buttons.append(btn)
            self.buttons.append(btn)

    def handle_big_click(self):
        self.cookies += self.cpc

    def buy_upgrade(self, u: Upgrade):
        purchased, new_amt = u.buy(self.cookies)
        if purchased:
            self.cookies = new_amt
        # else not enough cookies; we could flash UI, but keeping it simple

    # ----------------------------
    # Main loop
    # ----------------------------
    def run(self):
        running = True
        while running:
            dt = self.clock.tick(60) / 1000.0  # seconds
            self.update(dt)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.save_game()
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.save_game()
                        running = False
                    elif event.key == pygame.K_s:
                        self.save_game()
                    elif event.key == pygame.K_l:
                        self.load_game()
                for b in self.buttons:
                    b.handle_event(event)
            self.draw()
        pygame.quit()
        sys.exit(0)

    # ----------------------------
    # Update & Draw
    # ----------------------------
    def update(self, dt: float):
        # passive income
        self.cookies += self.cps * dt
        # enable/disable purchase buttons based on affordability
        for btn, u in [(b, u) for b, u in zip(self.auto_buttons, self.upgrades)] + \
                      [(b, u) for b, u in zip(self.click_buttons, self.click_upgrades)]:
            btn.enabled = self.cookies >= u.current_cost()

    def draw_panel(self, surf, rect, title):
        pygame.draw.rect(surf, (40, 40, 40), rect, border_radius=10)
        pygame.draw.rect(surf, (20, 20, 20), rect, 2, border_radius=10)
        t = self.ui_font.render(title, True, WHITE)
        surf.blit(t, (rect.x + 10, rect.y + 8))

    def draw(self):
        self.screen.fill((25, 25, 30))
        mouse_pos = pygame.mouse.get_pos()

        # Top header
        header_rect = pygame.Rect(20, 20, self.W - 40, 90)
        self.draw_panel(self.screen, header_rect, "Tiny Idle Clicker")
        cookies_txt = self.title_font.render(f"Cookies: {fmt_num(self.cookies)}", True, YELLOW)
        cps_txt = self.ui_font.render(f"CPS: {fmt_num(self.cps)}   |   CPC: {fmt_num(self.cpc)}", True, WHITE)
        self.screen.blit(cookies_txt, (header_rect.x + 15, header_rect.y + 40))
        self.screen.blit(cps_txt, (header_rect.x + 15, header_rect.y + 70))

        # Big click button panel
        left_rect = pygame.Rect(20, 120, 300, 400)
        self.draw_panel(self.screen, left_rect, "Clicker")
        self.big_click_btn.draw(self.screen, mouse_pos)

        # Auto upgrades panel
        center_rect = pygame.Rect(320, 120, 260, 400)
        self.draw_panel(self.screen, center_rect, "Auto Upgrades (CPS)")
        for btn, u in zip(self.auto_buttons, self.upgrades):
            btn.text = f"{u.name} (x{u.owned})\nCost: {fmt_num(u.current_cost())}\n+{u.cps}/s each"
            # draw color swatch
            pygame.draw.rect(self.screen, u.color, (btn.rect.x + 8, btn.rect.y + 8, 10, btn.rect.h - 16), border_radius=3)
            btn.draw(self.screen, mouse_pos)

        # Click upgrades panel
        right_rect = pygame.Rect(600, 120, 260, 400)
        self.draw_panel(self.screen, right_rect, "Click Upgrades (CPC)")
        for btn, u in zip(self.click_buttons, self.click_upgrades):
            btn.text = f"{u.name} (x{u.owned})\nCost: {fmt_num(u.current_cost())}\n+{fmt_num(u.cpc)}/click each"
            pygame.draw.rect(self.screen, u.color, (btn.rect.x + 8, btn.rect.y + 8, 10, btn.rect.h - 16), border_radius=3)
            btn.draw(self.screen, mouse_pos)

        # Footer
        footer = self.small_font.render("Tip: S=Save, L=Load, Esc=Quit (auto-saves). Costs grow each purchase.", True, (200, 200, 200))
        self.screen.blit(footer, (20, self.H - 24))

        pygame.display.flip()


def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
