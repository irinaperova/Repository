import pygame
from racer import RacerGame, W, H
from persistence import load_settings, save_settings, load_scores
from ui import Button, draw_text, WHITE, BLACK, DARK

pygame.init()
screen=pygame.display.set_mode((W,H)); pygame.display.set_caption('TSIS3 Racer')
clock=pygame.time.Clock(); font=pygame.font.SysFont('arial',24); small=pygame.font.SysFont('arial',20)
settings=load_settings(); username='Player'

def menu():
    global username
    buttons=[Button('Play',(210,250,180,48)),Button('Leaderboard',(210,310,180,48)),Button('Settings',(210,370,180,48)),Button('Quit',(210,430,180,48))]
    entering=True
    while True:
        screen.fill(DARK); draw_text(screen,'TSIS3 Racer',48,(W//2,100)); draw_text(screen,'Type name: '+username,24,(W//2,180))
        for b in buttons: b.draw(screen,font)
        for e in pygame.event.get():
            if e.type==pygame.QUIT: return 'quit'
            if e.type==pygame.KEYDOWN:
                if e.key==pygame.K_BACKSPACE: username=username[:-1] or 'Player'
                elif e.key==pygame.K_RETURN: entering=False
                elif e.unicode.isprintable() and len(username)<12:
                    if username=='Player': username=''
                    username+=e.unicode
            for b in buttons:
                if b.clicked(e): return b.text.lower()
        pygame.display.flip(); clock.tick(60)

def leaderboard():
    back=Button('Back',(220,690,160,45))
    while True:
        screen.fill(DARK); draw_text(screen,'Leaderboard Top 10',38,(W//2,60))
        for i,s in enumerate(load_scores(),1):
            line=f"{i}. {s['name']}  score:{s['score']}  dist:{s['distance']}  coins:{s['coins']}"
            screen.blit(small.render(line,True,WHITE),(80,110+i*42))
        back.draw(screen,font)
        for e in pygame.event.get():
            if e.type==pygame.QUIT: return 'quit'
            if back.clicked(e) or (e.type==pygame.KEYDOWN and e.key==pygame.K_ESCAPE): return 'menu'
        pygame.display.flip(); clock.tick(60)

def settings_screen():
    global settings
    sound=Button('Toggle Sound',(190,210,220,45)); color=Button('Change Car Color',(190,270,220,45)); diff=Button('Difficulty',(190,330,220,45)); back=Button('Save & Back',(190,430,220,45))
    colors=['blue','red','green','yellow']; diffs=['easy','normal','hard']
    while True:
        screen.fill(DARK); draw_text(screen,'Settings',42,(W//2,80))
        draw_text(screen,f"Sound: {settings['sound']}  Color: {settings['car_color']}  Difficulty: {settings['difficulty']}",22,(W//2,150))
        for b in [sound,color,diff,back]: b.draw(screen,font)
        for e in pygame.event.get():
            if e.type==pygame.QUIT: return 'quit'
            if sound.clicked(e): settings['sound']=not settings.get('sound',True)
            if color.clicked(e): settings['car_color']=colors[(colors.index(settings.get('car_color','blue'))+1)%len(colors)]
            if diff.clicked(e): settings['difficulty']=diffs[(diffs.index(settings.get('difficulty','normal'))+1)%len(diffs)]
            if back.clicked(e): save_settings(settings); return 'menu'
        pygame.display.flip(); clock.tick(60)

def game_over():
    retry=Button('Retry',(210,310,180,50)); main=Button('Main Menu',(210,380,180,50))
    while True:
        screen.fill(DARK); draw_text(screen,'Game Over',48,(W//2,170))
        retry.draw(screen,font); main.draw(screen,font)
        for e in pygame.event.get():
            if e.type==pygame.QUIT: return 'quit'
            if retry.clicked(e): return 'play'
            if main.clicked(e): return 'menu'
        pygame.display.flip(); clock.tick(60)

state='menu'
while state!='quit':
    if state=='menu': state=menu()
    elif state=='play': state=RacerGame(screen,settings,username).run()
    elif state=='leaderboard': state=leaderboard()
    elif state=='settings': state=settings_screen()
    elif state=='gameover': state=game_over()
    else: state='menu'
pygame.quit()
