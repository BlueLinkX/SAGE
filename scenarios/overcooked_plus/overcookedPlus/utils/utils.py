from functools import wraps
from datetime import datetime
import json


def log_step(func):
    """
    顶层装饰器：一次聚合 auto、agent 动作 和 状态快照，记录单条 step 日志
    要求 process_action 返回 [action_dict, ...]
    """

    @wraps(func)
    def wrapper(self, action):
        action_details = func(self, action)  # list of dicts
        autos = self._collect_auto()
        bug_ids = []
        for a in autos:
            bug_ids.extend(a.pop("bug_id", []))

        states = []
        for agent in self.item_Manager.agent:
            holding = None
            if hasattr(agent, "holding") and agent.holding:
                if hasattr(agent.holding, "containing"):
                    holding = {
                        "item":
                        getattr(agent.holding, "rawName", None),
                        "containing": [
                            getattr(it, "rawName", None)
                            for it in agent.holding.containing
                        ]
                    }
                else:
                    holding = getattr(agent.holding, "rawName", None)
            states.append({
                "agent_id": getattr(agent, "id", None),
                "position": (agent.x, agent.y),
                "holding": holding
            })
        last_entry = None
        for detail in action_details:
            bug_ids.extend(detail.pop("bug_id", []))
            event_type = detail.pop("type")
            agent_id = detail.pop("agent")
            position = detail.pop("position", None)
            target = ("{} to {}".format(detail.pop("from"), detail.pop("to"))
                      if event_type == "move" else detail.pop("item", None))

            entry = create_log_entry(
                event_type,
                agent_id,
                position,
                target,
                details={
                    "autos": autos,
                    "states": states,
                    "others": detail,
                },
            )
            last_entry = entry
            if self.output_log:
                self.log_manager.record(entry)

        return last_entry, bug_ids

    return wrapper


def create_log_entry(event_type,
                     agent_id=None,
                     position=None,
                     target=None,
                     change=None,
                     details=None):
    return {
        "timestamp": datetime.now().isoformat(),
        "event_type": event_type,
        "agent_id": agent_id or "auto",
        "position": position,
        "target": target or {},
        #"change": change or "",
        "details": details or {}
    }


class LogManager:

    def __init__(self, outfile="game_logs.jsonl"):
        self.outfile = outfile

    def record(self, entry):
        with open(self.outfile, "a", encoding="utf-8") as fp:
            fp.write(json.dumps(entry, ensure_ascii=False) + "\n")


def key2action(key):
    if key == "d":
        return 0
    elif key == "s":
        return 1
    elif key == "a":
        return 2
    elif key == "w":
        return 3
    else:
        return None
