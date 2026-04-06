//! MasterMind Control Plane - Rust library with Python bindings.
//!
//! This library provides the core logic for the MasterMind Control Plane,
//! including flow detection and task dispatching. It can be compiled as:
//! - A native Rust library (rlib) for use in Rust applications
//! - A Python extension module (cdylib) via PyO3 bindings
//!
//! ## PyO3 Spike (Phase 13)
//!
//! This spike measures the performance difference between:
//! 1. gRPC approach: Rust → gRPC → Python
//! 2. PyO3 approach: Python → Rust directly (no gRPC overhead)
//!
//! The goal is to generate data to inform future architecture decisions (v4.0+).

pub mod config;
pub mod flow;
pub mod grpc;
pub mod handlers;
pub mod postgres;
pub mod proto;

// PyO3 bindings module (only compiled when feature is enabled)
#[cfg(feature = "pyo3")]
pub mod bindings;
