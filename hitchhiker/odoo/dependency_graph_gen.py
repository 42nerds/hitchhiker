from __future__ import annotations

from typing import Any

from jinja2 import Environment, PackageLoader, select_autoescape


def gen_dependency_graph(
    loc_modules: dict[str, int], modules: list[tuple[str, list[str]]]
) -> str:
    cytoscape: dict[str, Any] = {"elements": []}
    added_mods = []

    def add_node(name: str) -> None:
        if name in added_mods:
            return
        added_mods.append(name)
        cytoscape["elements"].append(
            {
                "data": {
                    "id": name,
                    "label": name
                    + (f" - LOC: {loc_modules[name]}" if name in loc_modules else ""),
                    "grabbable": True,
                    "weight": loc_modules[name] if name in loc_modules else 0,
                }
            }
        )

    for module, dependencies in modules:
        if module in added_mods:
            continue
        add_node(module)
        for dependency in dependencies:
            if dependency not in added_mods:
                add_node(dependency)
            cytoscape["elements"].append(
                {
                    "data": {
                        "id": f"e-{module}-{dependency}",
                        "source": module,
                        "target": dependency,
                    }
                }
            )

    env = Environment(
        loader=PackageLoader("hitchhiker", "data/templates"),
        autoescape=select_autoescape(),
    )
    return env.get_template("dependency_graph.html.j2").render(
        json_data=cytoscape,
        max_loc=str(max(loc_modules.values())) if len(loc_modules) > 0 else "0",
    )
