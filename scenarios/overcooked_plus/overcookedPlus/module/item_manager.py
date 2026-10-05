from ..items import (
    Agent,
    Knife,
    Delivery,
    Tomato,
    Lettuce,
    Onion,
    Fish,
    Rice,
    Oven,
    Cheese,
    Dough,
    Plate,
    Pan,
    Steak,
    Sink,
    RiceCooker,
    TrashCan,
    Block,
    Counter,
    Sushi,
    Pizza,
    RoastFish,
    reset_item_registry,  # 添加重置函数
)
from ..constants import ITEMIDX, AGENTCOLOR


class ItemManager:
    """
    ItemManager class is responsible for managing all items in the environment.
    """

    def __init__(self, map_Manager):
        self.itemList = {}
        self.map_Manager = map_Manager
        self.init_items(self.map_Manager)

    def init_items(self, map_Manager):
        # 重置物品注册表以确保ID一致性
        reset_item_registry()

        map = map_Manager.map
        self.xlen = map_Manager.xlen
        self.ylen = map_Manager.ylen
        self.agent = []
        self.knife = []
        self.delivery = []
        self.tomato = []
        self.lettuce = []
        self.onion = []
        self.fish = []
        self.rice = []
        self.oven = []
        self.cheese = []
        self.dough = []
        self.plate = []
        self.pan = []
        self.steak = []
        self.sink = []
        self.ricecooker = []
        self.trash_can = []
        self.itemList = []
        self.block = []
        self.counter = []
        # 初始化可以被合成的物品，设置为consumed状态
        self.sushi = []
        self.pizza = []
        self.roastfish = []
        agent_idx = 0
        for x in range(self.xlen):
            for y in range(self.ylen):
                if map[x][y] == ITEMIDX["agent"]:
                    self.agent.append(Agent(x, y, color=AGENTCOLOR[agent_idx]))
                    agent_idx += 1
                elif map[x][y] == ITEMIDX["knife"]:
                    self.knife.append(Knife(x, y))
                elif map[x][y] == ITEMIDX["delivery"]:
                    self.delivery.append(Delivery(x, y))
                elif map[x][y] == ITEMIDX["tomato"]:
                    self.tomato.append(Tomato(x, y))
                elif map[x][y] == ITEMIDX["lettuce"]:
                    self.lettuce.append(Lettuce(x, y))
                elif map[x][y] == ITEMIDX["onion"]:
                    self.onion.append(Onion(x, y))
                elif map[x][y] == ITEMIDX["fish"]:
                    self.fish.append(Fish(x, y))
                elif map[x][y] == ITEMIDX["rice"]:
                    self.rice.append(Rice(x, y))
                elif map[x][y] == ITEMIDX["cheese"]:
                    self.cheese.append(Cheese(x, y))
                elif map[x][y] == ITEMIDX["oven"]:
                    self.oven.append(Oven(x, y))
                elif map[x][y] == ITEMIDX["dough"]:
                    self.dough.append(Dough(x, y))
                elif map[x][y] == ITEMIDX["plate"]:
                    self.plate.append(Plate(x, y, item_manager=self))
                elif map[x][y] == ITEMIDX["pan"]:
                    self.pan.append(Pan(x, y))
                elif map[x][y] == ITEMIDX["steak"]:
                    self.steak.append(Steak(x, y))
                elif map[x][y] == ITEMIDX["sink"]:
                    self.sink.append(Sink(x, y))
                elif map[x][y] == ITEMIDX["ricecooker"]:
                    self.ricecooker.append(RiceCooker(x, y))
                elif map[x][y] == ITEMIDX["trash_can"]:
                    self.trash_can.append(TrashCan(x, y))
                elif map[x][y] == ITEMIDX["block"]:
                    self.trash_can.append(Block(x, y))

                if map[x][y] != ITEMIDX["space"] and map[x][y] != ITEMIDX[
                        "block"] and map[x][y] != ITEMIDX["agent"]:
                    self.counter.append(Counter(x, y))

        # 初始化合成物品（即使地图上没有）
        # 这些物品在构造时默认为consumed状态，确保观测系统的一致性
        sushi_item = Sushi(-1, -1)  # 使用虚拟坐标
        self.sushi.append(sushi_item)

        pizza_item = Pizza(-1, -1)  # 使用虚拟坐标
        self.pizza.append(pizza_item)

        roastfish_item = RoastFish(-1, -1)  # 使用虚拟坐标
        self.roastfish.append(roastfish_item)

        self.itemDic = {
            "tomato": self.tomato,
            "lettuce": self.lettuce,
            "onion": self.onion,
            "fish": self.fish,
            "rice": self.rice,
            "cheese": self.cheese,
            "dough": self.dough,
            "oven": self.oven,
            "plate": self.plate,
            "knife": self.knife,
            "delivery": self.delivery,
            "agent": self.agent,
            "pan": self.pan,
            "steak": self.steak,
            "sink": self.sink,
            "ricecooker": self.ricecooker,
            "trash_can": self.trash_can,
            "counter": self.counter,
            "block": self.block,
            # 添加合成物品到字典中
            "sushi": self.sushi,
            "pizza": self.pizza,
            "roastfish": self.roastfish,
        }

        if not self.sink:
            for plate in self.plate:
                plate.dirtyable = False

        if not self.trash_can:
            for steak in self.steak:
                steak.burnable = False

        for key in self.itemDic:
            self.itemList += self.itemDic[key]
        pass

    def findItem(self, x, y, itemName):
        for item in self.itemDic[itemName]:
            if item.x == x and item.y == y:
                return item
        return None

    def get_items_at(self, x, y, counter_block_included=False):
        """返回位于指定格子的所有物品"""
        return [
            item for item in self.itemList if item.x == x and item.y == y and
            (counter_block_included or not isinstance(item, (Counter, Block)))
        ]

    def reset(self):
        self.init_items(self.map_Manager)
        pass
