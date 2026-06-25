# Design — memory-graph-recall-v1

## Overview

After Retrieval v1 and reranking, the next additive step is relational recall: expanding or boosting results based on useful links between memory and runtime entities.

## Approach

1. Keep graph recall behind the retrieval engine boundary.
2. Start with a tiny relational seam over existing entities and links.
3. Preserve deterministic local verification.
4. Avoid graph-database coupling in the first slice.

## Initial Targets

- memory_item → decision
- decision → task
- task → artifact

## Success Condition

Graph recall can enrich retrieval results without breaking stable callers or the current deterministic baseline.
