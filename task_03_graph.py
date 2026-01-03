import heapq
import networkx as nx

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

    add_edge_weights(G)
    return G


def add_edge_weights(G: nx.Graph) -> None:
    """Додає weight до кожного ребра: weight = 1 / speed_mbps."""
    for u, v, data in G.edges(data=True):
        speed = int(data.get("speed_mbps", 1))
        speed = max(speed, 1)
        data["weight"] = 1.0 / speed


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
            f"• Компоненти зв'яз.: [bold]{len(components)}[/bold]\n",
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


def dijkstra_from_source(G: nx.Graph, start: str) -> dict[str, float]:
    """Дейкстра: з однієї вершини до всіх інших (по weight)."""
    dist = {node: float("inf") for node in G.nodes()}
    dist[start] = 0.0

    pq = [(0.0, start)]  # (distance, node)

    while pq:
        cur_dist, u = heapq.heappop(pq)
        if cur_dist > dist[u]:
            continue

        for v in G.neighbors(u):
            w = float(G.edges[u, v].get("weight", 1.0))
            nd = cur_dist + w
            if nd < dist[v]:
                dist[v] = nd
                heapq.heappush(pq, (nd, v))

    return dist


def all_pairs_shortest_distances(G: nx.Graph) -> dict[str, dict[str, float]]:
    """
    Найкоротші відстані між всіма вершинами:
    запускаємо Дейкстру для кожної вершини як стартової.
    """
    result = {}
    for start in G.nodes():
        result[start] = dijkstra_from_source(G, start)
    return result


def print_distance_matrix(G: nx.Graph, all_pairs: dict[str, dict[str, float]]) -> None:
    """Матриця найкоротших відстаней (сума weight) через rich."""
    nodes = list(G.nodes())

    table = Table(
        title="Матриця найкоротших відстаней (Дейкстра, weight = 1/speed_mbps)",
        box=box.SIMPLE_HEAVY,
        show_lines=False,
    )
    table.add_column("From/To", style="bold", no_wrap=True)

    for n in nodes:
        table.add_column(n, justify="right", no_wrap=True)

    for src in nodes:
        row = [src]
        for dst in nodes:
            d = all_pairs[src][dst]
            row.append("0" if src == dst else f"{d:.4f}")
        table.add_row(*row)

    console.print(table)


def main() -> None:
    G = build_network_topology()

    analyze_graph(G)

    all_pairs = all_pairs_shortest_distances(G)
    print_distance_matrix(G, all_pairs)


if __name__ == "__main__":
    main()
