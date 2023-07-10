use clap::Parser;
use findpython::cli;

fn main() -> anyhow::Result<()> {
    let args = cli::Cli::parse();
    cli::main(args)
}
