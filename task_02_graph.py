import networkx as nx
import matplotlib.pyplot as plt

from collections import deque

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


def neighbors_sorted(G: nx.Graph, node: str) -> list[str]:
    """Повертає відсортований список сусідів вузла."""
    return sorted(G.neighbors(node))


def reconstruct_path(parent: dict, start: str, goal: str) -> list[str]:
    """Відновлення шляху з батьківської мапи."""
    if goal not in parent:
        return []
    cur = goal
    path = []
    while cur is not None:
        path.append(cur)
        cur = parent[cur]
    path.reverse()
    return path if path and path[0] == start else []


def bfs_path(G: nx.Graph, start: str, goal: str) -> tuple[list[str], list[str]]:
    """Пошук шляху BFS (черга) з відстеженням порядку відвідування."""
    q = deque([start])
    parent = {start: None}
    visit_order = []

    while q:
        v = q.popleft()
        visit_order.append(v)

        if v == goal:
            break

        for nb in neighbors_sorted(G, v):
            if nb not in parent:
                parent[nb] = v
                q.append(nb)

    return reconstruct_path(parent, start, goal), visit_order


def dfs_path(G: nx.Graph, start: str, goal: str) -> tuple[list[str], list[str]]:
    """Пошук шляху DFS (стек) з відстеженням порядку відвідування."""
    stack = [start]
    parent = {start: None}
    visit_order = []

    while stack:
        v = stack.pop()
        visit_order.append(v)

        if v == goal:
            break

        nbs = neighbors_sorted(G, v)
        for nb in reversed(nbs):
            if nb not in parent:
                parent[nb] = v
                stack.append(nb)

    return reconstruct_path(parent, start, goal), visit_order


def path_str(path: list[str]) -> str:
    """Форматований рядок шляху або повідомлення про відсутність."""
    return " → ".join(path) if path else "[red]Шлях не знайдено[/red]"


def print_compare(start: str, goal: str, bfs_p: list[str], dfs_p: list[str]) -> None:
    """Порівняння шляхів, знайдених BFS і DFS, з поясненням різниці."""
    table = Table(title="Порівняння шляхів (BFS vs DFS)", box=box.SIMPLE_HEAVY)
    table.add_column("Алгоритм", style="bold")
    table.add_column("Довжина (ребер)", justify="right")
    table.add_column("Шлях", overflow="fold")

    table.add_row("BFS", str(max(0, len(bfs_p) - 1)), path_str(bfs_p))
    table.add_row("DFS", str(max(0, len(dfs_p) - 1)), path_str(dfs_p))

    console.print(table)

    console.print(
        Panel.fit(
            "[bold]Чому шляхи можуть відрізнятись?[/bold]\n"
            "• [bold]BFS[/bold] (черга) обходить граф рівнями: 1 крок від старту, потім 2, 3…\n"
            "  У неваговому графі це дає шлях з мінімальною кількістю ребер.\n"
            "• [bold]DFS[/bold] (стек) йде вглиб: обирає перший доступний напрям і “пірнає” до кінця.\n"
            "  Тому повертає перший знайдений шлях, який залежить від порядку сусідів (у нас він фіксований через sorted()).",
            box=box.ROUNDED,
        )
    )


def print_visit_order_table(bfs_order: list[str], dfs_order: list[str]) -> None:
    """Вивід таблиці порядку відвідування вершин BFS і DFS."""
    table = Table(title="Visit Order (порядок відвідування вершин)", box=box.SIMPLE_HEAVY)
    table.add_column("Крок", justify="right", style="dim")
    table.add_column("BFS (черга)", style="bold")
    table.add_column("DFS (стек)", style="bold")

    max_len = max(len(bfs_order), len(dfs_order))
    for i in range(max_len):
        b = bfs_order[i] if i < len(bfs_order) else ""
        d = dfs_order[i] if i < len(dfs_order) else ""
        table.add_row(str(i + 1), b, d)

    console.print(table)


def main() -> None:
    G = build_network_topology()

    start, goal = "ISP", "Camera_1"

    bfs_p, bfs_order = bfs_path(G, start, goal)
    dfs_p, dfs_order = dfs_path(G, start, goal)

    console.print(
        Panel.fit(
            f"[bold]DFS і BFS: пошук шляху в мережевому графі[/bold]\n"
            f"Start: [cyan]{start}[/cyan]\n"
            f"Goal:  [cyan]{goal}[/cyan]",
            box=box.ROUNDED,
        )
    )

    print_visit_order_table(bfs_order, dfs_order)
    print_compare(start, goal, bfs_p, dfs_p)

    visualize_graph(G)


if __name__ == "__main__":
    main()
