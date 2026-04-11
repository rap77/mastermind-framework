//! Observability module for monitoring and metrics
//!
//! Provides latency tracking, distributed tracing integration,
//! and observability primitives for the control plane.

pub mod latency;

pub use latency::LatencyTracker;
