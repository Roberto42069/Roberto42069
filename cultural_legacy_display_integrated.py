import pygame
import random
from dotenv import load_dotenv
import math

load_dotenv()

# Initialize Pygame only when running display (not on import)
# This prevents crashes when imported in web server context
width, height = 800, 600
screen = None

# Fonts will be loaded when display is initialized
font = None
small_font = None
ai_font = None

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
        self.clock = None
        self.themes = cultural_themes
        self.display_initialized = False

    def run_display(self):
        """Run the cultural legacy display"""
        # Initialize Pygame here, not on import
        if not self.display_initialized:
            pygame.init()
            pygame.mixer.init()
            global screen, font, small_font, ai_font
            screen = pygame.display.set_mode((width, height))
            pygame.display.set_caption("Cultural Legacy Display - Roberto Villarreal Martinez")
            
            # Load fonts after Pygame is initialized
            try:
                font = pygame.font.Font("assets/Roboto-Regular.ttf", 48)
                small_font = pygame.font.Font("assets/Roboto-Regular.ttf", 20)
                ai_font = pygame.font.Font("assets/Roboto-Regular.ttf", 16)
            except:
                font = pygame.font.SysFont("arial", 48)
                small_font = pygame.font.SysFont("arial", 20)
                ai_font = pygame.font.SysFont("arial", 16)
            
            self.clock = pygame.time.Clock()
            self.display_initialized = True
        
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

    def generate_resonance(self, emotion, theme):
        """Generate entangled cultural resonance visualization"""
        
        # Map emotion to color modulation
        emotion_colors = {
            "happy": (255, 255, 0),
            "excited": (255, 100, 0),
            "sad": (100, 100, 255),
            "angry": (255, 0, 0),
            "neutral": (200, 200, 200),
            "curious": (150, 200, 255),
            "thoughtful": (150, 100, 255),
            "engaged": (0, 255, 0)
        }
        resonance_color = emotion_colors.get(emotion, (200, 200, 200))
        resonance_strength = 0.8 + 0.2 * random.random()  # Dynamic strength

        # Log to roberto's memory
        if self.roboto and hasattr(self.roboto, 'memory_system') and self.roboto.memory_system:
            try:
                self.roboto.memory_system.add_episodic_memory(
                    user_input=f"Resonance {emotion}",
                    roboto_response=f"Entangled with {theme} at strength {resonance_strength:.2f}",
                    emotion=emotion,
                    user_name=getattr(self.roboto, 'current_user', 'Roberto Villarreal Martinez')
                )
            except Exception as e:
                print(f"Error logging resonance to memory: {e}")

        return {
            "emotion": emotion,
            "theme": theme,
            "resonance_strength": resonance_strength,
            "color_modulation": resonance_color,
            "visualization": "Pulsing glyph with emotional resonance",
            "cultural_alignment": "Nahui Ollin cycle active"
        }

def integrate_with_roboto(roboto_instance):
    """Integrate cultural display with Roboto SAI"""
    display = CulturalLegacyDisplay(roboto_instance)

    # Add to Roboto instance
    roboto_instance.cultural_display = display

    print("🌅 Cultural Legacy Display integrated with Roboto SAI")
    print("🎨 Press SPACE to cycle through themes")

    return display

if __name__ == "__main__":
    # Only initialize display when run as standalone script
    display = CulturalLegacyDisplay()
    display.run_display()