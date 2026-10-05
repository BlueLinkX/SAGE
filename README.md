# SAGE
SAGE: Semantic-Aware Gray-Box Game Regression Testing with Large Language Models

## Overcooked Plus scenarios

The [Overcooked Plus environment](scenarios/overcooked_plus) provides 37 cooking
tasks, maps, rendering assets, bug predicates and a minimal interaction example.
See the [scenario README](scenarios/overcooked_plus/README.md) for the environment
interface, task settings and checks.

Clone this repository, then run with Python 3.10.14 and tkinter available:

```sh
git clone https://github.com/BlueLinkX/SAGE.git
cd SAGE/scenarios/overcooked_plus
python -m pip install -r requirements.txt
python -B example.py
```

Alternatively, [download the repository ZIP](https://github.com/BlueLinkX/SAGE/archive/refs/heads/main.zip),
extract it and open `scenarios/overcooked_plus`.

This release provides the experimental scenarios. The SAGE method implementation
and experiment datasets will be released separately.
