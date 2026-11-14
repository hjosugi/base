# FastAPI ハンズオン: 開発環境込みで Todo API を作る

このディレクトリは [base](../README.md) の中の FastAPI 用スターターです。コピーして、新しい API を始められます。
[reactbase](../reactbase) と [nextbase](../nextbase) の画面は、この API を使います。

FastAPI で小さな Todo API を作りながら、実務で使う開発環境を一式そろえるハンズオンです。
API の書き方だけでなく、次のものを最初から入れます。

- パッケージ管理: uv
- Linter / Formatter: Ruff
- 型チェック: mypy (strict + Pydantic plugin)
- テスト: pytest + TestClient + coverage
- デバッグ: VS Code (debugpy) / attach (nvim-dap も可) / pdb / FastAPI の debug モード
- コミット前チェック: pre-commit
- CI: GitHub Actions
- リアルタイム通知: WebSocket と SSE (Server-Sent Events)

このリポジトリは完成形です。各 Step は「空のディレクトリから順に作る」前提で書いています。
迷ったら完成形のファイルを見てください。

想定時間: 3〜4 時間 (Step 0〜10) + 2 時間 (Step 11〜13: WebSocket / SSE)

---

## 使うツールとバージョン

2026-11-13 時点で PyPI / GitHub の最新を確認し、すべてこの環境で実際に動かしています。

| ツール | バージョン | 役割 |
| --- | --- | --- |
| Python | 3.14 | 実行環境 (uv が自動で入れる) |
| uv | 0.11 | Python 本体・依存・venv・lock の管理 |
| FastAPI | 0.162 (`fastapi[standard]`) | Web フレームワーク。`fastapi` CLI と Uvicorn も入る |
| Pydantic / pydantic-settings | 2.14 / 2.16 | 入出力の検証 / 環境変数からの設定読み込み |
| Ruff | 0.17 | Linter + Formatter (flake8, isort, black の代わり) |
| mypy | 2.4 | 静的型チェック |
| pytest / pytest-cov | 9.2 / 7.1 | テスト / カバレッジ |
| pre-commit | 4.7 | `git commit` 時に自動チェック |
| debugpy | 1.8 | VS Code / nvim-dap が使う Python デバッガ |
| ty (任意) | 0.0.x (beta) | Astral 製の高速型チェッカー。今回は「試すだけ」 |
| websockets | 17.4 | `fastapi[standard]` に入っている。WebSocket の CLI クライアントとしても使う |
| xh (任意) | 0.26 | curl より楽な HTTP クライアント。SSE の確認にも使える |

---

## 全体像

### どのタイミングで何がチェックするか

```
  書く             保存               git commit             git push / PR
 ───────────>  ───────────────>  ─────────────────────>  ─────────────────>
  VS Code        Ruff 拡張          pre-commit              GitHub Actions
  - mypy 拡張    - format           - ruff check --fix      - uv sync --locked
  - Ruff 拡張    - fix / import     - ruff format           - ruff check
    (波線で表示)    の整理            - mypy                  - ruff format --check
                                    - uv-lock               - mypy
                                    - 末尾空白 / 改行 等     - pytest (coverage 90%)
```

同じ Ruff / mypy を 3 か所で動かします。
バージョンは `uv.lock` で固定するので、手元と CI で結果が変わりません。

### リクエストの流れ (Step 5〜6 で作る部分)

```
HTTP request
   |
   v
middleware.request_context      X-Request-ID を決める / 処理時間をログに出す
   |
   v
routers/todos.py                パス / クエリ / ボディを型で検証 (NG なら 422)
   |  Depends(get_repository)
   v
deps.get_repository             app.state.todo_repo を返す (テストで差し替え可能)
   |
   v
repository.InMemoryTodoRepository   dict にデータを保存
```

---

## 完成形のディレクトリ構成

```
fastapibase/
├── pyproject.toml            依存とツール設定 (ruff / mypy / pytest / fastapi)
├── uv.lock                   依存の lock ファイル (コミットする)
├── .python-version           Python 3.14
├── .pre-commit-config.yaml
├── .env.example              .env にコピーして使う
├── .editorconfig / .gitattributes   改行を LF に統一
├── .vscode/
│   ├── extensions.json       推奨拡張
│   ├── settings.json         保存時 format など
│   └── launch.json           デバッグ設定
├── .github/workflows/ci.yml
├── src/todo_api/
│   ├── main.py               create_app() と app
│   ├── config.py             Settings (pydantic-settings)
│   ├── log_config.py         ロギング設定 + request_id
│   ├── middleware.py         X-Request-ID と処理時間
│   ├── schemas.py            Pydantic モデル
│   ├── repository.py         Protocol + インメモリ実装
│   ├── deps.py               Depends 用の関数と型エイリアス
│   ├── events.py             EventBroker (pub/sub)       Step 11
│   ├── shutdown.py           停止シグナルでストリームを閉じる  Step 13
│   ├── static/demo.html      WebSocket / SSE のデモページ   Step 12
│   └── routers/
│       ├── health.py
│       ├── todos.py          CRUD + SSE (/todos/events)
│       ├── ws.py             WebSocket (/ws/todos)        Step 12
│       └── demo.py           GET /demo
└── tests/
    ├── conftest.py
    ├── test_health.py
    ├── test_todos.py
    ├── test_events.py        EventBroker の単体テスト
    ├── test_ws.py
    ├── test_sse.py
    └── test_shutdown.py
```

完成形をそのまま動かすだけなら、次の 3 行です。

```bash
uv sync
cp .env.example .env
uv run fastapi dev
```

---

## Step 0: 準備

### uv を入れる

```bash
# Linux / macOS
curl -LsSf https://astral.sh/uv/install.sh | sh
```

```powershell
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
# または
winget install --id=astral-sh.uv -e
```

```bash
uv --version
```

Python 本体は先に入れなくて大丈夫です。uv が `.python-version` を見て自動で取ってきます。

### VS Code の拡張

完成形の `.vscode/extensions.json` に推奨拡張を書いてあります。
フォルダを開くと「推奨拡張をインストールしますか」と出るので、全部入れてください。

| 拡張 ID | 用途 |
| --- | --- |
| `ms-python.python` | Python 本体のサポート (Pylance 込み) |
| `ms-python.debugpy` | Python Debugger |
| `charliermarsh.ruff` | Ruff (保存時 format / fix) |
| `ms-python.mypy-type-checker` | mypy の結果をエディタに表示 |
| `FastAPILabs.fastapi-vscode` | FastAPI 公式拡張。エンドポイント一覧とジャンプ |
| `tamasfe.even-better-toml` | pyproject.toml の補完 |
| `editorconfig.editorconfig` | .editorconfig を反映 |

---

## Step 1: プロジェクトを作る

```bash
uv init --package --python 3.14 fastapibase --name todo-api
cd fastapibase
```

`--package` を付けると `src/todo_api/` という src レイアウトで作られます。
src レイアウトにすると「インストールしたパッケージとして import する」形になり、テストとアプリで import の挙動がそろいます。

できたら `src/todo_api/__init__.py` の中身 (`def main()`) は消して、docstring だけにします。
`pyproject.toml` の `[project.scripts]` も今回は使わないので消します。

### 依存を追加する

```bash
# Runtime dependencies
uv add "fastapi[standard]" pydantic-settings

# Dev-only dependencies (go to [dependency-groups].dev)
uv add --dev ruff mypy pytest pytest-cov pre-commit debugpy
```

ポイント:

- `fastapi[standard]` で `fastapi` コマンド、Uvicorn、httpx (TestClient が使う) などがまとめて入ります。
- `--dev` で入れたものは `[dependency-groups]` の `dev` に入ります。本番イメージには入れません。
- `uv.lock` ができます。これはコミットします。全員と CI が同じバージョンを使うためです。
- 以後、コマンドは `uv run <cmd>` で実行します。venv の activate は不要です。

---

## Step 2: 最小の API を動かす

`src/todo_api/main.py` を作ります。

```python
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Hello, FastAPI!"}
```

`pyproject.toml` に、アプリの場所を書きます。

```toml
[tool.fastapi]
entrypoint = "todo_api.main:app"
```

起動します。

```bash
uv run fastapi dev
```

- http://127.0.0.1:8000 で JSON が返ります。
- http://127.0.0.1:8000/docs で Swagger UI が開きます。

### `uvicorn main:app --reload` との違い

古い記事では `uvicorn main:app --reload` で起動しています。
今の FastAPI では `fastapi dev` が推奨です。中身は Uvicorn なので、やっていることは同じです。違いは次の点です。

| | `fastapi dev` | `fastapi run` |
| --- | --- | --- |
| 用途 | 開発 | 本番 (コンテナなど) |
| reload | 有効 | 無効 |
| listen | 127.0.0.1 | 0.0.0.0 |
| `FASTAPI_ENV` | 未設定なら `development` をセット | 変更しない |

`[tool.fastapi] entrypoint` を書いておくと、CLI と VS Code の FastAPI 拡張の両方がアプリを見つけられます。

---

## Step 3: Ruff (Linter + Formatter)

Ruff 1 つで flake8 / isort / black / pyupgrade などの役割をまとめて担当します。

### 設定

`pyproject.toml` に追加します (完成形と同じ内容)。

```toml
[tool.ruff]
line-length = 88
src = ["src", "tests"]

[tool.ruff.lint]
select = [
    "E", "W", "F",   # pycodestyle / pyflakes
    "I",             # import order
    "N",             # naming
    "UP",            # pyupgrade (new syntax)
    "B",             # bugbear (common bugs)
    "SIM", "C4",     # simplify
    "DTZ",           # naive datetime
    "T10",           # left-over breakpoint()
    "T20",           # left-over print()
    "S",             # bandit (security)
    "PT",            # pytest style
    "ASYNC",         # async pitfalls
    "FAST",          # FastAPI-specific rules
    "RUF",           # Ruff-specific rules
]

[tool.ruff.lint.per-file-ignores]
"tests/**" = ["S101"]   # assert is fine in tests
```

`target-version` は書いていません。`requires-python = ">=3.14"` から自動で決まります。

完成形ではさらに `extend-exclude = ["*.md"]` を入れています。
Ruff 0.17 は Markdown の中のコードブロックも format 対象にするためです。
この README のコード片は抜粋なので、対象から外しています。

### 動かす

```bash
uv run ruff check          # lint
uv run ruff check --fix    # auto-fix what is safe to fix
uv run ruff format         # format
```

### わざと間違えてみる

`routers/health.py` にこう書くと:

```python
import os                      # not used
...
    breakpoint()               # left-over debugger
    print(settings)            # left-over print
    count: int = settings.env  # not used (and wrong type)
```

```
I001 [*] Import block is un-sorted or un-formatted
F401 [*] `os` imported but unused
T100 Trace found: `breakpoint` used
T201 `print` found
F841 Local variable `count` is assigned to but never used
```

`T10` / `T20` を入れておくと、デバッグ用のコードを消し忘れたままコミットするのを防げます。

`FAST` ルールは FastAPI 専用です。たとえば次の書き方は `FAST002` で指摘されます。

```python
def x(repo: TodoRepository = Depends(get_repository)) -> int: ...
# FAST002 FastAPI dependency without `Annotated`
```

### VS Code で保存時に整形する

`.vscode/settings.json`:

```jsonc
"[python]": {
  "editor.defaultFormatter": "charliermarsh.ruff",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.ruff": "explicit",
    "source.organizeImports.ruff": "explicit"
  }
}
```

---

## Step 4: 型チェック (mypy strict)

FastAPI は型ヒントで入力を検証します。型チェッカーを入れると、その型ヒント自体の間違いも見つかります。

### 設定

```toml
[tool.mypy]
strict = true
plugins = ["pydantic.mypy"]
files = ["src", "tests"]

[tool.pydantic-mypy]
init_forbid_extra = true
init_typed = true
warn_required_dynamic_aliases = true
```

- `strict = true`: 型ヒントのない関数などもエラーにします。新規プロジェクトなら最初から strict が楽です。
- `pydantic.mypy`: `TodoCreate(title=1)` のような、モデル生成時の型の間違いを検出します。

```bash
uv run mypy
```

### 例: よくある入門記事のコード

入門記事でよく見る次のコードは、動きますが型として間違っています。

```python
def read_item(item_id: int, q: str = None):
    ...
```

```
$ uv run ruff check
RUF013 PEP 484 prohibits implicit `Optional`

$ uv run mypy
error: Function is missing a return type annotation  [no-untyped-def]
error: Incompatible default for parameter "q" (default has type "None", parameter has type "str")  [assignment]
```

正しくはこうです。戻り値の型も書きます。

```python
def read_item(item_id: int, q: str | None = None) -> dict[str, int | str | None]:
    ...
```

### 例: 型の取り違え

```python
count: int = settings.env
```

```
error: Incompatible types in assignment (expression has type
"Literal['development', 'test', 'staging', 'production']", variable has type "int")
```

`Literal` で値の候補を絞っておくと、ここまで細かく分かります。

### (任意) ty を試す

ty は Astral (uv / Ruff の開発元) の型チェッカーです。とても速いですが、2026-11 時点ではまだ beta (0.0.x) です。
このハンズオンでは CI のゲートには mypy を使い、ty は「試すだけ」にします。

```bash
uvx ty check
```

完成形のコードは ty でもエラー 0 件です。
途中で ty は「`@asynccontextmanager` の戻り値は `AsyncIterator` ではなく `AsyncGenerator` で書く」と指摘しました。mypy は指摘しなかった点です。
2 つの型チェッカーは得意分野が少し違います。

---

## Step 5: Todo API 本体

ここで作るエンドポイント:

| Method | Path | 説明 | 主なステータス |
| --- | --- | --- | --- |
| GET | `/health` | 死活確認 | 200 |
| GET | `/todos?done=&limit=&offset=` | 一覧 (絞り込み・ページング) | 200 / 422 |
| GET | `/todos/stats` | 件数と完了率 | 200 |
| GET | `/todos/{todo_id}` | 1 件取得 | 200 / 404 / 422 |
| POST | `/todos` | 作成 | 201 / 422 |
| PATCH | `/todos/{todo_id}` | 一部更新 | 200 / 404 / 422 |
| DELETE | `/todos/{todo_id}` | 削除 | 204 / 404 |

完成形の `src/todo_api/` を上から順に作ります。ポイントだけ説明します。

### 5-1. schemas.py: 入出力の型

```python
class TodoCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")   # unknown field -> 422

    title: str = Field(min_length=1, max_length=100, examples=["Buy milk"])
    done: bool = False
```

- `Field(min_length=..., max_length=...)` の制約は、そのまま検証と Swagger UI に反映されます。
- `extra="forbid"` にすると、クライアントの typo (例: `"titel"`) を 422 で返せます。
- 作成用 (`TodoCreate`)、更新用 (`TodoUpdate`、全部 optional)、出力用 (`Todo`) を分けます。

### 5-2. repository.py: 保存先を Protocol で抽象化

```python
class TodoRepository(Protocol):
    def list_items(self, *, done: bool | None, limit: int, offset: int) -> list[Todo]: ...
    def get(self, todo_id: int) -> Todo | None: ...
    ...
```

- 今回はインメモリ (`dict`) 実装だけです。DB 版を作るときも、ルーター側は変えません。
- 同期 (sync) のエンドポイントはスレッドプールで動くので、更新系は `threading.Lock` で守ります。
- PATCH は `model_dump(exclude_unset=True)` で「送られてきたフィールドだけ」更新します。

### 5-3. deps.py: Depends と Annotated

```python
def get_repository(request: Request) -> TodoRepository:
    return cast(TodoRepository, request.app.state.todo_repo)

RepoDep = Annotated[TodoRepository, Depends(get_repository)]
```

ルーター側は `repo: RepoDep` と書くだけです。テストではこの `get_repository` を差し替えます (Step 8)。

### 5-4. routers/todos.py: パス / クエリ / ボディ

```python
@router.get("")
def list_todos(
    repo: RepoDep,
    done: bool | None = None,                          # query
    limit: Annotated[int, Query(ge=1, le=100)] = 20,   # query with range
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[Todo]:
    ...

@router.get("/{todo_id}")
def get_todo(todo_id: int, repo: RepoDep) -> Todo:   # path
    ...

@router.post("", status_code=status.HTTP_201_CREATED)
def create_todo(payload: TodoCreate, repo: RepoDep) -> Todo:   # body
    ...
```

- 引数がパスにあればパスパラメータ、Pydantic モデルならボディ、それ以外はクエリです。
- 戻り値の型 (`-> Todo`) がレスポンスの型になります。`response_model=` は不要です (戻り値と同じ型を `response_model=` にも書くと、Ruff の `FAST001` が「重複」と指摘します)。
- `/todos/stats` は `/todos/{todo_id}` より **前に** 定義します。ルートは上から順にマッチするからです。後ろに書くと `"stats"` を int に変換しようとして 422 (`int_parsing`) になります (確認済み)。

### 5-5. main.py: アプリファクトリ

```python
def create_app(settings: Settings | None = None) -> FastAPI:
    ...
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
        app.state.todo_repo = InMemoryTodoRepository()   # startup
        yield
        # shutdown

    app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)
    ...
    return app

app = create_app()
```

`create_app()` という関数にしておくと、テストごとに新しいアプリ (= 空のデータ) を作れます。

### 動かす

```bash
uv run fastapi dev
```

```bash
curl -i -X POST localhost:8000/todos -H 'content-type: application/json' -d '{"title":"Buy milk"}'
curl localhost:8000/todos
curl localhost:8000/todos/stats
curl -i localhost:8000/todos/abc          # 422: path param is not int
curl -i -X POST localhost:8000/todos -H 'content-type: application/json' -d '{"titel":"typo"}'   # 422
```

Swagger UI (`/docs`) の「Try it out」からでも同じことができます。

curl の代わりに [xh](https://github.com/ducaale/xh) を使うと、JSON のクォートを書かずに済みます
(Windows: `winget add ducaale.xh` / Arch 系: `pacman -S xh`)。

```bash
xh :8000/todos title=Buy\ milk          # POST JSON {"title": "Buy milk"}
xh :8000/todos done==true limit==5       # "==" is a query parameter
xh PATCH :8000/todos/1 done:=true        # ":=" is a raw JSON value (bool, number)
xh :8000/health X-Request-ID:abc123      # ":" is a header
```

---

## Step 6: 設定とログ

### 6-1. pydantic-settings で設定を読む

`config.py`:

```python
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="TODO_", env_file=".env", extra="ignore", validate_by_name=True,
    )

    app_name: str = "Todo API"
    env: Env = Field(default="production",
                     validation_alias=AliasChoices("FASTAPI_ENV", "TODO_ENV"))
    debug: bool = False
    log_level: LogLevel = "INFO"
```

- `TODO_DEBUG=true` のような環境変数、または `.env` から読みます。
- `env` は `fastapi dev` がセットする `FASTAPI_ENV` を読みます。デフォルトは安全側の `production` です。
- 型付きなので、`TODO_LOG_LEVEL=VERBOSE` のような間違った値は起動時にエラーになります。

```bash
cp .env.example .env
```

### 6-2. Request ID 付きのログ

`middleware.py` で、リクエストごとに ID を決めて `ContextVar` に入れます。
`log_config.py` の `logging.Filter` がその ID を全ログ行に付けます。

```
2026-11-13 00:03:27,313 DEBUG   [d2419c0607e2] todo_api.routers.todos: created todo: id=1 title='Buy milk' ...
2026-11-13 00:03:27,314 INFO    [d2419c0607e2] todo_api.middleware: POST /todos -> 201 (8.7 ms)
```

起動・停止のログはリクエストの外なので `[-]` になります。

- レスポンスヘッダ `X-Request-ID` にも同じ ID を返します。クライアントが送ってきた ID はそのまま使います。
- 障害調査では「この ID のログを全部見る」で 1 リクエストを追えます。
- sync のエンドポイントはスレッドプールで動きますが、`ContextVar` は引き継がれます (ログで確認済み)。

---

## Step 7: デバッグ

4 つの方法を順に試します。

### 7-1. VS Code で F5 (いちばん普段使い)

`.vscode/launch.json` (抜粋):

```jsonc
{
  "name": "FastAPI: debug (no reload)",
  "type": "debugpy",
  "request": "launch",
  "module": "fastapi",
  "args": ["dev", "--no-reload"],
  "envFile": "${workspaceFolder}/.env",
  "justMyCode": true
}
```

1. `routers/todos.py` の `create_todo` の中の行をクリックしてブレークポイントを置く
2. 実行とデバッグ (Ctrl+Shift+D) で「FastAPI: debug (no reload)」を選んで F5
3. Swagger UI か curl で `POST /todos` を送る
4. 止まったら「変数」パネルで `payload` を見る。デバッグコンソールで `payload.model_dump()` も実行できる

`--no-reload` にしている理由: reload を有効にすると、サーバ本体は別の子プロセスで動きます
(起動ログの `Started reloader process` と `Started server process` が別 PID)。
保存のたびにその子プロセスが入れ替わるので、デバッグ中は reload を切るほうが安定します。

`justMyCode: false` の「FastAPI: debug (library code too)」を使うと、FastAPI / Starlette / Pydantic の中までステップ実行できます。
「なぜ 422 になるのか」を追うときに便利です。

### 7-2. attach (ターミナルで起動して後から付ける)

```bash
uv run python -m debugpy --listen 5678 -m fastapi dev --no-reload
# Add --wait-for-client to stop until the debugger attaches.
```

- VS Code: 「Attach to debugpy (:5678)」を選んで F5
- Neovim (nvim-dap + nvim-dap-python):

  ```lua
  require("dap-python").setup("uv")
  -- Then :lua require("dap").continue() and pick "attach".
  -- Host 127.0.0.1, Port 5678.
  ```

同じ方法で Docker コンテナの中のプロセスにも付けられます (5678 を公開する)。

この手順は、DAP クライアントで attach -> ブレークポイント設定 -> リクエスト送信 -> 停止、まで確認済みです。

### 7-3. breakpoint() と pdb (エディタなし)

コードに 1 行足すだけです。

```python
breakpoint()
```

`uv run fastapi dev` のターミナルで `(Pdb)` プロンプトが出ます。

| コマンド | 意味 |
| --- | --- |
| `p payload` | 値を表示 |
| `pp payload.model_dump()` | 整形して表示 |
| `n` / `s` | 次の行 / 関数の中へ |
| `l` | 周りのコードを表示 |
| `c` | 続行 |

- `fastapi dev` は reload 有効のままでも pdb が使えます (Uvicorn が子プロセスに標準入力を渡すため。確認済み)。
- 環境変数 `PYTHONBREAKPOINT=0` で、全部の `breakpoint()` を無効にできます。
- 消し忘れは Ruff の `T100` と pre-commit が止めてくれます。

### 7-4. FastAPI の debug モードとログ

`.env` で `TODO_DEBUG=true` にすると、未処理の例外でトレースバックがレスポンスに出ます
(curl なら plain text、ブラウザなら HTML)。
`false` だと `Internal Server Error` だけです。本番では必ず `false` にします。

ログは `TODO_LOG_LEVEL=DEBUG` で詳細になります。

### 演習: バグを入れて追いかける

1. `routers/todos.py` の `todo_stats` で、ゼロ除算のガードを消します。

   ```python
   ratio = done / total   # remove: "if total else 0.0"
   ```

2. データが空の状態で `GET /todos/stats` を呼ぶと 500 になります。
3. `TODO_DEBUG=true` でトレースバックを見る、F5 でブレークポイントを置いて `total` の値を見る、の両方で原因を確認します。
4. `uv run pytest` を実行すると `test_stats_when_empty` が落ちることも確認します。
5. 元に戻します。

---

## Step 8: テスト (pytest + TestClient)

### fixture

`tests/conftest.py`:

```python
@pytest.fixture
def settings() -> Settings:
    return Settings(_env_file=None, env="test", debug=False, log_level="DEBUG")

@pytest.fixture
def app(settings: Settings) -> FastAPI:
    return create_app(settings)          # fresh app = empty data

@pytest.fixture
def client(app: FastAPI) -> Iterator[TestClient]:
    with TestClient(app) as c:           # "with" runs the lifespan
        yield c
```

- `_env_file=None` で、手元の `.env` がテストに影響しないようにします。
- `with TestClient(app)` にしないと lifespan が動かず、`app.state.todo_repo` がありません。

### パラメタライズで 422 をまとめて確認

```python
@pytest.mark.parametrize(
    "body",
    [
        {"title": ""},                  # too short
        {"title": "x" * 101},           # too long
        {"done": True},                 # title is missing
        {"title": "ok", "unknown": 1},  # extra field
    ],
)
def test_create_validation_error(client: TestClient, body: dict[str, object]) -> None:
    assert client.post("/todos", json=body).status_code == 422
```

### 依存の差し替え (dependency_overrides)

```python
def test_dependency_override(app: FastAPI, client: TestClient) -> None:
    fake: TodoRepository = FakeRepo()     # mypy checks it matches the Protocol
    app.dependency_overrides[get_repository] = lambda: fake
    ...
```

DB や外部 API を使う依存も、この方法でテスト用に差し替えられます。

### 実行

```bash
uv run pytest
```

```
20 passed
TOTAL   175   0   10   0   100%
Required test coverage of 90.0% reached. Total coverage: 100.00%
```

(Step 13 まで終えると 40 passed、カバレッジ 98% 台になります。)

- `pyproject.toml` の `[tool.coverage.report] fail_under = 90` で、カバレッジが 90% を切ると失敗します。
- 設定は `[tool.pytest]` (pytest 9.0 以降の書き方) に書いています。
- テストのデバッグ: VS Code のテストビューから「Debug Test」、または launch.json の「pytest: current file」。
  カバレッジとデバッガがぶつからないように `--no-cov` を付けています。

---

## Step 9: pre-commit

```bash
git init        # uv init で作成済みなら不要
uv run pre-commit install
uv run pre-commit run --all-files
```

```
trim trailing whitespace.................................................Passed
fix end of files.........................................................Passed
mixed line ending........................................................Passed
check yaml...............................................................Passed
check toml...............................................................Passed
check for merge conflicts................................................Passed
check for added large files..............................................Passed
uv-lock..................................................................Passed
ruff check...............................................................Passed
ruff format..............................................................Passed
mypy.....................................................................Passed
```

設計のポイント (`.pre-commit-config.yaml`):

- Ruff と mypy は `repo: local` + `uv run --frozen ...` にしています。
  pre-commit 用に別バージョンを持たず、`uv.lock` と同じバージョンで動かすためです。
- `language: unsupported` は pre-commit 4.4 で入った名前です (以前の `language: system` と同じ意味)。
- `uv-lock` フックは、`pyproject.toml` を変えたのに `uv.lock` を更新し忘れた状態を防ぎます。
- `mixed-line-ending --fix=lf` と `.gitattributes` で、Windows でも LF にそろえます。

Step 3 / 4 の「わざと間違える」をもう一度やって `git commit` すると、コミットが止まることを確認してください。

---

## Step 10: CI (GitHub Actions)

`.github/workflows/ci.yml`:

```yaml
steps:
  - uses: actions/checkout@v7
  - uses: astral-sh/setup-uv@68559e99cc807c1eb7e9238fd43a15bba460eec2 # v10.3.3
    with:
      enable-cache: true
  - run: uv sync --locked
  - run: uv run ruff check --output-format=github
  - run: uv run ruff format --check
  - run: uv run mypy
  - run: uv run pytest
```

- `uv sync --locked`: `uv.lock` が古いと失敗します。
- `--output-format=github`: Ruff の指摘が PR の差分の上に注釈として出ます。
- setup-uv は README でコミット SHA での固定を推奨しているので、それに合わせています。

---

## Step 11: リアルタイム通知の準備 (EventBroker)

ここから、Todo の変更をクライアントにリアルタイムで届けます。
同じイベントを WebSocket と SSE の両方で配信して、違いを比べます。

### WebSocket と SSE の違い

| | WebSocket | SSE (Server-Sent Events) |
| --- | --- | --- |
| 方向 | 双方向 | サーバ -> クライアントのみ |
| 通信 | HTTP から Upgrade した別プロトコル (`ws://`) | 普通の HTTP レスポンス (`text/event-stream`) |
| ブラウザの API | `WebSocket` | `EventSource` |
| 再接続 | 自分で書く | ブラウザが自動で行う。`Last-Event-ID` で続きから受け取れる |
| データ | テキスト / バイナリ | テキストのみ |
| 向いている用途 | チャット、共同編集、ゲーム | 通知、進捗表示、ログ、LLM の逐次出力 |
| FastAPI | `@router.websocket(...)` | `response_class=EventSourceResponse` (0.135.0 以降) |

「サーバから送るだけ」なら SSE のほうが簡単です。普通の HTTP なので、プロキシや認証もそのまま使えます。
クライアントからも頻繁に送るなら WebSocket を使います。

### 全体の形

```
 POST / PATCH / DELETE /todos ──┐
 WebSocket {"type":"create"} ───┤  broker.publish(...)
                                v
                ┌──────────────────────────────┐
                │ EventBroker                  │
                │  - 連番 id を振る             │
                │  - 直近 100 件を history に保持 │
                └──────────────────────────────┘
                   |  (購読者ごとに Queue)  |
                   v                        v
          GET /todos/events            /ws/todos
               (SSE)                  (WebSocket)
```

### events.py のポイント

- **スレッドセーフな publish**: CRUD のエンドポイントは同期 (`def`) なので、スレッドプールで動きます。
  購読者の `asyncio.Queue` はイベントループ側のものなので、`loop.call_soon_threadsafe` で渡します。
- **history で再送**: SSE の `Last-Event-ID` に対応するため、直近 100 件を `deque(maxlen=100)` で持ちます。
- **遅いクライアント対策**: Queue が一杯なら一番古いイベントを捨てて、警告ログを出します。
- **close()**: 購読者全員に `None` (終了の合図) を送り、`async for` を終わらせます。
- **1 プロセス限定**: `fastapi run --workers 2` のように複数プロセスにすると、イベントはプロセスをまたぎません。
  本番で複数台にするなら Redis Pub/Sub などを使います (発展課題)。

各エンドポイントでは、変更のあとに publish するだけです。

```python
@router.post("", status_code=status.HTTP_201_CREATED)
def create_todo(payload: TodoCreate, repo: RepoDep, broker: BrokerDep) -> Todo:
    todo = repo.add(payload)
    broker.publish("created", todo.id, todo)
    return todo
```

### deps.py: Request ではなく HTTPConnection を使う

```python
def get_broker(conn: HTTPConnection) -> EventBroker:
    return cast(EventBroker, conn.app.state.event_broker)
```

`HTTPConnection` は `Request` と `WebSocket` の共通の親クラスです。
`Request` のままだと、WebSocket のエンドポイントでこの依存が使えません。

### 単体テスト (async)

`tests/test_events.py` は HTTP を使わずに EventBroker だけをテストします。
async のテストには、FastAPI と一緒に入る anyio の pytest プラグインを使います (追加インストール不要)。

```python
pytestmark = pytest.mark.anyio

@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"

async def test_replay_after_last_event_id() -> None:
    broker = EventBroker()
    for i in range(1, 4):
        broker.publish("created", i)

    async with broker.subscribe(last_event_id=1) as sub:
        events = [await anext(sub) for _ in range(2)]

    assert [e.id for e in events] == [2, 3]
```

---

## Step 12: WebSocket

### エンドポイント (routers/ws.py)

```python
@router.websocket("/ws/todos")
async def todo_ws(websocket: WebSocket, repo: RepoDep, broker: BrokerDep) -> None:
    await websocket.accept()
    async with broker.subscribe() as sub, anyio.create_task_group() as tg:
        tg.start_soon(_forward_events, websocket, sub)   # broker -> client
        await _receive_loop(websocket, repo, broker)     # client -> server
        tg.cancel_scope.cancel()                         # client left
```

WebSocket は「送る」と「受ける」が同時に起きます。そこで 2 つのタスクに分けます。

- `_forward_events`: broker から来たイベントをクライアントへ送る
- `_receive_loop`: クライアントからのメッセージを読む。切断 (`WebSocketDisconnect`) で終わる

受信したメッセージは、Pydantic の判別共用体 (discriminated union) で検証します。

```python
class PingMessage(BaseModel):
    type: Literal["ping"]

class CreateMessage(BaseModel):
    type: Literal["create"]
    title: str = Field(min_length=1, max_length=100)

ClientMessage = Annotated[PingMessage | CreateMessage, Field(discriminator="type")]
client_message_adapter = TypeAdapter(ClientMessage)

message = client_message_adapter.validate_json(text)   # JSON parse + validation
```

- WebSocket では FastAPI の自動検証 (422) は使えません。メッセージの検証は自分で書きます。
- 不正なメッセージには `{"type": "error", ...}` を返し、**接続は切りません**。
- `match message: case PingMessage(): ...` で分岐します。

### 動かす: websockets の CLI

`fastapi[standard]` に入っている `websockets` に、対話型のクライアントがあります。

```bash
uv run python -m websockets ws://127.0.0.1:8000/ws/todos
```

実際の出力 (見やすく整えています):

```
Connected to ws://127.0.0.1:8000/ws/todos.
> {"type":"ping"}
< {"type":"pong"}
> {"type":"create","title":"via ws"}
< {"type":"event","data":{"id":3,"type":"created","todo_id":2,"todo":{"id":2,"title":"via ws","done":false,...}}}
> {"type":"create","title":""}
< {"type":"error","errors":[{"type":"string_too_short","loc":["create","title"],"msg":"String should have at least 1 character",...}]}
```

別のターミナルから HTTP で作成しても、WebSocket 側にイベントが届きます。

```bash
xh :8000/todos title=from-http
# or
curl -X POST localhost:8000/todos -H 'content-type: application/json' -d '{"title":"from-http"}'
```

### 動かす: ブラウザのデモページ

http://127.0.0.1:8000/demo を開きます。左が SSE、右が WebSocket です。
「Create via HTTP POST」「Create via WS」のどちらで作っても、両方の画面にイベントが出ることを確認します。
ブラウザの開発者ツールの Network タブで、WebSocket の接続を選ぶと、送受信したメッセージが一覧で見られます。

### テスト

```python
def test_ping_pong(client: TestClient) -> None:
    with client.websocket_connect("/ws/todos") as ws:
        ws.send_json({"type": "ping"})
        assert ws.receive_json() == {"type": "pong"}
```

- `websocket_connect` は `accept()` が終わった時点で戻ります。購読 (`broker.subscribe()`) はその後です。
  そのため「HTTP で作成 -> WS に届く」のテストでは、購読者数が 1 になるまで待ってから POST します (`wait_until_subscribed`)。
- サーバ停止時に close code 1001 で閉じることもテストしています。

### デバッグのコツ

- HTTP middleware (`@app.middleware("http")`) は WebSocket には効きません。
  そのため、エンドポイントの中で request_id を自分でセットしています。ログでは `[ws-xxxxxxxx]` と出ます。
- F5 のデバッグ (Step 7) はそのまま使えます。`_receive_loop` の `match` の行に止めて、`message` を見てみてください。
- close code の意味: `1000` 正常終了 / `1001` サーバが去る (このアプリの停止処理) / `1012` サーバ再起動 (Uvicorn が停止時に送る)。

---

## Step 13: SSE (Server-Sent Events)

### エンドポイント (routers/todos.py)

```python
@router.get("/events", response_class=EventSourceResponse)
async def todo_events(
    broker: BrokerDep,
    last_event_id: Annotated[int | None, Header()] = None,
) -> AsyncIterable[ServerSentEvent]:
    async with broker.subscribe(last_event_id) as sub:
        yield ServerSentEvent(comment="connected", retry=3000)
        async for event in sub:
            yield ServerSentEvent(data=event, event=event.type, id=str(event.id))
```

- `response_class=EventSourceResponse` にして `yield` するだけで SSE になります。
- `data=` に Pydantic モデルを渡すと JSON になります。
- `id=` を付けると、ブラウザが再接続するときに `Last-Event-ID` ヘッダで送り返してくれます。
- **購読してから** `connected` を送ります。逆にすると、その間のイベントを取りこぼします。
- `/events` も `/{todo_id}` より前に定義します (Step 5 の `/stats` と同じ理由)。
- FastAPI が自動でやってくれること: 15 秒イベントがないと `: ping` を送る (プロキシに切られないため)、`Cache-Control: no-cache`、`X-Accel-Buffering: no` (Nginx でバッファさせない)。

### 動かす: curl / xh

```bash
curl -N localhost:8000/todos/events
# or
xh -S :8000/todos/events
```

`-N` (curl) / `-S` (xh) は「バッファせずに届いた分から表示する」オプションです。
別のターミナルで POST / PATCH すると、次のように流れてきます (実際の出力)。

```
: connected
retry: 3000

event: created
data: {"id":1,"type":"created","todo_id":1,"todo":{"id":1,"title":"via curl","done":false,...}}
id: 1

event: updated
data: {"id":2,"type":"updated","todo_id":1,"todo":{"id":1,"title":"via curl","done":true,...}}
id: 2

: ping
```

最後の `: ping` は、何も起きないまま 15 秒たったときの keep-alive です。

### 続きから受け取る (Last-Event-ID)

```bash
curl -N -H 'Last-Event-ID: 1' localhost:8000/todos/events
```

id が 1 より大きいイベント (上の例なら id 2 以降) が、つないだ直後に再送されます。
ブラウザの `EventSource` は、切断されると `retry` の時間 (3 秒) 待って自動で再接続し、このヘッダを自動で付けます。
デモページで SSE を接続したまま、サーバを再起動して確認してください。
(このアプリの history はメモリ上なので、再起動をまたぐと消えます。そこは DB 化の課題です。)

### テスト

```python
with client.stream("GET", "/todos/events") as res:
    lines = res.iter_lines()
    read_event(lines)                                # ": connected"
    client.post("/todos", json={"title": "a"})
    created = read_event(lines)                      # event: created
# Leaving the block closes the connection.
```

- `TestClient.stream()` で、終わらないストリームも途中まで読めます。ブロックを抜けると接続が閉じ、購読も解除されます (テストで確認)。
- `read_event` は「空行までの行を 1 イベントとして読む」小さなパーサです (`tests/test_sse.py`)。

### ログの注意

```
INFO [50adbbacaf35] todo_api.events: subscribed (subscribers=1)
INFO [50adbbacaf35] todo_api.middleware: GET /todos/events -> 200 (7.3 ms)
...
INFO [50adbbacaf35] todo_api.events: unsubscribed (subscribers=0)
```

middleware のアクセスログは「レスポンスヘッダを返した時点」で出ます。なので SSE でも 7 ms のように表示されます。
接続していた時間は、同じ request_id の `subscribed` / `unsubscribed` のログで追います。

### 落とし穴: SSE をつないだままだと、停止も reload も終わらない

`shutdown.py` を入れる前は、次のようになりました。

```
WARNING:  WatchFiles detected changes in '...health.py'. Reloading...
INFO:     Shutting down
INFO:     Waiting for connections to close. (CTRL+C to force quit)
```

コードを保存しても再起動しません。理由は Uvicorn の停止の順番です。

1. 停止シグナル (Ctrl+C の SIGINT、reload の SIGTERM) を受ける
2. 新しい接続の受付を止め、**開いている接続が全部閉じるまで待つ**
3. そのあとで lifespan の shutdown を呼ぶ

SSE は終わらないレスポンスなので、2 で止まります。lifespan の shutdown で `broker.close()` しても、そこまで進みません。
WebSocket は Uvicorn が 1012 で閉じてくれるので、この問題は起きません。

対策として `shutdown.py` で、シグナルを受けた**瞬間に** `broker.close()` を呼ぶようにしています。

```python
def on_shutdown_signal(callback: Callable[[], None]) -> Callable[[], None]:
    loop = asyncio.get_running_loop()
    ...
    def handler(signum: int, frame: FrameType | None) -> None:
        loop.call_soon_threadsafe(callback)   # do very little in a signal handler
        original = originals[signum]
        if callable(original):
            original(signum, frame)           # then Uvicorn's own handler
```

- Uvicorn のハンドラを置き換えずに、前に挟んでから元のハンドラも呼びます。
- シグナルハンドラの中では最小限のことだけをします。`call_soon_threadsafe` で、処理をイベントループに渡すだけです。
- 対象は Uvicorn と同じ SIGINT / SIGTERM (Windows では SIGBREAK も) です。
- TestClient はアプリを別スレッドで動かします。シグナルはメインスレッドでしか扱えないので、その場合は何もしません。

対策後 (Linux で確認):

```
INFO  todo_api.shutdown: got signal SIGTERM: closing streams
INFO  todo_api.events: unsubscribed (subscribers=0)
INFO:     Shutting down
INFO:     Application shutdown complete.
INFO:     Started server process [1916]
```

SSE と WebSocket をつないだままでも、Ctrl+C で 1 秒以内に止まります。reload もすぐ再起動します。

別の方法として、`uvicorn` を直接使うなら `--timeout-graceful-shutdown 5` で「最大 5 秒だけ待つ」にもできます。
ただし `fastapi dev` にはこのオプションがありません。

### 演習

1. `main.py` の `on_shutdown_signal(...)` の行をコメントアウトして、SSE をつないだまま保存してみる。reload が止まることを確認したら戻す。
2. WebSocket に認証を付ける。ブラウザの `WebSocket` はカスタムヘッダを付けられないので、クエリパラメータのトークンか Cookie で確認する。失敗したら `websocket.close(code=1008)`。
3. LLM のような逐次出力を作る。`POST /chat/stream` で受け取った文字列を 1 単語ずつ `ServerSentEvent(data=word, event="token")` で返し、最後に `ServerSentEvent(raw_data="[DONE]", event="done")` を送る。
4. `uv run fastapi run --workers 2` で起動し、イベントが届かないクライアントが出ることを確認する。EventBroker を Redis Pub/Sub に置き換える設計を考える。

---

## コマンド早見表

| やりたいこと | コマンド |
| --- | --- |
| 依存を入れる | `uv sync` |
| 依存を追加 | `uv add <pkg>` / `uv add --dev <pkg>` |
| 開発サーバ | `uv run fastapi dev` |
| デバッガ待ち受けで起動 | `uv run python -m debugpy --listen 5678 -m fastapi dev --no-reload` |
| lint | `uv run ruff check` (`--fix` で自動修正) |
| format | `uv run ruff format` |
| 型チェック | `uv run mypy` |
| (任意) ty | `uvx ty check` |
| テスト | `uv run pytest` |
| テスト (カバレッジなし・最初の失敗で止める) | `uv run pytest --no-cov -x` |
| 全チェック | `uv run pre-commit run --all-files` |
| 依存の更新 | `uv lock --upgrade` |
| API を叩く (xh) | `xh :8000/todos` / `xh :8000/todos title=foo done:=false` |
| WebSocket に接続 | `uv run python -m websockets ws://127.0.0.1:8000/ws/todos` |
| SSE を見る | `curl -N localhost:8000/todos/events` / `xh -S :8000/todos/events` |
| デモページ | http://127.0.0.1:8000/demo |

---

## 発展課題

1. **DB を使う**: SQLAlchemy 2.x か SQLModel + SQLite で `TodoRepository` を実装します。ルーターは変えずに差し替えられることを確認します。
2. **async にする**: DB ドライバを async にして、エンドポイントを `async def` にします。Ruff の `ASYNC` ルールが、async の中のブロッキング呼び出しを指摘します。
3. **エラーレスポンスの統一**: `@app.exception_handler` で、独自例外を共通の JSON 形式で返します。
4. **認証**: `OAuth2PasswordBearer` + JWT の依存を作り、`Depends` で保護します。テストは `dependency_overrides` でユーザーを差し替えます。
5. **Docker 化**: `uv sync --locked --no-dev` でイメージを作り、`fastapi run` で起動します。debugpy の attach (Step 7-2) をコンテナに対して試します。

---

## 参考

- FastAPI CLI: https://fastapi.tiangolo.com/fastapi-cli/
- FastAPI Debugging: https://fastapi.tiangolo.com/tutorial/debugging/
- FastAPI Testing: https://fastapi.tiangolo.com/tutorial/testing/
- FastAPI Editor Support (VS Code 拡張): https://fastapi.tiangolo.com/editor-support/
- uv: https://docs.astral.sh/uv/
- Ruff rules: https://docs.astral.sh/ruff/rules/
- mypy: https://mypy.readthedocs.io/
- Pydantic mypy plugin: https://docs.pydantic.dev/latest/integrations/mypy/
- pytest configuration: https://docs.pytest.org/en/stable/reference/customize.html
- pre-commit: https://pre-commit.com/
- nvim-dap-python: https://github.com/mfussenegger/nvim-dap-python
- FastAPI WebSockets: https://fastapi.tiangolo.com/advanced/websockets/
- FastAPI Server-Sent Events: https://fastapi.tiangolo.com/tutorial/server-sent-events/
- HTML Standard (Server-sent events): https://html.spec.whatwg.org/multipage/server-sent-events.html
- xh: https://github.com/ducaale/xh
