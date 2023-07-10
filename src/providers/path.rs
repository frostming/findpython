use std::path::PathBuf;

use super::Provider;
use crate::PythonVersion;

/// A provider that searches Python interpreters in the PATH.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct PathProvider {
    paths: Vec<PathBuf>,
}

impl PathProvider {
    pub fn new() -> Self {
        let path_env = std::env::var_os("PATH").unwrap_or_default();
        Self {
            paths: std::env::split_paths(&path_env).collect(),
        }
    }
}

impl Provider for PathProvider {
    fn create() -> Option<Self> {
        Some(Self::new())
    }

    fn find_pythons(&self) -> Vec<PythonVersion> {
        self.paths
            .iter()
            .flat_map(|path| self.find_pythons_from_path(path, false))
            .collect()
    }
}

#[cfg(test)]
mod test {
    use super::*;

    #[test]
    fn test_find_pythons() {
        let provider = PathProvider::new();
        let mut pythons = provider.find_pythons();
        let python = pythons.first_mut().unwrap();
        assert!(python.is_valid());
        assert!(python.interpreter().is_ok());
        assert!(python.architecture().is_ok());
    }
}
