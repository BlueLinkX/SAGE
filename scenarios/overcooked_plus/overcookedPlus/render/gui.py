import os
import sys

import pygame
import numpy as np
import pygame.surfarray as surfarray

from .utils import *
from ..items import (
    Plate,
    Knife,
    Delivery,
    Agent,
    Food,
    Pan,
    RiceCooker,
    Sink,
    Counter,
    Block,
    MovableItem,
    FixedItem,
    Oven,
)
from ..constants import *

graphics_dir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "graphics"))


class GUI:
    """
    优化后的GUI类：
    1) 统一图片加载：convert_alpha() + 规范化 key + 尺寸缓存
    2) 静态背景与 screen 的像素格式对齐 + 预计算网格像素坐标
    3) 背景 Surface 与 cell Surface 统一 convert；cell Surface 复用而不是新建
    4) 只更新"脏矩形"，避免整屏 flip()
    """

    # 全局级别的图片缓存（所有 GUI 实例共享）
    _image_library = {}  # canonical_path -> Surface(convert_alpha)
    _scaled_library = {}  # (canonical_path, (w,h)) -> Surface(convert_alpha)

    @staticmethod
    def _canon(path: str) -> str:
        """规范化路径，统一使用操作系统的路径分隔符"""
        return os.path.normpath(path)

    @classmethod
    def _get_image(cls, path: str):
        """加载原始图片（convert_alpha），按规范化路径缓存"""
        key = cls._canon(path)
        surf = cls._image_library.get(key)
        if surf is None:
            if os.path.exists(key):
                try:
                    img = pygame.image.load(key)
                    # 统一使用 convert_alpha() 以支持透明度
                    surf = img.convert_alpha()
                    cls._image_library[key] = surf
                except pygame.error:
                    return None
            else:
                return None
        return surf

    @classmethod
    def _get_scaled(cls, path: str, size):
        """返回指定尺寸的已缩放 Surface，并按 (path,size) 缓存"""
        w, h = int(size[0]), int(size[1])
        key = (cls._canon(path), (w, h))
        surf = cls._scaled_library.get(key)
        if surf is None:
            base = cls._get_image(path)
            if base is None:
                return None
            try:
                scaled = pygame.transform.scale(base, (w, h))
                # 缩放后也使用 convert_alpha() 保持格式一致
                scaled = scaled.convert_alpha()
                cls._scaled_library[key] = scaled
                return scaled
            except pygame.error:
                return None
        return surf

    @staticmethod
    def _to_int_size(size):
        """确保尺寸为整数"""
        return (int(size[0]), int(size[1]))

    @classmethod
    def _create_fallback_surface(cls, size, color=(255, 0, 255)):
        """创建备用的彩色方块 surface（带 alpha）"""
        surf = pygame.Surface(cls._to_int_size(size), pygame.SRCALPHA)
        surf = surf.convert_alpha()
        surf.fill(color)
        return surf

    def __init__(self, env, headless=False):
        self._running = True
        self.env = env
        self.headless = headless

        # Visual parameters
        self.scale = 80  # num pixels per tile
        self.holding_scale = 0.5
        self.container_scale = 0.7
        self.height = self.scale * self.env.xlen
        self.width = self.scale * self.env.ylen
        self.tile_size = (self.scale, self.scale)
        self.holding_size = (int(self.holding_scale * self.scale),
                             int(self.holding_scale * self.scale))
        self.container_size = (int(self.container_scale * self.scale),
                               int(self.container_scale * self.scale))
        self.holding_container_size = (
            int(self.container_scale * self.holding_size[0]),
            int(self.container_scale * self.holding_size[1]),
        )

        # 状态/缓存
        self._last_state_hash = None
        self._cached_rgb = None
        self._background_surface = None  # 静态背景（convert）
        self._dynamic_surface = None  # 动态叠加层（全尺寸，convert_alpha）
        self._cell_hash = {}  # (x,y) -> hash
        self._cell_surface_pool = []  # Surface 复用池
        self._cell_surface_map = {}  # (x,y) -> Surface(tile_size, alpha)
        self._dirty_rects = []  # 本帧变更的矩形列表

        # 预加载图像
        pygame.init()
        pygame.font.init()

        if not headless:
            self.screen = pygame.display.set_mode((self.width, self.height))
            # 与显示缓冲对齐像素格式
        else:
            self.screen = pygame.Surface((self.width, self.height))

        # 预计算像素坐标，避免频繁计算
        # 坐标约定：env 坐标 (x, y) => 屏幕像素 (y * scale, x * scale)
        self._pixel_coords = {}
        for x in range(self.env.xlen):
            for y in range(self.env.ylen):
                self._pixel_coords[(x, y)] = (y * self.scale, x * self.scale)

        # 动态层初始化，与 screen 像素格式对齐
        self._dynamic_surface = pygame.Surface((self.width, self.height),
                                               pygame.SRCALPHA)
        try:
            # convert_alpha may fail when no video mode is set (headless)
            self._dynamic_surface = self._dynamic_surface.convert_alpha()
        except pygame.error:
            pass

        # 初始化 cell surface 池
        self._init_cell_surface_pool()

        # 标记需要初始完整渲染
        self._needs_full_render = True

        self._preload_images()

    def _init_cell_surface_pool(self):
        """初始化 cell surface 复用池"""
        # 预创建一些 cell surface 供复用
        pool_size = min(20, self.env.xlen * self.env.ylen)
        for _ in range(pool_size):
            surf = pygame.Surface(self.tile_size, pygame.SRCALPHA)
            try:
                surf = surf.convert_alpha()
            except pygame.error:
                # headless 模式下可能未设置 video mode，忽略
                pass
            self._cell_surface_pool.append(surf)

    def _get_cell_surface(self, key):
        """获取或创建 cell surface，优先从池中复用"""
        if key in self._cell_surface_map:
            return self._cell_surface_map[key]

        if self._cell_surface_pool:
            surf = self._cell_surface_pool.pop()
            surf.fill((0, 0, 0, 0))  # 清空内容
        else:
            surf = pygame.Surface(self.tile_size, pygame.SRCALPHA)
            try:
                surf = surf.convert_alpha()
            except pygame.error:
                # headless 模式下忽略
                pass

        self._cell_surface_map[key] = surf
        return surf

    def _return_cell_surface(self, key):
        """将 cell surface 返回到池中以供复用"""
        if key in self._cell_surface_map:
            surf = self._cell_surface_map.pop(key)
            if len(self._cell_surface_pool) < 20:  # 限制池大小
                self._cell_surface_pool.append(surf)

    def _preload_images(self):
        """预加载常用图像（仅入原图缓存，不缩放）"""
        image_names = [
            "delivery", "cutboard", "pan", "oven", "ricecooker", "tomato",
            "lettuce", "onion", "cheese", "dough", "fish", "rice", "steak",
            "plate", "sink", "trash_can", "knife"
        ]
        for color in ["red", "blue", "green", "yellow"]:
            image_names.append(f"agent-{color}")

        for name in image_names:
            path = f"{graphics_dir}/{name}.png"
            self._get_image(path)

    # -------------------- 坐标与位置 --------------------

    def scaled_location(self, loc):
        """loc = (row, col) == (y, x)；返回屏幕像素左上角坐标"""
        y, x = loc
        return self._pixel_coords.get((x, y), (x * self.scale, y * self.scale))

    def holding_location(self, loc):
        y, x = loc
        sx, sy = self.scaled_location(loc)
        return (int(sx + self.scale * (1 - self.holding_scale)),
                int(sy + self.scale * (1 - self.holding_scale)))

    def container_location(self, loc):
        y, x = loc
        sx, sy = self.scaled_location(loc)
        off = self.scale * (1 - self.container_scale) / 2
        return (int(sx + off), int(sy + off))

    def holding_container_location(self, loc):
        sx, sy = self.scaled_location(loc)
        factor = (1 - self.holding_scale
                  ) + (1 - self.container_scale) / 2 * self.holding_scale
        return (int(sx + self.scale * factor), int(sy + self.scale * factor))

    # -------------------- 绘制基础 --------------------

    def _draw_combined_ingredients(self,
                                   target_surf,
                                   ingredients,
                                   size,
                                   location,
                                   scale_factor=0.7):
        """组合食材的应急方案：缩小错位叠放"""
        if not ingredients:
            return
        size = self._to_int_size(size)
        small_size = (int(size[0] * scale_factor), int(size[1] * scale_factor))
        offsets = [(0, 0), (10, 10), (20, 5), (5, 20)]  # 最多 4 个

        fallback_colors = {
            'tomato': (255, 0, 0),
            'lettuce': (0, 255, 0),
            'onion': (255, 255, 0),
            'steak': (139, 69, 19),
            'fish': (0, 100, 255),
            'rice': (255, 255, 255),
            'cheese': (255, 255, 0),
            'dough': (222, 184, 135)
        }

        for i, ing in enumerate(ingredients[:4]):
            ox, oy = offsets[i] if i < len(offsets) else (0, 0)
            draw_loc = (min(location[0] + ox,
                            location[0] + size[0] - small_size[0]),
                        min(location[1] + oy,
                            location[1] + size[1] - small_size[1]))
            img = self._get_scaled(f"{graphics_dir}/{ing}.png", small_size)
            if img is not None:
                target_surf.blit(img, draw_loc)
            else:
                target_surf.blit(
                    self._create_fallback_surface(
                        small_size, fallback_colors.get(ing, (255, 0, 255))),
                    draw_loc)

    def draw(self, path, size, location, screen=None):
        """绘制图像（组合与单一），带缩放缓存与应急回退"""
        target = screen if screen is not None else self.screen
        size = self._to_int_size(size)

        # 组合食材（如 "steak-tomato"）
        if "-" in path:
            ingredients = path.split("-")
            sorted_path = "-".join(sorted(ingredients))
            image_path = f"{graphics_dir}/{sorted_path}.png"
            img = self._get_scaled(image_path, size)
            if img is None:
                self._draw_combined_ingredients(target, ingredients, size,
                                                location)
            else:
                target.blit(img, location)
            return

        # 单一图像
        image_path = f"{graphics_dir}/{path}.png"
        img = self._get_scaled(image_path, size)
        if img is not None:
            target.blit(img, location)
        else:
            target.blit(self._create_fallback_surface(size), location)

    def draw_contained(self, foodlist, size, location, screen=None):
        """绘制容器中的食材，支持应急渲染"""
        target = screen if screen is not None else self.screen
        size = self._to_int_size(size)
        if isinstance(foodlist, list) and len(foodlist) > 1:
            ingredients = [food for food in foodlist if food]
            if ingredients:
                content_name = "-".join(sorted(ingredients))
                self.draw(content_name, size, location, screen=target)
        else:
            veg, meat = foodlist
            if veg:
                self.draw(veg, size, location, screen=target)
            if meat:
                self.draw(meat, size, location, screen=target)

    # -------------------- 场景渲染 --------------------

    def _render_static_background(self):
        """渲染静态背景（FixedItem），只做一次；Surface 用 convert"""
        # 创建与 screen 像素格式一致的背景
        surf = pygame.Surface((self.width, self.height))
        surf = surf.convert()  # 与 screen 格式对齐
        surf.fill(Color.FLOOR)

        # 先画基础方块/台面
        for item in self.env.item_Manager.itemList:
            if not isinstance(item, FixedItem):
                continue
            sl = self.scaled_location((item.y, item.x))
            tile_rect = pygame.Rect(sl[0], sl[1], self.scale, self.scale)
            if isinstance(item, Block):
                pygame.draw.rect(surf, Color.BLOCK, tile_rect)
                pygame.draw.rect(surf, Color.BLOCK_BORDER, tile_rect, 1)
                pygame.draw.line(surf, Color.BLOCK_BORDER,
                                 (tile_rect.left, tile_rect.top),
                                 (tile_rect.right, tile_rect.bottom), 2)
                pygame.draw.line(surf, Color.BLOCK_BORDER,
                                 (tile_rect.right, tile_rect.top),
                                 (tile_rect.left, tile_rect.bottom), 2)
            elif isinstance(item, Counter):
                pygame.draw.rect(surf, Color.COUNTER, tile_rect)
                pygame.draw.rect(surf, Color.COUNTER_BORDER, tile_rect, 1)

        # 再画固定设施贴图（非 Block/Counter）
        for item in self.env.item_Manager.itemList:
            if isinstance(item, FixedItem) and not isinstance(
                    item, (Counter, Block)):
                sl = self.scaled_location((item.y, item.x))
                self.draw(item.name, self.tile_size, sl, screen=surf)

        self._background_surface = surf

    def _draw_items_on_surface(self, items, surface):
        """
        逐格渲染策略：
        1) 先找一个"非 Food"主目标，只画它；
        2) 若没有非 Food，则画 Food（可多画）。
        坐标在 cell 内部，统一从 (0,0) 开始绘制。
        """
        filtered = [
            it for it in items if not (hasattr(it, 'consumed') and it.consumed)
        ]

        priority_order = [
            Agent, Knife, (Pan, RiceCooker, Oven), Delivery, Sink, Plate
        ]
        target = None

        for kind in priority_order:
            if isinstance(kind, tuple):
                found = next((it for it in filtered if isinstance(it, kind)),
                             None)
            else:
                found = next((it for it in filtered if isinstance(it, kind)),
                             None)
            if found is not None:
                target = found
                break

        # 只画主目标
        if target is not None:
            sl = (0, 0)
            if isinstance(target, Agent):
                self.draw(f"agent-{target.color}",
                          self.tile_size,
                          sl,
                          screen=surface)
                if target.holding:
                    self.draw(target.holding.name,
                              self.holding_size,
                              self.holding_location((0, 0)),
                              screen=surface)
                    if isinstance(target.holding,
                                  Plate) and target.holding.containing:
                        self.draw_contained(target.holding.containedName[-2:],
                                            self.holding_container_size,
                                            self.holding_container_location(
                                                (0, 0)),
                                            screen=surface)
                return

            if isinstance(target, Knife):
                if target.holding:
                    self.draw(target.holding.name,
                              self.tile_size,
                              sl,
                              screen=surface)
                    if isinstance(target.holding,
                                  Plate) and target.holding.containing:
                        self.draw_contained(target.holding.containedName[-2:],
                                            self.container_size,
                                            self.container_location((0, 0)),
                                            screen=surface)
                    ing = target.holding
                    if isinstance(
                            ing, Food
                    ) and 0 < ing.cur_chopped_times < ing.required_chopped_times:
                        bar_position = (sl[0] + 5, sl[1] + 7)
                        bar_size = (self.scale - 10, 7)
                        progress = ing.cur_chopped_times / ing.required_chopped_times
                        self.draw_progress_bar(surface, bar_position, bar_size,
                                               progress, Color.PROGRESS_BAR)
                return

            if isinstance(target, (Pan, RiceCooker, Oven)):
                if target.holding:
                    self.draw(target.holding.name,
                              (int(self.scale * 0.9), int(self.scale * 0.9)),
                              (sl[0], sl[1] + 10),
                              screen=surface)
                    ing = target.holding
                    if isinstance(ing, Food):
                        if ing.cur_cooked_times < getattr(
                                ing, 'required_cooked_times', 0):
                            bar_position = (sl[0] + 5, sl[1] + 7)
                            bar_size = (self.scale - 10, 7)
                            progress = ing.cur_cooked_times / max(
                                getattr(ing, 'required_cooked_times', 1), 1)
                            self.draw_progress_bar(surface, bar_position,
                                                   bar_size, progress,
                                                   Color.PROGRESS_BAR)
                        elif hasattr(
                                ing, 'required_burned_times'
                        ) and ing.cur_cooked_times < ing.required_burned_times:
                            bar_position = (sl[0] + 5, sl[1] + 7)
                            bar_size = (self.scale - 10, 7)
                            progress = ing.cur_cooked_times / ing.required_burned_times
                            self.draw_progress_bar(surface, bar_position,
                                                   bar_size, progress,
                                                   Color.PROGRESS_BAR_BG)
                return

            if isinstance(target, Delivery):
                if target.holding:
                    self.draw(target.holding.name,
                              self.tile_size,
                              sl,
                              screen=surface)
                    if isinstance(target.holding,
                                  Plate) and target.holding.containing:
                        self.draw_contained(target.holding.containedName[-2:],
                                            self.container_size,
                                            self.container_location((0, 0)),
                                            screen=surface)
                return

            if isinstance(target, Sink):
                if target.holding:
                    self.draw(target.holding.name,
                              (int(self.scale * 0.6), int(self.scale * 0.6)),
                              (sl[0] + 5, sl[1] + 15),
                              screen=surface)
                    p = target.holding
                    if 0 < p.cur_wash_times < p.required_wash_times:
                        bar_position = (sl[0] + 5, sl[1] + 7)
                        bar_size = (self.scale - 10, 7)
                        progress = p.cur_wash_times / p.required_wash_times
                        self.draw_progress_bar(surface, bar_position, bar_size,
                                               progress, Color.PROGRESS_BAR)
                return

            if isinstance(target, Plate):
                self.draw(target.name, self.tile_size, sl, screen=surface)
                if target.containing:
                    content_names = [f.name for f in target.containing]
                    content_name = "-".join(sorted(content_names))
                    self.draw(content_name,
                              self.container_size,
                              self.container_location((0, 0)),
                              screen=surface)
                return

            return  # 理论上不会到这里

        # 没命中任何非 Food，则画 Food（可多画）
        for it in filtered:
            if isinstance(it, Food):
                if getattr(it, 'container', None) is None or isinstance(
                        it.container, Counter):
                    self.draw(it.name, self.tile_size, (0, 0), screen=surface)

    def _render_dynamic_layer(self):
        """
        用"动态大层"配合脏矩形：
        - 对 changed cell：先清空动态层该 rect，再把新的 cell_surface 画上去，并加入 dirty_rects；
        - 对 unchanged cell：不操作（保留上一帧的图像在动态层上）。
        - 对 now empty 的 cell：清空该 rect 并加入 dirty_rects。
        """
        dirty_rects = []

        # 如果需要完整渲染（首次渲染），强制更新所有cell
        force_update_all = self._needs_full_render
        if self._needs_full_render:
            self._needs_full_render = False

        for x in range(self.env.xlen):
            for y in range(self.env.ylen):
                key = (x, y)
                sl = self._pixel_coords[(x, y)]
                rect = pygame.Rect(sl[0], sl[1], self.scale, self.scale)

                draw_list = self.env.item_Manager.get_items_at(
                    x, y, counter_block_included=False)

                if not draw_list:
                    # 该格现在为空，如之前有内容则清空动态层并标脏
                    if key in self._cell_hash or force_update_all:
                        # 清空动态层对应区域为透明
                        self._dynamic_surface.fill((0, 0, 0, 0), rect)
                        dirty_rects.append(rect)
                        self._cell_hash.pop(key, None)
                        self._return_cell_surface(key)
                    continue

                # 构造轻量哈希
                states = []
                for obj in draw_list:
                    obs = obj.get_obs()
                    states.append((obj.__class__.__name__, tuple(obs)))
                new_hash = hash(tuple(states))

                if self._cell_hash.get(
                        key) == new_hash and not force_update_all:
                    # 未变化且非强制更新：动态层已有上一帧内容，无需重复绘制
                    continue

                # 更新该 cell 的渲染缓存
                cell_surf = self._get_cell_surface(key)
                cell_surf.fill((0, 0, 0, 0))  # 清空内容

                self._draw_items_on_surface(draw_list, cell_surf)
                self._cell_hash[key] = new_hash

                # 先清空动态层对应区域，再把 cell_surf 贴回去
                self._dynamic_surface.fill((0, 0, 0, 0), rect)
                self._dynamic_surface.blit(cell_surf, sl)
                dirty_rects.append(rect)

        return dirty_rects

    def _render_surface(self):
        """主渲染方法：组合静态背景和动态层"""
        if self._background_surface is None:
            self._render_static_background()

        # 先把背景整幅贴到 screen，再叠加动态层一次
        self.screen.blit(self._background_surface, (0, 0))
        self._dirty_rects = self._render_dynamic_layer()

        # 把本帧动态层也叠到 screen 上（一次 blit）
        self.screen.blit(self._dynamic_surface, (0, 0))

    def on_event(self, event):
        """事件处理"""
        if event.type == pygame.QUIT:
            self._running = False

    def on_render(self):
        """渲染并更新显示，使用脏矩形优化"""
        self._render_surface()

        if not self.headless:
            # 绘制任务信息文本（在脏矩形更新之前）
            self.display_info()

            if self._dirty_rects:
                # 文本区域也需要更新
                text_rect = pygame.Rect(0, 0, self.width, 50)  # 文本显示区域
                all_dirty_rects = self._dirty_rects + [text_rect]
                # 只更新脏矩形区域
                pygame.display.update(all_dirty_rects)
            else:
                # 如果没有脏矩形，使用 flip（但通常不会到这里）
                pygame.display.flip()
        return True

    # -------------------- 观测/信息 --------------------

    def _compute_state_hash(self):
        """计算全局状态哈希（用于 get_image_obs 缓存）"""
        state_data = []
        for item in self.env.item_Manager.itemList:
            if isinstance(item, (Counter, Block)):  # 静态不参与
                continue
            obs = item.get_obs()
            state_data.append((item.__class__.__name__, tuple(obs)))
        return hash(tuple(state_data))

    def get_image_obs(self):
        """获取图像观测（RGB），带全局缓存"""
        current_hash = self._compute_state_hash()
        if current_hash == self._last_state_hash and self._cached_rgb is not None:
            return self._cached_rgb

        self._last_state_hash = current_hash
        # 在 offscreen 的 screen 上渲染一次，再抓取像素
        self._render_surface()
        self._cached_rgb = self._convert_surface_to_rgb()
        return self._cached_rgb

    def get_rgb_array(self):
        """获取RGB数组"""
        return self.get_image_obs()

    def _convert_surface_to_rgb(self):
        """将 screen 转为 (H, W, 3) 的 uint8 NumPy 数组"""
        try:
            rgb_array = surfarray.array3d(self.screen)
            rgb_array = np.transpose(rgb_array,
                                     (1, 0, 2))  # (W,H,3) -> (H,W,3)
            return rgb_array.astype(np.uint8)
        except Exception:
            # 兜底（慢）
            img_int = pygame.PixelArray(self.screen)
            img_rgb = np.zeros([img_int.shape[1], img_int.shape[0], 3],
                               dtype=np.uint8)
            for i in range(img_int.shape[0]):
                for j in range(img_int.shape[1]):
                    color = pygame.Color(img_int[i][j])
                    img_rgb[j, i, 0] = color[1]
                    img_rgb[j, i, 1] = color[2]
                    img_rgb[j, i, 2] = color[3]
            del img_int
            return img_rgb

    def draw_progress_bar(self, screen, position, size, progress, color):
        """绘制进度条"""
        full_width, height = self._to_int_size(size)
        progress_width = int(full_width * progress)
        progress_rect = pygame.Rect(position[0], position[1], progress_width,
                                    height)
        pygame.draw.rect(screen, color, progress_rect)

    def display_info(self):
        """在屏幕画面上叠加简单文本信息（优化版本）"""
        if not hasattr(self.env, 'tasks') or not self.env.tasks:
            return

        task_text = "task:" + str(
            [str(task["ingredients"]) for task in self.env.tasks])

        if not pygame.font.get_init():
            pygame.font.init()

        # 缓存字体对象
        if not hasattr(self, '_info_font'):
            self._info_font = pygame.font.Font(None, 18)

        text = self._info_font.render(task_text, True, (0, 0, 0))
        self.screen.blit(text, (20, 20))

    def cleanup(self):
        """清理资源"""
        # 将所有 cell surface 返回到池中
        for key in list(self._cell_surface_map.keys()):
            self._return_cell_surface(key)

        # 清理缓存
        self._cell_hash.clear()

        # 注意：不清理全局图片缓存，因为可能被其他实例使用

    def force_full_render(self):
        """强制下一帧进行完整渲染"""
        self._needs_full_render = True
        self._cell_hash.clear()  # 清空cell哈希，强制重新渲染所有内容
