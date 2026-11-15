use std::{env, fs, process::ExitCode};

fn usage(program: &str) -> String {
    format!("Usage: {program} FILE [-n LIMIT]")
}

fn parse_args() -> Result<(String, usize), String> {
    let mut args = env::args();
    let program = args.next().unwrap_or_else(|| "wordcount".into());
    let mut path = None;
    let mut limit = 10;

    while let Some(arg) = args.next() {
        if arg == "-n" || arg == "--limit" {
            let value = args.next().ok_or_else(|| usage(&program))?;
            limit = value.parse().map_err(|_| {
                format!("limit must be a non-negative integer\n{}", usage(&program))
            })?;
        } else if path.replace(arg).is_some() {
            return Err(usage(&program));
        }
    }

    path.map(|path| (path, limit))
        .ok_or_else(|| usage(&program))
}

fn run() -> Result<(), String> {
    let (path, limit) = parse_args()?;
    let text = fs::read_to_string(&path).map_err(|error| format!("{path}: {error}"))?;

    for (word, count) in wordcount::top_words(&text, limit) {
        println!("{count:>6} {word}");
    }
    Ok(())
}

fn main() -> ExitCode {
    match run() {
        Ok(()) => ExitCode::SUCCESS,
        Err(error) => {
            eprintln!("wordcount: {error}");
            ExitCode::FAILURE
        }
    }
}
