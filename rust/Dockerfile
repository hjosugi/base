FROM rust:1.100.0-slim-bookworm

WORKDIR /app
COPY Cargo.toml Cargo.lock ./
COPY src ./src
COPY README.md ./
RUN cargo test --locked && cargo build --locked --release

ENTRYPOINT ["/app/target/release/wordcount"]
CMD ["README.md", "-n", "5"]
