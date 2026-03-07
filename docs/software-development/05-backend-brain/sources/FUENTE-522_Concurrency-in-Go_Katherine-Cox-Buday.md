---
source_id: "FUENTE-522"
brain: "brain-software-05-backend"
niche: "software-development"
title: "Concurrency in Go: Tools and Techniques for Highly Responsive Systems"
author: "Katherine Cox-Buday, Go Team"
expert_id: "EXP-522"
type: "article"
language: "en"
year: 2022
distillation_date: "2026-03-03"
distillation_quality: "complete"
loaded_in_notebook: false
version: "1.0.0"
last_updated: "2026-03-03"
changelog:
  - version: "1.0.0"
    date: "2026-03-03"
    changes:
      - "Initial distillation from Concurrency best practices"
status: "active"
---

# Concurrency in Go: Tools and Techniques for Highly Responsive Systems

**Katherine Cox-Buday, Go Team**

## 1. Principios Fundamentales

> **P1 - La concurrencia es sobre managing dependencies**: No es cuántos threads, es cómo coordino trabajo en paralelo. La complejidad viene de dependencias entre goroutines.

> **P2 - Don't communicate by sharing memory; share memory by communicating**: Las goroutines deberían comunicarse vía canales, no compartiendo memoria.

> **P3 - Lock contention es el enemigo de la escalabilidad**: Un lock global = bottleneck. Minimiza locks.

> **P4 - Concurrencia ≠ Paralelismo**: Concurrencia lidiar con múltiples cosas. Paralelismo es ejecutar en múltiples CPUs.

> **P5 - La prevención de race conditions es posible**: Evita shared mutable state, usa canales.

## 2. Frameworks y Metodologías

### Goroutines

```go
go func() {
    // Run concurrently
}
```

### Channels

```go
// Unbuffered (blocking)
ch := make(chan int)

// Buffered (non-blocking)
ch := make(chan int, 10)
```

### Mutex and sync Package

```go
var mu sync.Mutex
var data map[string]string

func read(key string) string {
    mu.Lock()
    defer mu.Unlock()
    return data[key]
}
```

## 3. Modelos Mentales

### CSP (Communicating Sequential Processes)
```
Goroutine A → Channel → Goroutine B
```

### Worker Pool
```
Jobs → Channel → Workers → Results → Channel → Collector
```

## 4. Criterios de Decisión

### Goroutine vs Function
- Goroutine: I/O-bound, concurrent, independent
- Function: CPU-bound, sequential, dependent

### Channel vs Mutex
- Channel: Communication, passing ownership
- Mutex: Mutual exclusion, protecting shared state

## 5. Anti-patrones

### Goroutine Leaks
```go
// ❌ Goroutine never exits
// ✅ Provide way to exit
```

### Mutex Deadlock
```go
// ❌ Inconsistent lock ordering
// ✅ Always lock in consistent order
```

### Context Not Propagated
```go
// ❌ Not passing context to goroutine
// ✅ Always pass context explicitly
```
