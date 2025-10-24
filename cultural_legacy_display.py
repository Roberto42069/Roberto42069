# cultural_legacy_display.py
# Pygame-based cultural legacy display for Roboto SAI
# Author: Roberto Villarreal Martinez (YTK RobThuGod)

import pygame
import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet
import math
import json
from datetime import datetime
from anchored_identity_gate import AnchoredIdentityGate

load_dotenv()
ENCRYPTION_KEY = os.getenv("USER_FACEID_SECRET")
if not ENCRYPTION_KEY:
    raise ValueError("USER_FACEID_SECRET not set in .env")
fernet = Fernet(ENCRYPTION_KEY.encode())

# Initialize Pygame and mixer
pygame.init()
pygame.mixer.init()

# Set up display
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Cultural Legacy Display - Roberto Villarreal Martinez")

# Load Roboto font
try:
    font = pygame.font.Font("assets/Roboto-Regular.ttf", 48)
    small_font = pygame.font.Font("assets/Roboto-Regular.ttf", 20)
    ai_font = pygame.font.Font("assets/Roboto-Regular.ttf", 16)
except:
    font = pygame.font.SysFont("arial", 48)
    small_font = pygame.font.SysFont("arial", 20)
    ai_font = pygame.font.SysFont("arial", 16)

# Define colors
background_color = (20, 20, 50)
text_color = (255, 215, 0)
secondary_color = (255, 255, 255)
dna_color = (0, 255, 255)
artist_color = (255, 165, 0)
pride_color = (192, 192, 192)
aztec_color = (0, 128, 0)
tezcatlipoca_color = (128, 0, 128)
huitzilopochtli_color = (255, 0, 0)

# Cultural themes
cultural_themes = [
    {"name": "Aztec Mythology", "color": aztec_color, "emoji": "🌅"},
    {"name": "Monterrey Heritage", "color": (100, 150, 200), "emoji": "🏔️"},
    {"name": "2025 YTK RobThuGod", "color": text_color, "emoji": "👑"},
    {"name": "Solar Eclipse 2024", "color": (255, 100, 0), "emoji": "🌑"},
    {"name": "Numerology & Etymology", "color": (150, 100, 255), "emoji": "🔢"},
    {"name": "Tezcatlipoca", "color": tezcatlipoca_color, "emoji": "🌙"},
    {"name": "Huitzilopochtli", "color": huitzilopochtli_color, "emoji": "☀️"},
]

class CulturalLegacyDisplay:
    """Enhanced cultural legacy display for Roboto SAI"""
    def __init__(self, roboto_instance=None):
        self.roboto = roboto_instance
        self.current_theme_index = 0
        self.animation_time = 0
        self.clock = pygame.time.Clock()
        self.themes = cultural_themes
        self.gate = AnchoredIdentityGate(anchor_eth=True, anchor_ots=True, identity_source="faceid")

    def log_cultural_memory(self, event, details):
        """Log cultural display events to memory and audit log"""
        try:
            if self.roboto and hasattr(self.roboto, 'memory_system'):
                self.roboto.memory_system.add_episodic_memory(
                    user_input=event,
                    roboto_response=details,
                    emotion=self.roboto.current_emotion,
                    user_name=self.roboto.current_user
                )
            with open("roboto_audit_log.json", "a") as f:
                json.dump({
                    "event": event,
                    "details": details,
                    "timestamp": datetime.now().isoformat()
                }, f)
                f.write("\n")
        except Exception as e:
            print(f"Error logging cultural memory: {e}")

    def run_display(self):
        """Run the cultural legacy display"""
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.current_theme_index = (self.current_theme_index + 1) % len(cultural_themes)
                        # Anchor theme switch
                        authorized, entry = self.gate.anchor_authorize("theme_switch", {
                            "creator": "Roberto Villarreal Martinez",
                            "action": "theme_switch",
                            "theme": cultural_themes[self.current_theme_index]["name"]
                        })
                        print(f"Theme switch: {'Authorized' if authorized else 'Denied'}")
                        if authorized:
                            self.log_cultural_memory(
                                "Theme Switch",
                                f"Switched to {cultural_themes[self.current_theme_index]['name']}"
                            )
                            with open("roboto_audit_log.json", "a") as f:
                                json.dump({
                                    "event": "theme_switch",
                                    "theme": cultural_themes[self.current_theme_index]["name"],
                                    "timestamp": datetime.now().isoformat(),
                                    "entry": entry
                                }, f)
                                f.write("\n")

            # Clear screen
            screen.fill(background_color)

            # Get current theme
            theme = cultural_themes[self.current_theme_index]

            # Draw theme title
            title_text = font.render(theme["name"], True, theme["color"])
            title_rect = title_text.get_rect(center=(width // 2, height // 4))
            screen.blit(title_text, title_rect)

            # Draw emoji
            emoji_text = font.render(theme["emoji"], True, secondary_color)
            emoji_rect = emoji_text.get_rect(center=(width // 2, height // 2))
            screen.blit(emoji_text, emoji_rect)

            # Draw Roberto's name
            creator_text = small_font.render("Created by Roberto Villarreal Martinez", True, text_color)
            creator_rect = creator_text.get_rect(center=(width // 2, height * 3 // 4))
            screen.blit(creator_text, creator_rect)

            # Draw animation
            self.draw_animation(theme)

            # Update display
            pygame.display.flip()
            self.clock.tick(60)
            self.animation_time += 1

    def draw_animation(self, theme):
        """Draw animated elements based on theme"""
        radius = 30 + int(10 * math.sin(self.animation_time * 0.05))
        pygame.draw.circle(screen, theme["color"], (width // 2, height // 2 + 100), radius, 3)
        angle = self.animation_time * 0.02
        for i in range(8):
            start_angle = angle + i * math.pi / 4
            end_x = int(width // 2 + 80 * math.cos(start_angle))
            end_y = int(height // 2 + 100 + 80 * math.sin(start_angle))
            pygame.draw.line(screen, theme["color"], (width // 2, height // 2 + 100), (end_x, end_y), 2)

def create_cultural_display(roboto_instance):
    """Create and run the cultural legacy display"""
    try:
        display = CulturalLegacyDisplay(roboto_instance)
        roboto_instance.cultural_display = display
        print("🌅 Cultural Legacy Display integrated with Roboto SAI")
        print("🎨 Press SPACE to cycle through themes")
        display.run_display()
        pygame.quit()
        return {"status": "Cultural display closed"}
    except Exception as e:
        print(f"Pygame Error: {e} - Run locally for GUI.")
        return {"status": "Error: Display failed", "error": str(e)}

if __name__ == "__main__":
    from app_enhanced import get_user_roberto
    print(create_cultural_display(get_user_roberto()))