import pygame
import sys
import math
from pygame.locals import *

# 初始化Pygame
pygame.init()

# 设置窗口
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('坦克大战')

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

# 坦克类
class Tank:
    def __init__(self, x, y, color, controls):
        self.x = x
        self.y = y
        self.color = color
        self.width = 40
        self.height = 40
        self.speed = 5
        self.angle = 0
        self.controls = controls
        self.bullets = []
        self.health = 100

    def move(self, keys):
        if keys[self.controls['up']]:
            self.y = max(0, self.y - self.speed)
            self.angle = 0
        if keys[self.controls['down']]:
            self.y = min(WINDOW_HEIGHT - self.height, self.y + self.speed)
            self.angle = 180
        if keys[self.controls['left']]:
            self.x = max(0, self.x - self.speed)
            self.angle = 270
        if keys[self.controls['right']]:
            self.x = min(WINDOW_WIDTH - self.width, self.x + self.speed)
            self.angle = 90

    def shoot(self):
        if len(self.bullets) < 3:  # 最多同时发射3颗子弹
            bullet = Bullet(self.x + self.width//2, self.y + self.height//2, self.angle)
            self.bullets.append(bullet)

    def draw(self, surface):
        # 绘制坦克主体
        tank_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, self.color, tank_rect)
        
        # 绘制炮管
        center_x = self.x + self.width//2
        center_y = self.y + self.height//2
        end_x = center_x + 20 * math.cos(math.radians(self.angle))
        end_y = center_y - 20 * math.sin(math.radians(self.angle))
        pygame.draw.line(surface, self.color, (center_x, center_y), (end_x, end_y), 4)

        # 绘制生命值条
        health_width = (self.width * self.health) // 100
        health_rect = pygame.Rect(self.x, self.y - 10, health_width, 5)
        pygame.draw.rect(surface, GREEN, health_rect)

# 子弹类
class Bullet:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.speed = 10
        self.angle = angle
        self.active = True

    def move(self):
        self.x += self.speed * math.cos(math.radians(self.angle))
        self.y -= self.speed * math.sin(math.radians(self.angle))
        
        # 检查是否超出屏幕
        if self.x < 0 or self.x > WINDOW_WIDTH or self.y < 0 or self.y > WINDOW_HEIGHT:
            self.active = False

    def draw(self, surface):
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), 3)

# 创建两个坦克
tank1_controls = {
    'up': K_w,
    'down': K_s,
    'left': K_a,
    'right': K_d,
    'shoot': K_SPACE
}

tank2_controls = {
    'up': K_UP,
    'down': K_DOWN,
    'left': K_LEFT,
    'right': K_RIGHT,
    'shoot': K_RETURN
}

tank1 = Tank(100, 300, BLUE, tank1_controls)
tank2 = Tank(700, 300, RED, tank2_controls)

# 游戏主循环
clock = pygame.time.Clock()
game_over = False

while not game_over:
    # 事件处理
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == KEYDOWN:
            if event.key == tank1_controls['shoot']:
                tank1.shoot()
            elif event.key == tank2_controls['shoot']:
                tank2.shoot()

    # 获取按键状态
    keys = pygame.key.get_pressed()
    
    # 移动坦克
    tank1.move(keys)
    tank2.move(keys)

    # 移动子弹
    for tank in [tank1, tank2]:
        for bullet in tank.bullets[:]:
            bullet.move()
            if not bullet.active:
                tank.bullets.remove(bullet)
                continue

    # 碰撞检测
    for bullet in tank1.bullets[:]:
        if (tank2.x < bullet.x < tank2.x + tank2.width and 
            tank2.y < bullet.y < tank2.y + tank2.height):
            tank2.health -= 10
            bullet.active = False
            tank1.bullets.remove(bullet)

    for bullet in tank2.bullets[:]:
        if (tank1.x < bullet.x < tank1.x + tank1.width and 
            tank1.y < bullet.y < tank1.y + tank1.height):
            tank1.health -= 10
            bullet.active = False
            tank2.bullets.remove(bullet)

    # 检查游戏是否结束
    if tank1.health <= 0 or tank2.health <= 0:
        game_over = True

    # 绘制
    screen.fill(BLACK)
    
    # 绘制坦克和子弹
    tank1.draw(screen)
    tank2.draw(screen)
    
    for tank in [tank1, tank2]:
        for bullet in tank.bullets:
            bullet.draw(screen)

    # 更新显示
    pygame.display.flip()
    clock.tick(60)

# 游戏结束
font = pygame.font.Font(None, 74)
if tank1.health <= 0:
    text = font.render('玩家2获胜！', True, RED)
else:
    text = font.render('玩家1获胜！', True, BLUE)
text_rect = text.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2))
screen.blit(text, text_rect)
pygame.display.flip()

# 等待几秒后退出
pygame.time.wait(3000)
pygame.quit()
sys.exit() 