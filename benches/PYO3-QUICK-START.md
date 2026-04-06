# PyO3 Quick Start — MasterMind v3.0

## Build PyO3 Module

```bash
cd apps/control-plane
cargo build --release --features pyo3
```

This creates:
- `target/release/libmastermind_control_plane.so` (872 KB)
- `target/release/mastermind_control_plane.so` (symlink for Python)

## Use in Python

```python
import sys
sys.path.insert(0, 'apps/control-plane/target/release')

import mastermind_control_plane

# Method 1: Direct function call
flow = mastermind_control_plane.detect_flow_py("Create a report")
print(flow)  # "async"

# Method 2: With metadata
metadata = mastermind_control_plane.detect_flow_with_metadata_py("Tell me a joke")
print(metadata["flow"])  # "sync"
print(metadata["word_count"])  # 4

# Method 3: Class-based (stateful)
detector = mastermind_control_plane.FlowDetector()
flow = detector.detect("Generate reports for multiple users")
print(flow)  # "batch"
```

## Run Benchmark

```bash
python3 benches/pyo3_vs_grpc.py
```

Expected output: ~3000x speedup vs gRPC

## Run Tests

```bash
# Rust tests
cd apps/control-plane
cargo test --release

# Python import test
python3 benches/pyo3_import_test.py
```

## Key Files

- `src/flow.rs` — Rust flow detection logic
- `src/bindings/mod.rs` — PyO3 bindings
- `benches/pyo3_vs_grpc.py` — Performance benchmark
- `benches/PYO3-SPIKE-SUMMARY.md` — Full results

## Performance

| Approach | Latency | Throughput |
|----------|---------|------------|
| PyO3 | 0.001 ms | 512K ops/sec |
| gRPC | 2.6 ms | 383 ops/sec |

**Speedup: 3000x** ⚡
