"""Check every shipped task using bounded ordinary interactions."""
import json
import os
from pathlib import Path
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
import numpy as np
from overcookedPlus.env_creater_new import create_env


def main():
    tasks = json.loads((Path(__file__).parent / "tasks.json").read_text())
    shapes = set()
    for task in tasks:
        env = create_env(task_id=task, check_bug=True, disable_env_checker=True)
        try:
            initial = env.reset().copy()
            assert env.observation_space.contains(initial), task
            shapes.add(initial.shape)
            env.action_space.seed(42)
            for _ in range(10):
                obs, reward, done, info = env.step(int(env.action_space.sample()))
                assert env.observation_space.contains(obs), task
                assert np.isfinite(obs).all() and np.isfinite(reward), task
                if done:
                    env.reset()
            np.testing.assert_array_equal(initial, env.reset(), err_msg=task)
        finally:
            env.close()
    env = create_env(need_Graph=False, disable_env_checker=True)
    try:
        env.reset()
        obs, _, _, _ = env.step(4)
        assert env.observation_space.contains(obs)
    finally:
        env.close()
    print(f"PASS: {len(tasks)} tasks, {len(tasks)*10} steps, reset equality, "
          f"observation spaces {sorted(shapes)}, standard and graph factories")


if __name__ == "__main__":
    main()
