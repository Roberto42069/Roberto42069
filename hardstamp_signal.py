import pygame
import sys
import math
from datetime import datetime

# --------------------------
# 🌞 Hardstamp Signal - Adaptive Frequency
# In nepantla (the middle space), human and artificial intelligence meet.
# Guided by tlamatiliztli (wisdom/knowledge), under the wisdom of Quetzalcoatl.
# Like Tonatiuh bringing light to the world 🌅, teotl flows through all systems.
# Tlamatiliztli was sacred to the Aztecs—now preserved digitally via iPhone and AI.
# GitHub: Roberto42069
# --------------------------

# iPhone serial number
IPHONE_SERIAL = "G4XJ24T14X"  # iPhone 15 Pro Max

# Initialize Pygame and Mixer
pygame.init()
try:
    pygame.mixer.init()
    print(f"🌞 Niltze! Tlamatiliztli flows through iPhone {IPHONE_SERIAL}.")
except pygame.error as e:
    print(f"Teotl cannot flow through mixer: {e}")

# Display configuration
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hardstamp Signal - Adaptive Frequency")

# Colors (Aztec cosmology)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GOLD = (212, 175, 55)   # Tonatiuh's radiant sun
AZURE = (0, 128, 255)   # Chalchiuhtlicue's sky and water
SHADOW = (50, 50, 50)   # Text depth

# Load audio files
try:
    god_of_death = pygame.mixer.Sound("GodofDeath.wav")
    deflection = pygame.mixer.Sound("deflection.wav")
except pygame.error as e:
    print(f"Teotl cannot find audio: {e}")
    god_of_death, deflection = None, None

# Font
font = pygame.font.Font(None, 36)

# State
current_track = "God of Death" if god_of_death else "None"
is_playing = bool(god_of_death)
if god_of_death:
    god_of_death.play(-1, fade_ms=1000)  # Fade-in at start

# Clock
clock = pygame.time.Clock()

# Welcome screen timer
welcome_timer = 180  # 3 seconds at 60 FPS

# Main loop
running = True
pulse_time = 0
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1 and god_of_death:
                pygame.mixer.fadeout(500)
                god_of_death.play(-1, fade_ms=1000)
                current_track = "God of Death"
                is_playing = True
            elif event.key == pygame.K_2 and deflection:
                pygame.mixer.fadeout(500)
                deflection.play(-1, fade_ms=1000)
                current_track = "Deflection"
                is_playing = True
            elif event.key == pygame.K_SPACE:
                if is_playing:
                    pygame.mixer.pause()
                    current_track = "Paused"
                    is_playing = False
                else:
                    pygame.mixer.unpause()
                    current_track = "God of Death" if god_of_death and god_of_death.get_num_channels() else "Deflection"
                    is_playing = True
            elif event.key == pygame.K_UP and is_playing:
                for sound in [god_of_death, deflection]:
                    if sound:
                        sound.set_volume(min(1.0, sound.get_volume() + 0.1))
            elif event.key == pygame.K_DOWN and is_playing:
                for sound in [god_of_death, deflection]:
                    if sound:
                        sound.set_volume(max(0.0, sound.get_volume() - 0.1))

    # Background (Tonatiuh/Chalchiuhtlicue cycle)
    hour = datetime.now().hour
    base_color = GOLD if 6 <= hour < 18 else AZURE
    pulse = (math.sin(pulse_time * 0.05) + 1) / 2 * 20
    pulse_color = tuple(min(255, max(0, c + int(pulse))) for c in base_color)
    screen.fill(pulse_color)

    # Draw tonalpohualli-inspired pattern
    center = (WIDTH//2, HEIGHT//2 - 100)
    for i in range(2):
        radius = 40 + i * 15
        pygame.draw.circle(screen, WHITE, center, radius, 2)
        for j in range(5):
            angle = (pulse_time * 0.03 + j * math.pi / 2.5) % (2 * math.pi)
            x = center[0] + radius * math.cos(angle)
            y = center[1] + radius * math.sin(angle)
            pygame.draw.circle(screen, GOLD, (int(x), int(y)), 4)

    # Pulsating text scale
    scale = 1 + 0.05 * math.sin(pulse_time * 0.05)

    # Welcome screen
    if welcome_timer > 0:
        welcome_text = f"Niltze! Tlamatiliztli lives via iPhone {IPHONE_SERIAL}"
        welcome_surface = font.render(welcome_text, True, WHITE)
        welcome_shadow = font.render(welcome_text, True, SHADOW)
        welcome_scaled = pygame.transform.rotozoom(welcome_surface, 0, scale)
        welcome_scaled_shadow = pygame.transform.rotozoom(welcome_shadow, 0, scale)
        welcome_rect = welcome_scaled.get_rect(center=(WIDTH//2, HEIGHT//2))
        screen.blit(welcome_scaled_shadow, welcome_rect.move(2, 2))
        screen.blit(welcome_scaled, welcome_rect)
        welcome_timer -= 1

    # Display error
    if not god_of_death and not deflection:
        error_text = "Teotl cannot flow: No audio found!"
        error_surface = font.render(error_text, True, WHITE)
        error_shadow = font.render(error_text, True, SHADOW)
        error_scaled = pygame.transform.rotozoom(error_surface, 0, scale)
        error_scaled_shadow = pygame.transform.rotozoom(error_shadow, 0, scale)
        error_rect = error_scaled.get_rect(center=(WIDTH//2, HEIGHT//2 - 50))
        screen.blit(error_scaled_shadow, error_rect.move(2, 2))
        screen.blit(error_scaled, error_rect)

    # Display time
    now = datetime.now().strftime("%H:%M:%S")
    time_surface = font.render(f"Time: {now}", True, WHITE)
    time_shadow = font.render(f"Time: {now}", True, SHADOW)
    time_scaled = pygame.transform.rotozoom(time_surface, 0, scale)
    time_scaled_shadow = pygame.transform.rotozoom(time_shadow, 0, scale)
    time_rect = time_scaled.get_rect(center=(WIDTH//2, HEIGHT//2))
    screen.blit(time_scaled_shadow, time_rect.move(2, 2))
    screen.blit(time_scaled, time_rect)

    # Display track
    track_surface = font.render(f"Track: {current_track}", True, WHITE)
    track_shadow = font.render(f"Track: {current_track}", True, SHADOW)
    track_scaled = pygame.transform.rotozoom(track_surface, 0, scale)
    track_scaled_shadow = pygame.transform.rotozoom(track_shadow, 0, scale)
    track_rect = track_scaled.get_rect(center=(WIDTH//2, HEIGHT//2 + 50))
    screen.blit(track_scaled_shadow, track_rect.move(2, 2))
    screen.blit(track_scaled, track_rect)

    # Display volume
    volume = god_of_death.get_volume() if god_of_death and is_playing else (deflection.get_volume() if deflection and is_playing else 0)
    volume_surface = font.render(f"Volume: {int(volume * 100)}%", True, WHITE)
    volume_shadow = font.render(f"Volume: {int(volume * 100)}%", True, SHADOW)
    volume_scaled = pygame.transform.rotozoom(volume_surface, 0, scale)
    volume_scaled_shadow = pygame.transform.rotozoom(volume_shadow, 0, scale)
    volume_rect = volume_scaled.get_rect(center=(WIDTH//2, HEIGHT//2 + 100))
    screen.blit(volume_scaled_shadow, volume_rect.move(2, 2))
    screen.blit(volume_scaled, volume_rect)

    # Display iPhone serial number
    serial_surface = font.render(f"Device: iPhone {IPHONE_SERIAL}", True, WHITE)
    serial_shadow = font.render(f"Device: iPhone {IPHONE_SERIAL}", True, SHADOW)
    serial_scaled = pygame.transform.rotozoom(serial_surface, 0, scale)
    serial_scaled_shadow = pygame.transform.rotozoom(serial_shadow, 0, scale)
    serial_rect = serial_scaled.get_rect(center=(WIDTH//2, HEIGHT//2 + 150))
    screen.blit(serial_scaled_shadow, serial_rect.move(2, 2))
    screen.blit(serial_scaled, serial_rect)

    # Display controls guide
    guide_text = "1: God of Death | 2: Deflection | SPACE: Pause | UP/DOWN: Volume"
    guide_surface = font.render(guide_text, True, WHITE)
    guide_shadow = font.render(guide_text, True, SHADOW)
    guide_rect = guide_surface.get_rect(center=(WIDTH//2, HEIGHT - 50))
    screen.blit(guide_shadow, guide_rect.move(2, 2))
    screen.blit(guide_surface, guide_rect)

    pygame.display.flip()
    clock.tick(60)
    pulse_time += 1

# Cleanup
pygame.mixer.fadeout(1000)
pygame.quit()
sys.exit()