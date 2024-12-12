from pygame import *
import time as t
import random
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression

init()
font.init()

size = 1200, 800
window = display.set_mode(size)
clock = time.Clock()

ft = font.Font(None, 50)


class GameSprite(sprite.Sprite):
    def __init__(self, img, x, y, width, height):
        super().__init__()
        self.image = transform.scale(image.load(img), (width, height))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.score = 0


    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))


class Birds(GameSprite):
    def __init__(self, img, x, y, width, height):
        super().__init__(img, x, y, width, height)
        self.jump = False
        self.y_vel = 0.2
        self.fall_speed = 4
        self.died = False

    def update(self):

        if self.jump:
            self.rect.y -= 20
            self.jump = False
            self.fall_speed = 4
        else:
            self.rect.y += self.fall_speed
            self.fall_speed += self.y_vel

        if self.rect.y <= 0 or self.rect.y >= size[1]:
            self.died = True

    def fall_bird(self):
        self.rect.y += self.fall_speed
        self.fall_speed += self.y_vel


class Pipe(GameSprite):
    def __init__(self, img, x, y, width, height, reverse=False):
        super().__init__(img, x, y, width, height)
        self.speed = 8
        self.reverse = reverse
        self.passed = False
        if self.reverse:
            self.image = transform.rotate(self.image, 180)

    def update(self):
        self.rect.x -= self.speed
        if self.rect.x <= -50:
            self.kill()
        if self.rect.x <= bird.rect.x and not self.passed:
            self.passed = True
            bird.score += 0.5

        if len(pipes) < 6:
            create_new_pipe()


def new_birds():
    bird = Birds('img/bird.png', 20, 300, 80, 80)
    return bird

pipes = sprite.Group()


def create_new_pipe():
    x = 1500
    for i in range(10):
        y1 = random.randint(100, 400)
        pipe = Pipe('img/pipe.png', x, size[1] - y1, 150, 400)
        pipes.add(pipe)

        y2 = y1 - random.randint(80, 120)
        pipe = Pipe('img/pipe.png', x, 0 - y2, 150, 400, True)
        pipes.add(pipe)
        x += random.randint(500, 700)




score = 0
create_new_pipe()
bird =new_birds()
high_score = 0
'''data = {
    "bird_y":bird.rect.y,
    "bird_x": 100,
    "bird_speed": bird.fall_speed,
    "pipe_gap_y": list(pipes)[0].rect.y - list(pipes)[1].rect.y + 400,  # розрив між трубами
    "bird_to_pipe_gap_y": bird.rect.y - (list(pipes)[0].rect.y + list(pipes)[1].rect.y + 400) / 2,  # положення пташки відносно проміжку

}'''

data = []
def save_data(data):
    df = pd.DataFrame(data)
    df.to_csv('output.csv', index=False)


def train_model(data):
    df = pd.DataFrame(data).fillna(0)
    if len(df) < 2:
        print("Недостатньо даних для навчання.")
        return None

    X = df[["bird_y", "bird_speed", "pipe_gap_y", "bird_to_pipe_gap_y", "pipe_x", "pipe_down_y", "pipe_up_y"]]
    y = df["jump"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.35)
    model = RandomForestClassifier(n_estimators=10)
    model.fit(X_train, y_train)
    return model


model = None
should_jump = False
gen = 1
while True:
    for e in event.get():
        if e.type == QUIT:
            quit()
        if e.type == KEYDOWN:
            if e.key == K_ESCAPE:
                quit()
    window.fill((100, 200, 200))
    bird.reset()
    pipes.draw(window)

    score_text = ft.render('Рахунок: ' + str(bird.score), True, (255, 255, 255))
    window.blit(score_text, (600, 50))


    if bird.died:
        bird.fall_bird()

    display.update()
    clock.tick(60)

    if sprite.spritecollide(bird, pipes, False) and not bird.died:
        bird.died = True
        gen += 1
    if not model and not bird.died:
        if gen <= 1:
            keys = key.get_pressed()
            if keys[K_SPACE]:
                should_jump = True

        data.append({
            "bird_y": bird.rect.y,
            "bird_speed": bird.fall_speed,
            "pipe_gap_y": list(pipes)[0].rect.y - list(pipes)[1].rect.y,

            "bird_to_pipe_gap_y": bird.rect.y - ( (list(pipes)[0].rect.y + list(pipes)[1].rect.y) / 2 ),
            "pipe_x": list(pipes)[0].rect.x,
            "pipe_down_y": list(pipes)[0].rect.y,
            "pipe_up_y": list(pipes)[1].rect.y,
            "jump": int(should_jump)
        })
        bird.jump = should_jump

    if  gen == 2:
        model = train_model(data)



    if model:
        X_input = pd.DataFrame([{
            "bird_y": bird.rect.y,
            "bird_speed": bird.fall_speed,
            "pipe_gap_y": list(pipes)[0].rect.y - list(pipes)[1].rect.y,
            "bird_to_pipe_gap_y": bird.rect.y - (list(pipes)[0].rect.y + list(pipes)[1].rect.y) / 2,
            "pipe_x": list(pipes)[0].rect.x,
            "pipe_down_y": list(pipes)[0].rect.y,
            "pipe_up_y": list(pipes)[1].rect.y,
        }])

        should_jump = model.predict(X_input)[0]
        bird.jump = bool(should_jump)

    bird.update()
    pipes.update()

    if bird.died:
        #save_data(data)
        t.sleep(0.5)
        score = 0
        pipes = sprite.Group()
        create_new_pipe()
        bird = new_birds()
        bird.died = False

    should_jump = False