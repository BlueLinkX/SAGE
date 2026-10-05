#!/usr/bin/python

import numpy as np
import weakref

# 合成配方表
synthesis_table = [
    [{}, {}],  # 占位符，将在文件末尾填充实际内容
]

# 全局物品注册表：用于跟踪所有物品实例（使用弱引用避免内存泄漏）
_item_registry = weakref.WeakKeyDictionary()
_type_counters = {}
# ID回收池：用于重用已废弃物品的ID
_recycled_ids = {}  # {class_name: [id1, id2, ...]}


def reset_item_registry():
    """重置物品注册表，用于环境重置"""
    global _item_registry, _type_counters, _recycled_ids
    _item_registry.clear()
    _type_counters.clear()
    _recycled_ids.clear()


def recycle_item_id(item):
    """回收物品的实例ID供后续重用"""
    global _recycled_ids
    class_name = item.__class__.__name__
    instance_id = item.instance_id

    if class_name not in _recycled_ids:
        _recycled_ids[class_name] = []

    if instance_id not in _recycled_ids[class_name]:
        _recycled_ids[class_name].append(instance_id)
        # 保持回收池有序，便于重用较小的ID
        _recycled_ids[class_name].sort()


def register_item(item):
    """注册物品实例，分配类型ID和实例ID（优先重用回收的ID）"""
    global _recycled_ids
    class_name = item.__class__.__name__

    # 如果是新类型，分配类型ID
    if class_name not in _type_counters:
        _type_counters[class_name] = {
            'type_id': len(_type_counters) + 1,  # 类型ID从1开始
            'instance_count': 0
        }

    # 优先使用回收的ID
    if class_name in _recycled_ids and _recycled_ids[class_name]:
        instance_id = _recycled_ids[class_name].pop(0)  # 取出最小的回收ID
    else:
        # 没有可回收的ID，分配新的
        _type_counters[class_name]['instance_count'] += 1
        instance_id = _type_counters[class_name]['instance_count']

    # 注册到全局表（使用弱引用，对象作为key）
    _item_registry[item] = {
        'type_id': _type_counters[class_name]['type_id'],
        'instance_id': instance_id,
        'class_name': class_name
    }

    return _type_counters[class_name]['type_id'], instance_id


def get_item_by_encoding(type_id, instance_id):
    """根据类型ID和实例ID查找物品对象"""
    for item, info in _item_registry.items():
        if info['type_id'] == type_id and info['instance_id'] == instance_id:
            return item  # 返回实际的物品对象
    return None


class Item(object):

    def __init__(self, pos_x, pos_y):
        self.x = pos_x
        self.y = pos_y
        # 注册物品并获取类型ID和实例ID
        self.type_id, self.instance_id = register_item(self)
        # 缓存观测结果，避免频繁重复计算
        self._obs_cache = None

    def invalidate_cache(self):
        """标记缓存失效。"""
        self._obs_cache = None

    def _compute_obs_vector(self):
        """实际观测向量的构建函数。子类可覆盖此函数。"""
        if hasattr(self, 'consumed') and self.consumed:
            return [-1.0, -1.0, self.unique_id]
        return [float(self.x) / 10, float(self.y) / 10, self.unique_id]

    def get_obs(self):
        if self._obs_cache is None:
            self._obs_cache = self._compute_obs_vector()
        return self._obs_cache

    @property
    def unique_id(self):
        """获取唯一标识：类型ID * 1000 + 实例ID"""
        raw_id = self.type_id * 100 + self.instance_id
        return raw_id / 1000.0


class MovableItem(Item):

    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y)
        self.initial_x = pos_x
        self.initial_y = pos_y
        # 标记：被哪个盘子包含/是否被合成消耗（用于观测侧去重）
        self.container = None
        self.consumed = False

    def move(self, x, y):
        self.x = x
        self.y = y
        self.invalidate_cache()

    def refresh(self):
        self.x = self.initial_x
        self.y = self.initial_y
        self.container = None
        self.consumed = False
        self.invalidate_cache()

    def _compute_obs_vector(self):
        """可移动物品观测：基础 + 包含状态"""
        if hasattr(self, 'consumed') and self.consumed:
            return [-1.0, -1.0, self.unique_id, -1.0]

        base = super()._compute_obs_vector()

        container_id = 0.0
        if self.container is not None:
            container_id = float(self.container.unique_id)

        return base + [container_id]


class Food(MovableItem):
    # 0 for unchoopped 1 for chopped
    def __init__(self, pos_x, pos_y, chopped=False, cooked=False):
        super().__init__(pos_x, pos_y)
        self.cur_chopped_times = 0
        self.required_chopped_times = 1
        self.cur_cooked_times = 0
        self.required_cooked_times = 0

    def refresh(self):
        super().refresh()
        self.cur_cooked_times = 0
        self.cur_chopped_times = 0
        self.invalidate_cache()

    @property
    def chopped(self):
        return self.cur_chopped_times >= self.required_chopped_times and self.required_chopped_times > 0

    @property
    def cooked(self):
        return self.cur_cooked_times >= self.required_cooked_times and self.required_cooked_times > 0

    @property
    def is_need_chop(self):
        if self.required_chopped_times == 0:
            return False
        else:
            return True

    @property
    def is_need_cook(self):
        if self.required_cooked_times == 0:
            return False
        else:
            return True

    def _compute_obs_vector(self):
        if hasattr(self, 'consumed') and self.consumed:
            return [-1.0, -1.0, self.unique_id, -1.0, -1.0, -1.0]

        base = super()._compute_obs_vector()

        chop_progress = min(
            1.0, (self.cur_chopped_times / max(self.required_chopped_times, 1)
                  if self.required_chopped_times > 0 else 0.0))
        cook_progress = min(
            1.0, (self.cur_cooked_times / max(self.required_cooked_times, 1)
                  if self.required_cooked_times > 0 else 0.0))

        return base + [chop_progress, cook_progress]


class Meat(Food):

    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y)
        self.required_cooked_times = 1
        self.cur_burned_times = 0
        self.required_burned_times = 40
        self.burnable = True  # 默认可烧焦

    def refresh(self):
        super().refresh()
        self.cur_burned_times = 0
        self.invalidate_cache()

    @property
    def burned(self):
        return (self.burnable
                and self.cur_burned_times >= self.required_burned_times
                and self.required_burned_times > 0)

    def _compute_obs_vector(self):
        if hasattr(self, 'consumed') and self.consumed:
            return [-1.0, -1.0, self.unique_id, -1.0, -1.0, -1.0, -1.0]

        base = super()._compute_obs_vector()

        burn_progress = min(
            1.0, (self.cur_burned_times / max(self.required_burned_times, 1)
                  if self.required_burned_times > 0 else 0.0))

        return base + [burn_progress]


class Tomato(Food):

    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y)
        self.rawName = "tomato"

    @property
    def name(self):
        if self.chopped:
            return "ChoppedTomato"
        else:
            return "FreshTomato"


class Lettuce(Food):

    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y)
        self.rawName = "lettuce"

    @property
    def name(self):
        if self.chopped:
            return "ChoppedLettuce"
        else:
            return "FreshLettuce"


class Onion(Food):

    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y)
        self.rawName = "onion"

    @property
    def name(self):
        if self.chopped:
            return "ChoppedOnion"
        else:
            return "FreshOnion"


class Rice(Food):

    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y)
        self.rawName = "rice"
        self.required_cooked_times = 1

    @property
    def name(self):
        if self.cooked:
            return "cookedRice"
        else:
            return "rice"


class Cheese(Food):

    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y)
        self.rawName = "cheese"

    @property
    def name(self):
        return "cheese"


class Dough(Food):

    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y)
        self.rawName = "dough"

    @property
    def name(self):
        return "dough"


class Steak(Meat):

    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y)
        self.rawName = "steak"

    @property
    def name(self):
        if self.burned:
            return "burnedSteak"
        elif self.chopped and self.cooked:
            return "welldoneSteak"
        elif self.chopped:
            return "choppedSteak"
        elif self.cooked:
            return "cookedSteak"
        else:
            return "rawSteak"


class Fish(Food):

    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y)
        self.rawName = "fish"

    @property
    def name(self):
        if self.chopped:
            return "choppedFish"
        else:
            return "fish"


class RoastFish(Food):

    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y)
        self.rawName = "roastfish"
        self.cur_burned_times = 0
        self.required_cooked_times = 1
        self.required_burned_times = 50
        self.burnable = True
        # 合成物品默认为consumed状态，在真正合成时会被激活
        self.consumed = True

    def refresh(self):
        super().refresh()
        # 重置烧焦状态和consumed状态
        self.cur_burned_times = 0
        self.consumed = True

    @property
    def burned(self):
        return (self.burnable
                and self.cur_burned_times >= self.required_burned_times
                and self.required_burned_times > 0)

    @property
    def name(self):
        if self.burned:
            return "burnedroastfish"
        if self.cooked:
            return "cookedroastfish"
        return "roastfish"


class Sushi(Food):

    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y)
        self.rawName = "sushi"
        # 合成物品默认为consumed状态，在真正合成时会被激活
        self.consumed = True

    def refresh(self):
        super().refresh()
        # 重置时回到consumed状态
        self.consumed = True

    @property
    def name(self):
        return "sushi"


class Pizza(Food):

    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y)
        self.rawName = "pizza"
        self.cur_burned_times = 0
        self.required_cooked_times = 1
        self.required_burned_times = 40
        self.burnable = True
        # 合成物品默认为consumed状态，在真正合成时会被激活
        self.consumed = True

    def refresh(self):
        super().refresh()
        # 重置烧焦状态和consumed状态
        self.cur_burned_times = 0
        self.consumed = True
        self.invalidate_cache()

    @property
    def burned(self):
        return (self.burnable
                and self.cur_burned_times >= self.required_burned_times
                and self.required_burned_times > 0)

    @property
    def name(self):
        if self.burned:
            return "burned_pizza"
        if self.cooked:
            return "cooked_pizza"
        else:
            return "pizza"

    def _compute_obs_vector(self):
        return super()._compute_obs_vector()


class FixedItem(Item):

    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y)
        self.holding = None
        self.holdable_list = []
        self.lock = False

    def hold(self, item):
        if item.__class__ in self.holdable_list and not self.holding:
            self.holding = item
            item.move(self.x, self.y)
            self.lock = True
            self.invalidate_cache()
            item.invalidate_cache()
            item.container = self
            return True
        else:
            return False

    def release(self):
        if self.holding:
            item = self.holding
            self.holding = None
            self.invalidate_cache()
            item.invalidate_cache()
            item.container = None
            return item

    def _compute_obs_vector(self):
        if hasattr(self, 'consumed') and self.consumed:
            return [-1.0, -1.0, self.unique_id, -1.0]

        base = super()._compute_obs_vector()

        holding_id = 0.0
        if self.holding is not None:
            holding_id = float(self.holding.unique_id)

        return base + [holding_id]


class Counter(FixedItem):

    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y)
        self.rawName = "counter"

    def hold(self, item):
        # Counter 可以接受任何物品，不受 holdable_list 限制
        self.holding = item
        item.move(self.x, self.y)
        self.lock = True  # 保持与父类一致的锁定行为
        self.invalidate_cache()
        item.invalidate_cache()
        item.container = self
        return True

    @property
    def name(self):
        if self.holding:
            return "counter_with_" + self.holding.name
        else:
            return "counter"


class Block(Counter):

    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y)
        self.rawName = "block"

    def hold(self, item):
        return False

    @property
    def name(self):
        return "block"


class Knife(FixedItem):

    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y)
        self.rawName = "knife"
        self.holdable_list = [Tomato, Onion, Lettuce, Steak, Fish]

    def chop(self):
        if self.holding:
            item = self.holding
            if item.is_need_chop:
                item.cur_chopped_times += 1
                item.invalidate_cache()
                if item.cur_chopped_times >= item.required_chopped_times:
                    # chopping finished; state reflected by property
                    self.lock = False
                    return True

    def hold(self, item):
        if not item.chopped:
            return super().hold(item)
        else:
            return False

    @property
    def name(self):
        return "cutboard"


class Pan(FixedItem):

    def __init__(self, pos_x, pos_y, burned_able=False):
        super().__init__(pos_x, pos_y)
        self.rawName = "pan"
        self.holdable_list = [Steak]
        self.burned_able = burned_able

    def cook(self):
        if self.holding:
            item = self.holding
            self.lock = True
            item.cur_cooked_times += 1
            item.invalidate_cache()
            if item.cur_cooked_times >= item.required_cooked_times:
                # cooking finished; state reflected by property
                self.lock = False
            if self.burned_able and hasattr(item, 'cur_burned_times'):
                item.cur_burned_times += 1
                if item.cur_burned_times >= item.required_burned_times:
                    self.lock = False
            item.invalidate_cache()

    def hold(self, item):
        if not item.cooked and item.chopped:
            return super().hold(item)
        else:
            return False

    @property
    def name(self):
        return "pan"


class RiceCooker(FixedItem):

    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y)
        self.rawName = "ricecooker"
        self.holdable_list = [Rice]
        self.burned_able = False

    def cook(self):
        if self.holding:
            item = self.holding
            self.lock = True
            item.cur_cooked_times += 1
            item.invalidate_cache()
            if item.cur_cooked_times >= item.required_cooked_times:
                # cooking finished; state reflected by property
                self.lock = False

    def hold(self, item):
        if not item.cooked:
            return super().hold(item)
        else:
            return False

    @property
    def name(self):
        return "ricecooker"


class Oven(FixedItem):

    def __init__(self, pos_x, pos_y, burned_able=False):
        super().__init__(pos_x, pos_y)
        self.rawName = "oven"
        # The oven now holds the raw food item directly instead of a plate
        self.holdable_list = [RoastFish, Pizza]
        self.burned_able = burned_able

    def cook(self):
        if self.holding:
            item = self.holding
            self.lock = True
            item.cur_cooked_times += 1
            item.invalidate_cache()
            if item.cur_cooked_times >= item.required_cooked_times:
                # cooking finished; state reflected by property
                self.lock = False
            if self.burned_able and hasattr(item, 'cur_burned_times'):
                item.cur_burned_times += 1

    def hold(self, item):
        if not item.cooked:
            return super().hold(item)
        else:
            return False

    @property
    def name(self):
        return "oven"


class Sink(FixedItem):

    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y)
        self.rawName = "sink"
        self.holdable_list = [Plate]

    def wash(self):
        if self.holding:
            item = self.holding
            if item.dirty:
                item.cur_wash_times += 1
                item.invalidate_cache()
                if item.cur_wash_times >= item.required_wash_times:
                    self.lock = False

    def hold(self, item):
        if item.__class__ in self.holdable_list and not self.holding and item.dirty and not item.containing:
            self.holding = item
            item.move(self.x, self.y)
            self.lock = True
            self.invalidate_cache()
            item.invalidate_cache()
            item.container = self
            return True
        else:
            return False

    @property
    def name(self):
        if self.holding:
            if self.holding.dirty:
                return "sink_with_dirtyplate"
            else:
                return "sink_with_plate"
        else:
            return "sink"


class Delivery(FixedItem):

    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y)
        self.holding = None
        self.rawName = "delivery"
        self.lock = True

    def deliver(self, plate):
        if plate.__class__ == Plate:
            # 在提交前将合成物品重新设置为consumed状态，而不是回收ID
            for item in plate.containing:
                # 如果是合成物品，重新设置为consumed状态
                if item.__class__.__name__ in ['Sushi', 'Pizza', 'RoastFish']:
                    item.consumed = True
                    item.container = None
                    item.move(-1, -1)  # 移到虚拟位置
                else:
                    # 普通物品回收ID
                    recycle_item_id(item)

            # synthesis_origin 中的物品已经被consumed，无需额外处理
            for item in plate.synthesis_origin:
                if not (hasattr(item, 'consumed') and item.consumed):
                    recycle_item_id(item)

            # 回收盘子本身的ID
            recycle_item_id(plate)
            plate.refresh()

    @property
    def name(self):
        return "delivery"


class Plate(MovableItem):

    def __init__(self, pos_x, pos_y, dirtyable=True, item_manager=None):
        super().__init__(pos_x, pos_y)
        self.containing = []
        self.synthesis_origin = []
        self.rawName = "plate"
        self.required_wash_times = 1
        self.cur_wash_times = self.required_wash_times
        self.dirtyable = dirtyable
        self.item_manager = item_manager  # 添加对 ItemManager 的引用

    @property
    def dirty(self):
        return (self.dirtyable
                and self.cur_wash_times < self.required_wash_times)

    def contained(self, item_class):
        """检查盘子是否包含指定类型的物品"""
        for i in self.containing:
            if i.__class__ == item_class:
                return True
        return False

    def try_synthesis(self):
        for sr in synthesis_table:
            if {_i.__class__ for _i in self.containing} == sr[0] and sr[1]:
                self.synthesis_origin.extend(self.containing)
                # 被合成消耗的原料做标记，回收ID，并从盘子内容清空
                for _i in self.synthesis_origin:
                    _i.consumed = True
                    _i.container = None
                    # 回收被消耗物品的ID供重用
                    recycle_item_id(_i)
                    _i.invalidate_cache()
                self.containing.clear()
                self.invalidate_cache()
                # 使用现有的 consumed 实例而不是创建新实例
                for r in sr[1]:
                    existing_item = self._get_consumed_item(r)
                    if existing_item:
                        # 激活现有实例
                        existing_item.consumed = False
                        existing_item.move(self.x, self.y)
                        existing_item.container = self
                        self.containing.append(existing_item)
                        existing_item.invalidate_cache()
                    else:
                        # 如果没有现有实例，创建新的（兜底机制）
                        new_item = r(self.x, self.y)
                        new_item.consumed = False
                        self.containing.append(new_item)

    def _get_consumed_item(self, item_class):
        """从 ItemManager 中获取对应类型的 consumed 实例"""
        if not self.item_manager:
            return None

        class_name = item_class.__name__.lower()
        if class_name in self.item_manager.itemDic:
            for item in self.item_manager.itemDic[class_name]:
                if hasattr(item, 'consumed') and item.consumed:
                    return item
        return None

    def contain(self, item):
        if isinstance(item, Meat) and not item.cooked:
            return False
        if (item.__class__ not in [Cheese, Dough]) and (not item.cooked
                                                        and not item.chopped):
            return False
        if len(self.containing) != 0:
            allow_contain = False
            for sr in synthesis_table:
                now_types = {_i.__class__ for _i in self.containing}
                now_types.add(item.__class__)
                if now_types <= sr[0]:
                    allow_contain = True
            if allow_contain:
                self.containing.append(item)
                # Move the newly contained item onto the plate so it no longer
                # stays at its previous location (e.g. a counter)
                item.move(self.x, self.y)
                item.container = self
                self.try_synthesis()
                item.invalidate_cache()
                self.invalidate_cache()
                return True
            else:
                return False
        else:
            if not self.dirty:
                self.containing.append(item)
                # Newly added item must be moved onto the plate immediately
                # to avoid lingering on the source counter
                item.move(self.x, self.y)
                item.container = self
                item.invalidate_cache()
                self.invalidate_cache()
                return True
            else:
                return False

    def move(self, x, y):
        super().move(x, y)
        if self.containing:
            for item in self.containing:
                item.move(x, y)

    def release(self):
        if self.containing:
            items = self.containing
            self.containing = []
            # 释放时，解除包含关系标记
            for it in items:
                it.container = None
                it.invalidate_cache()
            self.invalidate_cache()
            return items

    def refresh(self):
        super().refresh()
        self.containing = []
        self.synthesis_origin = []
        self.cur_wash_times = 0 if self.dirtyable else self.required_wash_times
        self.invalidate_cache()

    @property
    def name(self):
        if self.dirty:
            return "dirtyPlate"
        else:
            return "plate"

    @property
    def containedName(self):
        dishName = ""
        vegList = [Lettuce, Onion, Tomato, Cheese, Dough, Pizza, RoastFish]
        meatList = [Steak, Fish, Rice, Sushi]

        contained_veg = []
        contained_meat = []
        veg_name = ""
        meat_name = ""

        for item in self.containing:
            if item.__class__ in meatList:
                contained_meat.append(item.name)
            elif item.__class__ in vegList:
                contained_veg.append(item.name)

        veg_name = "-".join(contained_veg)
        meat_name = "-".join(contained_meat)
        dishName = veg_name + "-" + meat_name

        return dishName, veg_name, meat_name

    def _compute_obs_vector(self):
        if hasattr(self, 'consumed') and self.consumed:
            return [
                -1.0, -1.0, self.unique_id, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0
            ]

        base = super()._compute_obs_vector()

        wash_progress = min(
            1.0, (self.cur_wash_times / max(self.required_wash_times, 1)
                  if self.required_wash_times > 0 else 1.0))

        contained_ids = []
        sorted_items = sorted(self.containing[:4], key=lambda x: x.unique_id)
        for item in sorted_items:
            contained_ids.append(float(item.unique_id))
        while len(contained_ids) < 4:
            contained_ids.append(0.0)

        return base + [wash_progress] + contained_ids


class TrashCan(FixedItem):

    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y)
        self.rawName = "trash_can"
        self.lock = True

    def throw(self, item):
        # 回收被丢弃物品的ID
        if hasattr(item, 'containing'):  # 如果是盘子
            for contained_item in item.containing:
                recycle_item_id(contained_item)
            for origin_item in item.synthesis_origin:
                recycle_item_id(origin_item)
        recycle_item_id(item)
        item.refresh()

    @property
    def name(self):
        return "trash_can"


class Agent(MovableItem):

    def __init__(self, pos_x, pos_y, color=None):
        super().__init__(pos_x, pos_y)
        self.holding = None
        self.color = color
        self.moved = False
        self.obs = None
        self.pomap = None
        self.reward = []
        self.rawName = "agent"
        self.comm_log = []
        self.loc_log = []

    def pickup(self, item):
        #如果手中拿的东西是盘子
        if self.holding and isinstance(self.holding, Plate):
            success = self.holding.contain(item)
            if success:
                item.invalidate_cache()
                self.holding.invalidate_cache()
                self.invalidate_cache()
            return success
            #if not success:
            #    return False
            #else:
            #    item.move(self.x, self.y)
            #    return True
        else:
            self.holding = item
            item.move(self.x, self.y)
            item.invalidate_cache()
            item.container = self
            self.invalidate_cache()

            return True

    def putdown(self, x, y):
        item = self.release()
        item.move(x, y)
        return item

    def move(self, x, y):
        self.loc_log.append((self.x, self.y))
        super().move(x, y)
        self.moved = True
        if self.holding:
            self.holding.move(x, y)

    def receive(self, data):
        self.comm_log.append(data)

    def release(self):
        if self.holding:
            item = self.holding
            self.holding = None
            self.invalidate_cache()
            item.invalidate_cache()
            item.container = None
            return item

    def _compute_obs_vector(self):
        base_vector = [float(self.x), float(self.y), self.unique_id]
        holding_info = self.holding.unique_id if self.holding else 0.0
        return base_vector + [holding_info]


# 初始化合成配方表
synthesis_table.clear()
synthesis_table.extend([
    [{Rice, Fish}, {Sushi}],
    [{Dough, Tomato, Cheese}, {Pizza}],
    [{Onion, Lettuce, Fish}, {RoastFish}],
    [{Onion, Lettuce, Tomato, Steak}, {}],
    [{Onion, Lettuce, Tomato, Steak, Fish, Cheese, Rice}, {}],
])

# Reverse lookup table mapping final dish names to required ingredient names
reverse_synthesis_table = {}
for requires, results in synthesis_table:
    base_names = [cls(0, 0).rawName for cls in requires]
    for res_cls in results:
        reverse_synthesis_table[res_cls(0, 0).rawName] = base_names
