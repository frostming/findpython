use pyo3::exceptions::PyNotImplementedError;
use serde::ser::SerializeStruct;
use std::cell::RefCell;
use std::fmt;
use std::process::Stdio;
use std::time::Duration;
use std::{hash::Hash, io, path::PathBuf, str::FromStr};
use wait_timeout::ChildExt;

#[cfg(feature = "pyo3")]
use pep440_rs::PyVersion;
use pep440_rs::Version;
#[cfg(feature = "pyo3")]
use pyo3::{basic::CompareOp, prelude::*};

use crate::finder::MatchOptions;
use crate::helpers::calculate_file_hash;

static GET_VERSION_TIMEOUT: u64 = 5;

fn run_python_script(cmd: &str, script: &str, timeout: Option<u64>) -> Result<String, io::Error> {
    use std::process::Command;
    let args = vec!["-EsSc", script];
    let mut child = Command::new(cmd)
        .args(args)
        .stdout(Stdio::piped())
        .stderr(Stdio::null())
        .spawn()?;
    match timeout {
        Some(duration) => match child.wait_timeout(Duration::from_secs(duration as u64))? {
            Some(status) => {
                if status.success() {
                    Ok(
                        String::from_utf8(child.wait_with_output()?.stdout).map_err(|e| {
                            io::Error::new(
                                io::ErrorKind::Other,
                                format!("Command '{}' output is not valid UTF-8: {}", cmd, e),
                            )
                        })?,
                    )
                } else {
                    Err(io::Error::new(
                        io::ErrorKind::Other,
                        format!(
                            "Command '{}' failed with exit code {}",
                            cmd,
                            status.code().unwrap_or(-1)
                        ),
                    ))
                }
            }
            _ => {
                child.kill()?;
                child.wait()?;
                Err(io::Error::new(
                    io::ErrorKind::TimedOut,
                    format!("Command '{}' timed out", cmd),
                ))
            }
        },
        None => {
            let output = child.wait_with_output()?;
            if !output.status.success() {
                return Err(io::Error::new(
                    io::ErrorKind::Other,
                    format!(
                        "Command '{}' failed with exit code {}",
                        cmd,
                        output.status.code().unwrap_or(-1)
                    ),
                ));
            }
            Ok(String::from_utf8(output.stdout).map_err(|e| {
                io::Error::new(
                    io::ErrorKind::Other,
                    format!("Command '{}' output is not valid UTF-8: {}", cmd, e),
                )
            })?)
        }
    }
}

#[cfg_attr(feature = "pyo3", pyclass)]
#[derive(Debug, Clone)]
pub struct PythonVersion {
    /// The path to the Python executable.
    pub executable: PathBuf,
    version: RefCell<Option<Version>>,
    interpreter: RefCell<Option<PathBuf>>,
    architecture: RefCell<Option<String>>,
    /// Whether to keep the symlink to the Python executable.
    pub keep_symlink: bool,
}

impl PythonVersion {
    pub fn new(executable: PathBuf) -> Self {
        Self {
            executable,
            version: RefCell::new(None),
            interpreter: RefCell::new(None),
            architecture: RefCell::new(None),
            keep_symlink: false,
        }
    }

    pub fn with_version(mut self, version: Version) -> Self {
        self.version = RefCell::new(Some(version));
        self
    }

    pub fn with_interpreter(mut self, interpreter: PathBuf) -> Self {
        self.interpreter = RefCell::new(Some(interpreter));
        self
    }

    pub fn with_architecture(mut self, architecture: String) -> Self {
        self.architecture = RefCell::new(Some(architecture));
        self
    }

    pub fn with_keep_symlink(mut self, keep_symlink: bool) -> Self {
        self.keep_symlink = keep_symlink;
        self
    }

    pub fn real_path(&self) -> PathBuf {
        self.executable
            .canonicalize()
            .unwrap_or_else(|_| self.executable.clone())
    }

    pub fn is_valid(&self) -> bool {
        self.version().is_ok()
    }

    fn _get_version(&self) -> Result<Version, io::Error> {
        let script = "import platform; print(platform.python_version())";
        let output = run_python_script(
            &self.executable.to_string_lossy(),
            script,
            Some(GET_VERSION_TIMEOUT),
        )?;
        let version = output.trim().split('+').next().unwrap();
        Version::from_str(version).map_err(|e| {
            io::Error::new(
                io::ErrorKind::Other,
                format!("Failed to parse Python version '{}': {}", version, e),
            )
        })
    }

    fn _get_interpreter(&self) -> Result<PathBuf, io::Error> {
        let script = "import sys; print(sys.executable)";
        let output = run_python_script(&self.executable.to_string_lossy(), script, None)?;
        Ok(PathBuf::from(output.trim()))
    }

    fn _get_architecture(&self) -> Result<String, io::Error> {
        let script = "import platform; print(platform.architecture()[0])";
        run_python_script(&self.executable.to_string_lossy(), script, None)
            .map(|v| v.trim().to_string())
    }

    pub fn version(&self) -> Result<Version, io::Error> {
        let mut inner = self.version.borrow_mut();
        match inner.as_ref() {
            Some(version) => Ok(version.clone()),
            None => Ok(inner.insert(self._get_version()?).clone()),
        }
    }

    pub fn interpreter(&self) -> Result<PathBuf, io::Error> {
        let mut inner = self.interpreter.borrow_mut();
        match inner.as_ref() {
            Some(interpreter) => Ok(interpreter.clone()),
            None => Ok(inner.insert(self._get_interpreter()?).clone()),
        }
    }

    pub fn architecture(&self) -> Result<String, io::Error> {
        let mut inner = self.architecture.borrow_mut();
        match inner.as_ref() {
            Some(architecture) => Ok(architecture.clone()),
            None => Ok(inner.insert(self._get_architecture()?).clone()),
        }
    }

    pub fn content_hash(&self) -> Result<String, io::Error> {
        calculate_file_hash(&PathBuf::from(&self.executable))
    }

    pub fn matches(&self, options: &MatchOptions) -> bool {
        if let Some(name) = options.name.as_ref() {
            if self.executable.file_name().unwrap().to_str() != Some(name.as_str()) {
                return false;
            }
        }
        if let Some(arch) = options.architecture.as_ref() {
            if self.architecture().is_err() || self.architecture().unwrap().as_str() != arch {
                return false;
            }
        }

        if let Ok(version) = self.version() {
            if let Some(major) = options.major {
                if version.release.get(0) != Some(&major) {
                    return false;
                }
            }
            if let Some(minor) = options.minor {
                if version.release.get(1) != Some(&minor) {
                    return false;
                }
            }
            if let Some(patch) = options.patch {
                if version.release.get(2) != Some(&patch) {
                    return false;
                }
            }
            if let Some(dev) = options.dev {
                if version.is_dev() != dev {
                    return false;
                }
            }
            if let Some(pre) = options.pre {
                if version.is_pre() != pre {
                    return false;
                }
            }
            true
        } else {
            false
        }
    }
}

impl fmt::Display for PythonVersion {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(
            f,
            "{} {} @ {}",
            self.executable.file_name().unwrap().to_string_lossy(),
            self.version()
                .map_or("INVALID".to_string(), |v| v.to_string()),
            self.executable.to_string_lossy()
        )
    }
}

impl Hash for PythonVersion {
    fn hash<H: std::hash::Hasher>(&self, state: &mut H) {
        self.executable.hash(state);
    }
}

impl serde::Serialize for PythonVersion {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: serde::Serializer,
    {
        let mut s = serializer.serialize_struct("PythonVersion", 4)?;
        s.serialize_field("executable", &self.executable)?;
        s.serialize_field(
            "version",
            &self
                .version()
                .map_or("INVALID".to_string(), |v| v.to_string()),
        )?;
        s.serialize_field("architecture", &self.architecture().unwrap_or_default())?;
        s.serialize_field("interpreter", &self.interpreter().unwrap_or_default())?;
        s.end()
    }
}

impl PartialEq for PythonVersion {
    fn eq(&self, other: &Self) -> bool {
        self.executable == other.executable
    }
}

impl Eq for PythonVersion {}

#[cfg(feature = "pyo3")]
#[pymethods]
impl PythonVersion {
    #[new]
    #[pyo3(signature = (executable, *, interpreter = None, version = None, architecture = None, keep_symlink = false))]
    fn py_new(
        executable: PathBuf,
        interpreter: Option<PathBuf>,
        version: Option<PyVersion>,
        architecture: Option<String>,
        keep_symlink: bool,
    ) -> Self {
        let mut result = Self::new(executable).with_keep_symlink(keep_symlink);
        if let Some(interpreter) = interpreter {
            result = result.with_interpreter(interpreter);
        }
        if let Some(version) = version {
            result = result.with_version(version.0);
        }
        if let Some(architecture) = architecture {
            result = result.with_architecture(architecture);
        }
        result
    }

    #[getter]
    fn executable(&self) -> PathBuf {
        self.executable.clone()
    }

    #[getter]
    fn keep_symlink(&self) -> bool {
        self.keep_symlink
    }

    #[getter(version)]
    fn py_version(&self) -> Result<PyVersion, io::Error> {
        self.version().map(|v| PyVersion(v))
    }

    #[getter(interpreter)]
    fn py_interpreter(&self) -> Result<PathBuf, io::Error> {
        self.interpreter()
    }

    #[getter(architecture)]
    fn py_architecture(&self) -> Result<String, io::Error> {
        self.architecture()
    }

    #[pyo3(name = "is_valid")]
    fn py_is_valid(&self) -> bool {
        self.is_valid()
    }

    #[pyo3(name = "matches", signature = (major = None, minor = None, patch = None, pre = None, dev = None, name = None, architecture = None))]
    fn py_matches(
        &self,
        major: Option<usize>,
        minor: Option<usize>,
        patch: Option<usize>,
        pre: Option<bool>,
        dev: Option<bool>,
        name: Option<String>,
        architecture: Option<String>,
    ) -> bool {
        self.matches(&MatchOptions {
            major,
            minor,
            patch,
            pre,
            dev,
            name,
            architecture,
        })
    }

    fn __str__(&self) -> String {
        self.to_string()
    }

    fn __repr__(&self) -> String {
        format!(
            "<PythonVersion executable={}, version={}, arch={}>",
            self.executable.to_string_lossy(),
            self.version()
                .map_or("invalid".to_string(), |v| v.to_string()),
            self.architecture().unwrap_or("unknown".to_string())
        )
    }

    fn __richcmp__(&self, other: &Self, op: CompareOp) -> PyResult<bool> {
        match op {
            CompareOp::Eq => Ok(self == other),
            CompareOp::Ne => Ok(self != other),
            CompareOp::Le => Ok((self.version()?, self.executable.to_string_lossy().len())
                < (other.version()?, self.executable.to_string_lossy().len())),
            _ => Err(PyNotImplementedError::new_err("Not supported comparison")),
        }
    }
}

#[cfg(test)]
mod test {
    use super::*;
    use which::which;

    #[test]
    fn test_run_command() {
        let output = run_python_script(
            "python3",
            "import time; time.sleep(1); print('hello')",
            None,
        )
        .unwrap();
        assert_eq!(output, "hello\n");
    }

    #[test]
    fn test_run_command_with_timeout() {
        let output = run_python_script(
            "python3",
            "import time; time.sleep(1); print('hello')",
            Some(2),
        )
        .unwrap();
        assert_eq!(output, "hello\n");

        let output = run_python_script(
            "python3",
            "import time; time.sleep(2); print('hello')",
            Some(1),
        )
        .unwrap_err();
        assert_eq!(output.kind(), io::ErrorKind::TimedOut);
    }

    #[test]
    fn test_python_version_info() {
        let python = which("python3.11").unwrap();
        let python_version = PythonVersion::new(python.clone());
        assert!(python_version.is_valid());
        let version = python_version.version().unwrap();
        assert_eq!(version.release[..2], [3, 11]);
        assert!(python_version.interpreter().is_ok());
        assert!(python_version.content_hash().is_ok());
    }

    #[test]
    fn test_match_python() {
        let python = which("python3.11").unwrap();
        let python_version = PythonVersion::new(python);
        assert!(python_version.matches(&MatchOptions {
            name: Some("python3.11".to_string()),
            major: Some(3),
            minor: Some(11),
            ..MatchOptions::default()
        }));
    }
}
