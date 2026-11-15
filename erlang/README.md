# erlang

Erlang/OTP の CLI スターターです。OTP 29.1.2、rebar3 3.28.0、erlfmt 1.8.0、EUnit、xref、Dialyzer を使います。エディタは保守終了した Erlang LS ではなく ELP 2026-10-14 を使います。

## セットアップ

| 方法                                          | コマンド                                           |
| --------------------------------------------- | -------------------------------------------------- |
| 公式配布                                      | Erlang/OTP 29.1.2 と rebar3 3.28.0 を入れる        |
| mise                                          | `mise install`（ELP は公式 GitHub release を使用） |
| Nix（リポジトリ内）                           | `nix develop ..#erlang`                            |
| Docker (`erlang:29.1.2-slim` / rebar3 3.28.0) | `docker build -t erlang-starter .`                 |

```sh
rebar3 compile
rebar3 fmt -w
rebar3 fmt --check
rebar3 eunit
rebar3 xref
rebar3 dialyzer
rebar3 escriptize
_build/default/bin/word_count README.md -n 5
```

`rebar3 check` またはルートの `task check:erlang` で一式を確認します。初回の Dialyzer は PLT を作るため時間がかかります。

## Neovim (LazyVim)

`:LazyExtras` で `lang.erlang` を有効にします。ただし現行の LazyVim では移行途中の版があるため、ルート README の `elp` 上書き設定も入れてください。ELP は補完、定義ジャンプ、診断、整形を担当します。EUnit と Dialyzer はターミナルか Overseer から実行します。

コピー後はアプリケーション名 `word_count`、`rebar.config` の escript 名、モジュール名を変更します。`_build/` はコピーしません。
