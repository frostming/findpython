use shellexpand;
use std::path::PathBuf;

use super::Provider;

#[derive(Debug, Clone, PartialEq, Eq)]
pub(super) struct AsdfProvider {
    root: PathBuf,
}

impl AsdfProvider {
    pub fn new(root: PathBuf) -> Self {
        Self { root }
    }
}

impl Provider for AsdfProvider {
    fn create() -> Option<Self> {
        let pyenv_root = std::env::var_os("ASDF_DATA_DIR").unwrap_or("$HOME/.asdf".into());

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
        let versions_path = self.root.join("installs/python");
        match versions_path.read_dir() {
            Ok(entries) => entries
                .into_iter()
                .flat_map(|entry| match entry {
                    Ok(entry) if entry.path().is_dir() => {
                        let path = entry.path().join("bin");
                        if path.is_dir() {
                            super::find_pythons_from_path(&path, true)
                        } else {
                            vec![]
                        }
                    }
                    _ => vec![],
                })
                .collect(),
            Err(_) => vec![],
        }
    }
}
