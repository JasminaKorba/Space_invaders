import pygame, random, sys

pygame.init()

screen_info = pygame.display.Info()
SCREEN_WIDTH = screen_info.current_w
SCREEN_HEIGHT = screen_info.current_h
display_surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Invaders")

FPS = 60
clock = pygame.time.Clock()


class Game:
    def __init__(self, player, alien_group, player_bullets, alien_bullets):
        self.round_number = 1
        self.score = 0

        self.player = player
        self.alien_group = alien_group
        self.player_bullets = player_bullets
        self.alien_bullets = alien_bullets

        # Set sounds and music
        self.new_round_sound = pygame.mixer.Sound("next_level.wav")
        self.breach_sound = pygame.mixer.Sound("die.mp3")
        self.alien_hit_sound = pygame.mixer.Sound("alien_die.wav")
        self.player_hit_sound = pygame.mixer.Sound("die2.wav")
        self.player_hit_sound.set_volume(0.5)

        # Set fonts
        self.font = pygame.font.Font("font_1.ttf", 45)

    def update(self):
        self.shift_alliens()
        self.check_collisions()
        self.check_round_completion()

    def draw(self):
        # Set colors
        WHITE = (255, 255, 255)

        # Set HUD
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        score_rect = score_text.get_rect()
        score_rect.centerx = SCREEN_WIDTH // 2
        score_rect.top = 10

        round_text = self.font.render(f"Round: {self.round_number}", True, WHITE)
        round_rect = round_text.get_rect()
        round_rect.topleft = (20, 10)

        lives_text = self.font.render(f"Lives: {self.player.lives}", True, WHITE)
        lives_rect = lives_text.get_rect()
        lives_rect.topright = (SCREEN_WIDTH - 20, 10)

        # Blit the HUD to the display
        display_surface.blit(score_text, score_rect)
        display_surface.blit(round_text, round_rect)
        display_surface.blit(lives_text, lives_rect)
        pygame.draw.line(display_surface, WHITE, (0, 50), (SCREEN_WIDTH, 50), 4)

    def shift_alliens(self):
        # Determine if alien group hit a wall
        shift = False
        for alien in self.alien_group.sprites():
            if alien.rect.left <= 0 or alien.rect.right >= SCREEN_WIDTH:
                shift = True
        # Shift every alien down, change direction, and check for breach
        if shift:
            breach = False
            for alien in self.alien_group.sprites():
                # Shift down
                alien.rect.y += 10 * self.round_number
                # Reverse the direction and move the alien off the wall
                alien.direction *= -1
                alien.rect.x += alien.direction * alien.velocity
                # Check if an alien reached the SCREEN_HEIGHT
                if alien.rect.bottom >= SCREEN_HEIGHT:
                    breach = True

            # Alien breach the line
            if breach:
                self.breach_sound.play()
                self.player.lives -= 1
                self.check_game_status(
                    "Aliens breached the line!", "Press ENTER to continue"
                )

    def check_collisions(self):
        # See if any bullet in the player bullet group hit an alien in the alien group
        if pygame.sprite.groupcollide(
            self.player_bullets, self.alien_group, True, True
        ):
            pygame.mixer.find_channel(1).play(self.alien_hit_sound)
            self.score += 100
        # See if the player has collided with any alien bullet
        if pygame.sprite.spritecollide(self.player, self.alien_bullets, True):
            pygame.mixer.find_channel(2).play(self.player_hit_sound)
            self.player.lives -= 1
            self.check_game_status("You've been hitted!", "Press ENTER to continue")
        # See if the player has collided with any alien
        if pygame.sprite.spritecollide(self.player, self.alien_group, False):
            pygame.mixer.find_channel(2).play(self.player_hit_sound)
            self.player.lives -= 1
            self.check_game_status("You've been crashed!", "Press ENTER to continue")

    def check_round_completion(self):
        if not self.alien_group:
            self.score += 1000 * self.round_number
            self.round_number += 1
            self.start_new_round()

    def start_new_round(self):
        # Create a grid of Aliens 11 colums and 5 rows
        for i in range(11):
            for j in range(5):
                alien = Alien(
                    70 + (i * 70),
                    70 + (j * 70),
                    self.round_number,
                    self.alien_bullets,
                )
                my_alien_group.add(alien)
        self.player.reset()

        # Pause the game and prompt user to start
        pygame.mixer.find_channel(3).play(self.new_round_sound)
        self.pause_game(f"ROUND: {self.round_number}", "Press ENTER to begin")

    def check_game_status(self, main_text, sub_text):
        # Check to see the status of the game, and how the playe died
        # Empty the bullet groups and reset a player and remining aliens
        self.alien_bullets.empty()
        self.player_bullets.empty()
        self.player.reset()
        for alien in self.alien_group:
            alien.reset()
        # Check if the game is over or it is a simple raound reset
        if self.player.lives == 0:
            self.reset_game()
        else:
            self.pause_game(main_text, sub_text)

    def pause_game(self, main_text, sub_text):
        # Set colors
        WHITE = (255, 255, 255)
        BLACK = (0, 0, 0)

        # Create main pause text
        main_text = self.font.render(main_text, True, WHITE)
        main_rect = main_text.get_rect()
        main_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)

        sub_text = self.font.render(sub_text, True, WHITE)
        sub_rect = sub_text.get_rect()
        sub_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20)

        # Blit the pause text
        for i in range(58):
            display_surface.fill(BLACK)
            ufo_image = pygame.image.load(f"ufo_animation/frame{i}.png")
            ufo_rect = ufo_image.get_rect()
            ufo_rect.center = (400, 600)
            display_surface.blit(ufo_image, ufo_rect)
            display_surface.blit(main_text, main_rect)
            display_surface.blit(sub_text, sub_rect)

            pygame.display.update()

        # Pause the game until the user hit ENTER
        is_paused = True
        while is_paused:
            for event in pygame.event.get():
                # The user want to QUIT
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    # The user want to play again
                    if event.key == pygame.K_RETURN:
                        is_paused = False

    def reset_game(self):
        self.pause_game(
            f"You've been died! SCORE:{self.score}", "Press ENTER to play again"
        )

        # Reset game values
        self.score = 0
        self.round_number = 1
        self.player.lives = 5
        # Empty groups
        self.alien_group.empty()
        self.alien_bullets.empty()
        self.player_bullets.empty()
        # Start a new game
        self.start_new_round()


class Player(pygame.sprite.Sprite):
    def __init__(self, bullet_group):
        super().__init__()
        self.image = pygame.image.load(f"player_image/spaceship_1.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT

        self.lives = 5
        self.velocity = 15

        self.bullet_group = bullet_group

        self.shoot_sound = pygame.mixer.Sound("player_fire.wav")
        self.shoot_sound.set_volume(0.4)

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.velocity
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.velocity
        if keys[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= self.velocity
        if keys[pygame.K_DOWN] and self.rect.bottom < SCREEN_HEIGHT:
            self.rect.y += self.velocity

    def fire(self):
        # Restrict the number of bullets on screen at a time
        if len(self.bullet_group) < 5:
            pygame.mixer.find_channel(5).play(self.shoot_sound)
            PlayerBullet(self.rect.centerx, self.rect.top, self.bullet_group)

    def reset(self):
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT


class Alien(pygame.sprite.Sprite):
    def __init__(self, x, y, velocity, bullet_group):
        super().__init__()
        self.i = 1
        self.image = pygame.image.load(f"ufo{self.i}.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

        self.starting_x = x
        self.starting_y = y

        self.direction = 1
        self.velocity = velocity
        self.bullet_group = bullet_group

        self.shoot_sound = pygame.mixer.Sound("alien_fire.wav")
        self.shoot_sound.set_volume(0.5)

    def update(self):
        if self.i < 6:
            self.i += 1
        else:
            self.i = 1

        self.rect.x += self.direction * self.velocity

        # Randomly fire the bullet
        if random.randint(0, 3000) > 2999 and len(self.bullet_group) < 6:
            pygame.mixer.find_channel(4).play(self.shoot_sound)
            self.fire()

    def fire(self):
        AlienBullet(self.rect.centerx, self.rect.centery, self.bullet_group)

    def reset(self):
        self.rect.topleft = (self.starting_x, self.starting_y)
        self.direction = 1


class PlayerBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, bullet_group):
        super().__init__()
        self.image = pygame.image.load("r1.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y

        self.velocity = 10

        bullet_group.add(self)

    def update(self):
        self.rect.y -= self.velocity

        # If the bullet is off the screen, kill it
        if self.rect.bottom < 0:
            self.kill()


class AlienBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, bullet_group):
        super().__init__()
        self.image = pygame.image.load("r2.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y

        self.velocity = 4

        bullet_group.add(self)

    def update(self):
        self.rect.y += self.velocity

        # If the bullet is off the screen, kill it
        if self.rect.bottom > SCREEN_HEIGHT:
            self.kill()


class BackgroundObject:
    def __init__(self, img, buffer, speed):
        self.img = img
        self.buffer = buffer
        self.width = random.randint(-100, SCREEN_WIDTH - 400)
        self.height = -SCREEN_HEIGHT + self.buffer
        self.speed = speed

    def update(self):
        if self.height >= SCREEN_HEIGHT:
            self.buffer = random.randint(-2000, -1020)
            self.width = random.randint(-100, SCREEN_WIDTH - 400)
            self.height = -SCREEN_HEIGHT + self.buffer
        self.height += self.speed

    def draw(self):
        self.update()
        display_surface.blit(self.img, (self.width, self.height))


# Create a bullet groups
my_player_bullet_group = pygame.sprite.Group()
my_allien_bullet_group = pygame.sprite.Group()

# Create a player group and Player object
my_player_group = pygame.sprite.Group()
my_player = Player(my_player_bullet_group)
my_player_group.add(my_player)

# Create an aliens group. Will add Alien objects via the game's start ner round method
my_alien_group = pygame.sprite.Group()

# Create a Game object
my_game = Game(
    my_player, my_alien_group, my_player_bullet_group, my_allien_bullet_group
)
my_game.start_new_round()

# Create BackgroundObject
my_background_objects = []
buffer = 1020
speed = 2
for x in range(2):
    for i in range(1, 10):
        my_background_objects.append(
            BackgroundObject(
                pygame.image.load(f"o{i}.png").convert_alpha(), buffer, speed
            )
        )
        buffer -= 1000
        speed += 0.2


# The main game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            if event.key == pygame.K_SPACE:
                my_player.fire()

    # Fill the display_surface and draw the background
    display_surface.fill((0, 0, 0))
    for i in range(0, len(my_background_objects)):
        my_background_objects[i].draw()

    # Display and update all sprite groups
    my_player_group.update()
    my_player_group.draw(display_surface)

    my_alien_group.update()
    my_alien_group.draw(display_surface)

    my_player_bullet_group.update()
    my_player_bullet_group.draw(display_surface)

    my_allien_bullet_group.update()
    my_allien_bullet_group.draw(display_surface)

    # Update and draw Game object
    my_game.update()
    my_game.draw()

    # Update screen and tick the clock
    pygame.display.update()
    clock.tick(FPS)
