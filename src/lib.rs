#[cfg(feature = "pyo3")]
use pyo3::prelude::*;

pub mod cli;
pub mod providers;

mod finder;
mod helpers;
mod python;

pub use finder::{Finder, MatchOptions};
pub use python::PythonVersion;

/// A Python module implemented in Rust.
#[cfg(feature = "pyo3")]
#[pymodule]
fn findpython(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<Finder>()?;
    m.add_class::<PythonVersion>()?;
    Ok(())
}
