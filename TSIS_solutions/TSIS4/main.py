import pygame
from db import Database
from game import SnakeGame, W, H, load_settings, save_settings, WHITE, BLACK, DARK, GREEN, RED, BLUE

pygame.init()
screen=pygame.display.set_mode((W,H)); pygame.display.set_caption('TSIS4 Snake')
clock=pygame.time.Clock(); font=pygame.font.SysFont('arial',24); big=pygame.font.SysFont('arial',44,True); small=pygame.font.SysFont('arial',19)
db=Database(); username='Player'; last_result=(0,1)

class Button:
    def __init__(self,text,rect): self.text=text; self.rect=pygame.Rect(rect)
    def draw(self):
        color=(170,210,255) if self.rect.collidepoint(pygame.mouse.get_pos()) else (220,220,220)
        pygame.draw.rect(screen,color,self.rect,border_radius=8); pygame.draw.rect(screen,BLACK,self.rect,2,border_radius=8)
        surf=font.render(self.text,True,BLACK); screen.blit(surf,surf.get_rect(center=self.rect.center))
    def clicked(self,e): return e.type==pygame.MOUSEBUTTONDOWN and e.button==1 and self.rect.collidepoint(e.pos)

def text(s,size,pos,color=WHITE,center=True):
    f=big if size>=40 else font if size>=22 else small
    surf=f.render(s,True,color); rect=surf.get_rect(center=pos) if center else surf.get_rect(topleft=pos); screen.blit(surf,rect)

def menu():
    global username
    buttons=[Button('Play',(220,250,200,50)),Button('Leaderboard',(220,315,200,50)),Button('Settings',(220,380,200,50)),Button('Quit',(220,445,200,50))]
    while True:
        screen.fill(DARK); text('TSIS4 Snake',44,(W//2,90)); text('Username: '+username,24,(W//2,170))
        for b in buttons: b.draw()
        text('Type your name, Backspace to edit',19,(W//2,215))
        for e in pygame.event.get():
            if e.type==pygame.QUIT: return 'quit'
            if e.type==pygame.KEYDOWN:
                if e.key==pygame.K_BACKSPACE: username=username[:-1] or 'Player'
                elif e.unicode.isprintable() and len(username)<14:
                    if username=='Player': username=''
                    username+=e.unicode
            for b in buttons:
                if b.clicked(e): return b.text.lower()
        pygame.display.flip(); clock.tick(60)

def leaderboard():
    back=Button('Back',(240,660,160,45))
    while True:
        screen.fill(DARK); text('Leaderboard',44,(W//2,60))
        for i,(name,score,level,date) in enumerate(db.top10(),1):
            text(f'{i}. {name:<12} score:{score:<5} level:{level:<3} {date}',19,(55,105+i*42),WHITE,False)
        back.draw()
        for e in pygame.event.get():
            if e.type==pygame.QUIT: return 'quit'
            if back.clicked(e) or (e.type==pygame.KEYDOWN and e.key==pygame.K_ESCAPE): return 'menu'
        pygame.display.flip(); clock.tick(60)

def settings_screen():
    settings=load_settings(); colors=[[40,200,80],[60,140,240],[230,60,60],[240,210,60]]
    grid=Button('Toggle Grid',(220,225,200,48)); sound=Button('Toggle Sound',(220,290,200,48)); color=Button('Change Color',(220,355,200,48)); back=Button('Save & Back',(220,455,200,48))
    while True:
        screen.fill(DARK); text('Settings',44,(W//2,85)); text(f"Grid:{settings['grid']} Sound:{settings['sound']} Color:{settings['snake_color']}",19,(W//2,160))
        for b in [grid,sound,color,back]: b.draw()
        for e in pygame.event.get():
            if e.type==pygame.QUIT: return 'quit'
            if grid.clicked(e): settings['grid']=not settings.get('grid',True)
            if sound.clicked(e): settings['sound']=not settings.get('sound',True)
            if color.clicked(e): settings['snake_color']=colors[(colors.index(settings.get('snake_color',[40,200,80]))+1)%len(colors)] if settings.get('snake_color',[40,200,80]) in colors else colors[0]
            if back.clicked(e): save_settings(settings); return 'menu'
        pygame.display.flip(); clock.tick(60)

def game_over():
    retry=Button('Retry',(220,330,200,50)); main=Button('Main Menu',(220,395,200,50))
    best=db.personal_best(username)
    while True:
        screen.fill(DARK); text('Game Over',44,(W//2,150)); text(f'Personal best: {best}',24,(W//2,230))
        retry.draw(); main.draw()
        for e in pygame.event.get():
            if e.type==pygame.QUIT: return 'quit'
            if retry.clicked(e): return 'play'
            if main.clicked(e): return 'menu'
        pygame.display.flip(); clock.tick(60)

state='menu'
while state!='quit':
    if state=='menu': state=menu()
    elif state=='play': state=SnakeGame(screen,username,db).run()
    elif state=='leaderboard': state=leaderboard()
    elif state=='settings': state=settings_screen()
    elif state=='gameover': state=game_over()
    else: state='menu'
pygame.quit()
