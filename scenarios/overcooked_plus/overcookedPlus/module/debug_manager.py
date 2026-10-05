import tkinter as tk
from tkinter import scrolledtext
import queue
import threading
import time
from ..items import Counter, Food, Plate, MovableItem, FixedItem, Agent


class DebugManager:
    """
    一个独立的调试管理器，用于在单独的Tkinter窗口中显示和比较观测向量。
    支持快速模式以提高显示速度。
    """

    def __init__(self, gui_enable=False, debug=False, fast_mode=True):
        self.gui_enable = gui_enable
        self.debug = debug
        self.enabled = gui_enable and debug  # 只有当GUI和debug都启用时才启用

        self.root = None
        self.text_area = None
        self.queue = queue.Queue()
        self.gui_ready = threading.Event()
        self.fast_mode = fast_mode  # 默认使用快速模式

        self._previous_obs = None
        self._step_count = 0

        # 只有启用时才初始化GUI
        if self.enabled:
            # 在单独的线程中启动GUI，以防阻塞游戏主循环
            self.gui_thread = threading.Thread(target=self._start_gui,
                                               daemon=True)
            self.gui_thread.start()

            # 等待GUI初始化完成
            self.gui_ready.wait(timeout=5.0)
        else:
            # 如果未启用，立即设置为就绪状态
            self.gui_ready.set()

    def _start_gui(self):
        try:
            self.root = tk.Tk()
            self.root.title("OBS Vector Debug Console [快速模式]" if self.
                            fast_mode else "OBS Vector Debug Console [详细模式]")
            self.root.geometry("600x900")

            # 设置窗口属性，防止阻塞
            self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

            # 绑定键盘快捷键
            self.root.bind('<F1>', self._toggle_mode)
            self.root.focus_set()  # 确保窗口可以接收键盘事件

            self.text_area = scrolledtext.ScrolledText(self.root,
                                                       wrap=tk.WORD,
                                                       font=("Courier New",
                                                             10),
                                                       bg="#2e2e2e",
                                                       fg="white")
            self.text_area.pack(expand=True, fill='both')

            # 定义颜色标签
            self.text_area.tag_config('red', foreground='#ff6b6b')
            self.text_area.tag_config('black', foreground='white')
            self.text_area.tag_config('green', foreground='#69f0ae')
            self.text_area.tag_config('blue', foreground='#74b9ff')
            self.text_area.tag_config('yellow', foreground='#ffd166')
            self.text_area.config(state='disabled')

            # 显示初始帮助信息
            self.text_area.config(state='normal')
            help_text = "=== OBS Vector Debug Console ===\n"
            help_text += f"当前模式: {'快速' if self.fast_mode else '详细'}\n"
            help_text += "按 F1 切换快速/详细模式\n"
            help_text += "=" * 40 + "\n\n"
            self.text_area.insert(tk.END, help_text, ('blue', ))
            self.text_area.config(state='disabled')

            # 标记GUI已就绪
            self.gui_ready.set()

            # 启动队列检查
            self.root.after(20, self._check_queue)  # 更快的检查频率
            self.root.mainloop()
        except Exception as e:
            print(f"Debug GUI初始化失败: {e}")
            self.gui_ready.set()  # 即使失败也要设置事件，避免无限等待

    def _on_closing(self):
        """处理窗口关闭事件"""
        try:
            self.root.quit()
            self.root.destroy()
        except:
            pass

    def _toggle_mode(self, event=None):
        """切换快速/详细模式 (F1键)"""
        self.fast_mode = not self.fast_mode
        new_title = "OBS Vector Debug Console [快速模式]" if self.fast_mode else "OBS Vector Debug Console [详细模式]"
        if self.root:
            self.root.title(new_title)

        # 显示模式切换信息
        mode_text = "快速模式" if self.fast_mode else "详细模式"
        self.log(f"\n=== 切换到{mode_text} ===\n", 'yellow')

    def _check_queue(self):
        try:
            # 大幅增加批量处理消息数量，提高显示速度
            processed = 0
            max_process = 100  # 每次最多处理100条消息

            # 批量收集消息，减少GUI更新次数
            messages_to_process = []
            while not self.queue.empty() and processed < max_process:
                try:
                    message, color = self.queue.get_nowait()
                    messages_to_process.append((message, color))
                    processed += 1
                except queue.Empty:
                    break

            # 一次性更新GUI
            if messages_to_process and self.text_area and self.text_area.winfo_exists(
            ):
                self.text_area.config(state='normal')

                for message, color in messages_to_process:
                    if message == "__CLEAR__":
                        self.text_area.delete('1.0', tk.END)
                    else:
                        self.text_area.insert(tk.END, message, (color, ))

                self.text_area.config(state='disabled')
                self.text_area.see(tk.END)
                # 强制更新显示
                self.text_area.update_idletasks()
        except queue.Empty:
            pass
        except tk.TclError:
            # 窗口已关闭，停止处理
            return
        finally:
            if self.root and self.root.winfo_exists():
                # 减少检查间隔，提高响应速度
                self.root.after(20, self._check_queue)  # 20ms检查一次

    def log(self, message, color='black'):
        """向队列中添加消息，线程安全"""
        try:
            if self.root and self.gui_ready.is_set():
                self.queue.put((message, color))
        except:
            pass  # 静默忽略GUI相关错误

    def clear(self):
        """清空显示内容"""
        try:
            if self.root and self.gui_ready.is_set():
                self.queue.put(("__CLEAR__", None))
        except:
            pass  # 静默忽略GUI相关错误

    def update_obs(self, current_obs, step_count, item_list, tasks):
        """接收新的观测数据并更新调试窗口
        
        Args:
            current_obs: 当前观测向量
            step_count: 步骤计数
            item_list: 物品列表
            tasks: 任务列表
        """
        # 如果未启用，直接返回
        if not self.enabled:
            return

        self._step_count = step_count
        self._current_item_list = item_list  # 保存当前物品列表

        # 如果GUI不可用，回退到控制台输出
        if not self.gui_ready.is_set():
            self._console_output(current_obs, step_count, item_list, tasks)
            return
            return

        self.clear()

        if self.fast_mode:
            self._fast_update(current_obs, step_count)
            # 在快速模式下也显示详细模式的摘要信息
            self.log("\n--- 详细信息摘要 ---\n", 'blue')
            self._brief_detailed_summary(current_obs, item_list, tasks)
        else:
            # 先显示快速模式信息
            self._fast_update(current_obs, step_count)
            self.log("\n--- 详细观测信息 ---\n", 'blue')

            if self._previous_obs is None:
                self.log("Storing initial observation vector...\n")
                self._decode_and_log_obs(current_obs, None, item_list, tasks)
            else:
                self.log("Comparing with previous observation vector...\n")
                self._decode_and_log_obs(current_obs, self._previous_obs,
                                         item_list, tasks)

        self._previous_obs = current_obs.copy()
        if not self.fast_mode:
            self.log("\nUpdated history for next step comparison.\n", 'green')

    def _brief_detailed_summary(self, current_obs, item_list, tasks):
        """在快速模式下显示的详细信息摘要"""
        start_idx = 0

        active_items = [
            item for item in item_list if not isinstance(item, Counter)
        ]

        self.log(f"活跃物品数量: {len(active_items)}\n", 'green')

        for item in active_items[:5]:  # 只显示前5个物品
            item_obs = item.get_obs()
            item_info = f"{item.__class__.__name__}(ID:{item.unique_id})"
            self.log(f"  {item_info}: 长度={len(item_obs)}\n", 'black')

        if len(active_items) > 5:
            self.log(f"  ... 还有 {len(active_items) - 5} 个物品\n", 'black')

    def _fast_update(self, current_obs, step_count):
        """快速更新模式，显示详细的物品变化信息"""
        header = f"=== OBS Debug - Step {step_count} ===\n"
        self.log(header, 'blue')

        if self._previous_obs is None:
            self.log(f"初始观测 - 长度: {len(current_obs)}\n", 'green')
        else:
            # 快速差异检测 + 物品映射
            differences = []
            item_changes = {}  # 按物品分组的变化

            min_len = min(len(current_obs), len(self._previous_obs))

            for i in range(min_len):
                if abs(current_obs[i] - self._previous_obs[i]) > 1e-9:
                    differences.append({
                        "index":
                        i,
                        "previous":
                        self._previous_obs[i],
                        "current":
                        current_obs[i],
                        "diff":
                        current_obs[i] - self._previous_obs[i]
                    })

            # 将差异按物品分组
            if differences:
                item_list = self._get_current_item_list()
                for diff in differences:
                    item_info, field_name = self._map_index_to_item(
                        diff['index'], item_list)

                    if item_info not in item_changes:
                        item_changes[item_info] = []

                    item_changes[item_info].append({
                        'field': field_name,
                        'diff': diff
                    })

                # 显示按物品分组的变化
                self.log(
                    f"发现 {len(differences)} 个变化，涉及 {len(item_changes)} 个物品:\n",
                    'yellow')

                for item_info, changes in item_changes.items():
                    self.log(f"  🔸 {item_info}:\n", 'blue')
                    for change in changes[:3]:  # 每个物品最多显示3个变化
                        field = change['field']
                        diff = change['diff']
                        self.log(
                            f"    {field}: {diff['previous']:8.4f} -> {diff['current']:8.4f} ({diff['diff']:+8.4f})\n",
                            'red')

                    if len(changes) > 3:
                        self.log(f"    ... 还有 {len(changes) - 3} 个字段变化\n",
                                 'red')
            else:
                self.log("无变化\n", 'green')

        self.log(f"观测长度: {len(current_obs)}\n", 'black')

    def _get_current_item_list(self):
        """获取当前物品列表"""
        return getattr(self, '_current_item_list', [])

    def _map_index_to_item(self, index, item_list):
        """将观测向量索引映射到具体物品和字段"""
        current_idx = 0

        # 遍历所有物品
        for item in item_list:
            #if isinstance(item, Counter):
            #    continue

            item_obs_len = len(item.get_obs())

            if current_idx <= index < current_idx + item_obs_len:
                # 找到对应的物品
                field_index = index - current_idx
                field_name = self._get_field_name(item, field_index)
                item_info = f"{item.__class__.__name__}(ID:{item.unique_id})"
                return item_info, field_name

            current_idx += item_obs_len

        # 如果没找到，可能是任务编码部分
        return "Task", f"task_bit_{index - current_idx}"

    def _console_output(self, current_obs, step_count, item_list, tasks):
        """控制台输出备选方案"""
        print(f"\n=== OBS Debug Console - Step {step_count} ===")
        print(f"观测向量长度: {len(current_obs)}")

        if self._previous_obs is None:
            print("存储初始观测向量...")
            self._previous_obs = current_obs.copy()
        else:
            # 简单的差异检测
            differences = []
            min_len = min(len(current_obs), len(self._previous_obs))

            for i in range(min_len):
                if abs(current_obs[i] - self._previous_obs[i]) > 1e-9:
                    differences.append({
                        "index":
                        i,
                        "previous":
                        self._previous_obs[i],
                        "current":
                        current_obs[i],
                        "diff":
                        current_obs[i] - self._previous_obs[i]
                    })

            if differences:
                print(f"发现 {len(differences)} 个差异:")
                for diff in differences[:10]:  # 只显示前10个差异
                    print(
                        f"  [{diff['index']:03d}]: {diff['previous']:8.4f} -> {diff['current']:8.4f} (差值: {diff['diff']:+8.4f})"
                    )
                if len(differences) > 10:
                    print(f"  ... 还有 {len(differences) - 10} 个差异")
            else:
                print("观测向量无变化")

            self._previous_obs = current_obs.copy()
        print("=" * 50)

    def _get_field_name(self, item, index):
        """根据物品类型和索引，推断观测字段的名称"""
        base_fields = ["x", "y", "unique_id"]
        if index < len(base_fields):
            return base_fields[index]

        idx = index - len(base_fields)

        if isinstance(item, Agent):
            # Agent特有字段：手持状态、手持物品类型、手持物品实例ID、移动状态
            agent_fields = ["holding_id"]
            if idx < len(agent_fields):
                return agent_fields[idx]
        elif isinstance(item, Food):
            food_fields = [
                "container_id", "chop_progress", "cook_progress",
                "burn_progress"
            ]
            if idx < len(food_fields): return food_fields[idx]
        elif isinstance(item, Plate):
            plate_fields = ["container_id", "wash_progress"
                            ] + [f"item_{i+1}_id" for i in range(4)]
            if idx < len(plate_fields): return plate_fields[idx]
        elif isinstance(item, FixedItem):
            fixed_fields = ["holding_id"]
            if idx < len(fixed_fields): return fixed_fields[idx]
        elif isinstance(item, MovableItem):
            movable_fields = ["container_id"]
            if idx < len(movable_fields): return movable_fields[idx]

        return f"unknown_field_{idx}"

    def _decode_and_log_obs(self, current_obs, previous_obs, item_list, tasks):
        """解码、比较并记录观测向量"""
        start_idx = 0

        min_len = min(len(current_obs), len(
            previous_obs)) if previous_obs is not None else len(current_obs)

        # 1. 解码物品部分
        for item in item_list:
            #if isinstance(item, Counter):
            #    continue

            item_obs_len = len(item.get_obs())
            header = f"\n--- {item.__class__.__name__} (ID:{item.unique_id}) ---\n"
            self.log(header, 'yellow')

            for i in range(item_obs_len):
                idx = start_idx + i
                if idx >= len(current_obs): continue

                field_name = self._get_field_name(item, i)
                current_val = current_obs[idx]

                log_color = 'black'
                prev_val_str = ""

                if previous_obs is not None and (
                        idx >= min_len
                        or abs(current_val - previous_obs[idx]) > 1e-9):
                    log_color = 'red'
                    prev_val_str = f" (was {previous_obs[idx]:.4f})" if idx < min_len else " (new field)"

                log_msg = f"  [{idx:03d}] {field_name:<20s}: {current_val:.4f}{prev_val_str}\n"
                self.log(log_msg, log_color)

            start_idx += item_obs_len

        # 2. 解码任务部分
        # 从tasks中提取one-hot编码
        one_hot_task = []
        if tasks:
            for task in tasks:
                task_encoding = task.get("task_encoding", [])
                one_hot_task.extend(task_encoding)

        task_len = len(one_hot_task)
        if task_len > 0:
            self.log("\n--- Task Encoding ---\n", 'blue')
            for i in range(task_len):
                idx = start_idx + i
                if idx >= len(current_obs): continue

                current_val = current_obs[idx]
                log_color = 'black'
                prev_val_str = ""

                if previous_obs is not None and (
                        idx >= min_len
                        or abs(current_val - previous_obs[idx]) > 1e-9):
                    log_color = 'red'
                    prev_val_str = f" (was {previous_obs[idx]:.4f})" if idx < min_len else " (new field)"

                log_msg = f"  [{idx:03d}] Task Bit {i:<13d}: {current_val:.4f}{prev_val_str}\n"
                self.log(log_msg, log_color)

    def close(self):
        if self.root:
            self.root.quit()
            self.root.destroy()
