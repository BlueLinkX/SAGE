from ..constants import ITEMIDX


class ActionWrapper:
    """Wrapper class that encapsulates all state changing actions.

    The wrapper ensures that all changes to the map or item states go through
    a unified interface. It also gives a single place to hook additional logic
    such as cache invalidation for :class:`Item` instances.
    """

    def __init__(self, map_manager):
        self.map_manager = map_manager

    # ------------------------------------------------------------------
    # Basic helpers
    def move(self, item, to_x, to_y):
        """Move ``item`` to ``(to_x, to_y)`` while refreshing the map."""
        self.map_manager.move_item(item, to_x, to_y)
        # ``move_item`` will call ``item.move`` internally which already
        # invalidates caches in ``MovableItem.move``.
        return True

    def pickup(self, agent, item):
        """Agent picks up ``item`` from the map.

        The old tile is reverted back to counter. If the pickup fails the map
        remains unchanged.
        """
        old_x, old_y = item.x, item.y
        success = agent.pickup(item)
        if success:
            # Remove the item from the map. It should leave a counter behind.
            self.map_manager.set_tile(old_x, old_y, ITEMIDX["counter"])
        return success

    def pickup_from_device(self, agent, device):
        """Agent retrieves the item held by ``device``.

        ``device.release`` is responsible for clearing its holding state. No
        map change is required since the device tile remains the same.
        Returns the retrieved item or ``None`` if failed.
        """
        if device.holding and not device.lock:
            item = device.release()
            agent.pickup(item)
            return item
        return None

    # ------------------------------------------------------------------
    # Putdown related helpers
    def place_on_counter(self, agent, counter):
        """Put down the item held by ``agent`` onto ``counter``."""
        item = agent.putdown(counter.x, counter.y)
        if not item:
            return None
        self.map_manager.place_item(item, counter.x, counter.y)
        return item

    def add_to_container(self, agent, container):
        """Add the held item into ``container`` if possible."""
        if not agent.holding:
            return None
        if container.contain(agent.holding):
            item = agent.putdown(container.x, container.y)
            return item
        return None

    def hold_in_device(self, agent, device):
        """Place the held item into ``device`` if allowed."""
        item = agent.holding
        if not item:
            return None
        # Special case: oven only accepts raw food from a plate
        if device.rawName == "oven" and getattr(item, "rawName",
                                                None) == "plate":
            plate = item
            if plate.containing and hasattr(
                    plate.containing[0],
                    'rawName') and not plate.containing[0].cooked:
                food = plate.containing.pop(0)
                plate.invalidate_cache()
                if device.hold(food):
                    food.move(device.x, device.y)
                    return food
                else:
                    plate.containing.insert(0, food)
                    plate.invalidate_cache()
            return None
        if device.hold(item):
            agent.release()
            return item
        return None

    # ------------------------------------------------------------------
    def reset_item(self, item):
        """Refresh an item and place it back to the map at its coordinates."""
        item.refresh()
        self.map_manager.place_item(item, item.x, item.y)

    def transfer_device_to_plate(self, agent, device):
        """Move the item from ``device`` onto the plate held by ``agent``.

        Returns the moved item if successful, otherwise ``None``.
        """
        plate = agent.holding
        if not plate or plate.rawName != "plate":
            return None
        if device.holding and not device.lock and not plate.dirty:
            item = device.holding
            if plate.contain(item):
                device.release()
                return item
        return None
