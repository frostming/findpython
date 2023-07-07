use fancy_regex::Regex;
use lazy_static::lazy_static;
use std::{ffi::OsStr, io, os::macos::fs::MetadataExt, path::PathBuf};

#[cfg(target_os = "windows")]
lazy_static! {
    static ref KNOWN_EXECUTABLES: [&'static str; 3] = ["exe", "py", "bat"];
}

#[cfg(not(target_os = "windows"))]
lazy_static! {
    static ref KNOWN_EXECUTABLES: [&'static str; 6] = ["sh", "bash", "csh", "zsh", "fish", "py"];
}
lazy_static! {
    static ref PYTHON_IMPLEMENTATIONS: [&'static str; 10] = [
        "python",
        "ironpython",
        "jython",
        "pypy",
        "anaconda",
        "miniconda",
        "stackless",
        "activepython",
        "pyston",
        "micropython",
    ];
    static ref PYTHON_MATCHER: Regex = Regex::new(
        format!(
            r#"(?ix)
        ^((?P<implementation>{})
        (?:\d(?:\.?\d\d?[cpm]{{0,3}})?)?
        (?:(?<=\d)-[\d\.]+)*(?!w))
        (?P<suffix>\.(?:{}))?$
        "#,
            PYTHON_IMPLEMENTATIONS.join("|"),
            KNOWN_EXECUTABLES.join("|")
        )
        .as_str()
    )
    .unwrap();
}

pub fn path_is_python(path: &PathBuf) -> bool {
    looks_like_python(path.file_name().unwrap_or_default()) && path_is_known_executable(path)
}

fn looks_like_python(name: &OsStr) -> bool {
    PYTHON_MATCHER
        .is_match(name.to_str().unwrap_or_default())
        .unwrap_or_default()
}

fn path_is_known_executable(path: &PathBuf) -> bool {
    let path_meta = std::fs::metadata(path).unwrap();
    let mode = path_meta.st_mode();
    let extension = path.extension().map(|e| e.to_str().unwrap().to_lowercase());

    path_meta.is_file()
        && mode & 0o400 != 0  // is readable
        && (mode & 0o100 != 0  // is executable
            || extension.map_or(true, |e| KNOWN_EXECUTABLES.contains(&e.as_str()))  // has known extension
        )
}

pub fn calculate_file_hash(path: &PathBuf) -> Result<String, io::Error> {
    let mut file = std::fs::File::open(path)?;
    let mut hasher = md5::Context::new();
    std::io::copy(&mut file, &mut hasher)?;
    Ok(format!("{:x}", hasher.compute()))
}

pub fn suffix_preference(path: &PathBuf) -> usize {
    let ext = path.extension().map(|e| e.to_str().unwrap().to_lowercase());
    if let Some(ext) = ext {
        KNOWN_EXECUTABLES
            .iter()
            .position(|&e| e == ext.as_str())
            .unwrap_or_default()
    } else {
        0
    }
}
