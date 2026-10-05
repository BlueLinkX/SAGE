# NumPy 2.x compatibility: older gym/gymnasium code may reference np.bool8
import numpy as _np
if not hasattr(_np, "bool8"):
    _np.bool8 = _np.bool_  # type: ignore[attr-defined]

from gym.envs.registration import register
import pathlib

# Automatically determine the base module path for Gym registration
if __package__:
    base_prefix = __package__
else:
    # Fallback: infer base prefix from the file system path
    path = pathlib.Path(__file__).resolve()
    parts = path.parts
    try:
        idx = parts.index("overcookedPlus")
        base_prefix = ".".join(parts[i] for i in range(idx - 1, idx + 1))
    except ValueError:
        raise RuntimeError(
            "Cannot determine base prefix for Gym environment registration.")

# Register the standard Overcooked-Plus environment
register(
    id="Overcooked-Plus",
    entry_point=f"{base_prefix}.overcooked_env:OvercookedPlus",
)

# Register the graph-based Overcooked-Plus environment
register(
    id="Overcooked-Plus-Graph",
    entry_point=
    f"{base_prefix}.overcooked_env_with_graph:OvercookedEnvWithGraph",
)

# Optional: print to confirm successful registration
import logging

logger = logging.getLogger(__name__)
logger.debug("Registered Gym environments with entry_point base: %s",
             base_prefix)
