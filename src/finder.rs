use std::{collections::HashMap, io};

use crate::{helpers::suffix_preference, providers::*, PythonVersion};
use fancy_regex::Regex;
use lazy_static::lazy_static;

#[cfg(feature = "pyo3")]
use pyo3::prelude::*;

lazy_static! {
    static ref VERSION_REGEX: Regex = Regex::new(
        r#"(?x)
        ^(?P<major>\d+)(?:\.(?P<minor>\d+)(?:\.(?P<patch>[0-9]+))?)?\.?
        (?:(?P<prerel>[abc]|rc|dev)(?:(?P<prerelversion>\d+(?:\.\d+)*))?)
        ?(?P<postdev>(\.post(?P<post>\d+))?(\.dev(?P<dev>\d+))?)?
        (?:-(?P<architecture>32|64))?"#
    )
    .unwrap();
}

#[cfg_attr(feature = "pyo3", pyclass)]
pub struct Finder {
    providers: Vec<Box<dyn Provider>>,
    resolve_symlinks: bool,
    same_file: bool,
    same_interpreter: bool,
}

impl Finder {
    pub fn new() -> Self {
        Self {
            providers: vec![],
            resolve_symlinks: false,
            same_file: true,
            same_interpreter: true,
        }
    }
}

impl Default for Finder {
    fn default() -> Self {
        Self::new().select_providers(&ALL_PROVIDERS[..]).unwrap()
    }
}

impl Finder {
    pub fn select_providers(mut self, names: &[&str]) -> Result<Self, io::Error> {
        self.providers = names
            .iter()
            .map(|n| {
                get_provider(*n).ok_or_else(|| {
                    io::Error::new(io::ErrorKind::NotFound, format!("Provider {} not found", n))
                })
            })
            .collect::<Result<Vec<_>, _>>()?;
        Ok(self)
    }

    pub fn resolve_symlinks(mut self, resolve_symlinks: bool) -> Self {
        self.resolve_symlinks = resolve_symlinks;
        self
    }

    pub fn same_file(mut self, same_file: bool) -> Self {
        self.same_file = same_file;
        self
    }

    pub fn same_interpreter(mut self, same_interpreter: bool) -> Self {
        self.same_interpreter = same_interpreter;
        self
    }

    fn find_all_python_versions(&self) -> Vec<PythonVersion> {
        self.providers
            .iter()
            .flat_map(|p| p.find_pythons())
            .collect()
    }

    pub fn find_all(&self, text: Option<&str>, options: MatchOptions) -> Vec<PythonVersion> {
        let mut options = options;
        if let Some(s) = text {
            if let Some(o) = MatchOptions::from_version(s) {
                options = o.merge(options);
            }
        }

        let pythons = self.find_all_python_versions();
        let mut filtered = vec![];
        for python in pythons {
            if python.matches(&options) {
                filtered.push(python);
            }
        }
        self.deduplicate(filtered)
    }

    pub fn find(&self, text: Option<&str>, options: MatchOptions) -> Option<PythonVersion> {
        self.find_all(text, options).first().cloned()
    }

    fn deduplicate_key(&self, python: &mut PythonVersion) -> String {
        if !self.same_interpreter {
            return python.interpreter().unwrap().to_str().unwrap().to_string();
        }
        if !self.same_file {
            return python.content_hash().unwrap();
        }
        if self.resolve_symlinks && !python.keep_symlink {
            return python.real_path().to_str().unwrap().to_string();
        }
        python.executable.to_str().unwrap().to_string()
    }

    fn deduplicate(&self, versions: Vec<PythonVersion>) -> Vec<PythonVersion> {
        let mut result = HashMap::new();
        let mut versions = versions;

        versions.sort_by_cached_key(|p| {
            (
                p.executable.is_symlink(),
                suffix_preference(&p.executable),
                -(p.executable.to_string_lossy().len() as isize),
            )
        });

        for version in versions.iter_mut() {
            let key = self.deduplicate_key(version);
            result.entry(key).or_insert(version.to_owned());
        }
        let mut py_versions = result.into_values().collect::<Vec<_>>();
        py_versions.sort_by(|a, b| {
            (b.version().unwrap(), b.executable.to_string_lossy().len())
                .cmp(&(a.version().unwrap(), a.executable.to_string_lossy().len()))
        });
        py_versions
    }
}

#[cfg(feature = "pyo3")]
#[derive(FromPyObject)]
enum StringInt {
    STRING(String),
    INT(usize),
}

#[cfg(feature = "pyo3")]
#[pymethods]
impl Finder {
    #[new]
    #[pyo3(signature = (resolve_symlinks = false, no_same_file = false, no_same_interpreter = false, selected_providers = None))]
    fn py_new(
        resolve_symlinks: bool,
        no_same_file: bool,
        no_same_interpreter: bool,
        selected_providers: Option<Vec<String>>,
    ) -> Result<Self, io::Error> {
        let mut f = Self {
            providers: vec![],
            resolve_symlinks,
            same_file: !no_same_file,
            same_interpreter: !no_same_interpreter,
        };
        if let Some(names) = selected_providers {
            let names: Vec<&str> = names.iter().map(|v| v.as_str()).collect();
            f = f.select_providers(names.as_slice())?
        }
        Ok(f)
    }

    #[getter]
    fn get_resolve_symlinks(&self) -> bool {
        self.resolve_symlinks
    }

    #[setter]
    fn set_resolve_symlinks(&mut self, resolve_symlinks: bool) {
        self.resolve_symlinks = resolve_symlinks
    }

    #[getter]
    fn get_same_file(&self) -> bool {
        self.same_file
    }

    #[setter]
    fn set_same_file(&mut self, same_file: bool) {
        self.same_file = same_file
    }

    #[getter]
    fn get_same_interpreter(&self) -> bool {
        self.same_interpreter
    }

    #[setter]
    fn set_same_interpreter(&mut self, same_interpreter: bool) {
        self.same_interpreter = same_interpreter
    }

    #[pyo3(name = "find_all")]
    fn py_find_all(
        &self,
        major: Option<StringInt>,
        minor: Option<usize>,
        patch: Option<usize>,
        pre: Option<bool>,
        dev: Option<bool>,
        name: Option<String>,
        architecture: Option<String>,
    ) -> Vec<PythonVersion> {
        let text = if let Some(StringInt::STRING(s)) = &major {
            Some(s.as_str())
        } else {
            None
        };
        self.find_all(
            text,
            MatchOptions {
                major: if let Some(StringInt::INT(i)) = major {
                    Some(i)
                } else {
                    None
                },
                minor,
                patch,
                pre,
                dev,
                name,
                architecture,
            },
        )
    }

    #[pyo3(name = "find")]
    fn py_find(
        &self,
        major: Option<StringInt>,
        minor: Option<usize>,
        patch: Option<usize>,
        pre: Option<bool>,
        dev: Option<bool>,
        name: Option<String>,
        architecture: Option<String>,
    ) -> Option<PythonVersion> {
        let text = if let Some(StringInt::STRING(s)) = &major {
            Some(s.as_str())
        } else {
            None
        };
        self.find(
            text,
            MatchOptions {
                major: if let Some(StringInt::INT(i)) = major {
                    Some(i)
                } else {
                    None
                },
                minor,
                patch,
                pre,
                dev,
                name,
                architecture,
            },
        )
    }
}

#[derive(Debug, Clone, PartialEq, Eq, Default)]
pub struct MatchOptions {
    pub major: Option<usize>,
    pub minor: Option<usize>,
    pub patch: Option<usize>,
    pub pre: Option<bool>,
    pub dev: Option<bool>,
    pub name: Option<String>,
    pub architecture: Option<String>,
}

impl MatchOptions {
    pub fn from_version(version: &str) -> Option<Self> {
        match VERSION_REGEX.captures(version) {
            Ok(Some(capture)) => Some(Self {
                major: capture.name("major").map(|m| m.as_str().parse().unwrap()),
                minor: capture.name("minor").map(|m| m.as_str().parse().unwrap()),
                patch: capture.name("patch").map(|m| m.as_str().parse().unwrap()),
                pre: capture.name("prerel").map(|_| true),
                dev: capture.name("dev").map(|_| true),
                name: None,
                architecture: capture
                    .name("architecture")
                    .map(|m| format!("{}bit", m.as_str())),
            }),
            _ => None,
        }
    }

    pub fn merge(self, other: Self) -> Self {
        Self {
            major: other.major.or(self.major),
            minor: other.minor.or(self.minor),
            patch: other.patch.or(self.patch),
            pre: other.pre.or(self.pre),
            dev: other.dev.or(self.dev),
            name: other.name.or(self.name),
            architecture: other.architecture.or(self.architecture),
        }
    }
}

#[cfg(test)]
mod test {
    use super::*;

    #[test]
    fn test_find_pythons() {
        let finder = Finder::default();

        let pythons = finder.find_all(None, MatchOptions::default());
        assert!(pythons.len() > 0);
    }
}
