# Immer + Zustand Pattern — Critical Lesson

**Type:** technical
**Learned:** 2026-03-20
**Context:** Phase 05 gap closure — brainStore RAF batching fix

---

## The Problem

When using Zustand with `immer` middleware, the state returned by `get()` is **frozen** by Immer to guarantee immutability. Attempting to mutate it directly throws errors:

```typescript
// ❌ WRONG - Throws "Cannot add property 1, object is not extensible"
updateBrain: (brain) => {
  get()._queue.push(brain)  // Mutates frozen state
}
```

**Error:**
```
[Immer] minified error nr: 0
Uncaught TypeError: Cannot add property 1, object is not extensible at Array.push
```

## The Solution

All state mutations must occur inside the `set()` callback, where Immer provides a **mutable draft** via proxies:

```typescript
// ✅ CORRECT - Mutates draft inside set()
updateBrain: (brain) => {
  set(state => {
    state._queue.push(brain)  // state is mutable draft here
    if (!state._rafId) {
      const id = requestAnimationFrame(() => {
        get()._drainQueue()
      })
      state._rafId = id
    }
  })
}
```

## Why This Works

1. **`immer` middleware** wraps Zustand stores
2. **`get()`** returns the **frozen current state** (read-only)
3. **`set(state => { ... })`** provides a **mutable draft** created by Immer using proxies
4. Mutations on the draft are tracked and applied immutably by Immer
5. Direct mutations on frozen state violate Immer's guarantees

## When to Use Each

| Operation | Use | Why |
|-----------|-----|-----|
| Read state | `get()` | Fast read access to current state |
| Mutate state | `set(state => { ... })` | Draft is mutable inside callback |
| Read then mutate | `set(state => { ... get() ... })` | `get()` for read, `state` for mutation |

## Common Mistakes

1. **Direct mutation after get():** `get().items.push(x)` — ❌ Frozen state
2. **Mutation outside set():** `get().count++` — ❌ Frozen state
3. **Forgetting state parameter:** `set(() => { count++ })` — ❌ No draft access

## Related Patterns

- **RAF Batching:** Queue mutations in `_queue`, drain before paint
- **Map mutations with Immer:** `state.map.set(key, value)` works inside `set()`
- **Nested mutations:** `state.nested.prop = value` works inside `set()`

---

**Applies to:** Any Zustand store using `immer` middleware
**Fixed in:** `apps/web/src/stores/brainStore.ts` (Phase 05, Plan 05-04)
