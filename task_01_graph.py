import networkx as nx
import matplotlib.pyplot as plt

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box


console = Console()


def build_network_topology() -> nx.Graph:
    """
    Топологія невеликої мережі: квартира/малий офіс.
    Вузли = пристрої, ребра = з'єднання (кабель/Wi-Fi).
    """
    G = nx.Graph()

    # Вузли (типи пристроїв)
    nodes = [
        ("ISP", {"type": "internet"}),

        ("Router", {"type": "router"}),
        ("Switch", {"type": "switch"}),

        ("AP_1", {"type": "wifi_ap"}),
        ("AP_2", {"type": "wifi_ap"}),

        ("NAS", {"type": "server"}),
        ("HomeServer", {"type": "server"}),

        ("Laptop_1", {"type": "client"}),
        ("Laptop_2", {"type": "client"}),
        ("PC", {"type": "client"}),

        ("Phone_1", {"type": "client"}),
        ("Phone_2", {"type": "client"}),
        ("TV", {"type": "client"}),
        ("Printer", {"type": "client"}),

        ("IoT_Hub", {"type": "iot"}),
        ("Camera_1", {"type": "iot"}),
        ("Camera_2", {"type": "iot"}),
    ]
    G.add_nodes_from(nodes)

    # Ребра (з'єднання)
    edges = [
        ("ISP", "Router", {"kind": "wan", "speed_mbps": 1000}),
        ("Router", "Switch", {"kind": "ethernet", "speed_mbps": 1000}),

        ("Switch", "AP_1", {"kind": "ethernet", "speed_mbps": 1000}),
        ("Switch", "AP_2", {"kind": "ethernet", "speed_mbps": 1000}),

        ("Switch", "NAS", {"kind": "ethernet", "speed_mbps": 1000}),
        ("Switch", "HomeServer", {"kind": "ethernet", "speed_mbps": 1000}),
        ("Switch", "PC", {"kind": "ethernet", "speed_mbps": 1000}),
        ("Switch", "Printer", {"kind": "ethernet", "speed_mbps": 100}),

        ("AP_1", "Laptop_1", {"kind": "wifi", "speed_mbps": 600}),
        ("AP_1", "Phone_1", {"kind": "wifi", "speed_mbps": 300}),
        ("AP_1", "TV", {"kind": "wifi", "speed_mbps": 300}),

        ("AP_2", "Laptop_2", {"kind": "wifi", "speed_mbps": 600}),
        ("AP_2", "Phone_2", {"kind": "wifi", "speed_mbps": 300}),

        ("AP_2", "IoT_Hub", {"kind": "wifi", "speed_mbps": 150}),
        ("IoT_Hub", "Camera_1", {"kind": "wifi", "speed_mbps": 50}),
        ("IoT_Hub", "Camera_2", {"kind": "wifi", "speed_mbps": 50}),
    ]
    G.add_edges_from((u, v, attrs) for u, v, attrs in edges)

    return G


def analyze_graph(G: nx.Graph) -> None:
    """Аналіз основних характеристик графа + вивід через rich."""
    n = G.number_of_nodes()
    m = G.number_of_edges()

    degrees = dict(G.degree())
    avg_degree = sum(degrees.values()) / n
    density = nx.density(G)
    components = list(nx.connected_components(G))

    max_deg = max(degrees.values())
    hubs = [node for node, d in degrees.items() if d == max_deg]

    console.print(
        Panel.fit(
            f"[bold]Аналіз графа: інтернет-топологія (домашня/офісна мережа)[/bold]\n"
            f"• Вершини (пристрої): [bold]{n}[/bold]\n"
            f"• Ребра (зв'язки):   [bold]{m}[/bold]\n"
            f"• Середній ступінь:  [bold]{avg_degree:.2f}[/bold]\n"
            f"• Щільність графа:   [bold]{density:.4f}[/bold]\n"
            f"• Компоненти зв'яз.: [bold]{len(components)}[/bold]",
            box=box.ROUNDED,
        )
    )

    table = Table(title="Ступінь вершин (degree) — скільки прямих з'єднань має пристрій", box=box.SIMPLE_HEAVY)
    table.add_column("Пристрій", style="bold")
    table.add_column("Тип", justify="left")
    table.add_column("Degree", justify="right")

    for node, d in sorted(degrees.items(), key=lambda x: (-x[1], x[0])):
        table.add_row(node, str(G.nodes[node].get("type", "-")), str(d))

    console.print(table)

    console.print(
        Panel.fit(
            f"Найбільша кількість прямих з’єднань = [bold]{max_deg}[/bold]",
            box=box.ROUNDED,
        )
    )


def visualize_graph(G: nx.Graph) -> None:
    """Візуалізація графа з підписами вузлів та ребер."""
    plt.figure(figsize=(12, 7))

    pos = nx.spring_layout(G, seed=42)

    base_size = {
        "internet": 900,
        "router": 1200,
        "switch": 1200,
        "wifi_ap": 1000,
        "server": 950,
        "client": 700,
        "iot": 650,
    }
    node_sizes = [base_size.get(G.nodes[n].get("type", "client"), 700) for n in G.nodes()]

    nx.draw_networkx_nodes(G, pos, node_size=node_sizes, alpha=0.95)
    nx.draw_networkx_edges(G, pos, width=2, alpha=0.7)
    nx.draw_networkx_labels(G, pos, font_size=9)

    edge_labels = {(u, v): G.edges[u, v]["kind"] for u, v in G.edges()}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)

    plt.title("Модель реальної мережі: пристрої (вузли) та з'єднання (ребра)")
    plt.axis("off")
    plt.tight_layout()
    plt.show()


def main() -> None:
    G = build_network_topology()

    analyze_graph(G)
    visualize_graph(G)


if __name__ == "__main__":
    main()
