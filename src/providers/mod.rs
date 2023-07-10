use std::path::PathBuf;

use crate::helpers;
use crate::PythonVersion;
use lazy_static::lazy_static;

mod path;
mod pyenv;

pub use path::PathProvider;
pub use pyenv::PyenvProvider;

lazy_static! {
    pub static ref ALL_PROVIDERS: [&'static str; 2] = ["path", "pyenv"];
}

pub trait Provider: Send + Sync {
    fn create() -> Option<Self>
    where
        Self: Sized;

    fn find_pythons(&self) -> Vec<PythonVersion>;

    /// Find all Python versions under the given path.
    /// ### Arguments:
    ///
    /// path: The path to search for Python versions under.
    /// as_interpreter: Whether to use the path as an interpreter.
    ///     Must not be true if it might be a wrapper script.
    ///
    /// ### Returns:
    /// A list of Python versions found under the given path.
    fn find_pythons_from_path(&self, path: &PathBuf, as_interpreter: bool) -> Vec<PythonVersion> {
        match path.read_dir() {
            Ok(entries) => entries
                .into_iter()
                .filter_map(|entry| {
                    let path = entry.ok()?.path();
                    if helpers::path_is_python(&path) {
                        let mut python = PythonVersion::new(path.to_owned());
                        if as_interpreter {
                            python = python.with_interpreter(path.to_owned());
                        }
                        Some(python)
                    } else {
                        None
                    }
                })
                .collect(),
            Err(_) => vec![],
        }
    }
}

pub fn get_provider(name: &str) -> Option<Box<dyn Provider>> {
    match name {
        "path" => PathProvider::create().map(|p| Box::new(p) as Box<dyn Provider>),
        "pyenv" => PyenvProvider::create().map(|p| Box::new(p) as Box<dyn Provider>),
        _ => None,
    }
}
