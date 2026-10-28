import time

from pico2d import load_image
from transitions import Machine


class AutoRun:
    SPEED = 480
    SCALE = 1.5
    HALF_WIDTH = 75
    FRAME_DURATION = 0.06

    def __init__(self):
        self.last_update_at = 0
        self.frame_started_at = 0

    def enter(self, boy):
        now = time.monotonic()
        boy.frame = 0
        self.last_update_at = now
        self.frame_started_at = now

    def update(self, boy):
        now = time.monotonic()
        elapsed = now - self.last_update_at
        self.last_update_at = now
        boy.x += boy.face_dir * self.SPEED * elapsed

        left_edge = self.HALF_WIDTH
        right_edge = boy.SCREEN_WIDTH - self.HALF_WIDTH
        if boy.x <= left_edge:
            boy.x = left_edge
            boy.face_dir = 1
        elif boy.x >= right_edge:
            boy.x = right_edge
            boy.face_dir = -1

        frame_elapsed = now - self.frame_started_at
        boy.frame = int(frame_elapsed / self.FRAME_DURATION) % 8

    def draw(self, boy):
        flip = '' if boy.face_dir == 1 else 'h'
        boy.run_image.clip_composite_draw(
            boy.frame * 100, 0, 100, 100, 0, flip,
            boy.x, boy.y, 100 * self.SCALE, 100 * self.SCALE,
        )


class Boy:
    SCREEN_WIDTH = 800
    HALF_WIDTH = 50
    RUN_SPEED = 240
    RUN_FRAME_DURATION = 0.08
    SLEEP_HEIGHT_OFFSET = 15

    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.face_dir = 1
        self.held_directions = []
        self.idle_image = load_image('animation_sheet.png')
        self.run_image = load_image('run_animation.png')
        self.auto_run = AutoRun()
        self.idle_started_at = time.monotonic()
        self.last_run_update_at = self.idle_started_at
        self.run_frame_started_at = self.idle_started_at
        self.machine = Machine(
            model=self,
            states=[
                {'name': 'IDLE', 'on_enter': 'reset_idle_timer'},
                'SLEEP',
                {'name': 'RUN', 'on_enter': 'reset_run_animation'},
                {'name': 'AUTORUN', 'on_enter': 'enter_auto_run'},
            ],
            initial='IDLE',
            auto_transitions=False,
            transitions=[
                {'trigger': 'go_to_sleep', 'source': 'IDLE', 'dest': 'SLEEP'},
                {'trigger': 'wake_up', 'source': 'SLEEP', 'dest': 'IDLE'},
                {
                    'trigger': 'start_running',
                    'source': ['IDLE', 'SLEEP'],
                    'dest': 'RUN',
                },
                {
                    'trigger': 'start_auto_run',
                    'source': 'IDLE',
                    'dest': 'AUTORUN',
                },
                {
                    'trigger': 'cancel_auto_run',
                    'source': 'AUTORUN',
                    'dest': 'RUN',
                },
                {'trigger': 'stop_running', 'source': 'RUN', 'dest': 'IDLE'},
            ],
        )

    def update(self):
        if self.state == 'IDLE':
            self.frame = (self.frame + 1) % 8
            if time.monotonic() - self.idle_started_at >= 5:
                self.go_to_sleep()
        elif self.state == 'RUN':
            now = time.monotonic()
            elapsed = now - self.last_run_update_at
            self.last_run_update_at = now
            self.x = max(
                self.HALF_WIDTH,
                min(
                    self.SCREEN_WIDTH - self.HALF_WIDTH,
                    self.x + self.face_dir * self.RUN_SPEED * elapsed,
                ),
            )
            frame_elapsed = now - self.run_frame_started_at
            self.frame = int(frame_elapsed / self.RUN_FRAME_DURATION) % 8
        elif self.state == 'AUTORUN':
            self.auto_run.update(self)

    def reset_idle_timer(self):
        self.idle_started_at = time.monotonic()

    def enter_auto_run(self):
        self.auto_run.enter(self)

    def reset_run_animation(self):
        now = time.monotonic()
        self.frame = 0
        self.last_run_update_at = now
        self.run_frame_started_at = now

    def press_direction(self, direction):
        if self.state not in ('IDLE', 'SLEEP', 'RUN', 'AUTORUN'):
            return
        if direction in self.held_directions:
            self.held_directions.remove(direction)
        self.held_directions.append(direction)
        self.face_dir = direction
        if self.state == 'AUTORUN':
            self.cancel_auto_run()
        elif self.state in ('IDLE', 'SLEEP'):
            self.start_running()

    def release_direction(self, direction):
        if direction not in self.held_directions:
            return
        self.held_directions.remove(direction)
        if self.state != 'RUN':
            return
        if self.held_directions:
            self.face_dir = self.held_directions[-1]
        else:
            self.stop_running()

    def draw(self):
        if self.state == 'AUTORUN':
            self.auto_run.draw(self)
        elif self.state == 'SLEEP':
            row = 300 if self.face_dir == 1 else 200
            self.idle_image.clip_composite_draw(
                self.frame * 100, row, 100, 100, 1.5708, '',
                self.x, self.y - self.SLEEP_HEIGHT_OFFSET, 100, 100,
            )
        elif self.state == 'RUN':
            flip = '' if self.face_dir == 1 else 'h'
            self.run_image.clip_composite_draw(
                self.frame * 100, 0, 100, 100, 0, flip,
                self.x, self.y, 100, 100,
            )
        else:
            row = 300 if self.face_dir == 1 else 200
            self.idle_image.clip_draw(
                self.frame * 100, row, 100, 100, self.x, self.y,
            )
