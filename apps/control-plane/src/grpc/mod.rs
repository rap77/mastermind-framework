//! gRPC client module for Python Agent Runtime communication.
//!
//! This module provides the gRPC client that connects to the Python
//! Brain Runtime service and dispatches tasks for execution.

pub mod client;

pub use client::BrainRuntimeClient;
