use lazy_static::__Deref;
use std::cell::{Ref, RefCell, RefMut};
use std::process::Stdio;
use std::time::Duration;
use std::{fs, hash::Hash, io, path::PathBuf, str::FromStr};
use wait_timeout::ChildExt;

use pep440_rs::Version;

use crate::finder::MatchOptions;
use crate::helpers::calculate_file_hash;

static GET_VERSION_TIMEOUT: u64 = 5;

fn resolve_symlink(path: &PathBuf) -> Result<PathBuf, io::Error> {
    let mut path = path.clone();
    while fs::symlink_metadata(&path)?.file_type().is_symlink() {
        path = fs::read_link(path)?;
    }
    Ok(path)
}

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
            executable: fs::canonicalize(executable).unwrap(),
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
        resolve_symlink(&self.executable).unwrap_or_else(|e| self.executable.clone())
    }

    pub fn is_valid(&mut self) -> bool {
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
    }

    pub fn version(&self) -> Result<Version, io::Error> {
        let mut inner = self.version.borrow_mut();
        Ok(inner.get_or_insert(self._get_version()?).clone())
    }

    pub fn interpreter(&self) -> Result<PathBuf, io::Error> {
        let mut inner = self.interpreter.borrow_mut();
        Ok(inner.get_or_insert(self._get_interpreter()?).clone())
    }

    pub fn architecture(&self) -> Result<String, io::Error> {
        let mut inner = self.architecture.borrow_mut();
        Ok(inner.get_or_insert(self._get_architecture()?).clone())
    }

    pub fn content_hash(&self) -> Result<String, io::Error> {
        calculate_file_hash(&PathBuf::from(&self.executable))
    }

    pub fn matches(&mut self, options: &MatchOptions) -> bool {
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

impl Hash for PythonVersion {
    fn hash<H: std::hash::Hasher>(&self, state: &mut H) {
        self.executable.hash(state);
    }
}

impl PartialEq for PythonVersion {
    fn eq(&self, other: &Self) -> bool {
        self.executable == other.executable
    }
}

impl Eq for PythonVersion {}

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
        let mut python_version = PythonVersion::new(python.clone());
        assert!(python_version.is_valid());
        let version = python_version.version().unwrap();
        assert_eq!(version.release[..2], [3, 11]);
        assert!(python_version.interpreter().is_ok());
        assert!(python_version.content_hash().is_ok());
    }

    #[test]
    fn test_match_python() {
        let python = which("python3.11").unwrap();
        let mut python_version = PythonVersion::new(python);
        assert!(python_version.matches(&MatchOptions {
            name: Some("python3.11".to_string()),
            major: Some(3),
            minor: Some(11),
            ..MatchOptions::default()
        }));
    }
}
