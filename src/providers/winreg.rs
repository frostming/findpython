use std::io::Result;
use std::str::FromStr;
use pep440_rs::Version;
use winreg::enums::*;
use winreg::RegKey;
use winreg::HKEY;

use crate::PythonVersion;

use super::Provider;

static PYTHON_PATH: &'static str = r"Software\Python";

struct PythonRegSource {
    key: HKEY,
    flags: u32,
    arch: Option<&'static str>,
}


impl PythonRegSource {
    fn get_python(&self, reg: &RegKey) -> Result<PythonVersion> {
        let version = if let Ok(ver) = reg.get_value::<String, _>("Version") {
            Version::from_str(ver.as_str()).ok()
        } else {
            None
        };
        let install_path: String = reg.open_subkey_with_flags("InstallPath", KEY_READ | self.flags)?.get_value("ExecutablePath")?;
        let arch = reg.get_value::<String, _>("SysArchitecture").ok().or_else(|| self.arch.map(|a| a.to_string()));
        let mut py = PythonVersion::new(install_path.into());
        if let Some(arch) = arch {
            py = py.with_architecture(arch.as_str());
        }

        if let Some(version) = version {
            Ok(py.with_version(version))
        } else {
            Ok(py)
        }
    }

    fn find_all(&self) -> Vec<PythonVersion> {
        let hklm = RegKey::predef(self.key);
        let subkey = hklm.open_subkey_with_flags(PYTHON_PATH, KEY_READ | self.flags);
        
        if let Ok(key) = subkey {
            let companies = key.enum_keys().filter_map(|company| {
                key.open_subkey_with_flags(company.ok()?, KEY_READ | self.flags).ok()
            });
            companies.flat_map(|k| {
                k.enum_keys().filter_map(|tag| {
                    let py = tag.and_then(|t| k.open_subkey_with_flags(t, KEY_READ | self.flags)).ok()?;
                    self.get_python(&py).ok()
                }).collect::<Vec<_>>()
            }).collect::<Vec<_>>()
        } else {
            vec![]
        }
    }
}

fn get_sources() -> Vec<PythonRegSource> {
    if cfg!(target_pointer_width = "64") {
        vec![
            PythonRegSource {
                key: HKEY_CURRENT_USER,
                flags: 0,
                arch: None,
            },
            PythonRegSource {
                key: HKEY_LOCAL_MACHINE,
                flags: KEY_WOW64_64KEY,
                arch: Some("64bit"),
            },
            PythonRegSource {
                key: HKEY_LOCAL_MACHINE,
                flags: KEY_WOW64_32KEY,
                arch: Some("32bit"),
            },
        ]
    } else {
        vec![
            PythonRegSource {
                key: HKEY_CURRENT_USER,
                flags: 0,
                arch: Some("32bit"),
            },
            PythonRegSource {
                key: HKEY_LOCAL_MACHINE,
                flags: KEY_WOW64_64KEY,
                arch: Some("32bit"),
            },
        ]
    }
}

pub struct WinRegProvider {
    sources: Vec<PythonRegSource>
}

impl Provider for WinRegProvider {
    fn create() -> Option<Self>
        where
            Self: Sized {
        Some(Self { sources: get_sources() })
    }

    fn find_pythons(&self) -> Vec<PythonVersion> {
        self.sources.iter().flat_map(|s| s.find_all()).collect::<Vec<_>>()
    }
}

#[cfg(test)]
mod test {
    use super::*;

    #[test]
    fn test_find_python() {
        let provider = WinRegProvider::create().unwrap();
        let pythons = provider.find_pythons();
        assert!(pythons.len() > 0);
    }
}