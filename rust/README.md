# rust

Rust の CLI スターターです。Rust 1.100.0、2024 Edition、rustfmt、Clippy、標準テスト、rust-analyzer、CodeLLDB を揃えています。サンプルは依存パッケージなしの word-count CLI です。

## セットアップ

| 方法                                  | コマンド                                                                    |
| ------------------------------------- | --------------------------------------------------------------------------- |
| rustup                                | `rustup toolchain install 1.100.0 --component clippy,rust-analyzer,rustfmt` |
| mise                                  | `mise install`                                                              |
| Nix（リポジトリ内）                   | `nix develop ..#rust`                                                       |
| Docker (`rust:1.100.0-slim-bookworm`) | `docker build -t rust-starter .`                                            |

```sh
cargo run -- README.md -n 5
cargo fmt
cargo clippy --all-targets --all-features -- -D warnings
cargo test
```

まとめて確認するときは、リポジトリのルートから `task check:rust` を実行します。Docker では `docker run --rm rust-starter`、別のファイルを読むときは `docker run --rm -v "$PWD:/work:ro" rust-starter /work/README.md -n 5` です。

## Neovim (LazyVim)

`:LazyExtras` で `lang.rust`、`dap.core`、`test.core` を有効にします。`lang.rust` が rust-analyzer、rustfmt、Clippy、CodeLLDB、neotest を設定します。プロジェクトのディレクトリで `nvim` を起動し、`<leader>tt` でテスト、`<leader>dr` でデバッグ可能なターゲットを選べます。

## コピー後に変えるもの

- `Cargo.toml` の `name`、`description`
- `src/lib.rs` と `src/main.rs` のサンプル実装
- `.vscode/launch.json` のバイナリ名と引数

`target/` は生成物なのでコピーしません。`Cargo.lock` はアプリケーションの再現性のためコミットします。
