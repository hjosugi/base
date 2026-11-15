# elixir

Elixir の CLI スターターです。Elixir 1.20.5 と Erlang/OTP 29.1.2、Mix、ExUnit、ElixirLS を使います。サンプルは外部依存のない word-count CLI です。

## セットアップ

| 方法                                 | コマンド                                            |
| ------------------------------------ | --------------------------------------------------- |
| 公式配布                             | OTP 29.1.2 と Elixir 1.20.5 (OTP 29 build) を入れる |
| mise                                 | `mise install`                                      |
| Nix（リポジトリ内）                  | `nix develop ..#elixir`                             |
| Docker (`elixir:1.20.5-otp-29-slim`) | `docker build -t elixir-starter .`                  |

```sh
mix format
mix format --check-formatted
mix compile --warnings-as-errors
mix test
mix escript.build
./word_count README.md -n 5
```

ルートの `task check:elixir` で一式を確認します。Docker では `docker run --rm elixir-starter` を使います。

## Neovim (LazyVim)

`:LazyExtras` で `lang.elixir` と `test.core` を有効にします。ElixirLS、Mix formatter、neotest-elixir が使えます。`<leader>tt` でテストを実行できます。`.vscode/launch.json` は ElixirLS のデバッグアダプタ対応エディタ用です。

コピー後は `mix.exs` の `app` とモジュール名、escript 名を変更します。`_build/`、`deps/`、生成した `word_count` はコピーしません。
