# Todo — dashboard-realtime

## Execution Checklist

- [x] RT1: Event contract
⏱️ **Estimate**: N/A | **Actual**: 3.2m | **Deviation**: N/A | **Progress**: 3/3 (100%)
📊 **Avg/subtask**: 1.1m | **ETA**: 3.2m

  - [x] RT1.1: Review requirements and design context for RT1
  - [x] RT1.2: Implement RT1 end-to-end
  - [x] RT1.3: Run validation for RT1
  - depends_on: none
  - validation: Review event contract for explicit payload fields and event names.

- [x] RT2: Backend publication path
⏱️ **Estimate**: N/A | **Actual**: 3.4m | **Deviation**: N/A | **Progress**: 3/3 (100%)
📊 **Avg/subtask**: 1.1m | **ETA**: 3.4m

  - [x] RT2.1: Review requirements and design context for RT2
  - [x] RT2.2: Implement RT2 end-to-end
  - [x] RT2.3: Run validation for RT2
  - depends_on: RT1
  - validation: Run targeted backend tests for realtime publication.

- [x] RT3: Frontend consumption
⏱️ **Estimate**: N/A | **Actual**: 5.8m | **Deviation**: N/A | **Progress**: 3/3 (100%)
📊 **Avg/subtask**: 1.9m | **ETA**: 5.8m

  - [x] RT3.1: Review requirements and design context for RT3
  - [x] RT3.2: Implement RT3 end-to-end
  - [x] RT3.3: Run validation for RT3
  - depends_on: RT2
  - validation: Run frontend lint/typecheck for the affected realtime components.
