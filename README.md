# base

新しいプロジェクトを始めるときの土台（スターター）を 4 つ入れたリポジトリです。
どれも、そのディレクトリだけをコピーして使えます。

VS Code と Neovim (LazyVim) のどちらでも、保存時の整形、lint、型チェック、テスト、デバッグが動くようにしてあります。

| ディレクトリ               | 何の土台か                                | 主な中身                                                  |
| -------------------------- | ----------------------------------------- | --------------------------------------------------------- |
| [pythonbase](pythonbase)   | Python のライブラリ、コマンドラインツール | uv、Ruff、mypy、pytest、pre-commit                        |
| [fastapibase](fastapibase) | FastAPI の API（REST、WebSocket、SSE）    | 上に加えて FastAPI、Pydantic、13 ステップのハンズオン     |
| [reactbase](reactbase)     | React (Vite) の画面。fastapibase を呼ぶ   | Vite 8、React 19、TypeScript 7、Oxlint、oxfmt、Vitest     |
| [nextbase](nextbase)       | Next.js の画面。fastapibase を呼ぶ        | Next.js 16、TypeScript 5、ESLint、Tailwind、oxfmt、Vitest |

正確なバージョンは、それぞれの README とロックファイルにあります。

## 全体の構成

```
          ブラウザ
   ┌─────────┴──────────┐
   v                    v
reactbase            nextbase
Vite :5173           Next.js :3000
   │ /api/* を転送       │ /api/* を転送
   └─────────┬──────────┘
             v
        fastapibase
        FastAPI :8000
```

画面は 2 つとも、ブラウザから見ると自分のサーバーの `/api` を呼ぶだけです。開発サーバーが FastAPI に転送します。そのため、API 側に CORS の設定はいりません。

## 1. 必要なツール

| ツール  | 用途                                          | 確認したバージョン |
| ------- | --------------------------------------------- | ------------------ |
| git     |                                               | 2.56               |
| uv      | Python 本体、依存、venv の管理                | 0.13.8             |
| Node.js | reactbase、nextbase                           | 26.13.1            |
| pnpm    | JavaScript のパッケージ管理                   | 12.19.0            |
| Task    | 任意。ルートから全部を動かす `task` コマンド  | 3.54.0             |
| xh      | 任意。`curl` より短く書ける HTTP クライアント | 0.26.3             |

Node.js は 22.22.2 以上、24.15.0 以上、26 以上のどれかが必要です。Python は uv が自動で入れます。

```sh
# Arch 系 (CachyOS など)。Task のコマンド名は go-task になる
sudo pacman -S --needed git uv nodejs pnpm go-task xh
```

```powershell
# Windows (winget)。こちらは実機では確認していない
winget install Git.Git astral-sh.uv OpenJS.NodeJS.LTS pnpm.pnpm Task.Task ducaale.xh
```

## 2. 動かす

```sh
git clone https://github.com/hjosugi/base
cd base
task setup    # 4 つとも依存を入れる
task dev      # fastapibase と reactbase を同時に起動する
```

- <http://localhost:5173> が React の画面です。
- <http://127.0.0.1:8000/docs> が API の Swagger UI です。
- 止めるときは Ctrl+C です。

| コマンド        | 内容                                              |
| --------------- | ------------------------------------------------- |
| `task setup`    | 全部の依存を入れる                                |
| `task dev`      | fastapibase + reactbase                           |
| `task dev:next` | fastapibase + nextbase（<http://localhost:3000>） |
| `task api`      | fastapibase だけ                                  |
| `task react`    | reactbase だけ                                    |
| `task next`     | nextbase だけ                                     |
| `task check`    | 全部の lint、整形チェック、型チェック、テスト     |

Task を入れない場合は、各ディレクトリで直接実行します。

```sh
cd fastapibase && uv sync && uv run fastapi dev    # ターミナル 1
cd reactbase && pnpm install && pnpm dev           # ターミナル 2
```

## 3. 新しいプロジェクトを始める

使いたい base のディレクトリだけを取り出します。

```sh
# clone せずに 1 つだけ取り出す
npx tiged hjosugi/base/reactbase my-app

# clone 済みなら、コピーでもよい（node_modules や .venv は含めない）
cp -r base/reactbase my-app
```

そのあとの手順（名前の変更など）は、各 base の README の「使い方」にあります。

## 4. エディタの準備

### VS Code

次の拡張機能を入れます。各 base の `.vscode/settings.json` が、これらを前提にしています。

| 拡張機能                    | ID                              | 使う base               |
| --------------------------- | ------------------------------- | ----------------------- |
| Python（Debugger を含む）   | `ms-python.python`              | pythonbase、fastapibase |
| Ruff                        | `charliermarsh.ruff`            | pythonbase、fastapibase |
| Mypy Type Checker           | `ms-python.mypy-type-checker`   | pythonbase、fastapibase |
| FastAPI                     | `FastAPILabs.fastapi-vscode`    | fastapibase             |
| Even Better TOML            | `tamasfe.even-better-toml`      | pythonbase、fastapibase |
| Oxc                         | `oxc.oxc-vscode`                | reactbase、nextbase     |
| TypeScript (Native Preview) | `TypeScriptTeam.native-preview` | reactbase               |
| ESLint                      | `dbaeumer.vscode-eslint`        | nextbase                |
| Tailwind CSS IntelliSense   | `bradlc.vscode-tailwindcss`     | nextbase                |
| Vitest                      | `vitest.explorer`               | reactbase、nextbase     |
| EditorConfig                | `editorconfig.editorconfig`     | 全部                    |

```sh
for ext in ms-python.python charliermarsh.ruff ms-python.mypy-type-checker \
  FastAPILabs.fastapi-vscode tamasfe.even-better-toml oxc.oxc-vscode \
  TypeScriptTeam.native-preview dbaeumer.vscode-eslint bradlc.vscode-tailwindcss \
  vitest.explorer editorconfig.editorconfig; do
  code --install-extension "$ext"
done
```

開き方は 2 つあります。

- **1 つだけ開く**: `code reactbase` のように、base のディレクトリを開きます。
- **4 つまとめて開く**: `code base.code-workspace` を開きます。フォルダーごとに設定が分かれるので、Python は各自の `.venv`、JavaScript は各自の `node_modules` を使います。API とブラウザを同時にデバッグする構成「Full stack: FastAPI + React」も入っています。

保存すると整形されます。Ctrl+S で保存したときは、lint の自動修正も走ります。

### Neovim (LazyVim)

`:LazyExtras` を開いて、次の Extras を有効にします（行にカーソルを置いて `x`）。

| Extra                    | 用途                                                             |
| ------------------------ | ---------------------------------------------------------------- |
| `lang.python`            | pyright と Ruff の LSP、pytest（neotest）、デバッガ、venv の選択 |
| `lang.typescript`        | TypeScript と JavaScript の土台、Node とブラウザのデバッガ       |
| `lang.typescript.tsc`    | TypeScript 7 のネイティブ LSP                                    |
| `lang.typescript.oxc`    | Oxlint の LSP と oxfmt                                           |
| `linting.eslint`         | ESLint の LSP（nextbase）                                        |
| `lang.tailwind`          | Tailwind CSS の補完（nextbase）                                  |
| `lang.json`、`lang.toml` | `package.json` や `pyproject.toml` の補完                        |
| `dap.core`               | デバッガの画面とキー                                             |
| `test.core`              | テストの実行（neotest）                                          |
| `editor.overseer`        | 任意。`package.json` の scripts や Taskfile を選んで実行する     |

さらに、`~/.config/nvim/lua/plugins/` に次のファイルを置きます。

```lua
-- lua/plugins/base.lua
return {
  -- Run Vitest with <leader>tt. The test.core extra has no Vitest adapter.
  {
    "nvim-neotest/neotest",
    optional = true,
    dependencies = { "marilari88/neotest-vitest" },
    opts = { adapters = { ["neotest-vitest"] = {} } },
  },
  -- Use oxfmt only in a project that has an oxfmt config file.
  -- Without this, the oxc extra formats JS, TS and JSON files in every project.
  {
    "stevearc/conform.nvim",
    opts = {
      formatters = {
        oxfmt = {
          require_cwd = true,
          cwd = function(_, ctx)
            return vim.fs.root(ctx.dirname, { ".oxfmtrc.json", ".oxfmtrc.jsonc", "oxfmt.config.ts" })
          end,
        },
      },
    },
  },
}
```

使うときの注意です。

- **初回は LSP がまだ入っていません。** ファイルを開くと Mason がインストールを始めます。`<leader>cm` で終わったことを確認して、Neovim を開き直します。
- **base のディレクトリで起動します**（`cd fastapibase && nvim`）。デバッグ構成の `.vscode/launch.json` は、Neovim を起動したディレクトリから探すからです。
- **デバッグ構成は VS Code と共通です。** `<leader>dc` を押すと、`launch.json` の構成が選べます。
- **nextbase は TypeScript 5 です。** エディタの LSP には、Mason が入れた TypeScript 7 が使われます。`pnpm typecheck` と `pnpm build` は、プロジェクトの TypeScript 5 を使います。

## 5. ショートカット早見表

VS Code の列は初期設定のキーです（Windows と Linux）。自分でキーを変えている場合や、Vim 拡張を使っている場合は違います。
LazyVim の `<leader>` はスペースキーです。スペースを押して少し待つと、続きのキーの一覧が出ます。

### 移動と検索

| やりたいこと             | VS Code                      | LazyVim                    |
| ------------------------ | ---------------------------- | -------------------------- |
| ファイル名で開く         | Ctrl+P                       | `<leader>ff`               |
| プロジェクト全体を検索   | Ctrl+Shift+F                 | `<leader>/`                |
| ファイルツリー           | Ctrl+Shift+E                 | `<leader>e`                |
| 開いているファイルの一覧 | Ctrl+Tab                     | `<leader>,`                |
| 定義へ移動               | F12                          | `gd`                       |
| 参照を表示               | Shift+F12                    | `gr`                       |
| 元の場所に戻る           | Alt+←（Linux は Ctrl+Alt+-） | `<C-o>`                    |
| ファイル内のシンボル     | Ctrl+Shift+O                 | `<leader>ss`               |
| コマンドを名前で探す     | Ctrl+Shift+P                 | `<leader>sk`（キーの一覧） |

### 読む、直す

| やりたいこと                          | VS Code                               | LazyVim      |
| ------------------------------------- | ------------------------------------- | ------------ |
| 型やドキュメントを表示                | Ctrl+K Ctrl+I（マウスを乗せてもよい） | `K`          |
| 名前の変更                            | F2                                    | `<leader>cr` |
| コードアクション（import の追加など） | Ctrl+.                                | `<leader>ca` |
| import の整理                         | Shift+Alt+O                           | `<leader>co` |
| 整形                                  | Shift+Alt+F（Linux は Ctrl+Shift+I）  | `<leader>cf` |
| 次の問題へ                            | F8                                    | `]d`         |
| 問題の一覧                            | Ctrl+Shift+M                          | `<leader>xx` |
| 行のコメント切り替え                  | Ctrl+/                                | `gcc`        |
| 保存時の整形を止める、戻す            | —                                     | `<leader>uf` |

### 実行、テスト、デバッグ

| やりたいこと                   | VS Code                            | LazyVim                 |
| ------------------------------ | ---------------------------------- | ----------------------- |
| ターミナル                     | Ctrl+`                             | `<C-/>`                 |
| タスクを選んで実行             | Ctrl+Shift+P → Tasks: Run Task     | `<leader>oo`            |
| Git の画面                     | Ctrl+Shift+G                       | `<leader>gg`（lazygit） |
| 開いているファイルのテスト     | Ctrl+; F                           | `<leader>tt`            |
| カーソル位置のテスト           | Ctrl+; C                           | `<leader>tr`            |
| すべてのテスト                 | Ctrl+; A                           | `<leader>tT`            |
| カーソル位置のテストをデバッグ | Ctrl+; Ctrl+C                      | `<leader>td`            |
| テストの一覧                   | テストビュー（フラスコのアイコン） | `<leader>ts`            |
| ブレークポイント               | F9                                 | `<leader>db`            |
| デバッグの開始、続行           | F5                                 | `<leader>dc`            |
| ステップオーバー               | F10                                | `<leader>dO`            |
| ステップイン                   | F11                                | `<leader>di`            |
| ステップアウト                 | Shift+F11                          | `<leader>do`            |
| デバッグの停止                 | Shift+F5                           | `<leader>dt`            |
| 式を評価                       | デバッグコンソール                 | `<leader>de`            |
| デバッグの画面                 | Ctrl+Shift+D                       | `<leader>du`            |

### Neovim だけのもの

| キー              | 内容                                          |
| ----------------- | --------------------------------------------- |
| `<leader>cl`      | いまのファイルにつながっている LSP を表示     |
| `<leader>cm`      | Mason（LSP やフォーマッタのインストール状況） |
| `<leader>cv`      | Python の venv を選ぶ                         |
| `<leader>uh`      | インレイヒントの表示を切り替える              |
| `:LazyFormatInfo` | いまのファイルで使われるフォーマッタを表示    |

## 6. ハンズオン: API と画面をまたいで 1 項目足す

Todo に「優先度（priority）」を足します。fastapibase と reactbase の両方を変えます。
型チェッカーが「次に直す場所」を教えてくれることを確かめるのが目的です。

各 base の README にも、その base だけのハンズオンがあります。fastapibase のものが一番長く、空のディレクトリから API を作ります。

### 準備

```sh
task dev
```

<http://localhost:5173> で Todo を足せることを確認します。別のターミナルから API を呼ぶと、画面にもすぐ出ます。

```sh
xh :8000/todos title="from terminal"
# xh がなければ
curl -X POST localhost:8000/todos -H 'content-type: application/json' -d '{"title":"from terminal"}'
```

### 手順 1: 呼び出しをたどる

「定義へ移動」で、画面から API まで順に読みます。

1. `reactbase/src/components/TodoForm.tsx` の `onAdd`
2. `reactbase/src/useTodos.ts` の `add` と `createTodo`
3. `reactbase/src/api.ts` の `createTodo`（ここで `POST /api/todos` を送る）
4. `fastapibase/src/todo_api/routers/todos.py` の `create_todo`（ここで受ける）
5. `fastapibase/src/todo_api/schemas.py` の `TodoCreate` と `Todo`

### 手順 2: API の型に priority を足す

`fastapibase/src/todo_api/schemas.py` の 3 つのクラスに、1 行ずつ足します。

```python
class TodoCreate(BaseModel):
    ...
    done: bool = False
    priority: int = Field(default=2, ge=1, le=3)   # add


class TodoUpdate(BaseModel):
    ...
    done: bool | None = None
    priority: int | None = Field(default=None, ge=1, le=3)   # add


class Todo(BaseModel):
    ...
    done: bool
    priority: int   # add
    created_at: datetime
```

### 手順 3: 型チェッカーに次の場所を聞く

`fastapibase` で型チェックを実行します。

```sh
uv run mypy
```

```
src/todo_api/repository.py:50: error: Missing named argument "priority" for "Todo"  [call-arg]
tests/test_todos.py:126: error: Missing named argument "priority" for "Todo"  [call-arg]
```

`Todo` を作っている場所が 2 つ見つかりました。両方に足します。

```python
# src/todo_api/repository.py
            todo = Todo(
                id=self._next_id,
                title=data.title,
                done=data.done,
                priority=data.priority,   # add
                created_at=datetime.now(UTC),
            )
```

```python
# tests/test_todos.py (FakeRepo)
            done=False,
            priority=2,   # add
```

もう一度 `uv run mypy` を実行して、エラーが 0 件になることを確認します。

### 手順 4: テストを足す

`fastapibase/tests/test_todos.py` の最後に足します。

```python
def test_priority_defaults_to_2(client: TestClient) -> None:
    assert client.post("/todos", json={"title": "a"}).json()["priority"] == 2


def test_priority_out_of_range_is_422(client: TestClient) -> None:
    res = client.post("/todos", json={"title": "a", "priority": 4})
    assert res.status_code == 422
```

`uv run pytest` を実行します。42 件すべて通ります。エディタからも実行してみます（早見表の「開いているファイルのテスト」）。

### 手順 5: デバッガで値を見る

1. `task dev` を止めます（デバッガが同じポート 8000 を使うため）。画面だけ `task react` で起動し直します。
2. `fastapibase/src/todo_api/routers/todos.py` の `todo = repo.add(payload)` の行にブレークポイントを置きます。
3. デバッグ構成「FastAPI: debug (no reload)」を開始します。
4. priority を付けて Todo を作ります。

```sh
xh :8000/todos title="debug me" priority:=1
```

5. エディタで止まります。`payload.priority` が `1` になっていることを確認して、続行します。

### 手順 6: 画面の型に足す

`reactbase/src/api.ts` の `Todo` に 1 行足します。

```ts
export type Todo = {
  id: number;
  title: string;
  done: boolean;
  priority: number; // add: 1 (high) to 3 (low)
  created_at: string; // ISO 8601
};
```

`reactbase` で型チェックを実行します。

```sh
pnpm typecheck
```

```
src/App.test.tsx(7,7): error TS2741: Property 'priority' is missing in type '{ ... }' but required in type 'Todo'.
```

テスト用のデータに足りないと教えてくれます。`src/App.test.tsx` の `milk` に `priority: 2,` を足します。

### 手順 7: 画面に出す

`reactbase/src/components/TodoList.tsx` で、タイトルの次の行に足します。

```tsx
            <span className={todo.done ? 'done' : undefined}>{todo.title}</span>
            <small>P{todo.priority}</small>
```

画面を見ると、各 Todo に `P2` などが出ます。

### 手順 8: 全部のチェックを通す

```sh
task check
```

元に戻すときは `git checkout .` を実行します。

## 7. 確認したこと、していないこと

2026 年 11 月に、CachyOS (Linux) で次のことを実際に動かして確認しました。

- 4 つの base の lint、整形チェック、型チェック、テスト、ビルド（`task check` が通る）
- reactbase と nextbase から、プロキシ経由で fastapibase の作成、更新、削除ができること。reactbase では SSE も届くこと
- Neovim (LazyVim 16、Neovim 0.12): 4 つの base で LSP がつながり、診断が出て、保存時の整形がプロジェクトの設定どおりになること
- Neovim: pytest と Vitest を neotest で実行できること
- Neovim: `launch.json` の構成で、FastAPI と Vitest をブレークポイントで止められること
- 6 章のハンズオンの手順 2 から 8

次のことは確認していません。

- **VS Code の画面での動作。** 設定ファイルは書式と設定名を確認しただけです。保存時の整形、デバッグ構成、`base.code-workspace` の複合構成は、画面では試していません。
- **ブラウザのデバッグ構成**（Chrome、Brave）。
- **Neovim からの Next.js のデバッグ。** nextbase の構成は VS Code 用です。Neovim で「Next.js: debug full stack」を開始しても、サーバーが起動しませんでした。
- **Windows と macOS。**
