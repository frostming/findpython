use std::path::PathBuf;

use super::Provider;

#[derive(Debug, Clone, PartialEq, Eq)]
pub(super) struct RyeProvider {
    root: PathBuf,
}

impl RyeProvider {
    pub fn new(root: PathBuf) -> Self {
        Self { root }
    }
}

impl Provider for RyeProvider {
    fn create() -> Option<Self>
    where
        Self: Sized,
    {
        let rye_root = std::env::var_os("RYE_ROOT")
            .or_else(|| Some(dirs::home_dir()?.join(".rye").into_os_string()))?;
        Some(Self::new(rye_root.into()))
    }

    fn find_pythons(&self) -> Vec<crate::PythonVersion> {
        let py_root = self.root.join("py");
        match py_root.read_dir() {
            Ok(entries) => entries
                .into_iter()
                .filter_map(|entry| match entry {
                    Ok(entry) if !entry.path().is_symlink() => {
                        let python = entry.path().join("install/bin/python3");
                        if python.exists() {
                            Some(crate::PythonVersion::new(python.clone()).with_interpreter(python))
                        } else {
                            None
                        }
                    }
                    _ => None,
                })
                .collect(),
            Err(_) => vec![],
        }
    }
}
