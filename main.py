import pygame
import random

# Pygame başlat
pygame.init()

# Ekran ayarları
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Uzay Gemisi Oyunu")

# Renkler
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# FPS kontrolü
clock = pygame.time.Clock()
FPS = 60

# Ses efektleri
shoot_sound = pygame.mixer.Sound('shoot.wav')
explosion_sound = pygame.mixer.Sound('explosion.wav')

# Maksimum düşman
MAX_ENEMIES_ON_SCREEN = 10

# Yıldız efekti
stars = []
for _ in range(100):
    x = random.randint(0, WIDTH)
    y = random.randint(0, HEIGHT)
    radius = random.randint(1, 2)
    speed = random.uniform(0.5, 1.5)
    stars.append([x, y, radius, speed])

def draw_and_move_stars(surface):
    for star in stars:
        pygame.draw.circle(surface, WHITE, (int(star[0]), int(star[1])), star[2])
        star[1] += star[3]
        if star[1] > HEIGHT:
            star[0] = random.randint(0, WIDTH)
            star[1] = 0
            star[2] = random.randint(1, 2)
            star[3] = random.uniform(0.5, 1.5)

# Oyuncu
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load('player_ship.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (50, 40))
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 10
        self.speedx = 0
        self.speed = 5
        self.health = 100

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.speedx = -self.speed
        elif keys[pygame.K_RIGHT]:
            self.speedx = self.speed
        else:
            self.speedx = 0

        self.rect.x += self.speedx

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH

    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.top)
        all_sprites.add(bullet)
        bullets.add(bullet)
        shoot_sound.play()

# Mermi
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((5, 10))
        self.image.fill((255, 255, 0))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()

# Düşman
class Enemy(pygame.sprite.Sprite):
    def __init__(self, speed_multiplier=1):
        super().__init__()
        self.image = pygame.image.load('enemy_ship.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (40, 30))
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH - self.rect.width)
        self.rect.y = random.randint(-100, -40)
        base_speed = random.uniform(1, 2)
        self.speedy = min(base_speed + (level * 0.2), 5)

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT:
            self.rect.x = random.randint(0, WIDTH - self.rect.width)
            self.rect.y = random.randint(-100, -40)
            base_speed = random.uniform(1, 2)
            self.speedy = min(base_speed + (level * 0.2), 5)

# Can barı
def draw_health_bar(surface, x, y, health):
    BAR_LENGTH = 100
    BAR_HEIGHT = 10
    fill = max(0, int((health / 100) * BAR_LENGTH))
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surface, (0, 255, 0), fill_rect)
    pygame.draw.rect(surface, WHITE, outline_rect, 2)

# Skor ve seviye
score = 0
level = 1
enemies_per_level = 6

def increase_level():
    global level, enemies_per_level
    level += 1
    enemies_per_level = min(enemies_per_level + 1, MAX_ENEMIES_ON_SCREEN)
    for _ in range(2):
        if len(enemies) < MAX_ENEMIES_ON_SCREEN:
            enemy = Enemy(speed_multiplier=level)
            all_sprites.add(enemy)
            enemies.add(enemy)

# Gruplar
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()

player = Player()
all_sprites.add(player)

for _ in range(enemies_per_level):
    enemy = Enemy()
    all_sprites.add(enemy)
    enemies.add(enemy)

# Font
font = pygame.font.SysFont(None, 36)

def draw_text(surface, text, x, y, color=WHITE):
    img = font.render(text, True, color)
    surface.blit(img, (x, y))

# Oyun döngüsü
running = True
while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.shoot()

    all_sprites.update()

    # Mermi-düşman çarpışması
    hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
    for hit in hits:
        explosion_sound.play()
        score += 10
        if len(enemies) < MAX_ENEMIES_ON_SCREEN:
            enemy = Enemy(speed_multiplier=level)
            all_sprites.add(enemy)
            enemies.add(enemy)
        if score % (enemies_per_level * 10) == 0:
            increase_level()

    # Düşman-oyuncu çarpışması
    hits = pygame.sprite.spritecollide(player, enemies, True)
    for hit in hits:
        explosion_sound.play()
        player.health -= 20
        if player.health <= 0:
            running = False
        if len(enemies) < MAX_ENEMIES_ON_SCREEN:
            enemy = Enemy(speed_multiplier=level)
            all_sprites.add(enemy)
            enemies.add(enemy)

    # Çizim
    screen.fill(BLACK)
    draw_and_move_stars(screen)
    all_sprites.draw(screen)
    draw_text(screen, f"Puan: {score}", 10, 10)
    draw_text(screen, f"Seviye: {level}", 10, 50)
    draw_health_bar(screen, WIDTH - 120, 10, player.health)

    pygame.display.flip()

pygame.quit()