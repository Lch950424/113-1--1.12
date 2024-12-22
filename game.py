import pygame
import random
import os
import math
import pyautogui
import time

# 等待初始化（視需要調整時間）
time.sleep(1)

# 模擬切換輸入法快捷鍵（以 Windows 的 Alt + Shift 為例）
pyautogui.hotkey('alt', 'shift')
print("輸入法切換完成")

# 初始化 Pygame
pygame.init()

# 載入音效
shoot_sound = pygame.mixer.Sound("shoot.wav")
hit_sound = pygame.mixer.Sound("hit.wav")
damage_sound = pygame.mixer.Sound("damage.wav")

# 設定音效音量
shoot_sound.set_volume(0.3)    # 將射擊音效音量設為 30%
hit_sound.set_volume(0.4)      # 將擊中音效音量設為 40%
damage_sound.set_volume(0.6)   # 將受傷音效音量設為 60%

# 設定 MP3 文件的資料夾
mp3_folder = "music"

# 獲取 MP3 文件列表
mp3_files = [file for file in os.listdir(mp3_folder) if file.endswith(".mp3")]
if mp3_files:
    random_mp3 = random.choice(mp3_files)
    random_mp3_path = os.path.join(mp3_folder, random_mp3)
    pygame.mixer.music.load(random_mp3_path)
    pygame.mixer.music.play(-1)  # 無限循環播放
    print(f"正在播放: {random_mp3}")
else:
    print("資料夾中沒有 MP3 文件！")

# 設定音樂音量
pygame.mixer.music.set_volume(0.7)  # 將音樂音量設為 70%

# 設定視窗
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720  # 視窗大小
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Game")  # 視窗名稱
game_over = False  # 初始化遊戲狀態

# 設定顏色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
HEALTH_COLOR = (255, 0, 0)
LIGHT_YELLOW = (255, 239, 179)

# 設定血量
MAX_HEALTH = 100  # 玩家最大血量
current_health = MAX_HEALTH  # 當前血量
invincible = True  # 玩家受傷後無敵狀態
invincible_time = 2  # 無敵時間

# 設定玩家的參數
PLAYER_SIZE = 70  # 玩家圖片大小
player_x, player_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2  # 玩家起始位置(螢幕中心)
player_speed = 4  # 玩家移動速度
player_rect = pygame.Rect(player_x, player_y, PLAYER_SIZE, PLAYER_SIZE)  # 玩家大小

# 設定子彈的參數
BULLET_SIZE = 20  # 子彈圖片大小
bullets = []  # 用來存儲所有子彈的列表

# 設定敵人的參數
ENEMY_SIZE = 50  # 敵人圖片大小
enemies = []  # 用來存儲所有敵人的列表

# 設定敵人和子彈生成
NUM_INITIAL_ENEMIES = 3  # 開始時生成3個敵人
ENEMY_SPAWN_INTERVAL = 3000  # 每3秒生成一個新敵人
MIN_ENEMY_SPAWN_INTERVAL = 1500  # 最短生成間隔2秒
ENEMY_INCREMENT_INTERVAL = 5000  # 每5秒增加敵人生成數量
base_enemy_count = 1  # 每次生成的敵人數量基數

last_increment_time = pygame.time.get_ticks()  # 用於追蹤上次增量的時間
last_enemy_spawn_time = pygame.time.get_ticks()  # 追蹤上次生成敵人的時間
SHOOT_DELAY = 400  # 每0.4秒才能射擊一次
last_shoot_time = pygame.time.get_ticks()  # 追蹤上次射擊的時間

# 設定分數
score = 0  # 初始分數
start_time = pygame.time.get_ticks()  # 紀錄遊戲開始時間


# 載入圖片
# 玩家
player_image = pygame.image.load("player.png")
player_image = pygame.transform.scale(player_image, (PLAYER_SIZE, PLAYER_SIZE))
# 玩家(無敵時)
player_invincible_image = pygame.image.load("invincible.png")
player_invincible_image = pygame.transform.scale(player_invincible_image, (PLAYER_SIZE, PLAYER_SIZE))
# 近距離敵人
enemy_image = pygame.image.load("enemy.png")
enemy_image = pygame.transform.scale(enemy_image, (ENEMY_SIZE, ENEMY_SIZE))
# 遠距離敵人
enemy2_image = pygame.image.load("enemy2.png")
enemy2_image = pygame.transform.scale(enemy2_image, (ENEMY_SIZE, ENEMY_SIZE))
# 玩家子彈
bullet_image = pygame.image.load("bullet.png")
bullet_image = pygame.transform.scale(bullet_image, (BULLET_SIZE, BULLET_SIZE))
# 敵人子彈
bullet2_image = pygame.image.load("bullet2.png")
bullet2_image = pygame.transform.scale(bullet2_image, (BULLET_SIZE, BULLET_SIZE))


# 發射子彈（朝滑鼠游標方向）
def shoot_enemy_bullet(enemy_rect):
    bullet_rect = pygame.Rect(enemy_rect.centerx - 5, enemy_rect.bottom, 10, 20)
    bullet = {'rect': bullet_rect, 'type': 'enemy2'}  # 敵人子彈類型為 'enemy2'
    bullets.append(bullet)

def shoot_bullet():
    global last_shoot_time
    current_time = pygame.time.get_ticks()  # 取得當前時間
    if current_time - last_shoot_time >= SHOOT_DELAY:  # 檢查射擊間隔（0.4秒）
        mouse_x, mouse_y = pygame.mouse.get_pos()  # 取得滑鼠位置
        dx = mouse_x - (player_x + PLAYER_SIZE // 2)  # 計算相對於玩家的位置
        dy = mouse_y - (player_y + PLAYER_SIZE // 2)
        distance = math.sqrt(dx ** 2 + dy ** 2)  # 計算距離
        dx /= distance  # 正規化方向向量
        dy /= distance

        # 創建玩家的子彈（bullet1）
        bullet = {
            'rect': pygame.Rect(player_x + PLAYER_SIZE // 2 - BULLET_SIZE // 2,
                                player_y + PLAYER_SIZE // 2 - BULLET_SIZE // 2, BULLET_SIZE, BULLET_SIZE),
            'dx': dx,  # 子彈的方向
            'dy': dy   # 子彈的方向
        }
        bullets.append(bullet)  # 將子彈加入子彈列表
        shoot_sound.play()
        last_shoot_time = current_time  # 更新上次射擊時間


# 子彈移動
def move_bullets():
    global bullets
    for bullet in bullets[:]:
        if bullet.get('type') == 'enemy2':  # 檢查是否是敵人子彈（enemy2）
            speed_multiplier = 0.7  # 敵人子彈的速度較慢
        else:
            speed_multiplier = 1  # 玩家子彈的正常速度

        # 根據子彈的方向移動
        bullet['rect'].x += bullet['dx'] * 10 * speed_multiplier
        bullet['rect'].y += bullet['dy'] * 10 * speed_multiplier

        # 移除已經超出螢幕的子彈
        if bullet in bullets and (
            bullet['rect'].x < 0 or 
            bullet['rect'].x > SCREEN_WIDTH or 
            bullet['rect'].y < 0 or 
            bullet['rect'].y > SCREEN_HEIGHT):
            bullets.remove(bullet)

# 設定敵人參數
class Enemy:
    def __init__(self, x, y, image, is_shooter=False):
        self.rect = pygame.Rect(x, y, ENEMY_SIZE, ENEMY_SIZE)
        self.image = image
        self.is_shooter = is_shooter  # 敵人是否為射手
        self.last_shoot_time = 0  # 上次射擊時間

    def shoot(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shoot_time >= SHOOT_DELAY * 3.5:  # 射擊間隔
            dx = player_rect.centerx - self.rect.centerx
            dy = player_rect.centery - self.rect.centery
            distance = math.sqrt(dx ** 2 + dy ** 2)
            if distance != 0:
                dx /= distance
                dy /= distance
            bullet = {
                'rect': pygame.Rect(self.rect.centerx - BULLET_SIZE // 2,
                                    self.rect.centery - BULLET_SIZE // 2,
                                    BULLET_SIZE, BULLET_SIZE),
                'dx': dx * 0.5,  # 敵人子彈的速度較慢
                'dy': dy * 0.5,
                'type': 'enemy2'  # 標註為敵人子彈
            }
            bullets.append(bullet)
            self.last_shoot_time = current_time  # 更新上次射擊時間




# 創建敵人
def create_enemy():
    global enemies

    # 每次最多生成 3 個敵人
    max_new_enemies = min(3, base_enemy_count)  # 取基數與 3 的較小值

    for _ in range(max_new_enemies):  # 循環最多生成 3 個敵人
        edge = random.choice(["top", "bottom", "left", "right"])
        if edge == "top":
            enemy_x = random.randint(0, SCREEN_WIDTH - ENEMY_SIZE)
            enemy_y = 0
        elif edge == "bottom":
            enemy_x = random.randint(0, SCREEN_WIDTH - ENEMY_SIZE)
            enemy_y = SCREEN_HEIGHT - ENEMY_SIZE
        elif edge == "left":
            enemy_x = 0
            enemy_y = random.randint(0, SCREEN_HEIGHT - ENEMY_SIZE)
        elif edge == "right":
            enemy_x = SCREEN_WIDTH - ENEMY_SIZE
            enemy_y = random.randint(0, SCREEN_HEIGHT - ENEMY_SIZE)

        # 隨機選擇生成普通敵人還是射擊敵人
        is_shooter = random.random() < 0.3  # 30%的機率會是射擊敵人
        image = enemy_image if not is_shooter else enemy2_image
        enemies.append(Enemy(enemy_x, enemy_y, image, is_shooter))



# 檢查子彈與敵人的碰撞
def check_bullet_collisions():
    global enemies, bullets, score
    for bullet in bullets[:]:
        if bullet.get('type') == 'enemy2':  # 忽略敵人子彈
            continue

        for enemy in enemies[:]:
            if bullet['rect'].colliderect(enemy.rect):
                hit_sound.play()
                bullets.remove(bullet)
                
                if enemy.is_shooter:
                    score += 2  # 對射擊型敵人給 2 分
                else:
                    score += 1  # 普通敵人加 1 分

                enemies.remove(enemy)
                break

# 敵人移動方向
def move_enemies():
    global enemies, player_rect
    for enemy in enemies[:]:
        # 計算玩家與敵人的中心點
        enemy_center = (enemy.rect.x + ENEMY_SIZE // 2, enemy.rect.y + ENEMY_SIZE // 2)
        player_center = (player_x + PLAYER_SIZE // 2, player_y + PLAYER_SIZE // 2)
        
        # 計算朝向玩家的方向
        direction = (player_center[0] - enemy_center[0], player_center[1] - enemy_center[1])
        length = math.sqrt(direction[0] ** 2 + direction[1] ** 2)
        
        # 避免除以零錯誤
        if length != 0:
            direction = (direction[0] / length, direction[1] / length)
        
        # 設定敵人移動速度，射擊型敵人更慢
        move_speed = 2 if not enemy.is_shooter else 0.5  # 設定射擊型敵人更慢

        # 移動敵人
        enemy.rect.x += direction[0] * move_speed
        enemy.rect.y += direction[1] * move_speed

        # 如果敵人是射擊型敵人，讓它發射子彈
        if enemy.is_shooter:
            enemy.shoot()


# 處理玩家碰撞與扣血
def check_player_collisions():
    global current_health, invincible, invincible_time
    if invincible:
        current_time = pygame.time.get_ticks()
        if current_time - invincible_time > 1000:  # 1秒後無敵時間結束
            invincible = False

    if not invincible:
        # 玩家與敵人碰撞檢查
        for enemy in enemies:
            if player_rect.colliderect(enemy.rect):  # 玩家與敵人碰撞
                current_health -= 10
                damage_sound.play()
                invincible = True
                invincible_time = pygame.time.get_ticks()  # 重置無敵時間
                break  # 只扣一次血

        # 玩家與敵人子彈碰撞檢查
        for bullet in bullets[:]:  # 遍歷所有子彈
            if bullet.get('type') == 'enemy2' and bullet['rect'].colliderect(player_rect):  # 檢查敵人子彈
                current_health -= 10  # 扣血
                bullets.remove(bullet)  # 移除碰撞的子彈
                damage_sound.play()
                invincible = True  # 進入無敵狀態
                invincible_time = pygame.time.get_ticks()  # 重置無敵時間
                break  # 只扣一次血

        # 避免玩家與自己的子彈發生碰撞
        for bullet in bullets[:]:
            if bullet['rect'].colliderect(player_rect) and bullet.get('type') == 'player':  # 排除玩家自己的子彈
                continue  # 跳過與玩家自己的子彈碰撞的檢查

def reset_game():
    global current_health, player_x, player_y, player_rect, bullets, enemies, score, start_time, game_over, base_enemy_count
    current_health = MAX_HEALTH
    player_x, player_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
    player_rect = pygame.Rect(player_x, player_y, PLAYER_SIZE, PLAYER_SIZE)
    bullets = []
    enemies = []
    score = 0
    start_time = pygame.time.get_ticks()
    game_over = False  # 重設遊戲結束狀態
    base_enemy_count = 1  # 重置敵人生成數量基數
    for _ in range(NUM_INITIAL_ENEMIES):  # 重設初始敵人數量
        create_enemy()



# 顯示遊戲畫面
def draw_game():
    screen.fill(LIGHT_YELLOW)  # Set background color

    # Draw player
    if invincible:
        screen.blit(player_invincible_image, player_rect.topleft)  # Show invincible image when in invincible state
    else:
        screen.blit(player_image, player_rect.topleft)  # Show regular player image

    # Draw enemies
    for enemy in enemies:
        screen.blit(enemy.image, enemy.rect.topleft)  # Draw enemies based on their type

    # Display health bar
    health_bar_width = 200
    health_bar_height = 20
    health_bar_x = 10
    health_bar_y = 10
    pygame.draw.rect(screen, WHITE, (health_bar_x, health_bar_y, health_bar_width, health_bar_height))
    pygame.draw.rect(screen, HEALTH_COLOR, (health_bar_x, health_bar_y, (current_health / MAX_HEALTH) * health_bar_width, health_bar_height))

    font = pygame.font.SysFont(None, 30)
    health_text = font.render(f"HP: {current_health}", True, BLACK)
    screen.blit(health_text, (health_bar_x + health_bar_width + 10, health_bar_y))

    # Display score
    score_text = font.render(f"Score: {score}", True, BLACK)
    screen.blit(score_text, (health_bar_x, health_bar_y + health_bar_height + 10))

    # Display timer
    elapsed_time = (pygame.time.get_ticks() - start_time) // 1000
    minutes = elapsed_time // 60
    seconds = elapsed_time % 60
    timer_text = font.render(f"Time: {minutes:02}:{seconds:02}", True, BLACK)
    screen.blit(timer_text, (SCREEN_WIDTH - timer_text.get_width() - 10, 10))

    # Draw bullets
    for bullet in bullets:
        if bullet.get('type') == 'enemy2':  # Check if the bullet is of type 'enemy2'
            screen.blit(bullet2_image, bullet['rect'].topleft)  # Draw enemy2 bullet
        else:
            screen.blit(bullet_image, bullet['rect'].topleft)  # Draw regular player bullet

    pygame.display.flip()



# 顯示遊戲結束畫面
def show_game_over_screen():
    font = pygame.font.Font(None, 80)
    title_text = font.render("Game Over", True, BLACK)
    score_text = font.render(f"Score: {score}", True, BLACK)
    restart_text = font.render("Press R to Restart or Q to Quit", True, BLACK)
    screen.fill(LIGHT_YELLOW)
    screen.blit(
        title_text, 
        (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 4 - title_text.get_height() // 2)
    )
    screen.blit(
        score_text, 
        (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2 - score_text.get_height() // 2)
    )
    screen.blit(
        restart_text, 
        (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT * 3 // 4 - restart_text.get_height() // 2)
    )
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    waiting = False
                    game_loop()  # 重新開始遊戲
                if event.key == pygame.K_q:
                    pygame.quit()
                    exit()


# 主遊戲循環
def game_loop():
    global player_x, player_y, player_rect, bullets, last_enemy_spawn_time, ENEMY_SPAWN_INTERVAL, base_enemy_count, last_increment_time, game_over
    reset_game()

    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        
        if current_health <= 0:
            show_game_over_screen()  # 顯示遊戲結束畫面
            reset_game()  # 重置遊戲
            continue  # 繼續遊戲循環，避免執行後續邏輯

        if current_health > 0:
            # 玩家移動
            if keys[pygame.K_a]:
                player_x -= player_speed
            if keys[pygame.K_d]:
                player_x += player_speed
            if keys[pygame.K_w]:
                player_y -= player_speed
            if keys[pygame.K_s]:
                player_y += player_speed

            if pygame.mouse.get_pressed()[0]:
                shoot_bullet()

            player_rect.x = player_x
            player_rect.y = player_y
            player_rect.clamp_ip(screen.get_rect())

            # 動態調整敵人生成時間間隔與數量
            current_time = pygame.time.get_ticks()
            if current_time - last_enemy_spawn_time >= ENEMY_SPAWN_INTERVAL:
                create_enemy()
                last_enemy_spawn_time = current_time

            if current_time - last_increment_time >= ENEMY_INCREMENT_INTERVAL:
                ENEMY_SPAWN_INTERVAL = max(MIN_ENEMY_SPAWN_INTERVAL, ENEMY_SPAWN_INTERVAL - 100)  # 每5秒減少0.1秒生成間隔時間
                base_enemy_count += 1  # 增加敵人生成數量
                last_increment_time = current_time

            move_bullets()
            check_bullet_collisions()
            move_enemies()
            check_player_collisions()

        draw_game()
        clock.tick(60)

    pygame.quit()

# 顯示主畫面
def show_start_screen():
    # 使用支持中文的字型文件
    font = pygame.font.Font("NotoSansTC-Black.ttf", 80)
    title_text_chinese = font.render("按下空白鍵開始", True, BLACK)
    title_text_english = font.render("Press Space to Start", True, BLACK)
    screen.fill(LIGHT_YELLOW)
    
    # 顯示中文
    screen.blit(
        title_text_chinese, 
        (SCREEN_WIDTH // 2 - title_text_chinese.get_width() // 2, SCREEN_HEIGHT // 2 - title_text_chinese.get_height() - 10)
    )
    
    # 顯示英文
    screen.blit(
        title_text_english, 
        (SCREEN_WIDTH // 2 - title_text_english.get_width() // 2, SCREEN_HEIGHT // 2 + 10)
    )
    
    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                waiting = False


if __name__ == "__main__":
    show_start_screen()
    game_loop()
