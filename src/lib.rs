#[cfg(feature = "pyo3")]
use pyo3::prelude::*;

pub mod cli;
pub mod providers;

mod finder;
mod helpers;
mod python;

pub use finder::{Finder, MatchOptions};
pub use python::PythonVersion;

#[cfg(feature = "pyo3")]
#[pyfunction]
fn cli_main() -> PyResult<()> {
    use std::env;
    use clap::Parser;

    let args = cli::Cli::parse_from(env::args_os().skip(1));
    Ok(cli::main(args)?)
}

/// A Python module implemented in Rust.
#[cfg(feature = "pyo3")]
#[pymodule]
fn findpython(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<Finder>()?;
    m.add_class::<PythonVersion>()?;
    m.add_function(wrap_pyfunction!(cli_main, m)?)?;
    Ok(())
}
