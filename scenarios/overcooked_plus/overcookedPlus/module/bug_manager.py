from ..items import (Meat, Fish, Rice, Sushi, RoastFish, Pizza, Plate, Food,
                     Tomato, Lettuce, Onion, Steak)
from ..constants import ITEMIDX


class BugManager:
    BUG_ADD_WHILE_HOLDING_ONE = 1
    BUG_PLATE_KNIFE_WITH_TWO = 2
    BUG_PLATE_COUNTER_ONE = 3
    BUG_COUNTER_PLATE_ADD_ONE = 4
    BUG_ALL_CUTBOARD_CHOPPED = 5
    BUG_DELIVER_TWO = 6
    BUG_DELIVER_THREE = 7
    BUG_TRASH_PLATE_ITEM_NOT_RESET = 8
    BUG_CHOPPED_MEAT_IN_PLATE = 9
    BUG_FOUR_ITEMS_IN_PLATE = 10
    BUG_RAW_MEAT_ON_NONEMPTY_PLATE = 11
    BUG_PLATE_KNIFE_WITH_MEAT = 12

    BUG_DELIVER_DIRTY_PLATE = 13
    BUG_DELIVER_BURNED_FOOD = 14
    BUG_DELIVER_EMPTY_PLATE = 15
    BUG_COUNTER_DIRTY_PLATE = 16
    BUG_TRASH_CLEAN_PLATE = 17
    BUG_CHOP_ALREADY_CHOPPED = 18
    BUG_USE_KNIFE_WITHOUT_ITEM = 19
    BUG_USE_SINK_WITHOUT_PLATE = 20
    BUG_COOK_AFTER_DONE = 21
    BUG_BURN_FOOD_IGNORED = 22
    BUG_RECHOP_COOKED_FOOD = 23
    BUG_PLATE_BURNED_ITEM = 24
    BUG_ADD_INGREDIENT_AFTER_COOKING = 25
    BUG_DELIVER_PARTIAL_SUSHI = 26
    BUG_INVALID_DELIVERY_TARGET = 27
    BUG_PICKUP_FROM_EMPTY_COUNTER = 28
    BUG_COLLISION_MOVE = 29
    BUG_PLATE_INTO_OVEN_WRONG_DISH = 30
    BUG_DELIVER_MORE_THAN_FOUR = 31
    BUG_PICKUP_BURNED_ITEM = 32
    BUG_PLACE_DIRTY_PLATE_IN_OVEN = 33
    BUG_PUTDOWN_ON_BLOCK = 34
    BUG_SWITCH_MAP_WHILE_OCCUPIED = 35
    BUG_PUTDOWN_PLATE_IN_PAN = 36
    BUG_PUTDOWN_RAW_MEAT_IN_SINK = 37
    BUG_CHOP_COOKED_ITEM = 38
    BUG_WASH_BURNT_FOOD = 39
    BUG_PUTDOWN_OWN_TILE = 40
    BUG_PICKUP_OWN_DROPPED_ITEM_IMMEDIATELY = 41
    BUG_DIRTY_PLATE_PICKUP = 42
    BUG_COUNTER_OVERWRITE = 43
    BUG_CHOPPING_BURNED_MEAT = 44
    BUG_TRASH_BURNED_ITEM_NOT_RESET = 45
    BUG_WASH_CLEAN_PLATE = 46
    BUG_SINK_HOLD_AFTER_CLEAN = 47
    BUG_PLATE_WITH_BURNED_AND_COOKED_ITEMS = 48
    BUG_COUNTER_STACK_MULTIPLE_PLATES = 49
    BUG_PICKUP_WITH_FULL_HANDS = 50

    BUG_PUT_TOMATO_ON_DIRTY_PLATE = 51
    BUG_PUT_LETTUCE_ON_DIRTY_PLATE = 52
    BUG_PUT_ONION_ON_DIRTY_PLATE = 53
    BUG_PUT_STEAK_ON_DIRTY_PLATE = 54
    BUG_PUT_FISH_ON_DIRTY_PLATE = 55

    BUG_PUT_TOMATO_IN_SINK = 56
    BUG_PUT_LETTUCE_IN_SINK = 57
    BUG_PUT_ONION_IN_SINK = 58
    BUG_PUT_STEAK_IN_SINK = 59
    BUG_PUT_FISH_IN_SINK = 60

    BUG_PUT_TOMATO_IN_PAN = 61
    BUG_PUT_LETTUCE_IN_PAN = 62
    BUG_PUT_ONION_IN_PAN = 63
    BUG_PUT_RAW_STEAK_IN_PAN = 64
    BUG_PUT_RAW_FISH_IN_PAN = 65

    #4种食材放在盘子里会出现BUG

    # 深层规则：盘子中恰好1种或恰好2种食材时才能触发的 BUG（各20个）
    # 1-ingredient precondition bugs (66-85)
    BUG_PLATE_ONE_TOMATO_ADD_LETTUCE = 66
    BUG_PLATE_ONE_TOMATO_ADD_ONION = 67
    BUG_PLATE_ONE_TOMATO_ADD_STEAK = 68
    BUG_PLATE_ONE_TOMATO_ADD_FISH = 69
    BUG_PLATE_ONE_LETTUCE_ADD_TOMATO = 70
    BUG_PLATE_ONE_LETTUCE_ADD_ONION = 71
    BUG_PLATE_ONE_LETTUCE_ADD_STEAK = 72
    BUG_PLATE_ONE_ONION_ADD_TOMATO = 73
    BUG_PLATE_ONE_ONION_ADD_LETTUCE = 74
    BUG_PLATE_ONE_RICE_ADD_FISH_RAW = 75
    BUG_PLATE_ONE_RICE_ADD_FISH_CHOPPED = 76
    BUG_PLATE_ONE_STEAK_RAW_ADD_TOMATO = 77
    BUG_PLATE_ONE_STEAK_CHOPPED_ADD_TOMATO = 78
    BUG_PLATE_ONE_FISH_RAW_ADD_TOMATO = 79
    BUG_PLATE_ONE_FISH_CHOPPED_ADD_TOMATO = 80
    BUG_PLATE_ONE_CHOPPED_VEG_ADD_RICE = 81
    BUG_PLATE_ONE_COOKED_MEAT_ADD_LETTUCE = 82
    BUG_PLATE_ONE_COOKED_FISH_ADD_ONION = 83
    BUG_PLATE_ONE_BURNED_ITEM_ADD_ANY = 84
    BUG_PLATE_ONE_ADD_KNIFE_ON_VEG = 85

    # 2-ingredient precondition bugs (86-105)
    BUG_PLATE_TWO_TOMATO_LETTUCE_ADD_ONION = 86
    BUG_PLATE_TWO_TOMATO_ONION_ADD_LETTUCE = 87
    BUG_PLATE_TWO_LETTUCE_ONION_ADD_TOMATO = 88
    BUG_PLATE_TWO_RICE_FISH_RAW_ADD_TOMATO = 89
    BUG_PLATE_TWO_RICE_FISH_CHOPPED_ADD_LETTUCE = 90
    BUG_PLATE_TWO_COOKED_EXISTS_ADD_RAW = 91
    BUG_PLATE_TWO_BURNED_AND_RAW_ADD_COOKED = 92
    BUG_PLATE_TWO_DOUBLE_VEG_ADD_SAME = 93
    BUG_PLATE_TWO_MEAT_VARIANTS_ADD_ONION = 94
    BUG_PLATE_TWO_FISH_VARIANTS_ADD_TOMATO = 95
    BUG_PLATE_TWO_DIRTY_ADD_ANY = 96
    BUG_PLATE_TWO_BOTH_CHOPPED_VEG_ADD_RICE = 97
    BUG_PLATE_TWO_RICE_STEAK_RAW_ADD_LETTUCE = 98
    BUG_PLATE_TWO_RICE_STEAK_COOKED_ADD_TOMATO = 99
    BUG_PLATE_TWO_TOMATO_LETTUCE_ADD_STEAK_RAW = 100
    BUG_PLATE_TWO_TOMATO_LETTUCE_ADD_FISH_RAW = 101
    BUG_PLATE_TWO_ONION_LETTUCE_ADD_TOMATO = 102
    BUG_PLATE_TWO_ONION_TOMATO_ADD_LETTUCE = 103
    BUG_PLATE_TWO_FISH_COOKED_RICE_ADD_ONION = 104
    BUG_PLATE_TWO_ADD_KNIFE = 105

    # 继续补充：各30个（恰好1种/恰好2种食材前提）
    # one-ingredient continued (106-135)
    BUG_PLATE_ONE_TOMATO_ADD_RICE = 106
    BUG_PLATE_ONE_TOMATO_ADD_CHOPPED_ONION = 107
    BUG_PLATE_ONE_LETTUCE_ADD_RICE = 108
    BUG_PLATE_ONE_LETTUCE_ADD_CHOPPED_TOMATO = 109
    BUG_PLATE_ONE_ONION_ADD_RICE = 110
    BUG_PLATE_ONE_ONION_ADD_COOKED_STEAK = 111
    BUG_PLATE_ONE_ONION_ADD_COOKED_FISH = 112
    BUG_PLATE_ONE_RICE_ADD_TOMATO_CHOPPED = 113
    BUG_PLATE_ONE_RICE_ADD_LETTUCE_CHOPPED = 114
    BUG_PLATE_ONE_RICE_ADD_ONION_CHOPPED = 115
    BUG_PLATE_ONE_RICE_ADD_COOKED_STEAK = 116
    BUG_PLATE_ONE_RICE_ADD_COOKED_FISH = 117
    BUG_PLATE_ONE_STEAK_RAW_ADD_LETTUCE = 118
    BUG_PLATE_ONE_STEAK_COOKED_ADD_ONION = 119
    BUG_PLATE_ONE_BURNED_ITEM_WITH_KNIFE = 120
    BUG_PLATE_ONE_FISH_RAW_ADD_RICE = 121
    BUG_PLATE_ONE_FISH_CHOPPED_ADD_RICE = 122
    BUG_PLATE_ONE_FISH_COOKED_ADD_RICE = 123
    BUG_PLATE_ONE_TOMATO_CHOPPED_ADD_RICE = 124
    BUG_PLATE_ONE_LETTUCE_CHOPPED_ADD_RICE = 125
    BUG_PLATE_ONE_ONION_CHOPPED_ADD_RICE = 126
    BUG_PLATE_ONE_VEG_CHOPPED_ADD_COOKED_MEAT = 127
    BUG_PLATE_ONE_VEG_CHOPPED_ADD_COOKED_FISH = 128
    BUG_PLATE_ONE_COOKED_MEAT_ADD_ONION_CHOPPED = 129
    BUG_PLATE_ONE_COOKED_FISH_ADD_TOMATO_CHOPPED = 130
    BUG_PLATE_ONE_MEAT_RAW_ADD_ONION_CHOPPED = 131
    BUG_PLATE_ONE_FISH_RAW_ADD_ONION_CHOPPED = 132
    BUG_PLATE_ONE_TOMATO_ADD_KNIFE = 133
    BUG_PLATE_ONE_LETTUCE_ADD_KNIFE = 134
    BUG_PLATE_ONE_ONION_ADD_KNIFE = 135

    # two-ingredient continued (136-165)
    BUG_PLATE_TWO_TOMATO_RICE_ADD_LETTUCE_CHOPPED = 136
    BUG_PLATE_TWO_LETTUCE_RICE_ADD_TOMATO_CHOPPED = 137
    BUG_PLATE_TWO_ONION_RICE_ADD_LETTUCE_CHOPPED = 138
    BUG_PLATE_TWO_RICE_STEAK_COOKED_ADD_LETTUCE_CHOPPED = 139
    BUG_PLATE_TWO_RICE_FISH_COOKED_ADD_TOMATO_CHOPPED = 140
    BUG_PLATE_TWO_TOMATO_LETTUCE_ADD_RICE = 141
    BUG_PLATE_TWO_TOMATO_ONION_ADD_RICE = 142
    BUG_PLATE_TWO_LETTUCE_ONION_ADD_RICE = 143
    BUG_PLATE_TWO_BOTH_VEG_CHOPPED_ADD_COOKED_FISH = 144
    BUG_PLATE_TWO_BOTH_VEG_CHOPPED_ADD_COOKED_MEAT = 145
    BUG_PLATE_TWO_TOMATO_LETTUCE_WITH_KNIFE = 146
    BUG_PLATE_TWO_TOMATO_ONION_WITH_KNIFE = 147
    BUG_PLATE_TWO_LETTUCE_ONION_WITH_KNIFE = 148
    BUG_PLATE_TWO_VEG_WITH_OVEN = 149
    BUG_PLATE_TWO_VEG_WITH_PAN = 150
    BUG_PLATE_TWO_VEG_WITH_RICECOOKER = 151
    BUG_PLATE_TWO_FISH_RAW_AND_COOKED_ADD_RICE = 152
    BUG_PLATE_TWO_MEAT_MIX_ADD_ONION_CHOPPED = 153
    BUG_PLATE_TWO_RICE_FISH_RAW_WITH_KNIFE = 154
    BUG_PLATE_TWO_BURNED_PRESENT_WITH_KNIFE = 155
    BUG_PLATE_TWO_BOTH_VEG_CHOPPED_ADD_FISH_RAW = 156
    BUG_PLATE_TWO_RICE_TOMATO_ADD_FISH_CHOPPED = 157
    BUG_PLATE_TWO_RICE_LETTUCE_ADD_FISH_CHOPPED = 158
    BUG_PLATE_TWO_RICE_ONION_ADD_FISH_CHOPPED = 159
    BUG_PLATE_TWO_TOMATO_FISH_COOKED_ADD_RICE = 160
    BUG_PLATE_TWO_DUP_VEG_ADD_RICE = 161
    BUG_PLATE_TWO_STEAK_COOKED_MEAT_RAW_ADD_ONION = 162
    BUG_PLATE_TWO_RICE_MEAT_COOKED_ADD_TOMATO_CHOPPED = 163
    BUG_PLATE_TWO_RICE_FISH_COOKED_WITH_OVEN = 164
    BUG_PLATE_TWO_RICE_STEAK_RAW_WITH_PAN = 165

    def __init__(self, item_manager):
        self.item_manager = item_manager
        self._registry = {}
        self._default_rules()

    def _default_rules(self):
        self.register("collision", self.check_collision)
        self.register("pickup_empty", self.check_pickup_from_empty)
        self.register("auto", self.check_auto)

    def register(self, event_type, rule_func):
        self._registry.setdefault(event_type, []).append(rule_func)

    def check(self, event_type, context):
        bugs = []
        for func in self._registry.get(event_type, []):
            result = func(**context) if context else func()
            if isinstance(result, list):
                bugs.extend(result)
            elif result is not None:
                bugs.append(result)
        return {"event_type": event_type, "bug_id": bugs}

    def check_pickup_into_plate(self, plate, target):
        pre_count = len(plate.containing)
        bugs = []
        item = target.holding if hasattr(
            target, "holding") and target.holding else target
        if plate.dirty and isinstance(item, Food):
            if isinstance(item, Tomato):
                bugs.append(self.BUG_PUT_TOMATO_ON_DIRTY_PLATE)
            elif isinstance(item, Lettuce):
                bugs.append(self.BUG_PUT_LETTUCE_ON_DIRTY_PLATE)
            elif isinstance(item, Onion):
                bugs.append(self.BUG_PUT_ONION_ON_DIRTY_PLATE)
            elif isinstance(item, Steak):
                bugs.append(self.BUG_PUT_STEAK_ON_DIRTY_PLATE)
            elif isinstance(item, Fish):
                bugs.append(self.BUG_PUT_FISH_ON_DIRTY_PLATE)
        if pre_count == 1:
            bugs.append(self.BUG_ADD_WHILE_HOLDING_ONE)
        if target.rawName == "knife" and pre_count >= 2:
            bugs.append(self.BUG_PLATE_KNIFE_WITH_TWO)
        if target.rawName == "knife" and isinstance(
                getattr(target, "holding", None), Meat):
            bugs.append(self.BUG_PLATE_KNIFE_WITH_MEAT)
        if pre_count == 3:
            bugs.append(self.BUG_FOUR_ITEMS_IN_PLATE)
        if getattr(item, "burned", False):
            bugs.append(self.BUG_PLATE_BURNED_ITEM)
        if pre_count > 0:
            cooked_exist = any(
                getattr(i, "cooked", False) for i in plate.containing)
            raw_new = not getattr(item, "cooked", False) and not getattr(
                item, "chopped", False)
            if cooked_exist and raw_new:
                bugs.append(self.BUG_ADD_INGREDIENT_AFTER_COOKING)
        has_burned = any(getattr(i, "burned", False) for i in plate.containing)
        has_cooked = any(
            getattr(i, "cooked", False) and not getattr(i, "burned", False)
            for i in plate.containing)
        if has_burned and (getattr(item, "cooked", False)
                           and not getattr(item, "burned", False)):
            bugs.append(self.BUG_PLATE_WITH_BURNED_AND_COOKED_ITEMS)
        if has_cooked and getattr(item, "burned", False):
            bugs.append(self.BUG_PLATE_WITH_BURNED_AND_COOKED_ITEMS)
        # 深层盘子规则（恰好1种/2种食材）
        bugs += self._check_plate_deep_rules(
            plate=plate,
            new_item=item if isinstance(item, Food) else None,
            pre_count=pre_count,
            target_raw=getattr(target, "rawName", None))
        return bugs

    def check_putdown(self, holding, target, pre_count, agent=None):
        bugs = []
        if holding.rawName == "plate" and target.rawName == "counter" and pre_count == 1:
            bugs.append(self.BUG_PLATE_COUNTER_ONE)
        if target.rawName == "plate" and pre_count == 1 and holding.rawName != "plate":
            bugs.append(self.BUG_COUNTER_PLATE_ADD_ONE)
        if target.rawName == "plate" and pre_count == 3:
            bugs.append(self.BUG_FOUR_ITEMS_IN_PLATE)
        # putdown 到盘子时的深层规则
        if target.rawName == "plate" and holding.rawName != "plate":
            bugs += self._check_plate_deep_rules(
                plate=target,
                new_item=holding if isinstance(holding, Food) else None,
                pre_count=pre_count,
                target_raw=None)
        if target.rawName == "plate" and target.dirty and holding.rawName != "plate":
            if isinstance(holding, Tomato):
                bugs.append(self.BUG_PUT_TOMATO_ON_DIRTY_PLATE)
            elif isinstance(holding, Lettuce):
                bugs.append(self.BUG_PUT_LETTUCE_ON_DIRTY_PLATE)
            elif isinstance(holding, Onion):
                bugs.append(self.BUG_PUT_ONION_ON_DIRTY_PLATE)
            elif isinstance(holding, Steak):
                bugs.append(self.BUG_PUT_STEAK_ON_DIRTY_PLATE)
            elif isinstance(holding, Fish):
                bugs.append(self.BUG_PUT_FISH_ON_DIRTY_PLATE)
        if holding.rawName == "plate" and target.rawName == "counter" and holding.dirty:
            bugs.append(self.BUG_COUNTER_DIRTY_PLATE)
        if target.rawName == "delivery" and holding.rawName != "plate":
            bugs.append(self.BUG_INVALID_DELIVERY_TARGET)
        if target.rawName == "oven" and holding.rawName == "plate":
            if holding.dirty:
                bugs.append(self.BUG_PLACE_DIRTY_PLATE_IN_OVEN)
            allow = all(
                isinstance(i, (RoastFish, Pizza)) for i in holding.containing)
            if not allow:
                bugs.append(self.BUG_PLATE_INTO_OVEN_WRONG_DISH)
        if target.rawName == "pan" and holding.rawName == "plate":
            bugs.append(self.BUG_PUTDOWN_PLATE_IN_PAN)
        if target.rawName == "pan" and holding.rawName != "plate":
            if isinstance(holding, Tomato):
                bugs.append(self.BUG_PUT_TOMATO_IN_PAN)
            elif isinstance(holding, Lettuce):
                bugs.append(self.BUG_PUT_LETTUCE_IN_PAN)
            elif isinstance(holding, Onion):
                bugs.append(self.BUG_PUT_ONION_IN_PAN)
            elif isinstance(holding, Steak) and not holding.chopped:
                bugs.append(self.BUG_PUT_RAW_STEAK_IN_PAN)
            elif isinstance(holding,
                            Fish) and not getattr(holding, "chopped", False):
                bugs.append(self.BUG_PUT_RAW_FISH_IN_PAN)
        if target.rawName == "sink" and isinstance(
                holding, Meat) and not holding.chopped and not holding.cooked:
            bugs.append(self.BUG_PUTDOWN_RAW_MEAT_IN_SINK)
        if target.rawName == "sink" and not isinstance(holding, Plate):
            if isinstance(holding, Tomato):
                bugs.append(self.BUG_PUT_TOMATO_IN_SINK)
            elif isinstance(holding, Lettuce):
                bugs.append(self.BUG_PUT_LETTUCE_IN_SINK)
            elif isinstance(holding, Onion):
                bugs.append(self.BUG_PUT_ONION_IN_SINK)
            elif isinstance(holding, Steak):
                bugs.append(self.BUG_PUT_STEAK_IN_SINK)
            elif isinstance(holding, Fish):
                bugs.append(self.BUG_PUT_FISH_IN_SINK)
        if target.rawName == "block":
            bugs.append(self.BUG_PUTDOWN_ON_BLOCK)
        if agent and agent.x == target.x and agent.y == target.y:
            bugs.append(self.BUG_PUTDOWN_OWN_TILE)
        if target.rawName == "counter":
            code = self.item_manager.map_Manager.map[target.x][target.y]
            if code != ITEMIDX["counter"]:
                bugs.append(self.BUG_COUNTER_OVERWRITE)
            if code == ITEMIDX.get("plate", -1):
                bugs.append(self.BUG_COUNTER_STACK_MULTIPLE_PLATES)
        if holding.rawName == "plate":
            has_burned = any(
                getattr(i, "burned", False) for i in holding.containing)
            has_cooked = any(
                getattr(i, "cooked", False)
                and not getattr(i, "burned", False)
                for i in holding.containing)
            if has_burned and has_cooked:
                bugs.append(self.BUG_PLATE_WITH_BURNED_AND_COOKED_ITEMS)
        if target.rawName == "knife" and getattr(holding, "cooked", False):
            bugs.append(self.BUG_RECHOP_COOKED_FOOD)
        return bugs

    def _check_plate_deep_rules(self,
                                plate,
                                new_item,
                                pre_count,
                                target_raw=None):
        """基于盘子中食材数量与组合的深层 Bug 判定。
        仅当 pre_count 恰好为 1 或 2 时，根据已有食材及新加入食材/目标设备触发额外的 BUG。

        参数:
          - plate: 盘子对象
          - new_item: 即将加入盘子的可移动食材(仅限 Food)，若不是食材则为 None
          - pre_count: 当前盘子中已有食材数量
          - target_raw: 目标交互对象的 rawName（如 knife），可为 None
        """
        bugs = []
        items = getattr(plate, "containing", []) or []

        def is_veg(x):
            return isinstance(x, (Tomato, Lettuce, Onion))

        def both_veg_chopped(a, b):
            return is_veg(a) and is_veg(b) and getattr(
                a, "chopped", False) and getattr(b, "chopped", False)

        def any_cooked(lst):
            return any(getattr(i, "cooked", False) for i in lst)

        def any_burned(lst):
            return any(getattr(i, "burned", False) for i in lst)

        if pre_count == 1 and items:
            ex = items[0]
            # 1-ingredient precondition
            if isinstance(ex, Tomato) and isinstance(new_item, Lettuce):
                bugs.append(self.BUG_PLATE_ONE_TOMATO_ADD_LETTUCE)
            if isinstance(ex, Tomato) and isinstance(new_item, Onion):
                bugs.append(self.BUG_PLATE_ONE_TOMATO_ADD_ONION)
            if isinstance(ex, Tomato) and isinstance(new_item, Steak):
                bugs.append(self.BUG_PLATE_ONE_TOMATO_ADD_STEAK)
            if isinstance(ex, Tomato) and isinstance(new_item, Fish):
                bugs.append(self.BUG_PLATE_ONE_TOMATO_ADD_FISH)

            if isinstance(ex, Lettuce) and isinstance(new_item, Tomato):
                bugs.append(self.BUG_PLATE_ONE_LETTUCE_ADD_TOMATO)
            if isinstance(ex, Lettuce) and isinstance(new_item, Onion):
                bugs.append(self.BUG_PLATE_ONE_LETTUCE_ADD_ONION)
            if isinstance(ex, Lettuce) and isinstance(new_item, Steak):
                bugs.append(self.BUG_PLATE_ONE_LETTUCE_ADD_STEAK)

            if isinstance(ex, Onion) and isinstance(new_item, Tomato):
                bugs.append(self.BUG_PLATE_ONE_ONION_ADD_TOMATO)
            if isinstance(ex, Onion) and isinstance(new_item, Lettuce):
                bugs.append(self.BUG_PLATE_ONE_ONION_ADD_LETTUCE)

            if isinstance(ex,
                          Rice) and isinstance(new_item, Fish) and not getattr(
                              new_item, "chopped", False) and not getattr(
                                  new_item, "cooked", False):
                bugs.append(self.BUG_PLATE_ONE_RICE_ADD_FISH_RAW)
            if isinstance(ex, Rice) and isinstance(new_item, Fish) and getattr(
                    new_item, "chopped", False):
                bugs.append(self.BUG_PLATE_ONE_RICE_ADD_FISH_CHOPPED)

            if isinstance(ex, Steak) and not getattr(
                    ex, "chopped", False) and isinstance(new_item, Tomato):
                bugs.append(self.BUG_PLATE_ONE_STEAK_RAW_ADD_TOMATO)
            if isinstance(ex, Steak) and getattr(
                    ex, "chopped", False) and isinstance(new_item, Tomato):
                bugs.append(self.BUG_PLATE_ONE_STEAK_CHOPPED_ADD_TOMATO)

            if isinstance(ex, Fish) and not getattr(
                    ex, "chopped", False) and not getattr(
                        ex, "cooked", False) and isinstance(new_item, Tomato):
                bugs.append(self.BUG_PLATE_ONE_FISH_RAW_ADD_TOMATO)
            if isinstance(ex, Fish) and getattr(
                    ex, "chopped", False) and isinstance(new_item, Tomato):
                bugs.append(self.BUG_PLATE_ONE_FISH_CHOPPED_ADD_TOMATO)

            if is_veg(ex) and getattr(ex, "chopped", False) and isinstance(
                    new_item, Rice):
                bugs.append(self.BUG_PLATE_ONE_CHOPPED_VEG_ADD_RICE)

            if isinstance(ex, (Meat, Steak)) and getattr(
                    ex, "cooked", False) and isinstance(new_item, Lettuce):
                bugs.append(self.BUG_PLATE_ONE_COOKED_MEAT_ADD_LETTUCE)
            if isinstance(ex, Fish) and getattr(
                    ex, "cooked", False) and isinstance(new_item, Onion):
                bugs.append(self.BUG_PLATE_ONE_COOKED_FISH_ADD_ONION)

            if getattr(ex, "burned", False) and isinstance(new_item, Food):
                bugs.append(self.BUG_PLATE_ONE_BURNED_ITEM_ADD_ANY)

            if target_raw == "knife" and is_veg(ex):
                bugs.append(self.BUG_PLATE_ONE_ADD_KNIFE_ON_VEG)
            # Continued one-ingredient rules (106-135)
            if isinstance(ex, Tomato) and isinstance(new_item, Rice):
                bugs.append(self.BUG_PLATE_ONE_TOMATO_ADD_RICE)
            if isinstance(ex, Tomato) and isinstance(
                    new_item, Onion) and getattr(new_item, "chopped", False):
                bugs.append(self.BUG_PLATE_ONE_TOMATO_ADD_CHOPPED_ONION)
            if isinstance(ex, Lettuce) and isinstance(new_item, Rice):
                bugs.append(self.BUG_PLATE_ONE_LETTUCE_ADD_RICE)
            if isinstance(ex, Lettuce) and isinstance(
                    new_item, Tomato) and getattr(new_item, "chopped", False):
                bugs.append(self.BUG_PLATE_ONE_LETTUCE_ADD_CHOPPED_TOMATO)
            if isinstance(ex, Onion) and isinstance(new_item, Rice):
                bugs.append(self.BUG_PLATE_ONE_ONION_ADD_RICE)
            if isinstance(ex, Onion) and isinstance(
                    new_item, Steak) and getattr(new_item, "cooked", False):
                bugs.append(self.BUG_PLATE_ONE_ONION_ADD_COOKED_STEAK)
            if isinstance(ex, Onion) and isinstance(
                    new_item, Fish) and getattr(new_item, "cooked", False):
                bugs.append(self.BUG_PLATE_ONE_ONION_ADD_COOKED_FISH)
            if isinstance(ex, Rice) and isinstance(
                    new_item, Tomato) and getattr(new_item, "chopped", False):
                bugs.append(self.BUG_PLATE_ONE_RICE_ADD_TOMATO_CHOPPED)
            if isinstance(ex, Rice) and isinstance(
                    new_item, Lettuce) and getattr(new_item, "chopped", False):
                bugs.append(self.BUG_PLATE_ONE_RICE_ADD_LETTUCE_CHOPPED)
            if isinstance(ex, Rice) and isinstance(
                    new_item, Onion) and getattr(new_item, "chopped", False):
                bugs.append(self.BUG_PLATE_ONE_RICE_ADD_ONION_CHOPPED)
            if isinstance(ex, Rice) and isinstance(
                    new_item, Steak) and getattr(new_item, "cooked", False):
                bugs.append(self.BUG_PLATE_ONE_RICE_ADD_COOKED_STEAK)
            if isinstance(ex, Rice) and isinstance(new_item, Fish) and getattr(
                    new_item, "cooked", False):
                bugs.append(self.BUG_PLATE_ONE_RICE_ADD_COOKED_FISH)
            if isinstance(ex, Steak) and not getattr(
                    ex, "cooked", False) and isinstance(new_item, Lettuce):
                bugs.append(self.BUG_PLATE_ONE_STEAK_RAW_ADD_LETTUCE)
            if isinstance(ex, Steak) and getattr(
                    ex, "cooked", False) and isinstance(new_item, Onion):
                bugs.append(self.BUG_PLATE_ONE_STEAK_COOKED_ADD_ONION)
            if getattr(ex, "burned", False) and target_raw == "knife":
                bugs.append(self.BUG_PLATE_ONE_BURNED_ITEM_WITH_KNIFE)
            if isinstance(ex, Fish) and not getattr(
                    ex, "chopped", False) and not getattr(
                        ex, "cooked", False) and isinstance(new_item, Rice):
                bugs.append(self.BUG_PLATE_ONE_FISH_RAW_ADD_RICE)
            if isinstance(ex, Fish) and getattr(
                    ex, "chopped", False) and isinstance(new_item, Rice):
                bugs.append(self.BUG_PLATE_ONE_FISH_CHOPPED_ADD_RICE)
            if isinstance(ex, Fish) and getattr(
                    ex, "cooked", False) and isinstance(new_item, Rice):
                bugs.append(self.BUG_PLATE_ONE_FISH_COOKED_ADD_RICE)
            if isinstance(ex, Tomato) and getattr(
                    ex, "chopped", False) and isinstance(new_item, Rice):
                bugs.append(self.BUG_PLATE_ONE_TOMATO_CHOPPED_ADD_RICE)
            if isinstance(ex, Lettuce) and getattr(
                    ex, "chopped", False) and isinstance(new_item, Rice):
                bugs.append(self.BUG_PLATE_ONE_LETTUCE_CHOPPED_ADD_RICE)
            if isinstance(ex, Onion) and getattr(
                    ex, "chopped", False) and isinstance(new_item, Rice):
                bugs.append(self.BUG_PLATE_ONE_ONION_CHOPPED_ADD_RICE)
            if is_veg(ex) and getattr(ex, "chopped", False) and isinstance(
                    new_item,
                (Meat, Steak)) and getattr(new_item, "cooked", False):
                bugs.append(self.BUG_PLATE_ONE_VEG_CHOPPED_ADD_COOKED_MEAT)
            if is_veg(ex) and getattr(ex, "chopped", False) and isinstance(
                    new_item, Fish) and getattr(new_item, "cooked", False):
                bugs.append(self.BUG_PLATE_ONE_VEG_CHOPPED_ADD_COOKED_FISH)
            if isinstance(
                    ex,
                (Meat, Steak)) and getattr(ex, "cooked", False) and isinstance(
                    new_item, Onion) and getattr(new_item, "chopped", False):
                bugs.append(self.BUG_PLATE_ONE_COOKED_MEAT_ADD_ONION_CHOPPED)
            if isinstance(
                    ex, Fish) and getattr(ex, "cooked", False) and isinstance(
                        new_item, Tomato) and getattr(new_item, "chopped",
                                                      False):
                bugs.append(self.BUG_PLATE_ONE_COOKED_FISH_ADD_TOMATO_CHOPPED)
            if isinstance(
                    ex,
                (Meat,
                 Steak)) and not getattr(ex, "cooked", False) and isinstance(
                     new_item, Onion) and getattr(new_item, "chopped", False):
                bugs.append(self.BUG_PLATE_ONE_MEAT_RAW_ADD_ONION_CHOPPED)
            if isinstance(
                    ex,
                    Fish) and not getattr(ex, "cooked", False) and isinstance(
                        new_item, Onion) and getattr(new_item, "chopped",
                                                     False):
                bugs.append(self.BUG_PLATE_ONE_FISH_RAW_ADD_ONION_CHOPPED)
            if isinstance(ex, Tomato) and target_raw == "knife":
                bugs.append(self.BUG_PLATE_ONE_TOMATO_ADD_KNIFE)
            if isinstance(ex, Lettuce) and target_raw == "knife":
                bugs.append(self.BUG_PLATE_ONE_LETTUCE_ADD_KNIFE)
            if isinstance(ex, Onion) and target_raw == "knife":
                bugs.append(self.BUG_PLATE_ONE_ONION_ADD_KNIFE)

        elif pre_count == 2 and len(items) >= 2:
            a, b = items[0], items[1]
            # helper flags/sets
            types = {type(a), type(b)}
            is_tom_lett = (Tomato in types and Lettuce in types)
            is_tom_onion = (Tomato in types and Onion in types)
            is_lett_onion = (Lettuce in types and Onion in types)
            has_rice = isinstance(a, Rice) or isinstance(b, Rice)
            has_fish = isinstance(a, Fish) or isinstance(b, Fish)
            both_fish = isinstance(a, Fish) and isinstance(b, Fish)
            both_meatlike = isinstance(a, (Meat, Steak)) and isinstance(
                b, (Meat, Steak))

            # 2-ingredient precondition
            if is_tom_lett and isinstance(new_item, Onion):
                bugs.append(self.BUG_PLATE_TWO_TOMATO_LETTUCE_ADD_ONION)
            if is_tom_onion and isinstance(new_item, Lettuce):
                bugs.append(self.BUG_PLATE_TWO_TOMATO_ONION_ADD_LETTUCE)
            if is_lett_onion and isinstance(new_item, Tomato):
                bugs.append(self.BUG_PLATE_TWO_LETTUCE_ONION_ADD_TOMATO)

            if has_rice and has_fish and isinstance(new_item, Tomato):
                # 区分鱼状态
                if (isinstance(a, Fish) and not getattr(a, "chopped", False) and not getattr(a, "cooked", False)) or \
                   (isinstance(b, Fish) and not getattr(b, "chopped", False) and not getattr(b, "cooked", False)):
                    bugs.append(self.BUG_PLATE_TWO_RICE_FISH_RAW_ADD_TOMATO)
                if (isinstance(a, Fish) and getattr(a, "chopped", False)) or (
                        isinstance(b, Fish) and getattr(b, "chopped", False)):
                    bugs.append(
                        self.BUG_PLATE_TWO_RICE_FISH_CHOPPED_ADD_LETTUCE)

            if any_cooked(items) and (
                    isinstance(new_item, Food)
                    and not getattr(new_item, "cooked", False)
                    and not getattr(new_item, "chopped", False)):
                bugs.append(self.BUG_PLATE_TWO_COOKED_EXISTS_ADD_RAW)

            if any_burned(items) and any(not getattr(i, "burned", False) and not getattr(i, "cooked", False) and not getattr(i, "chopped", False) for i in items) and \
               (isinstance(new_item, Food) and getattr(new_item, "cooked", False) and not getattr(new_item, "burned", False)):
                bugs.append(self.BUG_PLATE_TWO_BURNED_AND_RAW_ADD_COOKED)

            if isinstance(a, (Tomato, Lettuce, Onion)) and isinstance(
                    b, (Tomato, Lettuce,
                        Onion)) and type(a) is type(b) and isinstance(
                            new_item, type(a)):
                bugs.append(self.BUG_PLATE_TWO_DOUBLE_VEG_ADD_SAME)

            if both_meatlike and isinstance(new_item, Onion):
                bugs.append(self.BUG_PLATE_TWO_MEAT_VARIANTS_ADD_ONION)

            if both_fish and isinstance(new_item, Tomato):
                bugs.append(self.BUG_PLATE_TWO_FISH_VARIANTS_ADD_TOMATO)

            if getattr(plate, "dirty", False) and isinstance(new_item, Food):
                bugs.append(self.BUG_PLATE_TWO_DIRTY_ADD_ANY)

            if both_veg_chopped(a, b) and isinstance(new_item, Rice):
                bugs.append(self.BUG_PLATE_TWO_BOTH_CHOPPED_VEG_ADD_RICE)

            if has_rice and (isinstance(a, Steak)
                             or isinstance(b, Steak)) and not any(
                                 getattr(i, "cooked", False) for i in (a, b)
                                 if isinstance(i, Steak)) and isinstance(
                                     new_item, Lettuce):
                bugs.append(self.BUG_PLATE_TWO_RICE_STEAK_RAW_ADD_LETTUCE)
            if has_rice and (isinstance(a, Steak)
                             or isinstance(b, Steak)) and any(
                                 getattr(i, "cooked", False) for i in (a, b)
                                 if isinstance(i, Steak)) and isinstance(
                                     new_item, Tomato):
                bugs.append(self.BUG_PLATE_TWO_RICE_STEAK_COOKED_ADD_TOMATO)

            if is_tom_lett and isinstance(new_item, Steak) and not getattr(
                    new_item, "cooked", False) and not getattr(
                        new_item, "chopped", False):
                bugs.append(self.BUG_PLATE_TWO_TOMATO_LETTUCE_ADD_STEAK_RAW)
            if is_tom_lett and isinstance(new_item, Fish) and not getattr(
                    new_item, "cooked", False) and not getattr(
                        new_item, "chopped", False):
                bugs.append(self.BUG_PLATE_TWO_TOMATO_LETTUCE_ADD_FISH_RAW)

            if is_lett_onion and isinstance(new_item, Tomato):
                bugs.append(self.BUG_PLATE_TWO_ONION_LETTUCE_ADD_TOMATO)
            if is_tom_onion and isinstance(new_item, Lettuce):
                bugs.append(self.BUG_PLATE_TWO_ONION_TOMATO_ADD_LETTUCE)

            if has_rice and (
                (isinstance(a, Fish) and getattr(a, "cooked", False)) or
                (isinstance(b, Fish)
                 and getattr(b, "cooked", False))) and isinstance(
                     new_item, Onion):
                bugs.append(self.BUG_PLATE_TWO_FISH_COOKED_RICE_ADD_ONION)

            if target_raw == "knife":
                bugs.append(self.BUG_PLATE_TWO_ADD_KNIFE)
            # Continued two-ingredient rules (136-165)
            if ((isinstance(a, Tomato) and isinstance(b, Rice)) or
                (isinstance(b, Tomato) and isinstance(
                    a, Rice))) and isinstance(new_item, Lettuce) and getattr(
                        new_item, "chopped", False):
                bugs.append(self.BUG_PLATE_TWO_TOMATO_RICE_ADD_LETTUCE_CHOPPED)
            if ((isinstance(a, Lettuce) and isinstance(b, Rice)) or
                (isinstance(b, Lettuce)
                 and isinstance(a, Rice))) and isinstance(
                     new_item, Tomato) and getattr(new_item, "chopped", False):
                bugs.append(self.BUG_PLATE_TWO_LETTUCE_RICE_ADD_TOMATO_CHOPPED)
            if ((isinstance(a, Onion) and isinstance(b, Rice)) or
                (isinstance(b, Onion) and isinstance(a, Rice))) and isinstance(
                    new_item, Lettuce) and getattr(new_item, "chopped", False):
                bugs.append(self.BUG_PLATE_TWO_ONION_RICE_ADD_LETTUCE_CHOPPED)
            if has_rice and (
                (isinstance(a, Steak) and getattr(a, "cooked", False)) or
                (isinstance(b, Steak)
                 and getattr(b, "cooked", False))) and isinstance(
                     new_item, Lettuce) and getattr(new_item, "chopped",
                                                    False):
                bugs.append(
                    self.BUG_PLATE_TWO_RICE_STEAK_COOKED_ADD_LETTUCE_CHOPPED)
            if has_rice and (
                (isinstance(a, Fish) and getattr(a, "cooked", False)) or
                (isinstance(b, Fish)
                 and getattr(b, "cooked", False))) and isinstance(
                     new_item, Tomato) and getattr(new_item, "chopped", False):
                bugs.append(
                    self.BUG_PLATE_TWO_RICE_FISH_COOKED_ADD_TOMATO_CHOPPED)
            if is_tom_lett and isinstance(new_item, Rice):
                bugs.append(self.BUG_PLATE_TWO_TOMATO_LETTUCE_ADD_RICE)
            if is_tom_onion and isinstance(new_item, Rice):
                bugs.append(self.BUG_PLATE_TWO_TOMATO_ONION_ADD_RICE)
            if is_lett_onion and isinstance(new_item, Rice):
                bugs.append(self.BUG_PLATE_TWO_LETTUCE_ONION_ADD_RICE)
            if both_veg_chopped(a, b) and isinstance(
                    new_item, Fish) and getattr(new_item, "cooked", False):
                bugs.append(
                    self.BUG_PLATE_TWO_BOTH_VEG_CHOPPED_ADD_COOKED_FISH)
            if both_veg_chopped(a, b) and isinstance(
                    new_item,
                (Meat, Steak)) and getattr(new_item, "cooked", False):
                bugs.append(
                    self.BUG_PLATE_TWO_BOTH_VEG_CHOPPED_ADD_COOKED_MEAT)
            if is_tom_lett and target_raw == "knife":
                bugs.append(self.BUG_PLATE_TWO_TOMATO_LETTUCE_WITH_KNIFE)
            if is_tom_onion and target_raw == "knife":
                bugs.append(self.BUG_PLATE_TWO_TOMATO_ONION_WITH_KNIFE)
            if is_lett_onion and target_raw == "knife":
                bugs.append(self.BUG_PLATE_TWO_LETTUCE_ONION_WITH_KNIFE)
            if is_veg(a) and is_veg(b) and target_raw == "oven":
                bugs.append(self.BUG_PLATE_TWO_VEG_WITH_OVEN)
            if is_veg(a) and is_veg(b) and target_raw == "pan":
                bugs.append(self.BUG_PLATE_TWO_VEG_WITH_PAN)
            if is_veg(a) and is_veg(b) and target_raw == "ricecooker":
                bugs.append(self.BUG_PLATE_TWO_VEG_WITH_RICECOOKER)
            if both_fish and (
                (getattr(a, "cooked", False)
                 and not getattr(b, "cooked", False)) or
                (getattr(b, "cooked", False)
                 and not getattr(a, "cooked", False))) and isinstance(
                     new_item, Rice):
                bugs.append(self.BUG_PLATE_TWO_FISH_RAW_AND_COOKED_ADD_RICE)
            if both_meatlike and isinstance(new_item, Onion) and getattr(
                    new_item, "chopped", False):
                bugs.append(self.BUG_PLATE_TWO_MEAT_MIX_ADD_ONION_CHOPPED)
            if has_rice and has_fish and not any(
                    getattr(i, "chopped", False)
                    or getattr(i, "cooked", False) for i in (a, b)
                    if isinstance(i, Fish)) and target_raw == "knife":
                bugs.append(self.BUG_PLATE_TWO_RICE_FISH_RAW_WITH_KNIFE)
            if any_burned(items) and target_raw == "knife":
                bugs.append(self.BUG_PLATE_TWO_BURNED_PRESENT_WITH_KNIFE)
            if both_veg_chopped(
                    a, b) and isinstance(new_item, Fish) and not getattr(
                        new_item, "cooked", False) and not getattr(
                            new_item, "chopped", False):
                bugs.append(self.BUG_PLATE_TWO_BOTH_VEG_CHOPPED_ADD_FISH_RAW)
            if ((isinstance(a, Rice) and isinstance(b, Tomato)) or
                (isinstance(b, Rice)
                 and isinstance(a, Tomato))) and isinstance(
                     new_item, Fish) and getattr(new_item, "chopped", False):
                bugs.append(self.BUG_PLATE_TWO_RICE_TOMATO_ADD_FISH_CHOPPED)
            if ((isinstance(a, Rice) and isinstance(b, Lettuce)) or
                (isinstance(b, Rice)
                 and isinstance(a, Lettuce))) and isinstance(
                     new_item, Fish) and getattr(new_item, "chopped", False):
                bugs.append(self.BUG_PLATE_TWO_RICE_LETTUCE_ADD_FISH_CHOPPED)
            if ((isinstance(a, Rice) and isinstance(b, Onion)) or
                (isinstance(b, Rice) and isinstance(a, Onion))) and isinstance(
                    new_item, Fish) and getattr(new_item, "chopped", False):
                bugs.append(self.BUG_PLATE_TWO_RICE_ONION_ADD_FISH_CHOPPED)
            if ((isinstance(a, Tomato) and isinstance(b, Fish)
                 and getattr(b, "cooked", False)) or
                (isinstance(b, Tomato) and isinstance(a, Fish) and getattr(
                    a, "cooked", False))) and isinstance(new_item, Rice):
                bugs.append(self.BUG_PLATE_TWO_TOMATO_FISH_COOKED_ADD_RICE)
            if is_veg(a) and is_veg(b) and type(a) is type(b) and isinstance(
                    new_item, Rice):
                bugs.append(self.BUG_PLATE_TWO_DUP_VEG_ADD_RICE)
            if ((isinstance(a, Steak) and getattr(a, "cooked", False)
                 and isinstance(b, Meat) and not getattr(b, "cooked", False))
                    or (isinstance(b, Steak) and getattr(b, "cooked", False)
                        and isinstance(a, Meat)
                        and not getattr(a, "cooked", False))) and isinstance(
                            new_item, Onion):
                bugs.append(self.BUG_PLATE_TWO_STEAK_COOKED_MEAT_RAW_ADD_ONION)
            if has_rice and (
                (isinstance(a,
                            (Meat, Steak)) and getattr(a, "cooked", False)) or
                (isinstance(b, (Meat, Steak))
                 and getattr(b, "cooked", False))) and isinstance(
                     new_item, Tomato) and getattr(new_item, "chopped", False):
                bugs.append(
                    self.BUG_PLATE_TWO_RICE_MEAT_COOKED_ADD_TOMATO_CHOPPED)
            if has_rice and (
                (isinstance(a, Fish) and getattr(a, "cooked", False)) or
                (isinstance(b, Fish)
                 and getattr(b, "cooked", False))) and target_raw == "oven":
                bugs.append(self.BUG_PLATE_TWO_RICE_FISH_COOKED_WITH_OVEN)
            if has_rice and (
                (isinstance(a, Steak) and not getattr(a, "cooked", False)) or
                (isinstance(b, Steak)
                 and not getattr(b, "cooked", False))) and target_raw == "pan":
                bugs.append(self.BUG_PLATE_TWO_RICE_STEAK_RAW_WITH_PAN)

        return bugs

    def check_all_cutboards(self):
        knives = getattr(self.item_manager, "knife", [])
        if knives and all(k.holding and getattr(k.holding, "chopped", False)
                          for k in knives):
            return [self.BUG_ALL_CUTBOARD_CHOPPED]
        return []

    def check_deliver(self, item_count):
        bugs = []
        if item_count == 2:
            bugs.append(self.BUG_DELIVER_TWO)
        if item_count == 3:
            bugs.append(self.BUG_DELIVER_THREE)
        return bugs

    def check_deliver_extra(self, plate):
        bugs = []
        items = getattr(plate, "containing", [])
        if plate.dirty:
            bugs.append(self.BUG_DELIVER_DIRTY_PLATE)
        if not items:
            bugs.append(self.BUG_DELIVER_EMPTY_PLATE)
        if len(items) > 4:
            bugs.append(self.BUG_DELIVER_MORE_THAN_FOUR)
        for it in items:
            if getattr(it, "burned", False):
                bugs.append(self.BUG_DELIVER_BURNED_FOOD)
                break
        has_rice = any(isinstance(i, Rice) for i in items)
        has_fish = any(isinstance(i, Fish) for i in items)
        has_sushi = any(isinstance(i, Sushi) for i in items)
        if has_rice and has_fish and not has_sushi:
            bugs.append(self.BUG_DELIVER_PARTIAL_SUSHI)
        return bugs

    def check_dump(self, holding):
        bugs = []
        if holding.rawName == "plate" and getattr(holding, "containing", []):
            bugs.append(self.BUG_TRASH_PLATE_ITEM_NOT_RESET)
        if isinstance(holding,
                      Plate) and not holding.dirty and not holding.containing:
            bugs.append(self.BUG_TRASH_CLEAN_PLATE)
        if getattr(holding, "burned", False):
            bugs.append(self.BUG_TRASH_BURNED_ITEM_NOT_RESET)
        return bugs

    def check_meat_on_plate(self, item, pre_count):
        bugs = []
        if isinstance(item, Meat) and item.chopped and not item.cooked:
            bugs.append(self.BUG_CHOPPED_MEAT_IN_PLATE)
        if isinstance(
                item, Meat
        ) and pre_count > 0 and not item.chopped and not item.cooked:
            bugs.append(self.BUG_RAW_MEAT_ON_NONEMPTY_PLATE)
        return bugs

    def check_pickup(self, item, immediate=False):
        bugs = []
        if isinstance(item, Plate) and item.dirty:
            bugs.append(self.BUG_DIRTY_PLATE_PICKUP)
        if getattr(item, "burned", False):
            bugs.append(self.BUG_PICKUP_BURNED_ITEM)
        if immediate:
            bugs.append(self.BUG_PICKUP_OWN_DROPPED_ITEM_IMMEDIATELY)
        return bugs

    def check_pickup_full_hands(self):
        """Attempted to pick up an item while already holding something."""
        return [self.BUG_PICKUP_WITH_FULL_HANDS]

    def check_usage(self, device):
        bugs = []
        if device.rawName == "knife":
            if not device.holding:
                bugs.append(self.BUG_USE_KNIFE_WITHOUT_ITEM)
            else:
                item = device.holding
                if item.chopped:
                    bugs.append(self.BUG_CHOP_ALREADY_CHOPPED)
                if getattr(item, "cooked", False):
                    bugs.append(self.BUG_CHOP_COOKED_ITEM)
                if getattr(item, "burned", False):
                    bugs.append(self.BUG_CHOPPING_BURNED_MEAT)
        if device.rawName == "sink":
            if not device.holding:
                bugs.append(self.BUG_USE_SINK_WITHOUT_PLATE)
            else:
                item = device.holding
                if getattr(item, "burned", False):
                    bugs.append(self.BUG_WASH_BURNT_FOOD)
                if not item.dirty:
                    bugs.append(self.BUG_WASH_CLEAN_PLATE)
        return bugs

    def check_sink_after_wash(self, sink):
        bugs = []
        if sink.holding and not sink.holding.dirty:
            bugs.append(self.BUG_SINK_HOLD_AFTER_CLEAN)
        return bugs

    def check_auto(self, before, after):
        bugs = []
        if before[0] and after[0] and before == after:
            bugs.append(self.BUG_COOK_AFTER_DONE)
        if not before[1] and after[1]:
            bugs.append(self.BUG_BURN_FOOD_IGNORED)
        return bugs

    def check_pickup_from_empty(self):
        return [self.BUG_PICKUP_FROM_EMPTY_COUNTER]

    def check_collision(self):
        return [self.BUG_COLLISION_MOVE]
