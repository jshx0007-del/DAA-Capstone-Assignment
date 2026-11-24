# Mini-Courier Planner

### Intelligent Parcel Prioritization, Packing Optimization and Delivery Route Planning System

**Design and Analysis of Algorithms (ETCCDA302) — Capstone Project**
**Department of Computer Science & Engineering, K.R. Mangalam University**

**Student:** Janvi Sehrawat **Roll No.:** _<2501350002>_

---

## Executive Overview

The Mini-Courier Planner is an integrated decision-support system for courier dispatch. All four core
algorithms were **implemented manually from first principles** in Python 3, with no built-in `sort()` for
prioritization, no NetworkX shortest-path routines, and no external TSP solvers.

- **Algorithms:** Merge Sort, 0/1 Knapsack (Dynamic Programming), Dijkstra (binary min-heap), Nearest Neighbor TSP.
- **Interfaces:** an interactive Streamlit web dashboard (`app.py`) and a full-featured terminal CLI with an automated demo runner (`main.py`).
- **Evidence:** benchmark tables (`.csv`) and charts (`.png`) saved in `reports/` and `screenshots/`, plus an automated unit-test suite.

---

## Table of Contents

1. [Project Introduction](#1-project-introduction)
2. [Problem Statement](#2-problem-statement)
3. [Objectives](#3-objectives)
4. [Technologies Used](#4-technologies-used)
5. [Project Architecture](#5-project-architecture)
6. [Algorithm Explanations](#6-algorithm-explanations)
7. [Time and Space Complexity Summary](#7-time-and-space-complexity-summary)
8. [Empirical Performance Analysis](#8-empirical-performance-analysis)
9. [Sample Input and Output Walkthrough](#9-sample-input-and-output-walkthrough)
10. [Generated Artifacts and Screenshots](#10-generated-artifacts-and-screenshots)
11. [Installation and Execution Instructions](#11-installation-and-execution-instructions)
12. [Uploading to GitHub](#12-uploading-to-github)
13. [Limitations](#13-limitations)
14. [Future Scope](#14-future-scope)
15. [Conclusion](#15-conclusion)

---

## 1. Project Introduction

In modern logistics and e-commerce supply chains, courier distribution centers receive thousands of
packages daily with distinct delivery deadlines, client priority levels, parcel weights, and destinations.
Before dispatching a vehicle, four algorithmic challenges must be solved together:

1. **Prioritization:** which parcels must be serviced first based on urgency and deadline?
2. **Packing optimization:** given a vehicle with a rigid payload capacity, which subset of prioritized parcels yields the maximum profit without exceeding the weight limit?
3. **Shortest path routing:** what is the shortest road distance from the central depot to every customer drop-off node?
4. **Tour scheduling (TSP):** in what sequence should the van visit the drop-offs and return to the depot while minimizing total driving distance and fuel use?

The **Mini-Courier Planner** connects foundational Computer Science algorithms into one automated pipeline
that answers all four questions.

---

## 2. Problem Statement

**Given:**

- A set of $n$ parcels, where each parcel $p_i$ is defined by $\langle \text{ID}, \text{Customer}, \text{Location}, \text{Weight } w_i, \text{Priority } r_i, \text{Deadline } d_i, \text{Value } v_i \rangle$.
- A delivery vehicle with maximum payload capacity $W$.
- A city road network represented as a weighted undirected graph $G = (V, E)$, where $V$ are junctions / delivery locations and $E$ are bidirectional roads weighted by driving distance in kilometers.
- A designated warehouse depot $s \in V$.

**The objective is to:**

1. Sort and rank all parcels deterministically by urgency.
2. Select a subset $S \subseteq \{1, \dots, n\}$ maximizing total revenue $\sum_{i \in S} v_i$ subject to $\sum_{i \in S} w_i \le W$.
3. Compute the shortest driving routes from depot $s$ to all unique destinations $V_{\text{dest}} = \{ \text{Location}(p_i) \mid i \in S \}$.
4. Construct a closed-loop delivery tour $T = \langle s, v_{\pi(1)}, v_{\pi(2)}, \dots, v_{\pi(k)}, s \rangle$ visiting every location in $V_{\text{dest}}$ with a short total driving distance.

---

## 3. Objectives

- **Algorithmic rigor:** implement all foundational algorithms manually (no built-in sorting, no NetworkX shortest-path functions, no third-party TSP solvers).
- **End-to-end integration:** connect Merge Sort, 0/1 Knapsack DP, Dijkstra's Algorithm, and Nearest Neighbor TSP into one workflow.
- **Empirical complexity analysis:** benchmark actual execution times with `time.perf_counter()` on Small ($n=10$), Medium ($n=100$), and Large ($n=500$) datasets to validate the theoretical bounds.
- **Accessible interfaces:** provide an interactive Streamlit web UI and a full-featured CLI.
- **Academic readiness:** provide unit tests, architecture documentation, and viva preparation material.

---

## 4. Technologies Used

| Purpose | Technology |
| :--- | :--- |
| Language | Python 3.10+ (standard library: `heapq`, `json`, `dataclasses`, `time`, `typing`, `unittest`) |
| Plotting | Matplotlib (`matplotlib.pyplot`) for route maps and runtime curves |
| Graph layout | NetworkX, used **only** for layout rendering and node plotting, **never** for Dijkstra or TSP |
| Web UI | Streamlit |
| Tabular data | Pandas, used only for UI tables and CSV export |

---

## 5. Project Architecture

```
CAPSTONE/
├── app.py                     # Interactive Streamlit web application
├── main.py                    # CLI application, interactive menu and automated demo runner
├── requirements.txt           # Python dependency specifications
├── README.md                  # Project documentation (this file)
├── CAPSTONE_REPORT.md         # Detailed 5-phase capstone project report
├── VIVA_QUESTIONS.md          # Viva questions with beginner-friendly answers
├── .gitignore                 # Git ignore rules for venv, caches and OS files
│
├── algorithms/                # Algorithmic core (all manually implemented)
│   ├── __init__.py
│   ├── sorting.py             # Merge Sort (priority desc, deadline asc, ID asc)
│   ├── knapsack.py            # 0/1 Knapsack DP with full 2D table backtracking
│   ├── dijkstra.py            # Dijkstra shortest path with heapq (min-heap)
│   ├── tsp.py                 # Nearest Neighbor TSP approximation
│   └── performance.py         # Benchmarking suite (time.perf_counter)
│
├── models/                    # Domain data models
│   ├── __init__.py
│   ├── parcel.py              # Parcel dataclass, validation and serialization
│   └── delivery_graph.py      # Adjacency-list DeliveryGraph data structure
│
├── data/                      # JSON sample datasets
│   ├── parcels.json           # 15 realistic parcels with varied weights and values
│   └── graph.json             # 11-node Delhi NCR delivery network
│
├── visualization/             # Plotting and rendering
│   ├── __init__.py
│   ├── graph_visualizer.py    # Delivery tour and graph visualizer
│   └── performance_charts.py  # Runtime bar charts, line plots and knapsack scaling
│
├── tests/                     # Automated unit and integration tests
│   ├── __init__.py
│   ├── test_sorting.py        # Empty, single, multi, tie-breakers, large dataset
│   ├── test_knapsack.py       # Zero capacity, oversized parcels, optimal DP verification
│   ├── test_dijkstra.py       # Shortest paths, multiple routes, disconnected nodes
│   ├── test_tsp.py            # Closed-loop tour, duplicate locations, unreachable nodes
│   └── test_integration.py    # End-to-end multi-algorithm pipeline tests
│
├── reports/                   # Benchmarks, CSV output and generated charts
│   ├── performance_results.csv
│   ├── performance_runtime_comparison.png
│   ├── performance_scaling_curves.png
│   ├── knapsack_capacity_impact.png
│   └── delivery_route_visualization.png
│
└── screenshots/               # Figures stored for report submission
    ├── delivery_route_visualization.png
    ├── knapsack_capacity_impact.png
    ├── performance_runtime_comparison.png
    └── performance_scaling_curves.png
```

---

## 6. Algorithm Explanations

### A. Sorting: Manual Merge Sort

- **File:** `algorithms/sorting.py`
- **Paradigm:** divide and conquer.
- **Logic:**
  1. Recursively split the parcel list into two halves until sublists have size $\le 1$.
  2. Merge the sorted sublists with a multi-criteria comparator `comes_before(a, b)`:
     - **Criterion 1:** higher priority first ($a.\text{priority} > b.\text{priority}$).
     - **Criterion 2:** earlier deadline first ($a.\text{deadline} < b.\text{deadline}$).
     - **Criterion 3:** lexicographic parcel ID as the tie-breaker ($a.\text{id} < b.\text{id}$).
- **Time:** $O(n \log n)$ in best, average and worst cases.
- **Space:** $O(n)$ auxiliary memory for merging.
- **Stability:** preserved, which guarantees deterministic ordering.

### B. Dynamic Programming: 0/1 Knapsack

- **File:** `algorithms/knapsack.py`
- **Paradigm:** dynamic programming (bottom-up tabulation).
- **Logic:**
  1. Build a 2D matrix `dp` of size $(n + 1) \times (W + 1)$, where `dp[i][w]` is the maximum revenue from the first $i$ prioritized parcels with capacity $w$.
  2. Base cases: `dp[0][w] = 0` and `dp[i][0] = 0`.
  3. Recurrence:

     $$\text{dp}[i][w] = \begin{cases} \text{dp}[i-1][w] & \text{if } w_i > w \\ \max(\text{dp}[i-1][w],\ \text{dp}[i-1][w - w_i] + v_i) & \text{if } w_i \le w \end{cases}$$

  4. Backtracking: trace back from `dp[n][W]` to extract the exact subset of parcels packed.
- **Time:** $O(n \cdot W)$ (pseudo-polynomial).
- **Space:** $O(n \cdot W)$ for the table.

### C. Graph Representation: Adjacency List

- **File:** `models/delivery_graph.py`
- **Structure:** a dictionary mapping node names to lists of `(neighbor, distance_km)` tuples.
- **Properties:** undirected, weighted by road distance.
- **Space:** $O(V + E)$, more efficient than an adjacency matrix $O(V^2)$ for sparse road networks ($E \ll V^2$).

### D. Shortest Path: Manual Dijkstra

- **File:** `algorithms/dijkstra.py`
- **Paradigm:** greedy algorithm with a min-heap.
- **Logic:**
  1. Set the distance to the source to $0$ and all others to $\infty$.
  2. Push `(0.0, source)` into a `heapq` priority queue.
  3. Pop the node $u$ with the smallest tentative distance.
  4. Relax every neighbor $v$ of $u$: if $\text{dist}[u] + \text{weight}(u, v) < \text{dist}[v]$, update $\text{dist}[v]$ and record $u$ as the predecessor of $v$.
  5. Follow the predecessor pointers backwards to rebuild the exact road path.
- **Time:** $O((V + E) \log V)$ with a binary min-heap.
- **Space:** $O(V + E)$ for the distance table, predecessors, and heap.

### E. Tour Optimization: Nearest Neighbor TSP Approximation

- **File:** `algorithms/tsp.py`
- **Paradigm:** greedy heuristic.
- **Logic:**
  1. Start the van at `Central Warehouse`.
  2. At the current node $u$, pick the unvisited destination $v$ with the smallest Dijkstra shortest-path distance $\text{dist}(u, v)$.
  3. Drive to $v$, append it to the itinerary, and mark it visited.
  4. Repeat until every selected delivery location is visited.
  5. Close the tour with the shortest path from the last stop back to `Central Warehouse`.
- **Heuristic disclaimer:** TSP is NP-hard. Nearest Neighbor runs in $O(k^2)$ time for $k$ stops. It gives fast, practical tours but does not guarantee the global optimum, because early greedy choices can force a long final return leg.

---

## 7. Time and Space Complexity Summary

| Module | Algorithm | Technique | Time Complexity | Auxiliary Space | Key Property |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Parcel prioritization | Merge Sort | Divide and conquer | $O(n \log n)$ | $O(n)$ | Stable; deterministic tie-breaking |
| Vehicle packing | 0/1 Knapsack | Dynamic programming | $O(n \cdot W)$ | $O(n \cdot W)$ | Optimal substructure; full-table backtracking |
| Road network | Adjacency list | Graph structure | $O(V + E)$ | $O(V + E)$ | Memory-efficient for sparse road maps |
| Shortest road paths | Dijkstra | Greedy (binary heap) | $O((V + E) \log V)$ | $O(V + E)$ | Non-negative edge weights |
| Delivery tour | Nearest Neighbor | Greedy TSP heuristic | $O(k^2 + k(V+E)\log V)$ | $O(V + E)$ | Fast polynomial approximation of an NP-hard problem |

---

## 8. Empirical Performance Analysis

Performance was measured with Python's high-resolution `time.perf_counter()` on the development machine.

### A. Execution Measurements

| Dataset Size | Algorithm | Elements Processed | Execution Time | Theoretical Complexity |
| :--- | :--- | :--- | ---: | :--- |
| **Small (10)** | Merge Sort | $n=10$ | 0.0149 ms | $O(n \log n)$ |
| **Small (10)** | 0/1 Knapsack DP | $n=10,\ W=50$ | 0.1316 ms | $O(n \cdot W)$ |
| **Small (10)** | Dijkstra (heap) | $V=10,\ E=20$ | 0.0186 ms | $O((V + E) \log V)$ |
| **Small (10)** | Nearest Neighbor TSP | $k=5$ | 0.1767 ms | $O(k^2)$ |
| **Medium (100)** | Merge Sort | $n=100$ | 0.2113 ms | $O(n \log n)$ |
| **Medium (100)** | 0/1 Knapsack DP | $n=100,\ W=200$ | 7.4802 ms | $O(n \cdot W)$ |
| **Medium (100)** | Dijkstra (heap) | $V=30,\ E=91$ | 0.1442 ms | $O((V + E) \log V)$ |
| **Medium (100)** | Nearest Neighbor TSP | $k=15$ | 1.5944 ms | $O(k^2)$ |
| **Large (500)** | Merge Sort | $n=500$ | 2.1197 ms | $O(n \log n)$ |
| **Large (500)** | 0/1 Knapsack DP | $n=500,\ W=500$ | 70.1319 ms | $O(n \cdot W)$ |
| **Large (500)** | Dijkstra (heap) | $V=100,\ E=336$ | 0.3044 ms | $O((V + E) \log V)$ |
| **Large (500)** | Nearest Neighbor TSP | $k=30$ | 8.8744 ms | $O(k^2)$ |

### B. Observations

1. **Merge Sort growth:** time rose smoothly from 0.015 ms at $n=10$ to 2.120 ms at $n=500$, consistent with $O(n \log n)$ scaling.
2. **Knapsack pseudo-polynomial growth:** time is proportional to both the item count $n$ and the capacity $W$. At $n=500,\ W=500$ the table has 250,501 entries and takes 70.13 ms. Sensitivity testing showed linear scaling with $W$.
3. **Dijkstra efficiency:** on a 100-node graph with 336 road segments it ran in only 0.304 ms thanks to the binary min-heap.
4. **TSP practicality:** Nearest Neighbor solved a 30-stop tour on a 100-node network in 8.87 ms, which is fast enough for real-time dispatch.

> Timings depend on the machine. Re-run `python -m algorithms.performance` to regenerate the table on your own computer.

---

## 9. Sample Input and Output Walkthrough

**Sample run with vehicle capacity $W = 35 \text{ kg}$**

1. **Intake:** 15 parcels loaded from `data/parcels.json`; road network loaded from `data/graph.json` (11 locations, 15 roads).
2. **Prioritization (Merge Sort), top 7 of 15:**

   | Rank | Parcel | Customer | Destination | Priority | Deadline | Weight | Value |
   | :-: | :-- | :-- | :-- | :-: | :-: | :-: | ---: |
   | 1 | Q204 | Tanvi Saxena | Janakpuri | 10 | 1 hr | 4 kg | ₹1800 |
   | 2 | Q209 | Rahul Chauhan | Lajpat Nagar | 10 | 1 hr | 5 kg | ₹1650 |
   | 3 | Q201 | Ishaan Mehta | Connaught Place | 9 | 2 hrs | 6 kg | ₹1450 |
   | 4 | Q207 | Nikhil Agarwal | Saket | 9 | 2 hrs | 3 kg | ₹1320 |
   | 5 | Q214 | Pallavi Rao | Rohini | 9 | 2 hrs | 5 kg | ₹1280 |
   | 6 | Q211 | Dev Malhotra | Connaught Place | 8 | 2 hrs | 2 kg | ₹1100 |
   | 7 | Q206 | Simran Kaur | Vasant Kunj | 8 | 3 hrs | 8 kg | ₹1250 |

3. **Packing (0/1 Knapsack DP):**
   - Selected parcels: `Q204`, `Q209`, `Q201`, `Q207`, `Q214`, `Q211`, `Q206`
   - Total weight: **33 kg / 35 kg** (94.3% utilization)
   - Total value: **₹9,850.00**
   - Remaining capacity: **2 kg** (the next parcel, Q213, weighs 7 kg and does not fit)
   - Left for a later trip: 8 parcels (Q213, Q202, Q215, Q208, Q203, Q212, Q205, Q210)

4. **Shortest paths (Dijkstra) from the warehouse to each of the 6 delivery stops:**

   | Destination | Distance | Road path |
   | :-- | ---: | :-- |
   | Connaught Place | 3.20 km | `Central Warehouse -> Connaught Place` |
   | Lajpat Nagar | 4.10 km | `Central Warehouse -> Lajpat Nagar` |
   | Saket | 4.70 km | `Central Warehouse -> Saket` |
   | Janakpuri | 8.80 km | `Central Warehouse -> Karol Bagh -> Janakpuri` |
   | Vasant Kunj | 9.10 km | `Central Warehouse -> Saket -> Vasant Kunj` |
   | Rohini | 9.90 km | `Central Warehouse -> Karol Bagh -> Rohini` |

5. **Route planning (Nearest Neighbor TSP):**

   | Leg | From → To | Distance |
   | :-: | :-- | ---: |
   | 1 | Central Warehouse → Connaught Place | 3.20 km |
   | 2 | Connaught Place → Lajpat Nagar | 7.30 km |
   | 3 | Lajpat Nagar → Saket | 7.20 km |
   | 4 | Saket → Vasant Kunj | 4.40 km |
   | 5 | Vasant Kunj → Janakpuri | 6.10 km |
   | 6 | Janakpuri → Rohini | 11.50 km |
   | 7 | Rohini → Central Warehouse | 9.90 km |

   - **Ordered route:** `Central Warehouse ➔ Connaught Place ➔ Lajpat Nagar ➔ Saket ➔ Vasant Kunj ➔ Janakpuri ➔ Rohini ➔ Central Warehouse`
   - **Total driving distance:** **49.60 km**
   - Note how the last two legs (11.50 km out to Rohini, then 9.90 km back) are long: this is the greedy
     weakness described in Section 13, because Nearest Neighbor leaves the far stop until last.

---

## 10. Generated Artifacts and Screenshots

All charts and benchmark data are stored in `reports/` (copies of the figures are also in `screenshots/`):

| File | Contents |
| :--- | :--- |
| `reports/performance_results.csv` | Full benchmark data table |
| `reports/performance_runtime_comparison.png` | Grouped logarithmic bar chart comparing all algorithms |
| `reports/performance_scaling_curves.png` | Input size $N$ versus execution time curves |
| `reports/knapsack_capacity_impact.png` | Capacity $W$ scaling curve showing linear $O(n \cdot W)$ growth |
| `reports/delivery_route_visualization.png` | Delivery network map with directional route arrows |

### Capturing live UI screenshots for submission

1. Start the app: `streamlit run app.py`
2. Open `http://localhost:8501` in your browser.
3. Visit each sidebar page: Dashboard, Parcel Prioritization, Packing Optimization, Delivery Graph, Shortest Path Finder, Route Optimization, Performance Analysis.
4. Capture each page (macOS: `Cmd + Shift + 4`; Windows: `Win + Shift + S`) and save the images into the `screenshots/` folder.

---

## 11. Installation and Execution Instructions

### Prerequisites

- Python 3.10 or newer
- Git (only needed for cloning and uploading)

### Step 1: Get the project

```bash
git clone https://github.com/<your-username>/mini-courier-planner.git
cd mini-courier-planner
```

If you already have the folder locally, just `cd` into it.

### Step 2: Create a virtual environment and install dependencies

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 3: Run the automated end-to-end demo (CLI)

Runs all four algorithms in sequence on the Delhi NCR data and prints each step:

```bash
python main.py --demo
```

### Step 4: Run the interactive terminal application

Interactive menu for adding parcels, setting a custom vehicle capacity, and calculating custom routes:

```bash
python main.py
```

### Step 5: Launch the Streamlit web application

```bash
streamlit run app.py
```

Then open `http://localhost:8501` in your browser.

### Step 6: Run the unit tests

```bash
python -m unittest discover tests -v
```

### Step 7: Re-run the benchmarks

Regenerates the CSV table and PNG charts:

```bash
python -m algorithms.performance
```

### Quick command reference

```bash
source venv/bin/activate
python main.py --demo
python main.py
streamlit run app.py
python -m unittest discover tests -v
python -m algorithms.performance
```

---

## 12. Uploading to GitHub

```bash
git init                                   # skip if the folder is already a Git repository
git add .
git commit -m "Mini-Courier Planner capstone"

# Create an empty repository on github.com first (e.g. 'mini-courier-planner'), then:
git remote add origin https://github.com/<your-username>/mini-courier-planner.git
git branch -M main
git push -u origin main
```

Make sure `venv/` is listed in `.gitignore` so the virtual environment is not uploaded.

---

## 13. Limitations

1. **Heuristic TSP bound:** Nearest Neighbor does not guarantee the minimum possible distance; poor early choices can give suboptimal tours.
2. **Knapsack integer capacity:** the standard 0/1 DP table needs integer weight units. Fractional weights must be scaled (for example kg to grams), which increases memory.
3. **Static traffic:** edge weights are fixed distances, not real-time travel times.

---

## 14. Future Scope

1. **Metaheuristic routing:** add 2-Opt or Simulated Annealing to refine the Nearest Neighbor tour.
2. **Multi-vehicle routing (CVRP):** extend from one van to a fleet of vehicles serving separate customer clusters.
3. **Time windows (VRPTW):** add hard customer availability windows alongside transit times.
4. **Live GIS integration:** connect the OpenStreetMap or Google Maps Distance Matrix API for live traffic routing.

---

## 15. Conclusion

The **Mini-Courier Planner** models and solves the courier dispatch problem end to end. Merge Sort gives a
deterministic priority order, 0/1 Knapsack Dynamic Programming selects the most valuable load, Dijkstra's
algorithm finds accurate shortest road paths, and Nearest Neighbor TSP schedules the delivery tour.
Benchmarks on small, medium, and large datasets follow the theoretical complexity models, making the project
a solid foundation for both academic study and practical logistics software.
