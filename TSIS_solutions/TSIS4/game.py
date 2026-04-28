import json, random, time
from pathlib import Path
import pygame
from db import Database

W,H=640,720; CELL=20; TOP=80; COLS=W//CELL; ROWS=(H-TOP)//CELL
WHITE=(255,255,255); BLACK=(0,0,0); GREEN=(40,200,80); RED=(230,60,60); DARKRED=(120,0,0); BLUE=(60,140,240); YELLOW=(240,210,60); PURPLE=(160,80,210); GRAY=(80,80,80); DARK=(25,25,35)
BASE=Path(__file__).resolve().parent; SETTINGS_FILE=BASE/'settings.json'
POWER_TYPES=['speed','slow','shield']

def load_settings():
    if not SETTINGS_FILE.exists(): SETTINGS_FILE.write_text(json.dumps({'snake_color':[40,200,80],'grid':True,'sound':True}, indent=2))
    return json.loads(SETTINGS_FILE.read_text())

def save_settings(s): SETTINGS_FILE.write_text(json.dumps(s, indent=2))

class SnakeGame:
    def __init__(self, screen, username, db=None):
        self.screen=screen; self.username=username or 'Player'; self.db=db or Database(); self.clock=pygame.time.Clock(); self.font=pygame.font.SysFont('arial',22); self.big=pygame.font.SysFont('arial',42,True); self.settings=load_settings(); self.best=self.db.personal_best(self.username); self.reset()
    def reset(self):
        self.snake=[(COLS//2, ROWS//2),(COLS//2-1,ROWS//2),(COLS//2-2,ROWS//2)]; self.dir=(1,0); self.next_dir=(1,0); self.score=0; self.level=1; self.eaten=0; self.speed=8; self.obstacles=[]; self.active=None; self.active_until=0; self.shield=False; self.power=None; self.power_spawn_time=0; self.food=None; self.poison=None; self.running=True; self.spawn_food(); self.spawn_poison(); self.spawn_power()
    def rand_empty(self):
        blocked=set(self.snake)|set(self.obstacles)
        while True:
            p=(random.randrange(COLS), random.randrange(ROWS))
            if p not in blocked: return p
    def spawn_food(self):
        self.food={'pos':self.rand_empty(),'value':random.choice([1,2,3]),'born':time.time()}
    def spawn_poison(self): self.poison=self.rand_empty() if random.random()<0.65 else None
    def spawn_power(self): self.power={'pos':self.rand_empty(),'type':random.choice(POWER_TYPES),'born':time.time()} if random.random()<0.5 else None
    def generate_obstacles(self):
        if self.level<3: return
        head=self.snake[0]; self.obstacles=[]
        for _ in range(min(5+self.level,16)):
            p=self.rand_empty()
            if abs(p[0]-head[0])+abs(p[1]-head[1])>4: self.obstacles.append(p)
    def rect(self,p): return pygame.Rect(p[0]*CELL, TOP+p[1]*CELL, CELL, CELL)
    def draw_cell(self,p,c): pygame.draw.rect(self.screen,c,self.rect(p).inflate(-2,-2),border_radius=4)
    def collision(self, head):
        return head[0]<0 or head[0]>=COLS or head[1]<0 or head[1]>=ROWS or head in self.snake[1:] or head in self.obstacles
    def handle_collision(self, head):
        if self.collision(head):
            if self.shield:
                self.shield=False; self.active=None; return False
            return True
        return False
    def update(self):
        if self.next_dir[0]!=-self.dir[0] or self.next_dir[1]!=-self.dir[1]: self.dir=self.next_dir
        head=(self.snake[0][0]+self.dir[0], self.snake[0][1]+self.dir[1])
        if self.handle_collision(head): self.end(); return
        self.snake.insert(0,head); grow=False
        if head==self.food['pos']:
            self.score+=self.food['value']*10; self.eaten+=1; grow=True; self.spawn_food()
            if self.eaten%4==0:
                self.level+=1; self.speed+=1; self.generate_obstacles()
        if self.poison and head==self.poison:
            for _ in range(2):
                if len(self.snake)>1: self.snake.pop()
            if len(self.snake)<=1: self.end(); return
            self.poison=None; self.spawn_poison()
        if self.power and head==self.power['pos']:
            t=self.power['type']; self.power=None; self.active=t
            if t=='shield': self.shield=True; self.active_until=0
            else: self.active_until=time.time()+5
        if not grow and self.running: self.snake.pop()
        if time.time()-self.food['born']>7: self.spawn_food()
        if self.power and time.time()-self.power['born']>8: self.power=None
        if not self.power and random.random()<0.02: self.spawn_power()
        if not self.poison and random.random()<0.01: self.spawn_poison()
        if self.active in ('speed','slow') and time.time()>self.active_until: self.active=None
    def current_speed(self):
        if self.active=='speed': return self.speed+5
        if self.active=='slow': return max(4,self.speed-4)
        return self.speed
    def draw(self):
        self.screen.fill(DARK); pygame.draw.rect(self.screen,(35,35,45),(0,TOP,W,H-TOP))
        if self.settings.get('grid',True):
            for x in range(0,W,CELL): pygame.draw.line(self.screen,(45,45,55),(x,TOP),(x,H))
            for y in range(TOP,H,CELL): pygame.draw.line(self.screen,(45,45,55),(0,y),(W,y))
        self.draw_cell(self.food['pos'], YELLOW)
        if self.poison: self.draw_cell(self.poison,DARKRED)
        if self.power: self.draw_cell(self.power['pos'], {'speed':BLUE,'slow':PURPLE,'shield':GREEN}[self.power['type']])
        for o in self.obstacles: self.draw_cell(o,GRAY)
        color=tuple(self.settings.get('snake_color',[40,200,80]))
        for p in self.snake: self.draw_cell(p,color)
        info=f"{self.username}  Score:{self.score}  Level:{self.level}  Best:{self.best}  Power:{self.active or 'None'}"
        self.screen.blit(self.font.render(info,True,WHITE),(12,18))
    def end(self):
        self.running=False; self.db.save_result(self.username,self.score,self.level)
    def run(self):
        acc=0
        while self.running:
            dt=self.clock.tick(60)/1000; acc+=dt
            for e in pygame.event.get():
                if e.type==pygame.QUIT: return 'quit'
                if e.type==pygame.KEYDOWN:
                    if e.key==pygame.K_ESCAPE: return 'menu'
                    if e.key==pygame.K_UP: self.next_dir=(0,-1)
                    if e.key==pygame.K_DOWN: self.next_dir=(0,1)
                    if e.key==pygame.K_LEFT: self.next_dir=(-1,0)
                    if e.key==pygame.K_RIGHT: self.next_dir=(1,0)
            if acc>=1/self.current_speed(): self.update(); acc=0
            self.draw(); pygame.display.flip()
        return 'gameover'
