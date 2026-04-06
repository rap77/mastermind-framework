//! PyO3 Python bindings for MasterMind Control Plane.
//!
//! This module provides Python bindings for the Rust flow detection logic,
//! allowing Python code to call Rust functions directly without gRPC overhead.
//!
//! ## Usage in Python
//!
//! ```python
//! import mastermind_control_plane
//!
//! # Detect flow from brief
//! flow = mastermind_control_plane.detect_flow("Create a report for me")
//! print(flow)  # "async"
//!
//! # Get detailed metadata
//! metadata = mastermind_control_plane.detect_flow_with_metadata("Create a report")
//! print(metadata)  # {"flow": "async", "word_count": 3, ...}
//! ```
//!
//! ## Performance
//!
//! This approach eliminates gRPC overhead (serialization, network, deserialization)
//! by using Python's C FFI to call Rust code directly.

use pyo3::prelude::*;
use pyo3::types::PyDict;

use crate::flow;

/// Python module definition for MasterMind Control Plane.
///
/// This function is called by PyO3 to initialize the Python module.
#[pymodule]
fn mastermind_control_plane(_py: Python, m: &PyModule) -> PyResult<()> {
    // Register the detect_flow function
    m.add_function(wrap_pyfunction!(detect_flow_py, m)?)?;

    // Register the detect_flow_with_metadata function
    m.add_function(wrap_pyfunction!(detect_flow_with_metadata_py, m)?)?;

    // Register the FlowDetector class
    m.add_class::<FlowDetector>()?;

    Ok(())
}

/// Detect the appropriate flow type from a user brief.
///
/// This is a Python binding for the Rust `flow::detect` function.
///
/// # Arguments
/// * `brief` - User's brief text
///
/// # Returns
/// Flow type as string ("auto", "sync", "async", "batch")
///
/// # Examples
/// ```python
/// import mastermind_control_plane
///
/// flow = mastermind_control_plane.detect_flow("Create a report")
/// print(flow)  # "async"
/// ```
#[pyfunction]
fn detect_flow_py(brief: &str) -> PyResult<String> {
    let flow = flow::detect(brief);
    Ok(flow.as_str().to_string())
}

/// Detect flow type with detailed metadata.
///
/// This is a Python binding for the Rust `flow::detect_with_metadata` function.
///
/// # Arguments
/// * `brief` - User's brief text
///
/// # Returns
/// Dictionary with flow detection metadata including:
/// - "flow": detected flow type
/// - "brief_length": character count
/// - "word_count": word count
/// - "has_batch_keywords": boolean
/// - "has_async_keywords": boolean
/// - "has_sync_keywords": boolean
///
/// # Examples
/// ```python
/// import mastermind_control_plane
///
/// metadata = mastermind_control_plane.detect_flow_with_metadata("Create a report")
/// print(metadata["flow"])  # "async"
/// print(metadata["word_count"])  # 3
/// ```
#[pyfunction]
fn detect_flow_with_metadata_py(py: Python, brief: &str) -> PyResult<PyObject> {
    let metadata = flow::detect_with_metadata(brief);

    // Convert Rust HashMap to Python dict
    let dict = PyDict::new(py);
    for (key, value) in metadata.iter() {
        dict.set_item(*key, value)?;
    }

    Ok(dict.into())
}

/// FlowDetector class for Python object-oriented usage.
///
/// This class provides a stateful interface to the Rust flow detector,
/// allowing for potential future enhancements like caching or configuration.
///
/// # Examples
/// ```python
/// import mastermind_control_plane
///
/// detector = mastermind_control_plane.FlowDetector()
/// flow = detector.detect("Create a report")
/// print(flow)  # "async"
/// ```
#[pyclass]
pub struct FlowDetector {
    /// Internal state (reserved for future use)
    _internal: (),
}

#[pymethods]
impl FlowDetector {
    /// Create a new FlowDetector instance.
    #[new]
    fn new() -> Self {
        Self { _internal: () }
    }

    /// Detect flow type from brief.
    ///
    /// # Arguments
    /// * `brief` - User's brief text
    ///
    /// # Returns
    /// Flow type as string
    fn detect(&self, brief: &str) -> PyResult<String> {
        let flow = flow::detect(brief);
        Ok(flow.as_str().to_string())
    }

    /// Detect flow type with detailed metadata.
    ///
    /// # Arguments
    /// * `brief` - User's brief text
    ///
    /// # Returns
    /// Dictionary with flow detection metadata
    fn detect_with_metadata(&self, py: Python, brief: &str) -> PyResult<PyObject> {
        let metadata = flow::detect_with_metadata(brief);

        let dict = PyDict::new(py);
        for (key, value) in metadata.iter() {
            dict.set_item(*key, value)?;
        }

        Ok(dict.into())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::flow;

    #[test]
    fn test_detect_flow_py_binding() {
        // Test that the binding correctly calls the Rust function
        let brief = "Create a report for me";
        let result = detect_flow_py(brief).unwrap();
        assert_eq!(result, "async");

        // Verify it matches the Rust function
        let rust_result = flow::detect(brief);
        assert_eq!(result, rust_result.as_str());
    }

    #[test]
    fn test_detect_flow_with_metadata_py_binding() {
        let brief = "Tell me a joke";
        let result = detect_flow_with_metadata_py(brief).unwrap();

        Python::with_gil(|py| {
            let dict: &PyDict = result.as_ref(py);
            assert_eq!(dict.get_item("flow").unwrap().to_string(), "sync");
            assert!(dict.get_item("word_count").is_some());
        });
    }
}
