from .overcooked_env import OvercookedPlus
import networkx as nx


class OvercookedEnvWithGraph(OvercookedPlus):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # allow multiple edges between the same states so that repeated
        # transitions with different actions are preserved
        self.graph = nx.MultiDiGraph()
        self.seen_nodes = set()
        self.last_obs_id = None
        self.last_action = None

    def reset(self):
        obs = super().reset()
        node_id = tuple(obs)
        # 只在第一次reset时添加起始节点
        if self.last_obs_id is None:
            self.graph.add_node(node_id, info=None)
            self.graph.graph["start_node"] = node_id
            self.graph.graph["end_node"] = []
            self.seen_nodes.add(node_id)
        self.last_obs_id = node_id
        return obs

    def step(self, action):
        obs, reward, done, info = super().step(action)
        node_id = tuple(obs)
        rewards = reward if isinstance(reward, list) else [reward]

        if self.rewardList["correct delivery"] in rewards:
            #print(self.last_obs_id)
            node_id = 'ENDING'
            #self.last_obs_id + (str(action), )
            if node_id not in self.graph.graph["end_node"]:
                self.graph.graph["end_node"].append(node_id)
            if node_id not in self.seen_nodes:
                self.graph.add_node(node_id)
                self.seen_nodes.add(node_id)
        if node_id not in self.seen_nodes:
            self.graph.add_node(node_id)
            self.seen_nodes.add(node_id)
            #print(f"Adding node")
        #else:
        #print(f"Revisiting node")
        primitive_action = action[0] if isinstance(action,
                                                   (list, tuple)) else action
        #确保primitive_action不是int object
        primitive_action = str(primitive_action)

        self.graph.add_edge(self.last_obs_id,
                            node_id,
                            action=primitive_action,
                            info=info)
        self.last_obs_id = node_id
        self.last_action = primitive_action
        return obs, reward, done, info

    def get_graph(self):
        return self.graph

    def has_endpoints(self) -> bool:
        """Return True if the captured graph contains at least one valid end node."""
        end_nodes = self.graph.graph.get("end_node")
        if not end_nodes:
            return False
        if not isinstance(end_nodes, (list, tuple, set)):
            end_nodes = [end_nodes]
        for node in end_nodes:
            if node in self.graph:
                return True
        return False
