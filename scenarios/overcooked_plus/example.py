"""Create a scenario, reset, and inspect a short explicit action sequence."""
import argparse
import json
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
from overcookedPlus.env_creater_new import create_env


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task", default="V2_task_01_tomato")
    parser.add_argument("--actions", type=int, nargs="+", default=[0, 0, 3, 1, 2],
                        choices=range(5))
    args = parser.parse_args()
    env = create_env(task_id=args.task, need_Graph=False, check_bug=True,
                     disable_env_checker=True)
    try:
        obs = env.reset()
        print(json.dumps({"task": args.task, "observation_shape": list(obs.shape),
                          "observation_dtype": str(obs.dtype),
                          "observation": obs.tolist()}))
        for step, action in enumerate(args.actions, 1):
            obs, reward, done, info = env.step(action)
            success = any(event.get("event_type") == "deliver" and
                          event.get("details", {}).get("others", {}).get("success") is True
                          for event in info.get("item_log", []))
            print(json.dumps({"step": step, "action": action, "reward": reward,
                              "done": bool(done), "delivery_success": success,
                              "bugs": info.get("bugs", []),
                              "observation_in_space": env.observation_space.contains(obs)}))
            if done:
                break
    finally:
        env.close()


if __name__ == "__main__":
    main()
