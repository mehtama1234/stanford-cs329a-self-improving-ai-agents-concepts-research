# planning-as-search — verified measured result (grid search, no model)
7x7 maze, start (0,0), goal (6,6), the only route winds around walls.
- greedy (only step strictly closer to goal, no backtracking): dead-ends after 7 steps at cell (2,5), reaches goal = FALSE.
- breadth-first search over whole paths: 20-step plan, expanded 28 cells, reaches goal = TRUE.
Script: scripts/experiments/planning_run.py. Insight: greedy gets stuck where progress needs moving away from the goal; search plans the whole route.
