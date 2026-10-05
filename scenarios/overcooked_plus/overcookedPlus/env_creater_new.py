"""Factory for the task set shipped with this package."""
import json
from pathlib import Path
import gym

rewardList = {
    "subtask finished": 5,
    "correct delivery": 1000,
    "partial delivery": -100,
    "wrong delivery": -500,
    "empty delivery": -1000,
    "step penalty": -1,
    "burned penalty": -10,
    "put_down_and_holding": 20,
}


def create_env(task_id="V2_task_01_tomato", check_bug=False,
               need_Graph=True, **kwargs):
    tasks = json.loads((Path(__file__).parent.parent / "tasks.json").read_text())
    if task_id not in tasks:
        raise ValueError(f"Task not included: {task_id}")
    config = dict(map_name=task_id, dynamic_map=False,
                  rewardList=rewardList.copy(), n_agent=1, n_task=1,
                  agent_communication=False, obs_radius=-1,
                  obs_mode="vector", GUI_enable=False, check_bug=check_bug)
    config.update(kwargs)
    return gym.make("Overcooked-Plus-Graph" if need_Graph else "Overcooked-Plus",
                    **config)
