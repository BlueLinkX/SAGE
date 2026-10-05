import random
import itertools
from ..constants import *
from ..items import reverse_synthesis_table


class TaskManager:
    """
    TaskManager class is responsible for managing the tasks in the environment.
    """

    def __init__(self,
                 get_step_count,
                 item_Manager,
                 n_task=2,
                 fixed_task=False,
                 min_ing=1,
                 max_ing=4,
                 task_pool=None):
        """
        Args:
            get_step_count (func): Function to get the step count of the environment.
            item_Manager (class): ItemManager class in the environment.
            n_task (int, optional): The number of tasks that can be completed simultaneously. Defaults to 2.
            fixed_task (bool, optional): Whether to enable fixed tasks. Defaults to False.
            min_ing (int, optional): The minimum number of ingredients required for each task. Defaults to 1.
            max_ing (int, optional): The maximum number of ingredients required for each task. Defaults to 4.
            task_pool (list, optional): List of tasks defined by ingredient codes. When
                provided, tasks will be drawn from this pool instead of being
                generated based on ``min_ing``/``max_ing``.
        """
        self.get_step_count = get_step_count
        self.item_Manager = item_Manager
        self.n_task = n_task
        self.min_ing = min_ing
        self.max_ing = max_ing
        self.fixed_task = fixed_task
        self.custom_task_pool = task_pool
        self.tasks = []
        self.taskpool = []
        self.inglist = []
        self.completed_tasks = []
        self.init_taskpool()
        self.replenish_task()

    def init_taskpool(self):
        # Filter available ingredients in the environment
        for key in self.item_Manager.itemDic:
            if key in INGLIST and self.item_Manager.itemDic[key]:
                self.inglist.append(key)
        if self.custom_task_pool:
            reverse_idx = {v: k for k, v in ITEMIDX.items()}
            for codes in self.custom_task_pool:
                ingredients = [reverse_idx.get(c) for c in codes]
                ingredients = [ing for ing in ingredients if ing in INGLIST]
                task = {
                    "ingredients": ingredients,
                    "task_encoding": self.encode_task(ingredients),
                    "task_start_time": -1,
                    "task_end_time": -1,
                }
                self.taskpool.append(task)
        else:
            if self.max_ing > len(self.inglist):
                self.max_ing = len(self.inglist)
            # Generate the task pool
            self.generate_task_pool()

    def generate_task_pool(self):
        for r in range(self.min_ing, self.max_ing + 1):
            for combination in itertools.combinations(self.inglist, r):
                task = {
                    "ingredients": combination,
                    "task_encoding": self.encode_task(combination),
                    "task_start_time": -1,
                    "task_end_time": -1,
                }
                self.taskpool.append(task)

    def encode_task(self, ingredients):
        # One-hot encoding logic
        encoding = [0] * len(INGLIST)
        for ing in ingredients:
            index = INGLIST.index(ing)
            encoding[index] = 1
        return encoding

    def _expand_names(self, names):
        """Expand composite dish names into their base ingredients."""
        expanded = []
        for n in names:
            if n in reverse_synthesis_table:
                expanded.extend(reverse_synthesis_table[n])
            else:
                expanded.append(n)
        return expanded

    def display_taskpool(self):
        # Display all tasks in the task pool
        for task in self.taskpool:
            print(
                f"Ingredients: {task['ingredients']}, Encoding: {task['task_encoding']}"
            )

    def check_task_completion(self, ingredients):
        step_count = self.get_step_count()
        ingredients_name = []
        for ing in ingredients:
            ingredients_name.extend(self._expand_names([ing.rawName]))
        for task in self.tasks:
            task_names = self._expand_names(task["ingredients"])
            if set(task_names) == set(ingredients_name):
                task["task_end_time"] = step_count
                self.completed_tasks.append(task)
                if not self.fixed_task:
                    self.tasks.remove(task)
                    self.replenish_task()
                return True
        return False

    def check_task_partial_completion(self, ingredients):
        """Return True if ingredients are a strict non-empty subset of any task."""
        if not ingredients:
            return 0
        ing_names = []
        for ing in ingredients:
            ing_names.extend(self._expand_names([ing.rawName]))
        ing_names = set(ing_names)
        for task in self.tasks:
            task_set = set(self._expand_names(task["ingredients"]))
            if ing_names < task_set:
                #计算当前任务的完成度
                completed_count = len(ing_names & task_set)
                total_count = len(task_set)
                return completed_count / total_count

        return 0

    def get_needed_ingredients(self):
        """Return a set of ingredient names required by current tasks."""
        needed = set()
        for task in self.tasks:
            needed.update(self._expand_names(task["ingredients"]))
        return needed

    def is_ingredient_needed(self, name: str) -> bool:
        """Check whether ``name`` is among any active task ingredients."""
        return name in self.get_needed_ingredients()

    def replenish_task(self):
        if self.fixed_task:
            random.seed(42)
        step_count = self.get_step_count()
        add_n_task = self.n_task - len(self.tasks)
        # Ensure there are still tasks in the task pool
        if self.taskpool:
            for _ in range(add_n_task):
                new_task = random.choice(self.taskpool)
                new_task["task_start_time"] = step_count
                self.tasks.append(new_task)

    def reset(self):
        self.tasks = []
        self.replenish_task()
        return self.tasks

    def set_tasks_from_encoding(self, encodings):
        """Restore current tasks from a list of one-hot encodings."""
        self.tasks = []
        step_count = self.get_step_count()
        for enc in encodings:
            matched = False
            for task in self.taskpool:
                if list(task["task_encoding"]) == list(enc):
                    new_task = task.copy()
                    new_task["task_start_time"] = step_count
                    new_task["task_end_time"] = -1
                    self.tasks.append(new_task)
                    matched = True
                    break
            if not matched:
                ingredients = [INGLIST[i] for i, v in enumerate(enc) if v]
                self.tasks.append({
                    "ingredients": ingredients,
                    "task_encoding": list(enc),
                    "task_start_time": step_count,
                    "task_end_time": -1,
                })
