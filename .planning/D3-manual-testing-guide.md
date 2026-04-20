# D3: Manual Testing Guide

**Purpose:** Complete the final 3 verification subtasks (D3.7, D3.8, D3.9) through manual testing.

**Time Required:** ~15 minutes
**Prerequisites:** MasterMind v3.0 running locally (http://localhost:3000)

---

## D3.7: Flow Designer Workflow Test

### Objective
Verify users can create, edit, export, and import flows visually.

### Steps

1. **Navigate to Flow Designer**
   - Open browser: `http://localhost:3000/flow-designer`
   - Expected: Canvas loads with grid background, palette on left, toolbar on top

2. **Create Flow**
   - Drag "Brain" node from palette to canvas
   - Drag "Gateway" node from palette to canvas
   - Drag "Adapter" node from palette to canvas
   - Expected: 3 nodes appear on canvas with distinct colors (blue, purple, green)

3. **Connect Nodes**
   - Hover over "Brain" node → see handle on right edge
   - Drag handle from "Brain" to "Gateway"
   - Drag handle from "Gateway" to "Adapter"
   - Expected: 2 edges connect nodes with bezier curves

4. **Edit Node**
   - Double-click "Brain" node
   - Expected: Configuration panel appears (stub - can be empty)
   - Close panel

5. **Export Flow**
   - Click "Export" button in toolbar (top right)
   - Expected: Browser downloads `flow-*.json` file

6. **Clear Canvas**
   - Click "Clear" button in toolbar
   - Expected: All nodes and edges removed

7. **Import Flow**
   - Click "Import" button in toolbar
   - Select the JSON file downloaded in step 5
   - Expected: Canvas restores with all 3 nodes and 2 edges

### Success Criteria
- [x] All 5 node types appear in palette
- [x] Nodes drag and drop correctly
- [x] Edges connect with bezier curves
- [x] Double-click opens config panel
- [x] Export downloads valid JSON
- [x] Import restores canvas correctly

**Result:** ✅ PASS / ❌ FAIL

---

## D3.8: Simulation Workflow Test

### Objective
Verify users can load executions, replay timeline, and detect errors visually.

### Steps

1. **Navigate to Simulation**
   - Open browser: `http://localhost:3000/simulation`
   - Expected: Canvas loads with timeline scrubber at bottom, event log on right

2. **Load Execution**
   - Click "Load Execution" button (or auto-load if mock data exists)
   - Expected: Canvas populates with nodes, timeline shows milestones
   - Verify: ErrorSummary shows total errors, slow nodes, execution time

3. **Replay Timeline**
   - Click "Play" button (▶) in ReplayControls
   - Expected: Timeline scrubber advances, nodes highlight in sequence
   - Watch for: Blue glow (running), green border (success), red background (failed)

4. **Detect Errors**
   - Scrub to a timestamp with errors (if mock data has them)
   - Expected: Failed nodes have red background + error tooltip
   - Expected: ErrorSummary updates error count

5. **Detect Slow Nodes**
   - Scrub to find slow nodes (latency > threshold)
   - Expected: Slow nodes have yellow border + "SLOW" badge
   - Expected: Edge labels show latency in ms

6. **Control Playback**
   - Click "Pause" button (⏸)
   - Expected: Timeline stops advancing
   - Click "Reset" button (⏹)
   - Expected: Timeline returns to start, nodes reset

7. **Change Speed**
   - Select "2x" from speed dropdown
   - Expected: Timeline advances 2x faster
   - Select "0.5x" from speed dropdown
   - Expected: Timeline advances 2x slower

8. **Navigate Milestones**
   - Click milestone marker on timeline
   - Expected: Scrubber jumps to that timestamp, node status updates

9. **Edit Flow (Integration Test)**
   - Click "Edit Flow" button
   - Expected: Redirects to `/flow-designer` with flow loaded

### Success Criteria
- [x] Execution loads and populates canvas
- [x] Timeline scrubber works with play/pause/reset
- [x] Nodes highlight correctly (blue=running, green=success, red=failed, yellow=slow)
- [x] ErrorSummary shows correct counts
- [x] Speed control works (0.5x, 1x, 2x, 5x)
- [x] "Edit Flow" button redirects to Flow Designer

**Result:** ✅ PASS / ❌ FAIL

---

## D3.9: Theme Toggle Test (All 6 Screens)

### Objective
Verify light/dark mode works on all screens with smooth transitions and persistence.

### Screens to Test
1. Command Center (`/command-center`)
2. Nexus (`/nexus`)
3. Strategy Vault (`/strategy-vault`)
4. Engine Room (`/engine-room`)
5. Flow Designer (`/flow-designer`)
6. Simulation (`/simulation`)

### Steps (Repeat for Each Screen)

1. **Navigate to Screen**
   - Open screen in browser
   - Note initial theme (light or dark)

2. **Toggle Theme**
   - Click ThemeToggle button (sun/moon icon) in top-right
   - Expected: Smooth transition (0.2s) to opposite theme
   - Verify: All components adapt (backgrounds, text, borders, React Flow canvas)

3. **Verify React Flow Adaptation** (Nexus, Flow Designer, Simulation)
   - Check: Node colors adapt (blue, purple, green, orange, yellow)
   - Check: Canvas background adapts (light gray → dark gray)
   - Check: Edge colors adapt (black → white)

4. **Verify Persistence**
   - Refresh page (F5)
   - Expected: Theme remains same (not reset to system default)
   - Check: `localStorage.getItem("theme")` returns "light" or "dark"

5. **Verify System Fallback**
   - Open DevTools → Application → Local Storage
   - Delete `theme` key
   - Refresh page
   - Expected: Theme matches system preference (OS dark/light mode)

### Success Criteria (Per Screen)
- [x] ThemeToggle button visible and clickable
- [x] Smooth transition (0.2s) between themes
- [x] All components adapt correctly
- [x] React Flow canvas adapts (Nexus, Flow Designer, Simulation)
- [x] Theme persists across page reloads
- [x] Falls back to system preference on first visit

**Overall Result:** ✅ PASS / ❌ FAIL

---

## Quick Reference: Testing Checklist

### D3.7: Flow Designer
- [ ] Drag nodes to canvas
- [ ] Connect nodes with edges
- [ ] Double-click to edit
- [ ] Export to JSON
- [ ] Import from JSON

### D3.8: Simulation
- [ ] Load execution
- [ ] Play/pause/reset timeline
- [ ] Detect errors (red nodes)
- [ ] Detect slow nodes (yellow badges)
- [ ] Change playback speed
- [ ] Click "Edit Flow" → redirects

### D3.9: Theme Toggle
- [ ] Command Center: toggle → colors adapt → persist
- [ ] Nexus: toggle → React Flow adapts → persist
- [ ] Strategy Vault: toggle → colors adapt → persist
- [ ] Engine Room: toggle → colors adapt → persist
- [ ] Flow Designer: toggle → nodes/canvas adapt → persist
- [ ] Simulation: toggle → all components adapt → persist

---

## Issue Reporting Template

If any test fails, document:

```markdown
### Subtask: D3.X

**Step Number:** X
**Expected Behavior:** [What should happen]
**Actual Behavior:** [What actually happened]
**Browser:** [Chrome/Firefox/Safari + version]
**Console Errors:** [Copy from DevTools console]
**Screenshot:** [Attach if applicable]
```

---

## Completion Instructions

After completing all manual tests:

1. Update `.planning/task-progress.json`:
   ```json
   "D3.7": { "status": "completed" },
   "D3.8": { "status": "completed" },
   "D3.9": { "status": "completed" }
   ```

2. Mark task D3 as complete:
   ```json
   "overall_status": "COMPLETE"
   ```

3. Proceed to ship v3.0:
   ```bash
   git tag v3.0 -m "MasterMind v3.0 - Visual Orchestration & Simulation"
   git push origin v3.0
   ```

---

**Happy Testing! 🚀**

*Generated for MasterMind v3.0 E2E Verification*
