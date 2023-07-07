use shellexpand;
use std::path::PathBuf;

use super::Provider;

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct PyenvProvider {
    root: PathBuf,
}

impl PyenvProvider {
    pub fn new(root: PathBuf) -> Self {
        Self { root }
    }
}

impl Provider for PyenvProvider {
    fn name(&self) -> &'static str {
        "pyenv"
    }

    fn create() -> Option<Self> {
        let pyenv_root = std::env::var_os("PYENV_ROOT").unwrap_or("$HOME/.pyenv".into());

        let root =
            shellexpand::env_with_context_no_errors(pyenv_root.to_str().unwrap(), |var_name| {
                let s = match var_name {
                    "HOME" => dirs::home_dir()?.into_os_string(),
                    var => std::env::var_os(var)?,
                };
                Some(s.into_string().unwrap())
            });

        let path = PathBuf::from(root.into_owned());
        if path.exists() {
            Some(Self::new(path))
        } else {
            None
        }
    }

    fn find_pythons(&self) -> Vec<crate::python::PythonVersion> {
        let versions_path = self.root.join("versions");
        match versions_path.read_dir() {
            Ok(entries) => entries
                .into_iter()
                .flat_map(|entry| match entry {
                    Ok(entry) => {
                        let path = entry.path();
                        if path.is_dir() {
                            self.find_pythons_from_path(&path.join("bin"), true)
                        } else {
                            vec![]
                        }
                    }
                    Err(_) => vec![],
                })
                .collect(),
            Err(_) => vec![],
        }
    }
}
