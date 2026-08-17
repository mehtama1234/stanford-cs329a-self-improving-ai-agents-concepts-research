"""Real planning-as-search run (no LLM needed). A goal at the end of a winding corridor.
A GREEDY agent that only takes steps which move it CLOSER to the goal dead-ends against a
wall; SEARCH (breadth-first over whole paths) snakes around and reaches the goal. Measured."""
import collections

# '.' = open, '#' = wall/trap. Start top-left, goal bottom-right. The only route is a snake:
MAZE = [
    "......#",
    "#####.#",
    "......#",
    "#.#####",
    "......#",
    "#.#####",
    "......G",
]
H=len(MAZE); W=len(MAZE[0])
START=(0,0); GOAL=(6,6)
def open_cell(r,c): return 0<=r<H and 0<=c<W and MAZE[r][c]!='#'
def nbrs(s):
    r,c=s
    return [(r+dr,c+dc) for dr,dc in [(-1,0),(1,0),(0,1),(0,-1)] if open_cell(r+dr,c+dc)]
def manh(s): return abs(s[0]-GOAL[0])+abs(s[1]-GOAL[1])

def greedy(maxsteps=100):
    """only step to a neighbor that is strictly CLOSER to the goal; if none, it is stuck."""
    s=START; path=[s]; visited={s}
    for _ in range(maxsteps):
        if s==GOAL: return True,path
        cand=[n for n in nbrs(s) if n not in visited and manh(n)<manh(s)]
        if not cand: return False,path        # dead end: every open move is away from the goal
        s=min(cand,key=manh); path.append(s); visited.add(s)
    return s==GOAL,path

def bfs():
    q=collections.deque([(START,[START])]); seen={START}; expanded=0
    while q:
        s,path=q.popleft(); expanded+=1
        if s==GOAL: return True,path,expanded
        for n in nbrs(s):
            if n not in seen: seen.add(n); q.append((n,path+[n]))
    return False,[],expanded

g_ok,g_path=greedy()
b_ok,b_path,b_exp=bfs()
print("=== planning-as-search: greedy vs search on a winding corridor ===")
print(f"  {H}x{W} maze, start {START}, goal {GOAL}; the only route to the goal winds back and forth.")
print(f"  greedy 'only step closer to the goal': reached goal = {g_ok}  "
      f"(dead-ended after {len(g_path)-1} steps at {g_path[-1]})")
print(f"  search over whole paths (breadth-first): reached goal = {b_ok}  "
      f"(found a {len(b_path)-1}-step plan, expanded {b_exp} cells)")

print("\n=== why search wins: it looks before it leaps ===")
print(f"  greedy insists every step move it closer, so at {g_path[-1]} — where the only open move goes")
print(f"  AWAY from the goal to get around a wall — it has no legal move and quits.")
print(f"  search never commits early: it fans out over {b_exp} cells and finds the {len(b_path)-1}-step")
print(f"  snake path, which repeatedly moves away from the goal to ultimately reach it. Planning the")
print(f"  whole route beats picking the best-looking next step.")
