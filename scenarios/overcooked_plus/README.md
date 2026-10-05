# Overcooked Plus experiment scenarios

A cooking environment with 37 tasks, configurable maps, interaction events and bug predicates.

## Install and run

Use Python 3.10.14 with tkinter. Install the pinned dependencies from the package directory:

```sh
python -m pip install -r requirements.txt
python -B example.py
python -B example.py --task V2_task_02_lettuce --actions 4 4
```

The example runs headlessly and prints the observation, reward, termination flag, delivery outcome and bug IDs. Its default action sequence delivers an empty plate and reports ID 15.

## Choose a task

Select an ID from `tasks.json`. Each task has a YAML configuration in `overcookedPlus/maps/` defining its layout, ingredients, task pool and delivery-attempt limit. Defaults use one agent, one task and vector observations.

```python
from overcookedPlus.env_creater_new import create_env

env = create_env(task_id="V2_task_01_tomato", check_bug=True,
                 need_Graph=False, disable_env_checker=True)
obs = env.reset()
obs, reward, done, info = env.step(4)
print(obs, reward, done, info["bugs"])
env.close()
```

The Gym interface returns `obs` from reset and `(obs, reward, done, info)` from step. Set `need_Graph=True` to record transitions; access the graph with `env.unwrapped.get_graph()`.

## Actions and observations

Actions are **0 right, 1 down, 2 left, 3 up, 4 wait**. Moving toward an adjacent item can interact with it. Pass an integer or a one-element action list.

Observations are float64 vectors of 190–235 values, depending on the map. They include item coordinates, IDs, states, progress, task encodings and map cells. Values retain their raw scale, with negative sentinels for consumed items; the declared Box is unbounded. Feature construction is in `items.py` and `module/preception_manager.py`.

Rewards are configured in `env_creater_new.py`. An episode ends on fixed-task success, its delivery-attempt limit or 200 steps. Successful delivery is recorded in `info["item_log"][...]["details"]["others"]["success"]`.

Seed sampled actions with `env.action_space.seed(42)`. The fixed-task manager uses Python seed 42 during initialization and reset.

## Bug output and checks

Enable `check_bug=True` to receive predicate IDs in `info["bugs"]`; `info["item_log"]` provides interaction details. Definitions are in `module/bug_manager.py`. IDs describe detected conditions, including action and state checks; interpret each against its predicate. For delivery, ID 13 identifies a dirty plate and ID 15 an empty plate.

```sh
python -B check_runtime.py
python -B test_delivery.py
```

These checks exercise all 37 tasks and replay successful, empty-plate and dirty-plate deliveries. `verified_demonstrations.json` contains six successful action sequences.

## License and attribution

No new license is assigned. Preserve attribution to the author's modified Overcooked Plus and
its upstream projects: https://github.com/BlueLinkX/Overcooked-Plus and
https://github.com/rosewang2008/gym-cooking. Check applicable code/artwork licenses
and the author's permission before external redistribution.
