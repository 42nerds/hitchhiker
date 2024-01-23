import json

import click
import click_odoo
import matplotlib.pyplot as plt
import networkx as nx


@click.command()
@click_odoo.env_options(default_log_level="error")
@click.option("--say-hello", is_flag=True)
def main(env, say_hello):
    graph = nx.MultiDiGraph()
    cytoscape = {"elements": []}
    nodesize = {}
    for u in env["ir.module.module"].search([("state", "=", "installed")]):
        if u.name not in nodesize:
            nodesize[u.name] = 1
            graph.add_node(u.name)
            cytoscape["elements"].append({"data": {"id": u.name, "grabbable": True}})
        for dependency in u.dependencies_id.mapped(lambda x: x.name):
            if dependency not in nodesize:
                cytoscape["elements"].append(
                    {"data": {"id": dependency, "grabbable": True}}
                )
                graph.add_node(dependency)
            graph.add_edge(dependency, u.name)
            cytoscape["elements"].append(
                {
                    "data": {
                        "id": f"e-{u.name}-{dependency}",
                        "source": dependency,
                        "target": u.name,
                    }
                }
            )

    pos = nx.drawing.nx_agraph.graphviz_layout(graph, prog="dot")

    plt.figure(3, figsize=(25, 10))
    nx.draw(
        graph, pos, node_size=[nodesize[n] * 3000 for n in list(graph)], node_shape="s"
    )
    for k, v in pos.items():
        x, y = v
        plt.text(x, y, k, ha="center", va="center")
    plt.draw()
    plt.savefig("test.svg")
    plt.savefig("test.png")
    print(json.dumps(cytoscape))


if __name__ == "__main__":
    main()
