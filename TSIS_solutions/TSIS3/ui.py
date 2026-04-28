import pygame

WHITE=(255,255,255); BLACK=(0,0,0); GRAY=(210,210,210); DARK=(45,45,55)

class Button:
    def __init__(self, text, rect):
        self.text=text; self.rect=pygame.Rect(rect)
    def draw(self, screen, font):
        mouse=pygame.mouse.get_pos()
        color=(180,210,255) if self.rect.collidepoint(mouse) else GRAY
        pygame.draw.rect(screen,color,self.rect,border_radius=8)
        pygame.draw.rect(screen,BLACK,self.rect,2,border_radius=8)
        surf=font.render(self.text,True,BLACK)
        screen.blit(surf,surf.get_rect(center=self.rect.center))
    def clicked(self,event):
        return event.type==pygame.MOUSEBUTTONDOWN and event.button==1 and self.rect.collidepoint(event.pos)

def draw_text(screen, text, size, pos, color=WHITE, center=True):
    font=pygame.font.SysFont('arial', size, bold=size>=32)
    surf=font.render(text, True, color)
    rect=surf.get_rect(center=pos) if center else surf.get_rect(topleft=pos)
    screen.blit(surf, rect)
