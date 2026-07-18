# 108. Phase 20-21 Operating Bundle

## 1. Purpose

Define the live Phase 20-21 RAG slice as one operating bundle so runtime,
observability, and documentation share a single boundary.

This bundle is the handoff point between:

- Phase 20 substrate work
- Phase 21 Brain #1 RAG execution
- Phase 21.5 evaluation gate preparation

## 2. Bundle Boundary

### In scope

- `brain_embeddings` retrieval substrate
- `RAGContextBuilder` prompt injection
- per-brain coordinator-owned `RAGObservation`
- bulk observation handoff to `task_runner`
- experience metadata and LangSmith propagation
- offline evaluation helpers and gate scaffolding

### Out of scope

- manual ingestion scale-out
- brains 2-7 rollout
- cross-brain learning
- any new loop/selector work

## 3. Runtime Contract

The coordinator owns the RAG signal.

The runner only consumes observations.

The canonical runtime object is:

```python
RAGObservation(enabled: bool, latency_ms: int | None)
```

The runner-facing access pattern is bulk:

```python
get_rag_observations_for_brains(brain_ids)
```

## 4. What Exists Now

- `RAGContextBuilder` injects `[RETRIEVED CONTEXT]` only when retrieval returns data.
- `StatelessCoordinator` stores one `RAGObservation` per brain.
- `task_runner` consumes observations in batch for the executed brain set.
- `rag_enabled` and `rag_retrieval_latency_ms` flow into experience metadata.
- LangSmith metadata is updated non-blockingly.

## 5. What Is Still Partial

- the bundle is packaged in docs and runtime, but not yet elevated to a separate phase artifact in code
- evaluation gate metrics are scaffolded, and the full pass/fail policy is defined in `109-PHASE-21.5-EVALUATION-GATE.md`

## 6. Exit Criteria

This bundle is complete when:

- Brain #1 retrieval is the only enabled pilot path
- `RAGObservation` remains the single runner-facing signal
- bulk observation handoff is stable
- evaluation metrics define a concrete gate verdict via `109-PHASE-21.5-EVALUATION-GATE.md`
- the runtime and canonical docs agree on the next step
