import random, time
import pygame
from persistence import save_score

W,H=600,760
ROAD_LEFT,ROAD_RIGHT=90,510
LANES=[140,220,300,380,460]
WHITE=(255,255,255); BLACK=(0,0,0); RED=(220,50,50); BLUE=(50,120,230); GREEN=(40,180,80); YELLOW=(240,210,60); ORANGE=(240,130,30); GRAY=(100,100,100); PURPLE=(150,80,210)
CAR_COLORS={"blue":BLUE,"red":RED,"green":GREEN,"yellow":YELLOW}

class Obj:
    def __init__(self, kind, x, y, speed, color, w=36, h=50):
        self.kind=kind; self.rect=pygame.Rect(x-w//2,y,w,h); self.speed=speed; self.color=color; self.created=time.time()
    def update(self, boost=0): self.rect.y += self.speed + boost
    def draw(self,s): pygame.draw.rect(s,self.color,self.rect,border_radius=7)

class RacerGame:
    def __init__(self, screen, settings, username):
        self.screen=screen; self.settings=settings; self.username=username or 'Player'; self.clock=pygame.time.Clock(); self.font=pygame.font.SysFont('arial',22); self.big=pygame.font.SysFont('arial',38,True)
        self.difficulty={"easy":0.8,"normal":1.0,"hard":1.35}.get(settings.get('difficulty','normal'),1.0)
        self.reset()
    def reset(self):
        self.player=pygame.Rect(W//2-18,H-105,36,58); self.player_speed=7; self.objects=[]; self.coins=0; self.distance=0; self.score=0; self.finish=5000
        self.spawn_timer=0; self.power_timer=0; self.active=None; self.active_until=0; self.shield=False; self.running=True; self.game_over=False
    def safe_x(self):
        choices=[x for x in LANES if abs(x-self.player.centerx)>60]
        return random.choice(choices or LANES)
    def spawn(self):
        density=1+self.distance/1300
        if random.random()<0.55*self.difficulty*density: self.objects.append(Obj('traffic',self.safe_x(),-70,random.randint(4,7),RED))
        if random.random()<0.30*self.difficulty*density: self.objects.append(Obj(random.choice(['barrier','oil','bump']),self.safe_x(),-60,random.randint(3,6),random.choice([GRAY,BLACK,ORANGE]),46,30))
        if random.random()<0.35: self.objects.append(Obj('coin',random.choice(LANES),-35,4,YELLOW,24,24))
        if random.random()<0.12 and not self.active: self.objects.append(Obj(random.choice(['nitro','shield','repair']),random.choice(LANES),-40,4,random.choice([BLUE,PURPLE,GREEN]),30,30))
    def draw_road(self):
        self.screen.fill((30,140,60)); pygame.draw.rect(self.screen,(45,45,45),(ROAD_LEFT,0,ROAD_RIGHT-ROAD_LEFT,H))
        for x in LANES[:-1]:
            for y in range(-60,H,90): pygame.draw.line(self.screen,WHITE,(x+40,y),(x+40,y+45),3)
    def activate(self,kind):
        if kind=='nitro': self.active='Nitro'; self.active_until=time.time()+4
        elif kind=='shield': self.active='Shield'; self.shield=True; self.active_until=0
        elif kind=='repair':
            if self.objects: self.objects=self.objects[1:]
            self.score+=50
    def update(self):
        keys=pygame.key.get_pressed()
        if keys[pygame.K_LEFT]: self.player.x-=self.player_speed
        if keys[pygame.K_RIGHT]: self.player.x+=self.player_speed
        if keys[pygame.K_UP]: self.player.y-=self.player_speed
        if keys[pygame.K_DOWN]: self.player.y+=self.player_speed
        self.player.clamp_ip(pygame.Rect(ROAD_LEFT,0,ROAD_RIGHT-ROAD_LEFT,H))
        now=time.time(); boost=4 if self.active=='Nitro' and now<self.active_until else 0
        if self.active=='Nitro' and now>=self.active_until: self.active=None
        self.distance += 1.2 + boost*0.3; self.score = self.coins*100 + int(self.distance)
        self.spawn_timer+=1
        if self.spawn_timer>max(12,45-int(self.distance/250)):
            self.spawn(); self.spawn_timer=0
        for o in self.objects[:]:
            o.update(boost); 
            if o.kind in ['nitro','shield','repair'] and time.time()-o.created>6: self.objects.remove(o); continue
            if o.rect.top>H: self.objects.remove(o); continue
            if self.player.colliderect(o.rect):
                if o.kind=='coin': self.coins+=1; self.score+=100; self.objects.remove(o)
                elif o.kind in ['nitro','shield','repair']: self.activate(o.kind); self.objects.remove(o)
                elif self.shield: self.shield=False; self.active=None; self.objects.remove(o)
                else: self.end()
        if self.distance>=self.finish: self.end()
    def draw(self):
        self.draw_road()
        for o in self.objects: o.draw(self.screen)
        color=CAR_COLORS.get(self.settings.get('car_color','blue'),BLUE)
        pygame.draw.rect(self.screen,color,self.player,border_radius=8)
        texts=[f"Player: {self.username}",f"Score: {self.score}",f"Coins: {self.coins}",f"Distance: {int(self.distance)}/{self.finish}",f"Power: {self.active or 'None'}"]
        for i,t in enumerate(texts): self.screen.blit(self.font.render(t,True,WHITE),(12,10+i*25))
        if self.shield: self.screen.blit(self.font.render('Shield protects next hit',True,GREEN),(350,15))
    def end(self):
        save_score(self.username,self.score,self.distance,self.coins); self.running=False; self.game_over=True
    def run(self):
        while self.running:
            for e in pygame.event.get():
                if e.type==pygame.QUIT: return 'quit'
                if e.type==pygame.KEYDOWN and e.key==pygame.K_ESCAPE: return 'menu'
            self.update(); self.draw(); pygame.display.flip(); self.clock.tick(60)
        return 'gameover'
