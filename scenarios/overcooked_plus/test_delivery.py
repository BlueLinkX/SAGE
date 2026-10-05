import json
import os
import unittest
from pathlib import Path

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT', '1')

import numpy as np
from overcookedPlus.overcooked_env import OvercookedPlus
from overcookedPlus.env_creater_new import rewardList


def make_env(task='V2_task_01_tomato'):
    return OvercookedPlus(
        rewardList=rewardList.copy(), n_agent=1, n_task=1,
        map_name=task, obs_radius=-1, GUI_enable=False, check_bug=True,
    )


class DeliveryTests(unittest.TestCase):
    def test_normal_deliveries_and_reset(self):
        demos = json.loads((Path(__file__).parent / 'verified_demonstrations.json')
                           .read_text(encoding='utf-8-sig'))
        for demo in demos:
            with self.subTest(task=demo['task']):
                env = make_env(demo['task'])
                try:
                    initial = env.reset().copy()
                    self.assertTrue(env.observation_space.contains(initial))
                    for repeat in range(2):
                        if repeat:
                            np.testing.assert_array_equal(env.reset(), initial)
                        for action in demo['actions']:
                            obs, reward, done, info = env.step([action])
                            self.assertTrue(env.observation_space.contains(obs))
                            self.assertFalse({13, 15}.intersection(info['bugs']))
                        event = info['item_log'][0]
                        self.assertEqual(event['event_type'], 'deliver')
                        self.assertTrue(event['details']['others']['success'])
                        self.assertTrue(done)
                        self.assertEqual(reward, rewardList['correct delivery'])
                        self.assertEqual(env.total_return, demo['return'])
                        self.assertEqual(env.env_step, demo['steps'])
                finally:
                    env.close()

    def test_empty_then_dirty_empty_delivery(self):
        env = make_env()
        try:
            env.reset()
            # Pick up the initial clean empty plate and deliver it.
            for action in [0, 0, 3, 1, 2]:
                _, reward, _, info = env.step([action])
            self.assertEqual(info['bugs'], [15])
            self.assertEqual(reward, rewardList['empty delivery'])
            self.assertFalse(info['item_log'][0]['details']['others']['success'])
            # The delivered plate respawns dirty. Pick it up and deliver again.
            for action in [3, 3, 1, 2]:
                _, reward, _, info = env.step([action])
            self.assertEqual(info['bugs'], [13, 15])
            self.assertEqual(reward, rewardList['empty delivery'])
            self.assertFalse(info['item_log'][0]['details']['others']['success'])
            env.reset()
            self.assertFalse(env.item_Manager.plate[0].dirty)
            for action in [0, 0, 3, 1, 2]:
                _, _, _, info = env.step([action])
            self.assertEqual(info['bugs'], [15])
        finally:
            env.close()


if __name__ == '__main__':
    unittest.main()
