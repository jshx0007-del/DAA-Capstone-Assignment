# ACADEMIC CAPSTONE PROJECT REPORT

**Course Title:** Design and Analysis of Algorithms (ETCCDA302)  
**Project Title:** Mini-Courier Planner — Intelligent Parcel Prioritization, Packing Optimization and Delivery Route Planning System  
**Institution:** Department of Computer Science & Engineering, K.R. Mangalam University  
**Student Level:** B.Tech Computer Science & Engineering  

---

## Executive Summary

The **Mini-Courier Planner** is an integrated software system that addresses the operational challenges of modern last-mile courier logistics. By synthesizing four foundational computer science algorithmic paradigms—**Divide-and-Conquer (Merge Sort)**, **Dynamic Programming (0/1 Knapsack)**, **Greedy Graph Traversal with Min-Heap (Dijkstra's Algorithm)**, and **Heuristic Route Approximation (Nearest Neighbor TSP)**—the project implements an end-to-end automated logistics planning pipeline.

All algorithmic engines were manually developed from mathematical first principles in Python 3 without reliance on high-level algorithmic libraries (such as built-in sort wrappers, NetworkX shortest-path routines, or external TSP solvers). High-resolution empirical performance benchmarking (`time.perf_counter()`) across small ($n=10$), medium ($n=100$), and large ($n=500$) datasets verified theoretical asymptotic bounds. Both an interactive terminal CLI and a Streamlit web interface were deployed.

---

## Phase 1: Courier Problem Design and Planning

### 1.1 Problem Context & Industry Relevance
In courier hubs (e.g., in Gurugram NCR), packages arrive continuously. Distribution hubs face four key bottlenecks:
1. **Urgency Bottleneck**: High-priority and fast-expiring deliveries must not be delayed by bulk or standard consignments.
2. **Payload Bottleneck**: Delivery vehicles have physical payload limits ($W$ kg). Loading sub-optimally wastes vehicle trips or breaches safety regulations.
3. **Road Distance Bottleneck**: Cities comprise complex road intersections, one-way avenues, and varied road lengths; simple Euclidean distance fails to reflect real road travel.
4. **Sequencing Bottleneck**: Visiting stops randomly leads to backtracking, excessive fuel consumption, and delivery delays.

### 1.2 System Pipeline Architecture
The system models a sequential 5-stage pipeline:

```
[Incoming Parcel Registry]
           │
           ▼
[Phase 2A: Manual Merge Sort Engine]
           │ (Deterministic priority & deadline ordering)
           ▼
[Phase 2B: 0/1 Knapsack DP Packing Engine]
           │ (Optimal cargo selection under payload constraint W)
           ▼
[Phase 3A: Delivery Road Graph & Adjacency List]
           │ (Weighted undirected graph G=(V, E))
           ▼
[Phase 3B: Dijkstra Shortest Path Engine (heapq)]
           │ (True shortest road path between depot and all stops)
           ▼
[Phase 3C: Nearest Neighbor TSP Tour Engine]
           │ (Closed-loop delivery sequence s -> v1 -> v2 ... -> s)
           ▼
[Dispatch Manifest, Driver Itinerary & Network Visualization]
```

---

## Phase 2: Package Prioritization and Box Filling

### 2.1 Package Prioritization (Manual Merge Sort)
- **Objective**: Sort pending packages to ensure critical consignments receive scheduling priority.
- **Sorting Criteria**:
  1. Priority rank ($10 = \text{Emergency/High Value}$, $1 = \text{Standard}$) in **descending** order.
  2. Delivery deadline in hours ($1\text{h} < 2\text{h} < 8\text{h}$) in **ascending** order.
  3. Unique Parcel ID (e.g., `P101` before `P102`) as a deterministic tie-breaker.
- **Algorithmic Justification**: Merge Sort divides the input array recursively until singletons are formed ($T(n) = 2T(n/2) + O(n)$). By the Master Theorem, $T(n) \in \Theta(n \log n)$ across worst, average, and best cases. Furthermore, Merge Sort is **stable**, ensuring parcels with identical sorting criteria preserve their natural arrival order.

### 2.2 Vehicle Box Filling (0/1 Knapsack Dynamic Programming)
- **Objective**: Pack the delivery vehicle of capacity $W$ with a subset of parcels that maximizes cumulative monetary/service profit $\sum v_i$ such that $\sum w_i \le W$.
- **Mathematical Recurrence**:
  Let $dp[i][w]$ denote the maximum value obtainable using a subset of the first $i$ prioritized parcels with a weight limit of $w$:
  $$\text{dp}[i][w] = \begin{cases} \text{dp}[i-1][w] & \text{if } w_i > w \\ \max(\text{dp}[i-1][w], \text{dp}[i-1][w - w_i] + v_i) & \text{if } w_i \le w \end{cases}$$
- **Reconstruction by Backtracking**:
  Starting at cell $(n, W)$:
  - If $dp[i][w] \ne dp[i-1][w]$, item $i$ was chosen. We append parcel $i-1$, decrement $w \leftarrow w - w_i$, and decrement $i \leftarrow i - 1$.
  - Otherwise, item $i$ was not chosen; decrement $i \leftarrow i - 1$.
- **Complexity Analysis**:
  - Time Complexity: $O(n \cdot W)$ operations.
  - Space Complexity: $O(n \cdot W)$ for table storage.
  - Pseudo-polynomial property: The algorithm depends on the numeric value of $W$, not just input length.

---

## Phase 3: Route Maker and Graph Processing

### 3.1 Graph Representation: Adjacency List
The urban road delivery network is represented as a weighted undirected graph $G = (V, E)$:
- **Vertices ($V$)**: Geographic delivery hubs (e.g., `Central Warehouse`, `Cyber City`, `Sector 14`, `MG Road`, `Golf Course Road`, `Sohna Road`, etc.).
- **Edges ($E$)**: Bidirectional roads weighted by driving distances in kilometers.
- **Storage**: Adjacency list storing `Dict[str, List[Tuple[str, float]]]`.
- **Advantage over Adjacency Matrix**: For road networks where average degree per vertex is small ($d \ll V$), the adjacency list uses $O(V + E)$ space compared to $O(V^2)$ matrix memory.

### 3.2 Shortest Road Distance (Manual Dijkstra Algorithm)
- **Objective**: Determine the shortest driving path and road distance from `Central Warehouse` to every chosen delivery location.
- **Mechanism**:
  - Employs a binary min-heap (`heapq`) storing `(tentative_distance, node_name)`.
  - Maintains `distances` dictionary initialized to $\infty$ (source $= 0.0$) and `predecessors` dictionary initialized to `None`.
  - At each step, extracts the vertex $u$ with minimum tentative distance and relaxes outgoing edges $(u, v, \text{weight})$.
- **Complexity**: $O((V + E) \log V)$ time using binary heap, $O(V + E)$ auxiliary space.

### 3.3 Route Tour Generation (Nearest Neighbor TSP Approximation)
- **Objective**: Generate a viable closed-loop tour starting at the warehouse, delivering to all destination nodes, and returning to the warehouse.
- **Mechanism**:
  1. $T \leftarrow [s]$, $\text{Current} \leftarrow s$, $\text{Unvisited} \leftarrow V_{\text{dest}} \setminus \{s\}$.
  2. While $\text{Unvisited} \ne \emptyset$:
     - For each candidate $c \in \text{Unvisited}$, look up shortest path distance $\text{dist}(\text{Current}, c)$ via Dijkstra.
     - Choose $v^* = \arg\min_{c \in \text{Unvisited}} \text{dist}(\text{Current}, c)$.
     - Append $v^*$ to $T$, remove from $\text{Unvisited}$, and set $\text{Current} \leftarrow v^*$.
  3. Close tour: Add leg from last stop back to warehouse $s$.
- **Approximation Discussion**:
  TSP is strongly NP-Hard ($O(2^k k^2)$ via Held-Karp dynamic programming). The Nearest Neighbor heuristic runs in polynomial time $O(k^2 + k(V+E)\log V)$ where $k$ is the number of stops. Although greedy decisions can occasionally lead to a longer return leg, it provides a fast and practical solution for delivery logistics.

---

## Phase 4: Performance Testing and Optimization

### 4.1 Empirical Measurement Methodology
Benchmarking was executed using Python's `time.perf_counter()` to obtain sub-millisecond precision.
Three dataset configurations were tested:
- **Small Dataset**: 10 parcels, vehicle capacity $W = 50$, 10 graph nodes, 5 delivery stops.
- **Medium Dataset**: 100 parcels, vehicle capacity $W = 200$, 30 graph nodes, 15 delivery stops.
- **Large Dataset**: 500 parcels, vehicle capacity $W = 500$, 100 graph nodes, 30 delivery stops.

### 4.2 Benchmark Results

| Algorithm | Theoretical Time Complexity | Small ($n=10$) | Medium ($n=100$) | Large ($n=500$) |
| :--- | :--- | :--- | :--- | :--- |
| **Merge Sort** | $O(n \log n)$ | **0.0149 ms** | **0.2113 ms** | **2.1197 ms** |
| **0/1 Knapsack DP** | $O(n \cdot W)$ | **0.1316 ms** | **7.4802 ms** | **70.1319 ms** |
| **Dijkstra (Heap)** | $O((V + E) \log V)$ | **0.0186 ms** | **0.1442 ms** | **0.3044 ms** |
| **Nearest Neighbor TSP** | $O(k^2 + k(V+E)\log V)$ | **0.1767 ms** | **1.5944 ms** | **8.8744 ms** |

### 4.3 0/1 Knapsack Capacity Sensitivity Analysis
To confirm the $O(n \cdot W)$ pseudo-polynomial nature of the Knapsack DP, item count was held constant at $N = 100$ while vehicle capacity $W$ was varied from 20 to 1500 kg:

| Fixed Items ($N$) | Vehicle Capacity ($W$) | Table Cells ($N \times W$) | Execution Time (ms) |
| :--- | :--- | :--- | :--- |
| 100 | 20 kg | 2,121 | 0.8142 ms |
| 100 | 50 kg | 5,151 | 1.8791 ms |
| 100 | 100 kg | 10,201 | 3.6625 ms |
| 100 | 200 kg | 20,301 | 7.3912 ms |
| 100 | 400 kg | 40,501 | 15.1104 ms |
| 100 | 800 kg | 80,901 | 29.8421 ms |
| 100 | 1500 kg | 151,601 | 56.4019 ms |

**Finding**: The execution time scales in direct proportion to $W$, providing empirical proof of the $O(n \cdot W)$ recurrence.

---

## Phase 5: Final Report and Demonstration

### 5.1 Verification Checklist
- [x] Merge Sort implemented manually without Python `list.sort()` or `sorted()`.
- [x] 0/1 Knapsack DP constructed manually with a 2D matrix and backtracking.
- [x] Delivery road graph implemented as an adjacency list.
- [x] Dijkstra algorithm implemented manually using binary min-heap (`heapq`).
- [x] Nearest Neighbor TSP implemented manually using shortest-path distances.
- [x] All 28 automated unit tests pass successfully.
- [x] Genuine empirical measurements recorded in `reports/performance_results.csv`.
- [x] Real charts generated and saved in `reports/` and `screenshots/`.
- [x] Streamlit web application (`app.py`) and CLI (`main.py`) operational.

### 5.2 Verification Evidence and Output Locations
- **Visual Network Route Plot**: `reports/delivery_route_visualization.png`
- **Algorithmic Bar Chart**: `reports/performance_runtime_comparison.png`
- **Scaling Growth Curves**: `reports/performance_scaling_curves.png`
- **Knapsack Capacity Curve**: `reports/knapsack_capacity_impact.png`
- **Benchmark CSV Table**: `reports/performance_results.csv`

---

## Conclusion

The Mini-Courier Planner provides a rigorous, demonstrable synthesis of classic algorithmic techniques applied to an authentic engineering problem. The project demonstrates the distinction between theoretical complexity and empirical execution, highlights the trade-offs between exact DP solutions and heuristic approximations, and prepares students for academic evaluation and industry software design.

