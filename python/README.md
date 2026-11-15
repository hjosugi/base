# python

Python のスタータープロジェクトです。このディレクトリをコピーして、新しいライブラリやコマンドラインツールを始めます。Web フレームワークは入っていません。API を作るときは [fastapi](../fastapi) を使います。

| 項目                 | 内容               | バージョン    |
| -------------------- | ------------------ | ------------- |
| 言語                 | Python             | 3.15.2        |
| パッケージ管理       | uv                 | 0.13.8 で確認 |
| リンタ、フォーマッタ | Ruff               | 0.17.5        |
| 型チェック           | mypy（strict）     | 2.4.1         |
| テスト               | pytest、pytest-cov | 9.2.0、7.1.0  |
| コミット前チェック   | pre-commit         | 4.7.0         |
| デバッガ             | debugpy            | 1.8.22        |

サンプルとして、テキストの単語を数える小さなコマンドが入っています。

## セットアップ方法

| 方法                                        | コマンド                                                             |
| ------------------------------------------- | -------------------------------------------------------------------- |
| uv                                          | `uv sync`（Python 3.15.2 も自動取得）                                |
| mise                                        | `mise install && uv sync`                                            |
| Nix（リポジトリ内）                         | `nix develop ..#python`                                              |
| Docker (`python:3.15.2-slim` / `uv:0.13.8`) | `docker build -t python-starter . && docker run --rm python-starter` |

## 使い方

```sh
# 1. このディレクトリをコピーする
cp -r python /path/to/my-tool
cd /path/to/my-tool

# 2. 依存を入れる（Python 本体も uv が入れる）
uv sync

# 3. 動かす
uv run wordcount README.md -n 5
```

`.venv` がすでにある場合は、コピーに含めません。コピー先で `uv sync` をやり直します。

コピーしたあとに、名前を自分のプロジェクトに合わせて変えます。

1. `src/wordcount_cli/` のディレクトリ名を変えます（例: `src/my_tool/`）。
2. `pyproject.toml` の `name`、`[project.scripts]`、`--cov=wordcount_cli`、`per-file-ignores` のパスを変えます。
3. `tests/` と `src/` の `from wordcount_cli...` を変えます。
4. `.vscode/launch.json` の `"module": "wordcount_cli.cli"` を変えます。
5. `uv sync` を実行して、`uv run pytest` が通ることを確認します。

## コマンド

| コマンド                            | 内容                                       |
| ----------------------------------- | ------------------------------------------ |
| `uv run wordcount FILE [-n 数]`     | サンプルのコマンドを実行する               |
| `uv run ruff check`                 | lint（`--fix` を付けると自動で直す）       |
| `uv run ruff format`                | 整形する（`--check` を付けると調べるだけ） |
| `uv run mypy`                       | 型チェック                                 |
| `uv run pytest`                     | テストとカバレッジ（90% 未満は失敗）       |
| `uv run pytest --no-cov -x`         | カバレッジなし。最初の失敗で止める         |
| `uv run pre-commit install`         | コミットのたびにチェックが動くようにする   |
| `uv run pre-commit run --all-files` | すべてのチェックをいま実行する             |
| `uv add パッケージ名`               | 依存を足す（開発用は `uv add --dev`）      |

コマンドは `uv run` で実行します。venv の activate はいりません。

## ディレクトリ構成

```
python/
├── pyproject.toml            依存と、ruff / mypy / pytest の設定
├── uv.lock                   依存のバージョンを固定する（コミットする）
├── .python-version           Python 3.15.2
├── .pre-commit-config.yaml
├── .editorconfig / .gitattributes   改行を LF にそろえる
├── .github/workflows/ci.yml  リポジトリのルートに置いたときに動く CI
├── .vscode/
│   ├── settings.json         保存時の整形
│   ├── launch.json           デバッグの構成
│   └── extensions.json       必要な拡張機能
├── src/wordcount_cli/
│   ├── wordcount.py          処理の本体（入出力をしない関数）
│   └── cli.py                コマンドラインの入口
└── tests/
    ├── test_wordcount.py
    └── test_cli.py
```

`src/` の下にパッケージを置く形（src レイアウト）です。テストは、インストールされたパッケージを import します。

## ハンズオン

エディタの操作は [ルートの README のショートカット早見表](../README.md#5-ショートカット早見表) を見てください。

### 1. 動かす

```sh
uv sync
uv run wordcount README.md -n 5
uv run pytest
```

### 2. lint と整形を見る

`src/wordcount_cli/wordcount.py` の最後に次の 2 行を足して保存します。

```python
import os
x = {'a':1}
```

- 保存すると整形されます（`{"a": 1}` になります）。
- `uv run ruff check` を実行します。`import os` が未使用（F401）など、3 件の指摘が出ます。
- 足した行を消します。

### 3. 型チェックを見る

`src/wordcount_cli/cli.py` の `limit: int = args.limit` の下に、次の行を足します。

```python
    limit = "10"
```

`uv run mypy` を実行します。次のエラーが出ます。

```
error: Incompatible types in assignment (expression has type "str", variable has type "int")
```

足した行を消します。

### 4. テストを壊して直す

1. `src/wordcount_cli/wordcount.py` の `word.lower()` を `word` に変えます。
2. `uv run pytest` を実行します。`test_count_ignores_case_and_punctuation` が失敗します。
3. 元に戻します。

エディタからテストを実行する方法も試します。VS Code はテストビュー、Neovim は `<leader>tt`（ファイル全体）と `<leader>tr`（カーソル位置のテスト）です。

### 5. デバッガで止める

1. `src/wordcount_cli/wordcount.py` の `ranked = sorted(...)` の行にブレークポイントを置きます。
2. デバッグ構成「wordcount: run (README.md)」を開始します。
3. 止まったら `counts` の中身を見ます。デバッグコンソールで `counts.most_common(3)` も実行できます。
4. `tests/test_wordcount.py` を開いて「pytest: current file」も試します。

### 6. コミット前チェックを入れる

```sh
git init
uv run pre-commit install
uv run pre-commit run --all-files
```

手順 2 や 3 の間違いを入れたまま `git commit` をすると、コミットが止まります。

## デバッグ

デバッグ構成は `.vscode/launch.json` にあります。VS Code でも Neovim (nvim-dap) でも同じファイルを使います。

| 構成                       | 使う場面                                                    |
| -------------------------- | ----------------------------------------------------------- |
| wordcount: run (README.md) | サンプルのコマンドを引数付きで実行する。`args` を変えて使う |
| Python: current file       | 開いているファイルを実行する                                |
| pytest: current file       | 開いているテストファイルを実行する                          |
| Attach to debugpy (:5678)  | ターミナルで起動したプログラムにあとから接続する            |

エディタなしで止めるときは、コードに `breakpoint()` を 1 行足します。消し忘れは Ruff（T100）が見つけます。

## 困ったとき

- **`uv run` が Python をダウンロードし始める**: 正常です。`.python-version` の Python がまだないときに、uv が入れます。
- **保存しても整形されない (VS Code)**: Ruff 拡張機能（`charliermarsh.ruff`）が入っているか確認します。
- **エディタが import を解決できない**: インタープリタが `.venv` になっているか確認します。VS Code は「Python: Select Interpreter」、Neovim は `<leader>cv` です。
- **`uv_build` のバージョンのエラーが出る**: `pyproject.toml` の `[build-system]` の範囲を、いまの uv に合わせます。
