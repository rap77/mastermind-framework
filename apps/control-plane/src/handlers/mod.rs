//! HTTP handlers module.
//!
//! This module provides Axum handlers for HTTP endpoints.

pub mod tasks;

pub use tasks::{AutoTaskRequest, AutoTaskResponse, AppState, create_auto_task};
