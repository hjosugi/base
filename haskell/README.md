# haskell

Haskell の CLI スターターです。安定版 GHC 9.14.1、Cabal 3.18.2.0、HLS 2.15.0.0、Fourmolu 0.21.0.0 を基準にしています。サンプルは Haskell 標準の `base` パッケージだけで動く word-count CLI です。

## セットアップ

| 方法                                                     | コマンド                                                                                                         |
| -------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| GHCup                                                    | `ghcup install ghc 9.14.1 && ghcup set ghc 9.14.1 && ghcup install cabal 3.18.2.0 && ghcup install hls 2.15.0.0` |
| mise                                                     | `mise install`（GHC/HLS は pinned `mise-ghcup`、Fourmolu は公式 GitHub release を使用）                          |
| Nix（リポジトリ内）                                      | `nix develop ..#haskell`                                                                                         |
| Docker (`haskell:9.14.1-slim-bookworm` / Cabal 3.18.2.0) | `docker build -t haskell-starter .`                                                                              |

Fourmolu は `ghcup install fourmolu 0.21.0.0` で追加します。Nix は `flake.lock` の再現性を優先し、現在 GHC 9.14.1 / Cabal 3.16.1.0 / HLS 2.13.0.0 / Fourmolu 0.19.0.1 です。最新ツール一式を同じ版で使う場合は mise または GHCup を選びます。

```sh
cabal build all
cabal run word-count -- README.md -n 5
fourmolu --mode inplace app src test
fourmolu --mode check app src test
cabal test all
cabal check
```

ルートの `task check:haskell` は整形、ビルド、テストをまとめて実行します。Docker では `docker run --rm haskell-starter` を使います。

## Neovim (LazyVim)

`:LazyExtras` で `lang.haskell`、`dap.core`、`test.core` を有効にします。HLS、Fourmolu、HLint、neotest-haskell、haskell-debug-adapter が接続されます。`<localleader>r` で REPL、`<leader>tt` でテスト、`<leader>dc` でデバッグ構成を選べます。

コピー後は `word-count.cabal` の `name`、実行ファイル名、モジュール名と `.vscode/launch.json` を変更します。`dist-newstyle/` はコピーしません。
