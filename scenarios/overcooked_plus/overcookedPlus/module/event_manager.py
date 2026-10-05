from .item_manager import ItemManager
from .action_wrapper import ActionWrapper
from ..items import MovableItem, FixedItem, Plate
from ..constants import (ITEMIDX, DIRECTION, AGENTCOLOR, ActionType,
                         PrimitiveAction)
from ..items import reverse_synthesis_table
from ..utils.utils import LogManager, create_log_entry, log_step
from .bug_manager import BugManager


class EventManager:
    """
    处理全部游戏动作，并在每个游戏 step 生成一条日志：
    - 收集自动交互结果
    - 收集每个 agent 的动作结果
    - 收集每个 agent 的状态快照（位置 + 持有物）
    """

    def __init__(self,
                 item_Manager,
                 map_Manager,
                 task_Manager,
                 rewardList,
                 output_log=False):
        self.item_Manager = item_Manager
        self.map_Manager = map_Manager
        self.action_wrapper = ActionWrapper(map_Manager)
        self.task_Manager = task_Manager
        self.rewardList = rewardList
        self.reverse_itemidx = {v: k for k, v in ITEMIDX.items()}
        self.log_manager = LogManager()
        self.output_log = output_log
        self.bug_manager = BugManager(self.item_Manager)
        self.last_dropped = {}

    def _item_related_to_task(self, item):
        """Return True if the item or its components are needed for any task."""
        if not item:
            return False

        def _expand(it):
            name = getattr(it, "rawName", "")
            return reverse_synthesis_table.get(name, [name])

        if item.rawName == "plate":
            for ing in item.containing:
                names = _expand(ing)
                if not any(
                        self.task_Manager.is_ingredient_needed(n)
                        for n in names):
                    return False
            return bool(item.containing)

        names = _expand(item)
        return any(self.task_Manager.is_ingredient_needed(n) for n in names)

    @log_step
    def process_action(self, action):
        """
        每个游戏 step 的入口，由 @log_step 装饰器负责：
          1. 先收集自动交互
          2. 调用本函数分发 agent 动作，收集返回细节
          3. 装饰器再统一写日志
        返回值：列表 of action details dict
        """
        if not isinstance(action, list):
            action = [action]

        action_details = []
        for idx, agent in enumerate(self.item_Manager.agent):
            detail = {
                "type": ActionType.NONE.value,
                "agent": agent.color,
                "item": None,
                "bug_id": [],
                "position": (agent.x, agent.y),
            }
            agent_action = int(action[idx])
            if agent.moved:
                action_details.append(detail)
                continue
            agent.moved = True
            agent.reward.append(self.rewardList["step penalty"])

            if agent_action < 4:
                result = self._dispatch(agent, agent_action, action)
                if result is not None:
                    detail = result
                else:
                    if self.output_log:
                        invalid_entry = create_log_entry(
                            "invalid_action",
                            agent_id=agent.color,
                            position=(agent.x, agent.y),
                            target={"action": agent_action})
                        self.log_manager.record(invalid_entry)
            action_details.append(detail)

        return action_details

    def _dispatch(self, agent, act, full_action):
        tx, ty = self._calc(agent, act)
        code = self.map_Manager.map[tx][ty]
        name = self.reverse_itemidx.get(code)

        if name == "space":
            return self._do_move(agent, tx, ty)
        if name == "agent":
            return self._do_collision(agent, tx, ty, full_action)
        target = self.item_Manager.findItem(tx, ty, name)
        if target:
            return self._do_interaction(agent, target)

        raise ValueError(
            f"Invalid action: {act} at position ({tx}, {ty}) with item code {code} ({name})"
        )

    def _do_move(self, agent, tx, ty):
        old = (agent.x, agent.y)
        self.action_wrapper.move(agent, tx, ty)
        return {
            "type": ActionType.MOVE.value,
            "agent": agent.color,
            "from": old,
            "to": (tx, ty),
            "position": (tx, ty),
            "bug_id": []
        }

    def _do_collision(self, agent, tx, ty, full_action):
        # 保留原有碰撞处理逻辑
        target_agent = self.item_Manager.findItem(tx, ty, "agent")
        if target_agent and not target_agent.moved:
            agent.moved = False
            target_action = full_action[AGENTCOLOR.index(target_agent.color)]
            if target_action < 4:
                ntx, nty = (target_agent.x + DIRECTION[target_action][0],
                            target_agent.y + DIRECTION[target_action][1])
                if ntx == agent.x and nty == agent.y:
                    target_agent.move(ntx, nty)
                    agent.move(tx, ty)
                    agent.moved = True
                    target_agent.moved = True
        return {
            "type": ActionType.COLLISION.value,
            "agent": agent.color,
            "position": (tx, ty),
            "bug_id": self.bug_manager.check("collision", {})["bug_id"]
        }

    def _do_interaction(self, agent, target):
        # 无持物：pickup 或 usage
        if not agent.holding:
            if target.rawName == "counter":
                return {
                    "type": ActionType.NONE.value,
                    "agent": agent.color,
                    "item": target.rawName,
                    "position": (agent.x, agent.y),
                    "bug_id": self.bug_manager.check("pickup_empty",
                                                     {})["bug_id"]
                }
            if isinstance(target, MovableItem):
                success = self.action_wrapper.pickup(agent, target)
                bugs = self.bug_manager.check_pickup(target, False)
                if self.last_dropped.get(agent.color) is target:
                    bugs += self.bug_manager.check_pickup(target, True)
                    self.last_dropped.pop(agent.color, None)
                if success and ((target.rawName == "plate")
                                or self._item_related_to_task(target)):
                    agent.reward[-1] += self.rewardList["put_down_and_holding"]
                return {
                    "type": ActionType.PICKUP.value,
                    "agent": agent.color,
                    "item": target.rawName,
                    "position": (agent.x, agent.y),
                    "bug_id": bugs
                }
            elif isinstance(target, FixedItem):
                if target.rawName == "oven" and target.holding:
                    # items in the oven must be taken out with a plate
                    return self._do_usage(agent, target)
                if not target.lock and target.holding:
                    item = self.action_wrapper.pickup_from_device(
                        agent, target)
                    if item:
                        if (target.rawName == "pan"
                                and getattr(item, "cooked", False)
                                and not getattr(item, "burned", False)
                                and self._item_related_to_task(item)):
                            agent.reward[-1] += self.rewardList[
                                "subtask finished"]
                        if (item.rawName == "plate" and getattr(
                                item, "dirty",
                                False)) or self._item_related_to_task(item):
                            agent.reward[-1] += self.rewardList[
                                "put_down_and_holding"]
                        bugs = self.bug_manager.check_pickup(item, False)
                        if self.last_dropped.get(agent.color) is item:
                            bugs += self.bug_manager.check_pickup(item, True)
                            self.last_dropped.pop(agent.color, None)
                        return {
                            "type": ActionType.PICKUP.value,
                            "agent": agent.color,
                            "item": item.rawName,
                            "position": (agent.x, agent.y),
                            "bug_id": bugs
                        }
                    return self._do_usage(agent, target)
                else:
                    return self._do_usage(agent, target)
        # 有持物：根据持物类型分流
        else:
            name = agent.holding.rawName
            if name == "plate":
                if target.rawName == "delivery":
                    return self._do_deliver(agent, target)
                if target.rawName == "trash_can":
                    return self._do_dump(agent)
                if target.rawName == "oven":
                    if target.holding:
                        return self._do_pickup_into_plate(agent, target)
                    return self._do_putdown(agent, target)
                if target.rawName in ("counter", "sink"):
                    return self._do_putdown(agent, target)
                return self._do_pickup_into_plate(agent, target)
            else:
                if target.rawName == "trash_can":
                    return self._do_dump(agent)
                return self._do_putdown(agent, target)

    def _do_usage(self, agent, target):
        bug_id = self.bug_manager.check_usage(target)
        if target.rawName == "knife":
            if target.holding:
                item = target.holding
                success = target.chop()
                if self._item_related_to_task(item):
                    agent.reward[-1] += self.rewardList[
                        "subtask finished"] / item.required_chopped_times
                bug_id = []
                if success:
                    bug_id += self.bug_manager.check_all_cutboards()
                return {
                    "type": ActionType.CHOP.value,
                    "agent": agent.color,
                    "item": target.rawName,
                    "success": success,
                    "position": (agent.x, agent.y),
                    "bug_id": bug_id
                }
        if target.rawName == "sink":
            if target.holding:
                success = target.wash()
                item = target.holding
                if self._item_related_to_task(item):
                    agent.reward[-1] += self.rewardList[
                        "subtask finished"] / item.required_wash_times
                bug_id += self.bug_manager.check_sink_after_wash(target)

                return {
                    "type": ActionType.WASH.value,
                    "agent": agent.color,
                    "item": target.rawName,
                    "success": success,
                    "position": (agent.x, agent.y),
                    "bug_id": bug_id
                }

        return {
            "type": ActionType.NONE.value,
            "agent": agent.color,
            "item": target.rawName,
            "position": (agent.x, agent.y),
            "bug_id": bug_id
        }

    def _do_deliver(self, agent, target):
        plate = agent.release()
        dish_name = plate.containedName
        # 投递后自动 dump
        containing = plate.containing
        correct = self.task_Manager.check_task_completion(containing)
        partial_number = 0
        if correct:
            for it in containing:
                if it.rawName in ("pizza", "roastfish"):
                    if getattr(it, "burned", False):
                        correct = False
                        break
                    if not getattr(it, "cooked", False):
                        correct = False
                        partial_number = 1
                        break
        if not correct and partial_number == 0:
            partial_number = self.task_Manager.check_task_partial_completion(
                containing)
        if correct:
            agent.reward[-1] = self.rewardList["correct delivery"]
        else:
            if not containing:
                agent.reward[-1] = self.rewardList["empty delivery"]
            elif partial_number != 0:
                agent.reward[
                    -1] = self.rewardList["partial delivery"] * partial_number
            else:
                agent.reward[-1] = self.rewardList["wrong delivery"]
        bug_id = self.bug_manager.check_deliver(len(containing))
        bug_id += self.bug_manager.check_deliver_extra(plate)
        # 正确处理合成物品的回收
        if plate.synthesis_origin:
            # 回收原料到地图
            for item in plate.synthesis_origin:
                self.action_wrapper.reset_item(item)

            # 回收合成物品到 consumed 状态
            for item in containing:
                if item.rawName not in ("pizza", "sushi", "roastfish"):
                    self.action_wrapper.reset_item(item)
                else:
                    item.refresh()

            plate.containing = []
            plate.synthesis_origin = []
        else:
            # 没有合成的情况，所有物品都回收到地图
            for item in containing:
                self.action_wrapper.reset_item(item)
        self.action_wrapper.reset_item(plate)
        return {
            "type": ActionType.DELIVER.value,
            "agent": agent.color,
            "item": dish_name,
            "dishname": dish_name,
            "success": correct,
            "partial_success": partial_number,
            "position": (agent.x, agent.y),
            "bug_id": bug_id
        }

    def _do_dump(self, agent):
        holding_item = agent.release()
        items = [holding_item]
        if isinstance(holding_item, Plate):
            items.extend(holding_item.containing)

        if any([hasattr(item, "burned") and item.burned for item in items]):
            agent.reward[-1] += self.rewardList["subtask finished"]
        elif isinstance(items[0],
                        Plate) and not self._item_related_to_task(items[0]):
            agent.reward[-1] -= self.rewardList["subtask finished"] * 2

        else:
            agent.reward[-1] -= self.rewardList["subtask finished"] * 10
        # dump logic
        bug_id = self.bug_manager.check_dump(holding_item)
        plate = holding_item if isinstance(holding_item, Plate) else None
        if plate and plate.synthesis_origin:
            for item in plate.synthesis_origin:
                self.action_wrapper.reset_item(item)

            for item in plate.containing:
                if item.rawName in ("pizza", "sushi", "roastfish"):
                    item.consumed = True
                    item.move(-1, -1)
                    item.container = None
                    item.invalidate_cache()
                else:
                    self.action_wrapper.reset_item(item)

            plate.containing = []
            plate.synthesis_origin = []
            self.action_wrapper.reset_item(plate)
        else:
            for item in items:
                if hasattr(item,
                           'rawName') and item.rawName in ("pizza", "sushi",
                                                           "roastfish"):
                    item.consumed = True
                    item.move(-1, -1)
                    item.container = None
                    item.invalidate_cache()
                else:
                    self.action_wrapper.reset_item(item)
            if plate:
                plate.containing = []
        return {
            "type": ActionType.DUMP.value,
            "agent": agent.color,
            "item": [it.rawName for it in items],
            "position": (agent.x, agent.y),
            "bug_id": bug_id
        }

    def _do_putdown(self, agent, target):
        bug_id = []
        return_dict_success = {
            "type": ActionType.PUTDOWN.value,
            "agent": agent.color,
            "item": target.rawName,
            "success": True,
            "position": (agent.x, agent.y)
        }
        return_dict_fail = {
            "type": ActionType.PUTDOWN.value,
            "agent": agent.color,
            "item": target.rawName,
            "success": False,
            "position": (agent.x, agent.y)
        }
        dest = target.rawName
        if agent.holding.rawName == "plate":
            bug_id += self.bug_manager.check_putdown(
                agent.holding, target, len(agent.holding.containing), agent)
        elif dest == "plate":
            bug_id += self.bug_manager.check_putdown(agent.holding, target,
                                                     len(target.containing),
                                                     agent)
        if dest == "counter":
            item = self.action_wrapper.place_on_counter(agent, target)
            if item.rawName == "plate" or self._item_related_to_task(item):
                agent.reward[-1] -= self.rewardList["put_down_and_holding"]
            return_dict_success["bug_id"] = bug_id
            return return_dict_success
        elif dest == "delivery":
            return_dict_fail["bug_id"] = bug_id
            return return_dict_fail
        elif hasattr(target, "containing"):
            item = self.action_wrapper.add_to_container(agent, target)
            if item:
                if self._item_related_to_task(item):
                    if target.rawName == "plate":
                        agent.reward[-1] += self.rewardList[
                            "put_down_and_holding"]
                    agent.reward[-1] += self.rewardList["put_down_and_holding"]
                return_dict_success["bug_id"] = bug_id
                return return_dict_success
        elif hasattr(target, "hold"):
            item = self.action_wrapper.hold_in_device(agent, target)
            if item:
                if ((target.rawName == "pan" or target.rawName == "ricecooker"
                     or target.rawName == "oven")
                        and self._item_related_to_task(item)):
                    agent.reward[-1] += self.rewardList["subtask finished"] * 5
                    agent.reward[-1] += self.rewardList["put_down_and_holding"]
                if self._item_related_to_task(item):
                    agent.reward[-1] += self.rewardList["put_down_and_holding"]
                if item.rawName == "plate" and item.dirty and target.rawName != "sink":
                    agent.reward[-1] -= self.rewardList["put_down_and_holding"]
                return_dict_success["bug_id"] = bug_id
                return return_dict_success
        return_dict_fail["bug_id"] = bug_id
        return return_dict_fail

    def _do_pickup_into_plate(self, agent, target):
        plate = agent.holding
        pre_len = len(plate.containing)
        bug_id = self.bug_manager.check_pickup_into_plate(plate, target)
        pick_item = target.holding if isinstance(target, FixedItem) else target
        bug_id += self.bug_manager.check_meat_on_plate(pick_item, pre_len)
        #如果target是FixedItem的话
        if isinstance(target, FixedItem):
            item = self.action_wrapper.transfer_device_to_plate(agent, target)
            success = item is not None
            if success:
                bug_id += self.bug_manager.check_pickup(item, False)
                if self.last_dropped.get(agent.color) is item:
                    bug_id += self.bug_manager.check_pickup(item, True)
                    self.last_dropped.pop(agent.color, None)
                if self._item_related_to_task(item):
                    agent.reward[-1] += self.rewardList["put_down_and_holding"]
                    if target.rawName in ("oven", "ricecooker", "pan"):
                        agent.reward[
                            -1] += self.rewardList["subtask finished"] * 5
            return {
                "type": ActionType.PICKUP_INTO_PLATE.value,
                "agent": agent.color,
                "item": item.rawName if success else target.rawName,
                "plate": plate.rawName,
                "success": success,
                "position": (agent.x, agent.y),
                "bug_id": bug_id
            }
        elif isinstance(target, MovableItem):
            if not plate.dirty:
                success = self.action_wrapper.pickup(agent, target)
                if success:
                    bug_id += self.bug_manager.check_pickup(target, False)
                    if self.last_dropped.get(agent.color) is target:
                        bug_id += self.bug_manager.check_pickup(target, True)
                        self.last_dropped.pop(agent.color, None)
                    agent.reward[-1] += self.rewardList["put_down_and_holding"]
                    if self._item_related_to_task(target):
                        agent.reward[-1] += self.rewardList[
                            "put_down_and_holding"]
                return {
                    "type": ActionType.PICKUP_INTO_PLATE.value,
                    "agent": agent.color,
                    "item": target.rawName,
                    "plate": plate.rawName,
                    "success": success,
                    "position": (agent.x, agent.y),
                    "bug_id": bug_id
                }

        return {
            "type": ActionType.PICKUP_INTO_PLATE.value,
            "agent": agent.color,
            "item": target.rawName,
            "success": False,
            "position": (agent.x, agent.y),
            "bug_id": bug_id
        }

    def _collect_auto(self):
        """收集所有自动设备（pan, ricecooker, oven）的状态变化"""
        autos = []
        # 平底锅
        for pan in self.item_Manager.pan:
            if pan.holding:
                item = pan.holding
                if not pan.holding.cooked and self._item_related_to_task(item):
                    for ag in self.item_Manager.agent:
                        ag.reward[-1] += 0
                        #self.rewardList[
                        #    "subtask finished"] / item.required_cooked_times
                before = (pan.holding.cooked, pan.holding.burned)
                pan.cook()
                after = (pan.holding.cooked, pan.holding.burned)
                bug = self.bug_manager.check("auto", {
                    "before": before,
                    "after": after
                })["bug_id"]
                delta = {
                    "cooked": (before[0], after[0]),
                    "burned": (before[1], after[1])
                }
                for ag in self.item_Manager.agent:
                    if self._item_related_to_task(
                            item) and before[1] != after[1]:
                        ag.reward[-1] += self.rewardList["burned penalty"]
                autos.append({"device": "pan", "delta": delta, "bug_id": bug})
        # 电饭煲
        for cooker in self.item_Manager.ricecooker:
            if cooker.holding:
                item = cooker.holding
                if not cooker.holding.cooked and self._item_related_to_task(
                        item):
                    for ag in self.item_Manager.agent:
                        ag.reward[-1] += self.rewardList[
                            "subtask finished"] / item.required_cooked_times
                before = cooker.holding.cooked
                cooker.cook()
                after = cooker.holding.cooked
                bug = self.bug_manager.check("auto", {
                    "before": (before, False),
                    "after": (after, False)
                })["bug_id"]
                if before != after:
                    autos.append({
                        "device": "ricecooker",
                        "delta": {
                            "cooked": (before, after)
                        },
                        "bug_id": bug
                    })
        # 烤箱
        for oven in self.item_Manager.oven:
            if oven.holding:
                food = oven.holding
                if not food.cooked and self._item_related_to_task(food):
                    for ag in self.item_Manager.agent:
                        ag.reward[-1] += (self.rewardList["subtask finished"] /
                                          food.required_cooked_times)
                before = (food.cooked, food.burned)
                oven.cook()
                after = (food.cooked, food.burned)
                bug = self.bug_manager.check("auto", {
                    "before": before,
                    "after": after
                })["bug_id"]
                delta = {
                    "cooked": (before[0], after[0]),
                    "burned": (before[1], after[1])
                }
                for ag in self.item_Manager.agent:
                    if self._item_related_to_task(
                            food) and before[1] != after[1]:
                        ag.reward[-1] += self.rewardList["burned penalty"]
                autos.append({"device": "oven", "delta": delta, "bug_id": bug})
        return autos

    def _calc(self, agent, act):
        dx, dy = DIRECTION[act]
        tx, ty = agent.x + dx, agent.y + dy
        if not (0 <= tx < self.map_Manager.xlen
                and 0 <= ty < self.map_Manager.ylen):
            raise ValueError("Target coordinate out of map bounds")
        return tx, ty
