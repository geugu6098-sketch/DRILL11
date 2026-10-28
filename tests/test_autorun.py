import unittest
from unittest.mock import patch

import boy


class FakeImage:
    def __init__(self):
        self.draw_calls = []

    def clip_draw(self, *args):
        self.draw_calls.append(('clip_draw', args))

    def clip_composite_draw(self, *args):
        self.draw_calls.append(('clip_composite_draw', args))


class AutoRunTests(unittest.TestCase):
    def setUp(self):
        self.clock = 10.0
        self.images = {}

        def load_image(name):
            image = FakeImage()
            self.images[name] = image
            return image

        self.image_patcher = patch('boy.load_image', side_effect=load_image)
        self.image_patcher.start()
        self.addCleanup(self.image_patcher.stop)

        self.clock_patcher = patch(
            'boy.time.monotonic',
            side_effect=lambda: self.clock,
        )
        self.clock_patcher.start()
        self.addCleanup(self.clock_patcher.stop)

        self.boy = boy.Boy()

    def test_auto_run_moves_faster_and_draws_larger(self):
        self.boy.start_auto_run()
        self.clock = 10.5
        self.boy.update()
        self.boy.draw()

        self.assertEqual(self.boy.state, 'AUTORUN')
        self.assertEqual(self.boy.x, 640)
        draw_call = self.images['run_animation.png'].draw_calls[-1]
        self.assertEqual(draw_call[1][-2:], (150.0, 150.0))

    def test_auto_run_reverses_at_both_screen_edges(self):
        self.boy.x = 700
        self.boy.start_auto_run()

        self.clock = 10.2
        self.boy.update()
        self.assertEqual(self.boy.x, 725)
        self.assertEqual(self.boy.face_dir, -1)

        self.clock = 11.6
        self.boy.update()
        self.assertEqual(self.boy.x, 75)
        self.assertEqual(self.boy.face_dir, 1)

    def test_direction_key_cancels_auto_run_into_run(self):
        self.boy.start_auto_run()
        self.boy.press_direction(-1)

        self.assertEqual(self.boy.state, 'RUN')
        self.assertEqual(self.boy.face_dir, -1)

    def test_auto_run_can_start_from_run_and_keeps_facing_direction(self):
        self.boy.press_direction(-1)
        self.boy.request_auto_run()

        self.assertEqual(self.boy.state, 'AUTORUN')
        self.assertEqual(self.boy.face_dir, -1)


if __name__ == '__main__':
    unittest.main()
