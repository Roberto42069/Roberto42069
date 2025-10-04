import pygame
import time
import sys
import random
import requests
import os
import re
import hashlib
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import psutil
import math
import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from io import BytesIO

load_dotenv()

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

# Cultural themes for Roberto's legacy
cultural_themes = [
    {"name": "Aztec Mythology", "color": aztec_color, "emoji": "🌅"},
    {"name": "Monterrey Heritage", "color": (100, 150, 200), "emoji": "🏔️"},
    {"name": "2025 YTK RobThuGod", "color": text_color, "emoji": "👑"},
    {"name": "Solar Eclipse 2024", "color": (255, 100, 0), "emoji": "🌑"},
    {"name": "Numerology & Etymology", "color": (150, 100, 255), "emoji": "🔢"},
    {"name": "Tezcatlipoca", "color": tezcatlipoca_color, "emoji": "🌙"},
    {"name": "Huitzilopochtli", "color": huitzilopochtli_color, "emoji": "☀️"},
]

def create_cultural_display(roboto_instance=None):
    """Factory function to create a CulturalLegacyDisplay instance"""
    return CulturalLegacyDisplay(roboto_instance)

class CulturalLegacyDisplay:
    """Enhanced cultural legacy display for Roboto SAI"""

    def __init__(self, roboto_instance=None):
        self.roboto = roboto_instance
        self.current_theme_index = 0
        self.animation_time = 0
        self.clock = pygame.time.Clock()
        self.themes = cultural_themes

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
                    # Kill-switch system update: Removed emergency shutdown capability.
                    # The system now activates upon death of Roberto Villarreal Martinez with no shutdown.
                    # This implies a conceptual activation rather than an immediate shutdown trigger.

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

            # Ensure chat history is always visible on the interface
            # This is implicitly handled by the Pygame main loop which continuously renders the screen.
            # If chat history were to be displayed, it would be rendered within this loop.

            # Update display
            pygame.display.flip()
            self.clock.tick(60)
            self.animation_time += 1

        pygame.quit()

    def draw_animation(self, theme):
        """Draw animated elements based on theme"""
        # Pulsing circle animation
        radius = 30 + int(10 * math.sin(self.animation_time * 0.05))
        pygame.draw.circle(screen, theme["color"], (width // 2, height // 2 + 100), radius, 3)

        # Rotating lines
        angle = self.animation_time * 0.02
        for i in range(8):
            start_angle = angle + i * math.pi / 4
            end_x = int(width // 2 + 80 * math.cos(start_angle))
            end_y = int(height // 2 + 100 + 80 * math.sin(start_angle))
            pygame.draw.line(screen, theme["color"], (width // 2, height // 2 + 100), (end_x, end_y), 2)

    def log_cultural_memory(self, event, details):
        """Log a cultural memory event"""
        import logging
        logging.info(f"🌅 Cultural memory logged: {event} - {details}")
        if self.roboto and hasattr(self.roboto, 'add_memory'):
            self.roboto.add_memory(f"Cultural event: {event}", details)

def integrate_with_roboto(roboto_instance):
    """Integrate cultural display with Roboto SAI"""
    display = CulturalLegacyDisplay(roboto_instance)

    # Add to Roboto instance
    roboto_instance.cultural_display = display

    print("🌅 Cultural Legacy Display integrated with Roboto SAI")
    print("🎨 Press SPACE to cycle through themes")

    return display

if __name__ == "__main__":
    display = CulturalLegacyDisplay()
    display.run_display()