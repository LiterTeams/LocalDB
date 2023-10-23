use pyo3::prelude::*;
use pyo3::types::IntoPyDict;


#[pyfunction]
fn get_free_id(datas, temp) -> PyResult<Integer> {

}

#[pyfunction]
fn sum_as_string(a: usize, b: usize) -> PyResult<String> {
    Ok((a + b).to_string())
}

/// A Python module implemented in Rust.
#[pymodule]
fn rust(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(sum_as_string, m)?)?;
    Ok(())
}