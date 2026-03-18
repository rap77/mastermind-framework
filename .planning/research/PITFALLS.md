# Pitfalls Research

**Domain:** Next.js 16 + React Flow + Magic UI + Tailwind 4 + Zustand — Added to existing FastAPI backend
**Researched:** 2026-03-18
**Confidence:** HIGH (verified through official docs, React Flow changelog, GitHub issues, CVE databases)

> Note: This file supersedes the v2.0 PITFALLS.md (backend refactoring pitfalls). Those remain valid
> for `apps/api/`. This file covers **only v2.1 frontend addition pitfalls** for `apps/web/`.

---

## Critical Pitfalls

### Pitfall 1: React Flow CSS Import Location — Silent Style Breakage

**What goes wrong:**
You import `@xyflow/react/dist/style.css` in a component file or layout.tsx. In Tailwind 4, this
causes React Flow's built-in styles (handles, edges, minimap, background) to be silently overridden
or missing. Nodes render without handles. The canvas background is gone. Edge lines disappear.
Everything "works" in the sense that no error is thrown, but the DAG looks broken.

**Why it happens:**
Tailwind 4 is a CSS-first configuration engine. It processes stylesheets through a cascade layer
system. When React Flow CSS is imported outside the layer system (e.g., directly in a `.tsx` file),
Tailwind's cascade can override it with lower-specificity rules. In v3 this was not an issue because
Tailwind used a different specificity model.

**How to avoid:**
Move the React Flow CSS import into `global.css`, placed inside `@layer base`, AFTER the Tailwind
import. The correct order in `apps/web/src/app/globals.css` is:

```css
@import "tailwindcss";
@import "tw-animate-css";

@layer base {
  @import "@xyflow/react/dist/style.css";
}
```

Remove any `import '@xyflow/react/dist/style.css'` from `.tsx` files.

**Warning signs:**
- React Flow canvas renders but edges are invisible
- Node handles don't appear on hover
- DAG background grid is missing
- Works in dev but breaks after production build (build ordering differs)

**Phase to address:**
Phase 1 (Frontend Foundation). Set this up before writing any React Flow component. Verify with a
smoke test: render a 2-node, 1-edge graph and confirm handles and edges are visible.

---

### Pitfall 2: Magic UI Component Installer Fails on Tailwind 4 Projects

**What goes wrong:**
Running `npx shadcn@latest add` for a Magic UI component throws:
`ENOENT: no such file or directory, open '.../tailwind.config.ts'`

The installer expected a Tailwind 3 config file that doesn't exist in Tailwind 4 projects. The
component does not install. Developers waste hours debugging the CLI, assuming their project setup
is wrong.

**Why it happens:**
Magic UI's component registry was originally written against Tailwind 3. Tailwind 4 eliminates
`tailwind.config.ts` entirely in favor of CSS-only configuration. The Magic UI installer was patched
(PR #620) but some components and animation utilities still need manual CSS definition because they
relied on `tailwind.config.ts` to inject keyframes and animation classes.

**How to avoid:**
1. Use `npx shadcn@latest` (not `@canary`) — the fix has shipped
2. After installing any Magic UI animated component (Marquee, SparklesText, etc.), verify the
   required `@keyframes` are present in `globals.css`. If animations are missing, add them manually
3. For Bento Grid specifically: it uses CSS variables for color theming — verify they match your
   Tailwind 4 theme variables (v4 uses `--color-*` prefix, not Tailwind 3's `colors.*` config)
4. Check `https://magicui.design/docs/tailwind-v4` for the current migration guide

**Warning signs:**
- `ENOENT: tailwind.config.ts` error during `npx shadcn add`
- Animations installed but don't play (keyframes missing from CSS)
- Component renders but colors are wrong (CSS variable mismatch)
- `@apply` directives in component files throw errors (Tailwind 4 `@apply` is more restricted)

**Phase to address:**
Phase 1 (Frontend Foundation). Install and smoke-test ONE Magic UI animated component (e.g.,
Bento Grid) before building the full Command Center. Catch this early — adding it later means
retrofitting color tokens and animations across all components.

---

### Pitfall 3: React Flow + shadcn/ui Nodes — Drag Stolen by Interactive Elements

**What goes wrong:**
You build a custom brain node using shadcn Button, Input, or Select components inside the node.
In the DAG, clicking a button drags the node instead of triggering the button's onClick. Or
scrolling a Select dropdown scrolls the canvas instead. The node appears interactive but isn't.

**Why it happens:**
React Flow wraps every node in a drag listener. Mouse events on child elements bubble up to the
node's drag handler unless explicitly stopped. shadcn components don't know they're inside a React
Flow node and don't apply the necessary stop-propagation classes.

**How to avoid:**
Apply React Flow utility classes to every interactive element inside a custom node:
- `nodrag` — prevents the node from being dragged when the user interacts with this element
- `nopan` — prevents the canvas from panning when clicking and dragging this element

For shadcn components this means adding className on the wrapper or the component's `className` prop:

```tsx
// Button inside a node
<Button className="nodrag nopan" onClick={handleClick}>
  View Details
</Button>

// Input inside a node
<Input className="nodrag nopan" value={label} onChange={...} />

// For react-select or similar — wrap the container
<div className="nodrag nopan">
  <Select ... />
</div>
```

Use `BaseNode` from React Flow UI (updated for shadcn compatibility) instead of a plain `<div>` as
the node wrapper — it handles the correct wrapper structure out of the box.

**Warning signs:**
- Clicking a button inside a node moves the node
- Text inputs inside nodes are impossible to focus without dragging
- Select dropdowns close immediately when trying to scroll options
- Only detectable through manual interaction testing, not unit tests

**Phase to address:**
Phase 2 (The Nexus — DAG View). Address before building any brain node component. Create a
single `BrainNode` base component with the utility classes as the standard, so all 24 node
variants inherit correct behavior.

---

### Pitfall 4: WebSocket in Next.js App Router — SSR Crashes and Hydration Mismatches

**What goes wrong:**
You create a Zustand WebSocket store and call `new WebSocket(...)` at module level or in the store
initializer. The Next.js build crashes with `ReferenceError: WebSocket is not defined` during
SSR because `window` and `WebSocket` don't exist on the server. Or you guard with
`typeof window !== 'undefined'` but the component still produces a hydration mismatch because
server and client render different initial states.

**Why it happens:**
Next.js app router runs every component on the server first by default. Even `"use client"` components
are pre-rendered on the server for their initial HTML. The WebSocket API is browser-only. Zustand
stores initialized at module level run during SSR.

**How to avoid:**
1. Never initialize a WebSocket connection outside a `useEffect` or a client-only init function
2. In the Zustand WS dispatcher store, use lazy initialization:
   ```ts
   // WRONG — runs during SSR
   const socket = new WebSocket(WS_URL);

   // CORRECT — lazy, client-only
   connect: () => {
     if (typeof window === 'undefined') return;
     const socket = new WebSocket(WS_URL);
     set({ socket });
   }
   ```
3. Wrap the component that calls `store.connect()` in `dynamic()` with `ssr: false` if it must
   connect immediately on mount:
   ```ts
   const WsProvider = dynamic(() => import('./WsProvider'), { ssr: false });
   ```
4. Use `useEffect` in the Zustand subscriber to call `connect()` on the client side

**Warning signs:**
- Build-time error: `ReferenceError: WebSocket is not defined`
- Console error: `Hydration failed because the server rendered HTML didn't match the client`
- WS connects in development but crashes in production build
- Connection fires twice (StrictMode double-invoke in dev)

**Phase to address:**
Phase 1 (Frontend Foundation). The WS dispatcher is the spine of the entire real-time UI. Get
the SSR-safe initialization pattern right before building any subscriber components. A wrong
pattern here cascades to every real-time feature.

---

### Pitfall 5: Zustand WebSocket Store — 24 Simultaneous Updates Cause Re-render Storm

**What goes wrong:**
The FastAPI backend fires 24 `brain_step_completed` events within milliseconds when a parallel
execution completes. Each event hits the Zustand store, which updates a single `brains` object.
All 24 Bento Grid tiles and all 24 React Flow nodes re-render synchronously. The UI freezes for
300-500ms. At 60fps this drops to single-digit frames during the burst.

**Why it happens:**
- If all 24 brains share one Zustand slice (e.g., `brains: Record<BrainId, BrainState>`), any
  update to one brain triggers all subscribers that use that slice
- Even with per-brain selectors, 24 rapid `setState` calls create 24 separate React reconciliation
  cycles, since React 19's automatic batching only covers events in a single synchronous call chain
- The WS `onmessage` handler is an async event, so batching does NOT automatically apply

**How to avoid:**
1. Use per-brain selectors to minimize subscriber scope:
   ```ts
   // WRONG — re-renders all 24 components on any brain update
   const brains = useWsStore(state => state.brains);

   // CORRECT — re-renders only when THIS brain changes
   const brain = useWsStore(state => state.brains[brainId]);
   ```
2. Batch WS messages using `requestAnimationFrame` instead of immediate `setState`:
   ```ts
   let pendingUpdates: BrainEvent[] = [];
   let rafScheduled = false;

   ws.onmessage = (event) => {
     pendingUpdates.push(JSON.parse(event.data));
     if (!rafScheduled) {
       rafScheduled = true;
       requestAnimationFrame(() => {
         useWsStore.setState(applyBatch(pendingUpdates));
         pendingUpdates = [];
         rafScheduled = false;
       });
     }
   };
   ```
3. Memoize custom React Flow node components with `React.memo` — prevents re-render when parent
   re-renders but the node's own data hasn't changed
4. For Bento Grid tiles, use the Zustand `subscribe` API (not hooks) for high-frequency updates
   that should drive animation without React re-renders

**Warning signs:**
- UI freezes for 200-500ms when all brains complete in parallel (4.65x speedup means they burst)
- Chrome DevTools shows 24+ React renders in a single 16ms frame
- React Flow canvas jank during brain execution
- `console.log` in a tile component fires 24 times per execution cycle

**Phase to address:**
Phase 2 (Command Center). Must implement the RAF batching pattern before building the Bento Grid,
not after. Retrofitting it later requires touching every subscriber component.

---

### Pitfall 6: JWT Authentication — middleware.ts Is Not a Security Boundary

**What goes wrong:**
You implement JWT verification ONLY in `middleware.ts` to protect routes. An attacker sends a
request with the `x-middleware-subrequest` header (CVE-2025-29927) and bypasses all authentication,
reaching protected API routes and pages directly. This is a real, disclosed critical CVE affecting
all Next.js versions before 15.2.3.

**Why it happens:**
Next.js middleware uses an internal header `x-middleware-subrequest` to prevent infinite middleware
loops. Before the patch, any external request could forge this header and skip middleware entirely.
This is a design flaw, not a configuration error.

**How to avoid:**
1. Use Next.js 15.2.3+ or 16.x (patch included) — verify in `package.json`
2. NEVER rely solely on `middleware.ts` for auth. Verify the JWT in every Server Component and
   Route Handler that accesses protected data:
   ```ts
   // In every protected Server Component or Route Handler:
   const session = await verifyJWT(cookies().get('token')?.value);
   if (!session) redirect('/login');
   ```
3. Store JWT in `httpOnly` cookie, not `localStorage`. Browser WS connections can't send custom
   headers, so the token must be accessible to the server
4. For the FastAPI WebSocket endpoint: pass the JWT as a query param at connect time ONLY
   (short-lived token). Rotate it — the WS connection doesn't re-auth after initial handshake

**Warning signs:**
- Next.js version < 15.2.3 in `package.json`
- `middleware.ts` is the only place JWT is checked
- Protected pages accessible via direct URL after stripping cookies
- localStorage used for JWT (XSS attack surface)

**Phase to address:**
Phase 1 (Frontend Foundation). Auth architecture is foundational — wrong decisions here require
rewriting every protected page. Check Next.js version before writing a single line of auth code.

---

### Pitfall 7: CORS + WebSocket — Two Different Problems, One Misconfiguration

**What goes wrong:**
You configure FastAPI CORS to allow `http://localhost:3000`. HTTP requests from Next.js work.
But the WebSocket connection from the frontend fails with a 403 or connects but immediately closes.
Or you proxy HTTP through Next.js rewrites thinking it will also proxy WebSocket — it won't.
Next.js rewrites do NOT proxy WebSocket upgrade requests in Next.js 15. Next.js 16 introduces
`proxy.js` but with Node.js runtime constraints.

**Why it happens:**
- CORS is HTTP-only. WebSocket upgrade handshake (`ws://`) uses HTTP for the initial handshake but
  is a separate protocol — browsers apply different same-origin checks
- FastAPI's `CORSMiddleware` allows the WS handshake origin but developers often forget to include
  `allow_credentials=True` when using `httpOnly` cookies for auth
- Next.js rewrites proxy HTTP traffic through the Next.js server, masking CORS. But WS traffic goes
  directly from the browser to FastAPI — CORS must be explicitly allowed on FastAPI

**How to avoid:**
1. Never proxy WebSocket through Next.js — connect the browser directly to FastAPI WS endpoint
2. Configure FastAPI CORS explicitly for both HTTP and WS origins:
   ```python
   app.add_middleware(
     CORSMiddleware,
     allow_origins=["http://localhost:3000", "http://web:3000"],
     allow_credentials=True,   # Required for httpOnly cookie auth
     allow_methods=["*"],
     allow_headers=["*"],
   )
   ```
3. In `apps/web/next.config.ts`, use rewrites only for REST API calls (hides CORS in dev, works in prod behind nginx):
   ```ts
   rewrites: async () => [{
     source: '/api/:path*',
     destination: 'http://localhost:8000/:path*',
   }]
   ```
   Do NOT attempt to rewrite WebSocket paths — connect directly from the client

**Warning signs:**
- HTTP requests work but WS gives `403 Forbidden` on handshake
- WebSocket connects but closes after `1006` code (abnormal closure)
- CORS errors only appear in browser console, not server logs (origin header mismatch)
- Works on localhost but breaks in Docker (container hostnames differ from localhost)

**Phase to address:**
Phase 1 (Frontend Foundation). Wire up the FastAPI CORS config and test a raw WebSocket connection
from the browser before building any React component. A broken WS connection makes every
subsequent feature untestable.

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| WS in Context API instead of Zustand | Simpler setup | Re-renders entire subtree on every message | Never for 24 brains — use Zustand |
| Single `brains` Zustand slice, no selectors | Faster to write | Re-render storm on parallel brain bursts | Acceptable for single brain, never for 24 |
| JWT in localStorage | No cookie setup needed | XSS attack surface, WS auth complexity | Never in production |
| `nodrag`/`nopan` added reactively (bug reports) | Less upfront work | Broken UX shipped, hard to find all instances | Never — add to BaseNode template from day one |
| React Flow CSS in component imports | Works locally | Breaks in production Tailwind 4 build | Never — must be in globals.css |
| `typeof window !== 'undefined'` guards for WS | Quick fix | Hydration mismatches, hard-to-trace bugs | Acceptable as stopgap, not permanent |
| Middleware-only JWT verification | Less code per route | CVE-2025-29927 bypass risk | Never — always verify at data access point |

---

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| **React Flow + Tailwind 4** | Import `@xyflow/react/dist/style.css` in `.tsx` | Import inside `@layer base` in `globals.css` |
| **Magic UI + Tailwind 4** | Run `npx shadcn@latest add` and assume it works | Verify keyframes in `globals.css` after install |
| **Zustand + WebSocket** | Initialize socket at module level | Lazy init in `connect()` action, call from `useEffect` |
| **Next.js + FastAPI WS** | Proxy WS through Next.js rewrites | Direct browser → FastAPI connection |
| **JWT + WebSocket** | Pass JWT as Authorization header | Browser WS API has no custom headers — use query param (short-lived token) |
| **shadcn inside React Flow node** | No utility classes | Every interactive element gets `nodrag nopan` classes |
| **FastAPI CORS + cookies** | Missing `allow_credentials=True` | Required when using `httpOnly` cookies for auth |
| **Docker networking + WS** | Hardcode `localhost:8000` in WS URL | Use environment variable, different value in container vs host |

---

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| **Zustand slice too coarse** | All 24 nodes re-render on any brain update | Per-brain selectors: `state => state.brains[id]` | Immediately — visible at 24 brains |
| **WS burst without RAF batching** | UI freeze 200-500ms during parallel brain completion | RAF-based message accumulator in WS store | When 5+ brains complete simultaneously |
| **React Flow nodes not memoized** | Every parent re-render cascades to all 24 nodes | `React.memo` on every node component | At 10+ nodes with frequent updates |
| **Magic UI animations on 24 tiles** | GPU thrash, frame drops during bulk updates | Disable complex animations during active execution (CSS class toggle) | When all 24 brains are animating simultaneously |
| **React Flow edge re-calculation** | Slow edge routing on node position changes | Avoid dynamic edge path recalculation for status-only updates | With complex DAG layouts |

---

## Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| **JWT only in middleware.ts** | CVE-2025-29927 auth bypass — attacker skips all protection | Verify JWT at every protected Server Component and Route Handler |
| **JWT in localStorage** | XSS steals auth token | Store in `httpOnly; Secure; SameSite=Strict` cookie |
| **WS token in long-lived query param** | Token in server logs, browser history | Use short-lived (60s) pre-auth token for WS handshake only |
| **`allow_origins=["*"]` with credentials** | CORS spec error — browser blocks the request | Explicit origin list, never wildcard with `allow_credentials=True` |
| **SECRET_KEY hardcoded in apps/api** | Git history exposes key forever | Load from `MM_SECRET_KEY` env var before v2.1 ships |

---

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| **No WS reconnect on disconnect** | UI silently goes stale — brain events lost after network blip | Zustand store exponential backoff reconnect strategy |
| **All 24 Bento tiles animate simultaneously** | Visual chaos, nothing stands out | Animate only the actively changing tile, idle tiles are static |
| **React Flow node glow on every WS message** | Glow for 1ms — imperceptible | Debounce visual state — hold "active" state for minimum 500ms |
| **DAG re-layout on every brain update** | Nodes jump around during execution | Lock DAG positions during execution, only layout on load |
| **WS connection shown as loading forever** | User doesn't know if WS failed | 5s timeout → show "Connecting..." → show error with retry button |

---

## "Looks Done But Isn't" Checklist

- [ ] **React Flow CSS:** Import in `globals.css` inside `@layer base` — verify handles and edges visible in production build
- [ ] **Magic UI keyframes:** Animated components play their animations — verify in production build, not just dev
- [ ] **nodrag/nopan:** Every interactive element inside BrainNode has utility classes — verify by clicking buttons without node moving
- [ ] **WS SSR safety:** `npm run build` succeeds without `WebSocket is not defined` — verify before any WS feature
- [ ] **JWT security:** Every protected Server Component and Route Handler independently verifies JWT — verify with middleware disabled
- [ ] **CORS + credentials:** WS connects successfully from browser to FastAPI:8000 — verify with `httpOnly` cookie present
- [ ] **Docker WS URL:** WS URL uses env var, connects correctly inside and outside Docker network — verify both contexts
- [ ] **Parallel brain burst:** Render 24 simultaneous Zustand updates in test — verify no UI freeze >16ms

---

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| **React Flow CSS in wrong location** | LOW | Move import to `globals.css @layer base`, rebuild |
| **Magic UI missing keyframes** | LOW | Add `@keyframes` manually to `globals.css` |
| **nodrag/nopan missing from nodes** | MEDIUM | Audit all node components, add to BaseNode wrapper, cascades to all 24 variants |
| **WS SSR crashes** | MEDIUM | Refactor store init to lazy pattern, wrap consumers in `dynamic(ssr: false)` |
| **Re-render storm** | HIGH | Requires restructuring Zustand slices + adding RAF batching + memoizing all node components |
| **JWT middleware-only auth** | HIGH | Add JWT verification to every protected route — can be 20+ files |
| **CORS misconfiguration** | LOW | Fix FastAPI `CORSMiddleware` config, restart API container |
| **WS proxy through Next.js** | MEDIUM | Remove rewrite rule, update WS URL to direct FastAPI endpoint, handle CORS properly |

---

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| React Flow CSS import location | Phase 1 — Frontend Foundation | `npm run build` + smoke test: 2-node graph with visible handles and edges |
| Magic UI Tailwind 4 compatibility | Phase 1 — Frontend Foundation | One animated Magic UI component renders and animates in prod build |
| WS SSR safety (hydration) | Phase 1 — Frontend Foundation | `npm run build` produces zero `WebSocket is not defined` errors |
| JWT security (CVE-2025-29927) | Phase 1 — Frontend Foundation | Middleware disabled → protected pages still reject unauthenticated requests |
| CORS + WebSocket setup | Phase 1 — Frontend Foundation | Browser WS connects to FastAPI:8000 from Next.js:3000 |
| nodrag/nopan on interactive nodes | Phase 2 — The Nexus (DAG) | Click button inside BrainNode → button fires, node does not move |
| Zustand re-render storm | Phase 2 — Command Center (Bento Grid) | 24 simultaneous Zustand updates complete in <16ms (1 frame) |
| Docker WS URL env var | Phase 3 — Integration | WS connects correctly in `docker compose up` and in host dev server |

---

## Sources

- [React Flow UI: React 19 & Tailwind CSS 4 Updates (Oct 2025)](https://reactflow.dev/whats-new/2025-10-28) — HIGH confidence (official changelog)
- [React Flow Utility Classes — nodrag, nopan](https://reactflow.dev/learn/customization/utility-classes) — HIGH confidence (official docs)
- [Magic UI Issue #548 — tailwind.config.ts missing with Tailwind v4](https://github.com/magicuidesign/magicui/issues/548) — HIGH confidence (resolved, PR #620)
- [CVE-2025-29927 — Next.js Middleware Authorization Bypass](https://projectdiscovery.io/blog/nextjs-middleware-authorization-bypass) — HIGH confidence (disclosed CVE)
- [Zustand WebSocket integration discussion](https://github.com/pmndrs/zustand/discussions/2779) — MEDIUM confidence (community)
- [React Flow Performance Guide](https://reactflow.dev/learn/advanced-use/performance) — HIGH confidence (official docs)
- [Next.js WebSocket proxy limitations](https://github.com/vercel/next.js/discussions/38057) — MEDIUM confidence (community + official discussion)
- [FastAPI WebSocket JWT authentication](https://dev.to/hamurda/how-i-solved-websocket-authentication-in-fastapi-and-why-depends-wasnt-enough-1b68) — MEDIUM confidence (real-world post-mortem)
- [React 19 batching behavior for async events](https://codehustle.tech/posts/react-19-features-guide-complete-update/) — MEDIUM confidence (multiple sources agree)
- [Next.js authentication guide — httpOnly cookies](https://nextjs.org/docs/app/guides/authentication) — HIGH confidence (official docs)

---
*Pitfalls research for: MasterMind Framework v2.1 — War Room Frontend*
*Researched: 2026-03-18*
