import os
import pygame
import neat
import time
import random
pygame.font.init()

WIN_WIDTH = 500   # Screen width
WIN_HEIGHT = 800    # Screem Height
FLOOR = 730
GEN = 0
BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))]  # Loads all the images of the bird
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))  # Loads base/ground image
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))  # Loads Pipe image
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))     # Loads Background image

STAT_FONT = pygame.font.SysFont("comicssans", 50)
END_FONT = pygame.font.SysFont("comicsans", 70)

WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("Flappy Bird")

class Bird:
    IMGS = BIRD_IMGS    #
    MAX_ROTATION = 25   # max tilt allowed to the bird
    ROT_VEL = 20     
    ANIMATION_TIME = 5  # how many animation per second

    def __init__(self, x, y):
        self.x = x      # The x coordinate of the bird 
        self.y = y      # The y coordinate of the bird
        self.tilt = 0   # The tilt tells the bird tilting 
        self.tick_count = 0  # This stores the last jump
        self.vel = 0    # This tells the velocity of the bird
        self.height = self.y    # This will be used to know where the bird was last time
        self.img_count = 0  # This will be used to change the bird image depeneding on its value
        self.img = self.IMGS[0] # which image of the bird is to be displayed

    def jump(self):
        self.vel = -10.5     # To move the bird up
        self.tick_count = 0 # to reset the bird tick count
        self.height = self.y # stores the bird last height

    def move(self):
        self.tick_count +=1 # incremented with each call
        d = self.vel*self.tick_count + 1.5 * (self.tick_count)**2 # This formula for changing the bird pixel 
        
        if d >= 16: # to keep terminal velocity at 16
            d = 16

        if d < 0: # when bird is going up to move little further up
            d -= 2

        self.y =self.y + d # to move the bird up

        if d < 0  or self.y < self.height + 50: # when the bird is going up
            if self.tilt < self.MAX_ROTATION:   # to directly set the tilt to max rotation
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -90: # when the bird is going down
                self.tilt -=self.ROT_VEL # to make it nose dive

    def draw(self, win):
        self.img_count +=1  # this img count is increased with each call

        if self.img_count <= self.ANIMATION_TIME: # when the count is less than animation time 
            self.img = self.IMGS[0] # wings are down
        elif self.img_count <= self.ANIMATION_TIME*2:    # when the count is less than animation time *2
            self.img = self.IMGS[1] # wings are parallel
        elif self.img_count <= self.ANIMATION_TIME*3:    # when the count is less than animation time *3
            self.img = self.IMGS[2] # wings are up
        elif self.img_count <= self.ANIMATION_TIME*4: # when the count is less than animation time *4
            self.img = self.IMGS[1] # wings are parllel 
        elif self.img_count == self.ANIMATION_TIME*4 + 1:   # when the count is equal to animation time * 4 + 1
            self.img = self.IMGS[0] # wings are down
            self.img_count = 0 # mg count is reseted again

        if self.tilt <= -80:    # if the bird is falling down the image should not change
            self.img = self.IMGS[1] # the image of level wings
            self.img_count = self.ANIMATION_TIME*2  # the count should start from the wings up
        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(center = self.img.get_rect(topleft = (self.x, self.y)).center)
        win.blit(rotated_image , new_rect.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)



class Pipe:
    GAP = 200
    VEL = 5

    def __init__(self, x):
        self.x = x
        self.height = 0

        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG,False,True)
        self.PIPE_BOTTOM = PIPE_IMG

        self.passed = False
        self.set_height()

    def set_height(self):
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.GAP + self.height

    def move (self):
        self.x -= self.VEL
    
    def draw(self,win):
        win.blit(self.PIPE_TOP,(self.x, self.top))
        win.blit(self.PIPE_BOTTOM,(self.x, self.bottom))

    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask,top_offset)

        if  t_point or b_point:
            return True

        return False

class Base:
    VEL = 5
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self,y):
        self.y = y
        self.x1 = 0
        self.x2=self.WIDTH

    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1+ self.WIDTH

    def draw(self,win):
        win.blit(self.IMG, (self.x1,self.y))
        win.blit(self.IMG, (self.x2,self.y))



def draw_window(win, birds, pipes, base, score, gen, pipe_ind):
    if gen == 0:
        gen = 1
    win.blit(BG_IMG, (0, 0))
    for pipe in pipes:
        pipe.draw(win)

    base.draw(win)

    for bird in birds:
        bird.draw(win)

    text = STAT_FONT.render("Score:" +str(score), 1, (255,255,255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))

    score_label = STAT_FONT.render("Gens: " + str(gen-1),1,(255,255,255))
    win.blit(score_label, (10, 10))

    score_label = STAT_FONT.render("Alive: " + str(len(birds)),1,(255,255,255))
    win.blit(score_label, (10, 50))

    pygame.display.update()

def main(genomes, config):
    global WIN,GEN
    win = WIN
    GEN += 1

    nets = []
    ge = []
    birds = []

    for _,g in genomes:
        g.fitness = 0
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Bird(230,350))
        ge.append(g)

    #win = pygame.display.set_mode((WIN_WIDTH,WIN_HEIGHT))
    #bird = Bird(230, 350)
    base = Base(FLOOR)
    pipes = [Pipe(700)]
    clock =  pygame.time.Clock()
    score = 0

    run = True
    while run and len(birds) > 0:
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
                break
        # bird.move()
        pipe_ind = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x +pipes[0].PIPE_TOP.get_width():
                pipe_ind = 1
        else:
            run = False
            break

        for x, bird in enumerate(birds):
            bird.move()
            ge[x].fitness += 0.1

            output = nets[x].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))

            if output[0] > 0.5:
                bird.jump()

        add_pipe = False
        rem = []
        for pipe in pipes:
            for x, bird in enumerate(birds):
                if pipe.collide(bird):
                    ge[x].fitness -=1
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)

                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)
            pipe.move()
        
        if add_pipe:
            score +=1
            for g in ge:
                g.fitness += 5
            pipes.append(Pipe(WIN_WIDTH))

        for r in rem:
            pipes.remove(r)

        for x, bird in enumerate(birds):
            if bird.y + bird.img.get_height()-10 >= FLOOR or bird.y < 0:
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)

        base.move()
        draw_window(WIN, birds, pipes, base, score, GEN, pipe_ind)
    

def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(main, 50)


if __name__ == "__main__":
    #main()
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run(config_path)