use anyhow::anyhow;
use clap::Parser;

use crate::{Finder, MatchOptions};

#[derive(Parser, Debug)]
#[command(author, version, about, long_about = None)]
pub struct Cli {
    /// Return all matching Python versions
    #[arg(short, long)]
    all: bool,

    /// Resolve symlinks and remove duplicate results
    #[arg(long)]
    resolve_symlinks: bool,

    /// Remove duplicate results that are the same binary
    #[arg(long = "no-same-file", action=clap::ArgAction::SetFalse, default_value_t = true)]
    same_file: bool,

    /// Remove duplicate results that wrap the same Python interpreter
    #[arg(long = "no-same-python", action=clap::ArgAction::SetFalse, default_value_t = true)]
    same_python: bool,

    /// Select provider names(comma-separated) to use
    #[arg(long)]
    providers: Option<String>,

    /// The output format
    #[arg(short, long, value_parser = ["default", "json", "path"], default_value = "default")]
    output: String,

    /// The version spec to find, e.g. 3|3.8|python3
    version_spec: Option<String>,
}

pub fn main(cli: Cli) -> anyhow::Result<()> {
    let mut finder = Finder::default()
        .resolve_symlinks(cli.resolve_symlinks)
        .same_file(cli.same_file)
        .same_interpreter(cli.same_python);

    if let Some(names) = cli.providers {
        let v = names.split(',').into_iter().map(|n| {
            if !crate::providers::ALL_PROVIDERS.contains(&n) {
                Err(anyhow!(format!("Provider {} not found", n)))
            } else {
                Ok(n)
            }
        }).collect::<Result<Vec<_>, _>>()?;
        finder = finder.select_providers(&v)?;
    }

    let mut options = MatchOptions::default();
    if let Some(version_spec) = cli.version_spec.as_deref() {
        options = options.version_spec(version_spec);
    }

    let paths = if cli.all {
        finder.find_all(options)
    } else {
        finder.find(options).map_or(vec![], |v| vec![v])
    };

    if paths.len() == 0 {
        return Err(anyhow!("No matching Python versions found"));
    }
    eprintln!("Found matching Python versions:");
    match cli.output.as_str() {
        "default" => {
            for path in paths {
                println!("{}", path);
            }
        }
        "path" => {
            for path in paths {
                println!("{}", path.executable.to_string_lossy());
            }
        }
        "json" => {
            let json = if cli.all {
                serde_json::to_string_pretty(&paths)?
            } else {
                serde_json::to_string_pretty(&paths[0])?
            };
            println!("{}", json);
        }
        _ => {
            return Err(anyhow!("Unsupported output format"));
        }
    }
    Ok(())
}
