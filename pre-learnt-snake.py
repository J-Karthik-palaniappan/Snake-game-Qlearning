import pygame,random
import numpy as np
pygame.init()
font=pygame.font.SysFont('arial',30)
size=20
class game:
    def __init__(self):
        self.w=600
        self.h=480
        #self.qtab=np.zeros((2**11,3))
        self.qtab=np.load('data.npy')
        self.display=pygame.display.set_mode((self.w,self.h))
        pygame.display.set_caption('snake game')
        self.clock=pygame.time.Clock()
        self.restart()

    def restart(self):
        self.head=(self.w//2,self.h//2)
        self.snake=[self.head]
        self.new_food()
        self.direction=1
        self.score=0
        self.move=0
        
    def new_food(self):
        x=random.randrange(0,self.w-size,size)
        y=random.randrange(0,self.h-size,size)
        self.food=(x,y)
        if self.food in self.snake: self.new_food()

    def new_head(self):
        x=self.head[0]
        y=self.head[1]
        if self.direction==1: y-=size
        elif self.direction==2: x+=size
        elif self.direction==3: y+=size
        else : x-=size
        self.head=(x,y)
        if self.collide(self.head): return 0
        self.snake.insert(0,self.head)
        return 1

    def draw(self):
        for i in self.snake:
            pygame.draw.rect(self.display,'dark blue',pygame.Rect(i[0],i[1],size,size))
            pygame.draw.rect(self.display,'blue',pygame.Rect(i[0]+4,i[1]+4,size-8,size-8))
        pygame.draw.rect(self.display,'red',pygame.Rect(self.food[0],self.food[1],size,size))
        text=font.render("score:"+str(self.score),True,"white")
        self.display.blit(text,(0,0))
        pygame.display.flip()

    def collide(self,head):
        if(head in self.snake): return 1
        elif head[0]<0 or head[0]==self.w or head[1]<0 or head[1]==self.h: return 1
        return 0

    def get_state(self):
        t=self.direction==1
        r=self.direction==2
        d=self.direction==3
        l=self.direction==4
        ht=(self.head[0],self.head[1]-size)
        hr=(self.head[0]+size,self.head[1])
        hd=(self.head[0],self.head[1]+size)
        hl=(self.head[0]-size,self.head[1])
        state=[
            (t and self.collide(ht))or(r and self.collide(hr))or(d and self.collide(hd))or(l and self.collide(hl)), #top danger
            (t and self.collide(hr))or(r and self.collide(hd))or(d and self.collide(hl))or(l and self.collide(ht)), #left danger
            (t and self.collide(hl))or(r and self.collide(ht))or(d and self.collide(hr))or(l and self.collide(hd)), #right danger
            t,r,d,l, #directions
            self.food[1]<self.head[1], #food top
            self.food[0]>self.head[0], #food right
            self.food[1]>self.head[1], #food down
            self.food[0]<self.head[0], #food left
        ]
        n=0
        for ind,val in enumerate(state):
            n+=(2**ind)*val
        return n
    
    def play(self):
        reward=0
        out=0
        if self.new_head():
            if self.head==self.food:
                self.score+=1
                reward+=10
                self.new_food()
            else:
                self.snake.pop()
        else:
            reward-=10
            out=1
        self.display.fill('black')
        self.draw()
        self.clock.tick(20)
        return reward,out

    def change_direction(self,move):
        if move==1:
            if(self.direction!=4): self.direction+=1
            else: self.direction=1
        elif move==2:
            if(self.direction!=1): self.direction-=1
            else: self.direction=4

    def train(self):
        old=self.get_state()
        if random.randint(1,70)>self.move:
            move=random.randint(0,2)
        else:
            move=np.argmax(self.qtab[old,:])
        self.change_direction(move)
        reward,out=self.play()
        new=self.get_state()
        self.qtab[old,move]=0.9*self.qtab[old,move]+0.1*(reward+0.3*np.max(self.qtab[new,:]))
        self.move+=1
        self.save()
        return out

    def save(self):
        np.save("data.npy",self.qtab,allow_pickle=True)

main=game()
itr=0
while(1):
    if main.train() or itr>len(main.snake)*100:
        main.restart()
        itr=0
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            pygame.quit()
            exit()
    itr+=1
       
        
