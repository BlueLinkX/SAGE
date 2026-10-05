import numpy as np
import copy
from ..items import *
from ..constants import *


class PreceptionManager:
    """
    PreceptionManager class - 基于新的items观测向量系统
    完全使用items.get_obs()方法，消除所有旧的观测逻辑
    """

    def __init__(
        self,
        obs_radius,
        obs_mode,
        map_Manager,
        item_Manager,
        task_Manager,
        gui,
        agent_communication,
    ):
        self.obs_radius = obs_radius
        self.obs_mode = obs_mode
        self.map_Manager = map_Manager
        self.gui = gui
        self.xlen = map_Manager.xlen
        self.ylen = map_Manager.ylen
        self.item_Manager = item_Manager
        self.task_Manager = task_Manager
        self.agent_communication = agent_communication

        self._init_obs()

    def _init_obs(self):
        """初始化观测系统"""
        self.itemList = self.item_Manager.itemList
        self.agent = self.item_Manager.agent
        self.n_agent = len(self.agent)

        # 初始化观测 - 不需要设置oneHotTask，因为它现在是property
        self._update_agent_observations()

    def _get_task_encoding(self):
        """获取任务的one-hot编码"""
        # 保持原有的任务编码逻辑
        if hasattr(self.task_Manager, 'oneHotTask'):
            return self.task_Manager.oneHotTask
        else:
            # 如果没有任务信息，返回空列表
            return []

    def _normalize_coordinates(self, item):
        """标准化坐标到[0,1]范围"""
        return item.x / self.xlen, item.y / self.ylen

    def _get_vector_obs(self):
        """获取向量观测状态（排序版本，确保顺序一致性）"""
        state = []

        # 使用新的items观测向量系统，按unique_id排序确保一致性
        for item in self.itemList:
            # 获取物品的观测向量（已包含consumed的特殊标识）
            item_obs = item.get_obs()
            #if isinstance(item, Counter):
            #    continue
            state.extend(item_obs)

        # 增加2个item 约14格的占位符
        state.extend([0] * 14)

        # 添加任务信息
        state.extend(self.oneHotTask)

        #拉直且用最大值100来归一化self.map_Manager.map
        state.extend(v * 0.01 for row in self.map_Manager.map for v in row)

        return [np.array(state)] * self.n_agent

    def _get_image_state(self):
        """获取图像观测状态"""
        return [self.gui.get_image_obs()] * self.n_agent

    def _update_agent_observations(self):
        """更新智能体观测"""
        if self.obs_mode == "vector":
            obs_list = self._get_vector_obs()
        elif self.obs_mode == "image":
            obs_list = self._get_image_state()
        else:
            # 混合模式或其他模式
            obs_list = self._get_vector_obs()

        # 为每个智能体分配观测
        for i, agent in enumerate(self.agent):
            agent.obs = obs_list[i]

    def get_obs(self):
        """
        获取当前观测
        
        Returns
        -------
        obs : list
            observation for each agent.
        """
        # 智能体通信代码，用户可以修改这部分
        comm_list = []
        if self.agent_communication:
            for agent in self.item_Manager.agent:
                if len(agent.comm_log) == 0:
                    comm_list.append([0] * self.n_agent)
                else:
                    comm_list.append(agent.comm_log[-1])
        comm_list = np.array(comm_list)
        comm_list = np.expand_dims(comm_list, axis=1)

        if self.obs_mode == "vector":
            obs = self._get_vector_obs()
        elif self.obs_mode == "image":
            obs = self._get_image_obs()

        # 处理智能体通信
        if self.agent_communication:
            return np.concatenate((obs, comm_list), axis=1)
        else:
            return obs

    def reset(self):
        """重置观测管理器"""
        # 重新初始化
        self._init_obs()

    def _get_image_obs(self):
        """
        生成图像观测
        Returns
        -------
        image_obs : list
            每个智能体的图像观测
        """
        if self.obs_radius <= 0:
            return [self.gui.get_image_obs()] * self.n_agent

        po_obs = []
        frame = self.gui.get_image_obs()
        old_image_width, old_image_height, channels = frame.shape
        new_image_width = int((old_image_width / self.xlen) *
                              (self.xlen + 2 * (self.obs_radius - 1)))
        new_image_height = int((old_image_height / self.ylen) *
                               (self.ylen + 2 * (self.obs_radius - 1)))
        color = (0, 0, 0)
        obs = np.full((new_image_height, new_image_width, channels),
                      color,
                      dtype=np.uint8)

        x_center = (new_image_width - old_image_width) // 2
        y_center = (new_image_height - old_image_height) // 2

        obs[
            x_center:x_center + old_image_width,
            y_center:y_center + old_image_height,
        ] = frame

        for idx, agent in enumerate(self.agent):
            agent_obs = self._get_PO_obs(obs, agent.x, agent.y,
                                         old_image_width, old_image_height)
            po_obs.append(agent_obs)
        return po_obs

    def _get_PO_obs(self, obs, x, y, ori_width, ori_height):
        """计算部分可观测的图像"""
        x1 = (x - 1) * int(ori_width / self.xlen)
        x2 = (x + self.obs_radius * 2) * int(ori_width / self.xlen)
        y1 = (y - 1) * int(ori_height / self.ylen)
        y2 = (y + self.obs_radius * 2) * int(ori_height / self.ylen)
        return obs[x1:x2, y1:y2]

    @property
    def oneHotTask(self):
        """获取任务的独热编码"""
        tasks = self.task_Manager.tasks
        return [code for task in tasks for code in task["task_encoding"]]

    def reset(self):
        """重置感知管理器并返回初始观测"""
        self._init_obs()
        return self.get_obs()
