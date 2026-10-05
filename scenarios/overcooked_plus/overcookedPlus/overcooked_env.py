import gym
import numpy as np
import copy
from .render.gui import GUI
from gym import spaces
from .items import *
from .constants import *
from .module.map_manager import MapManager
from .module.item_manager import ItemManager
from .module.event_manager import EventManager
from .module.preception_manager import PreceptionManager
from .module.task_manager import TaskManager
from .module.debug_manager import DebugManager


class OvercookedPlus(gym.Env):
    """
    Overcooked Domain Description
    ------------------------------
    Agent with primitive actions ["right", "down", "left", "up"]

    1) Agent is allowed to pick up/put down food/plate on the counter;
    2) Agent is allowed to chop food into pieces if the food is on the cutting board counter;
    3) Agent is allowed to deliver food to the delivery counter;
    4) Only unchopped food is allowed to be chopped;
    """

    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 30}

    def __init__(
        self,
        rewardList,
        n_agent,
        n_task=2,
        map_name="mapC",
        obs_radius=2,
        obs_mode="vector",
        debug=False,
        dynamic_map=None,
        agent_communication=False,
        GUI_enable=False,
        human_player=False,
        min_ing=None,
        max_ing=None,
        check_bug=False,
    ):
        """
        Args:
            rewardList (list): Custom reward function in the format:
                rewardList = {
                    "subtask finished": 10,
                    "correct delivery": 200,
                    "partial delivery": 0,
                    "wrong delivery": -5,
                    "step penalty": -0.1,
                    "burned penalty": -2,
                }
            n_agent (int): The specified number of agents, which cannot exceed the map configuration limit.
            n_task (int, optional): The number of tasks that can be completed simultaneously. Defaults to 2.
            map_name (str, optional): The name of the map configuration file, which exists in the maps/ folder in YAML format. Defaults to "mapC".
            obs_radius (int, optional): Observation radius, 0 for full observability. Defaults to 2.
            obs_mode (str, optional): Observation mode, options are "vector" or "image". Defaults to "vector".
            debug (bool, optional): For development debugging purposes. Defaults to False.
            dynamic_map (bool, optional): Whether to enable dynamic maps (requires support from the map configuration file). Defaults to None.
            max_trials (int, optional): Maximum number of delivery attempts allowed in one game. If ``None`` the
                value will be loaded from the map file.
            agent_communication (bool, optional): Whether to enable communication between agents. Defaults to False.
            GUI (bool, optional): Whether to enable GUI display. Defaults to False.
            human_player (bool, optional): Whether to enable human players. Defaults to False.
            min_ing (int, optional): Minimum ingredients per task. If ``None`` the value
                will be loaded from the map file.
            max_ing (int, optional): Maximum ingredients per task. If ``None`` the value
                will be loaded from the map file.
        
        Returns:
            OvercookedPlus object
        """
        self.rewardList = rewardList
        self.debug = debug
        self.n_agent = n_agent
        self.obs_mode = obs_mode
        self.obs_radius = obs_radius
        self.GUI_enable = GUI_enable
        self.human_player = human_player
        self.n_task = n_task
        self.agent_communication = agent_communication
        self.check_bug = check_bug

        self.env_step = 0
        self.total_return = 0
        self.discount = 1

        self.map_Manager = MapManager(map_name, n_agent, dynamic_map)
        self.ylen, self.xlen = self.map_Manager.dimensions
        self.item_Manager = ItemManager(self.map_Manager)

        map_cfg = self.map_Manager.map_config
        if min_ing is None:
            min_ing = map_cfg.get("min_ing", 1)
        if max_ing is None:
            max_ing = map_cfg.get("max_ing", 4)
        task_pool = map_cfg.get("task_pool")
        self.fixed_task = isinstance(task_pool, list) and len(task_pool) == 1
        self.max_trials = map_cfg.get("max_trials", float("inf"))
        self.cur_trials = 0

        self.task_Manager = TaskManager(
            self.get_step_count,
            self.item_Manager,
            self.n_task,
            self.fixed_task,
            min_ing,
            max_ing,
            task_pool=task_pool,
        )
        self.event_Manager = EventManager(
            self.item_Manager,
            self.map_Manager,
            self.task_Manager,
            rewardList,
        )
        self.GUI = GUI(self, headless=not self.GUI_enable)
        self.preception_Manager = PreceptionManager(
            obs_radius, obs_mode, self.map_Manager, self.item_Manager,
            self.task_Manager, self.GUI, self.agent_communication)

        # 初始化self.debug_manager
        self.debug_manager = DebugManager(self.GUI_enable, self.debug)

        # action: move(up, down, left, right), stay
        self.action_space = spaces.Discrete(5)

        observation = np.asarray(self.get_obs())
        # Vector coordinates and IDs depend on the map and item population;
        # communication values have no declared numeric bounds.
        low, high = (0, 255) if observation.dtype == np.uint8 else (-np.inf, np.inf)
        self.observation_space = spaces.Box(
            low=low, high=high, shape=observation.shape, dtype=observation.dtype)

    def get_obs(self):
        if self.n_agent == 1:
            return self.preception_Manager.get_obs()[0]
        else:
            return self.preception_Manager.get_obs()

    @property
    def state_size(self):
        return self.get_state().shape[0]

    @property
    def obs_size(self):
        return [self.observation_space.shape[0]] * self.n_agent

    @property
    def n_action(self):
        return [a.n for a in self.action_spaces]

    @property
    def action_spaces(self):
        return [self.action_space] * self.n_agent

    @property
    def map(self):
        return self.map_Manager.map

    @property
    def tasks(self):
        return self.task_Manager.tasks

    @property
    def agent(self):
        return self.item_Manager.agent

    def get_step_count(self):
        return self.env_step

    def get_avail_actions(self):
        return [self.get_avail_agent_actions(i) for i in range(self.n_agent)]

    def get_avail_agent_actions(self, nth):
        return [1] * self.action_spaces[nth].n

    def action_space_sample(self, i):
        return np.random.randint(self.action_spaces[i].n)

    def reset(self):
        """
        Returns
        -------
        obs : list
            observation for each agent.
        """
        self.total_return = 0
        self.env_step = 0
        self.discount = 1
        self.map_Manager.reset()
        self.item_Manager.reset()
        self.task_Manager.reset()
        self.preception_Manager.reset()
        self.cur_trials = 0

        if self.GUI_enable:
            self.render()
        return self.get_obs()

    def step(self, action):
        """
        Parameters
        ----------
        action: list
            action for each agent
        Returns
        -------
        obs : list
            observation for each agent.
        rewards : list
            reward for each agent.
        terminate : list
        info : dictionary
        """
        #if isinstance(action, int):
        #    action = [action]

        done = False
        info = {}
        info["cur_mac"] = action
        info["mac_done"] = [True] * self.n_agent
        info["timestep"] = self.env_step
        info["item_log"] = []
        if self.check_bug:
            info["bugs"] = []

        all_action_done = False

        for agent in self.agent:
            agent.moved = False

        # if self.debug:
        #     print("in overcooked primitive actions:", action)

        while not all_action_done:
            item_log, bug_info = self.event_Manager.process_action(action)
            info["item_log"].append(item_log)
            if self.check_bug:
                info["bugs"].extend(bug_info)
            if item_log.get("event_type") == "deliver":
                self.cur_trials += 1
                if self.cur_trials >= self.max_trials:
                    done = True

            all_action_done = True
            for agent in self.agent:
                if agent.moved == False:
                    all_action_done = False

        self.env_step += 1
        self.discount *= 0.99
        reward_list = [agent.reward[-1] for agent in self.agent]
        # Accumulate total return for logging at episode end
        if self.n_agent == 1:
            self.total_return += float(reward_list[0])
        else:
            self.total_return += float(np.sum(reward_list))
        done = True if self.env_step >= 200 else done
        if self.fixed_task:
            done = True if any([
                r == self.rewardList["correct delivery"] for r in reward_list
            ]) else done
        if done:
            episode_info = {
                "r": self.total_return,
                "l": self.env_step,
            }
            info["episode"] = episode_info

        if self.map_Manager.dynamic_map == True:
            self.map_Manager.check_switch_map(self.agent)

        if self.GUI_enable:
            self.render()

        # 更新debug信息
        if self.debug_manager and self.debug_manager.enabled:
            obs = self.get_obs()
            current_obs = obs[0] if isinstance(obs, list) and obs else obs
            self.debug_manager.update_obs(current_obs, self.env_step,
                                          self.item_Manager.itemList,
                                          self.task_Manager.tasks)

        if self.n_agent == 1:
            return self.get_obs(), reward_list[0], done, info
        else:
            return self.get_obs(), reward_list, done, info

    def broadcast(self, message):
        """broadcast message to all agents

        Args:
            message (list): message from each agent, len(message) == len(self.agent)
        """
        if self.agent_communication:
            for i in range(len(message)):
                for j in range(len(self.agent)):
                    if i != j:
                        self.agent[j].comm_log.append(message[j])

    def render(self, mode="human"):
        return self.GUI.on_render()

    def load_state_from_obs(self, obs_vector):
        """Restore environment state based on a full vector observation.

        This utility assumes ``obs_radius`` is 0 so the observation encodes the
        complete game state. Only position and simple status information stored
        in the observation will be restored.
        """
        if self.obs_mode != "vector" or self.obs_radius != 0:
            raise ValueError(
                "load_state_from_obs requires vector observations with"
                " obs_radius=0")

        obs = list(obs_vector)
        idx = 0

        # start from a clean map
        self.map_Manager.map = copy.deepcopy(self.map_Manager.initMap)

        for item in self.item_Manager.itemList:
            x = int(round(obs[idx] * self.xlen))
            idx += 1
            y = int(round(obs[idx] * self.ylen))
            idx += 1

            x = max(0, min(self.xlen - 1, x))
            y = max(0, min(self.ylen - 1, y))

            if isinstance(item, MovableItem):
                item.move(x, y)
            else:
                item.x = x
                item.y = y

            raw = getattr(item, "rawName", None)
            if raw:
                self.map_Manager.set_tile(x, y,
                                          ITEMIDX.get(raw, ITEMIDX["space"]))

            if isinstance(item, Food):
                item.cur_chopped_times = int(
                    round(obs[idx] * item.required_chopped_times))
                idx += 1
            if isinstance(item, Meat):
                item.cur_cooked_times = int(
                    round(obs[idx] * item.required_cooked_times))
                idx += 1

        encodings = []
        n_ing = len(INGLIST)
        while idx + n_ing <= len(obs):
            chunk = obs[idx:idx + n_ing]
            encodings.append([int(round(v)) for v in chunk])
            idx += n_ing

        self.task_Manager.set_tasks_from_encoding(encodings)
        self.preception_Manager.reset()
