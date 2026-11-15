# next

Next.js のスタータープロジェクトです。このディレクトリをコピーして、新しいプロジェクトを始めます。`create-next-app` の既定の構成（App Router、TypeScript、ESLint、Tailwind CSS、Turbopack）に、フォーマッタ、テスト、エディタの設定、小さな Todo ページを足しています。Todo ページは [fastapi](../fastapi) の API を使います。

| 項目           | 内容                                         | バージョン           |
| -------------- | -------------------------------------------- | -------------------- |
| フレームワーク | Next.js（App Router、Turbopack）             | 16.4.6               |
| UI             | React、React DOM                             | 19.3.0               |
| 言語           | TypeScript                                   | 5.9.3                |
| リンタ         | ESLint、eslint-config-next                   | 9.39.5、16.4.6       |
| CSS            | Tailwind CSS、@tailwindcss/turbopack         | 4.3.3                |
| フォーマッタ   | oxfmt                                        | 0.78.0               |
| テスト         | Vitest、jsdom、@vitejs/plugin-react          | 5.1.0、31.0.1、6.3.0 |
| テスト         | @testing-library/react、@testing-library/dom | 16.3.3、10.4.2       |
| パッケージ管理 | pnpm                                         | 12.20.0              |
| 実行環境       | Node.js                                      | 26.13.1 で確認       |

Node.js は 22.22.2 以上、24.15.0 以上、26 以上のどれかが必要です。これは jsdom の条件です。

ほかのパッケージのバージョンは `pnpm-lock.yaml` にあります。

## セットアップ方法

| 方法                                  | コマンド                                                                      |
| ------------------------------------- | ----------------------------------------------------------------------------- |
| Node.js / pnpm                        | Node.js 26.13.1 と pnpm 12.20.0 を入れて `pnpm install`                       |
| mise                                  | `mise install && pnpm install --frozen-lockfile`                              |
| Nix（リポジトリ内）                   | `nix develop ..#next`                                                         |
| Docker (`node:26.13.1-bookworm-slim`) | `docker build -t next-starter . && docker run --rm -p 3000:3000 next-starter` |

## 使い方

```sh
# 1. このディレクトリをコピーする
cp -r next /path/to/my-app
cd /path/to/my-app

# 2. パッケージを入れる
pnpm install

# 3. 環境変数のファイルを作る
cp .env.example .env.local

# 4. 開発サーバーを起動する
pnpm dev
```

ブラウザで <http://localhost:3000> を開きます。

Todo ページは API を使います。別のターミナルで [fastapi](../fastapi) を起動します。next の隣に fastapi があるときは、次のコマンドです。

```sh
cd ../fastapi && uv run fastapi dev
```

別の場所にコピーしたときは、fastapi のディレクトリに移動して `uv run fastapi dev` を実行します。

API が動いていなくても、ページは表示されます。そのときは、API の起動方法がページに出ます。

コピーしたあとに、次の 3 つを自分のプロジェクトに合わせて変えます。

- `package.json` の `name`
- `app/layout.tsx` の `metadata`（ページのタイトルと説明）
- `components/api-unavailable.tsx` の中の起動コマンド（API の場所が変わる場合）

`node_modules` と `.next` がすでにある場合は、コピーに含めません。コピー先で `pnpm install` をやり直します。

## コマンド

| コマンド         | 内容                                                         |
| ---------------- | ------------------------------------------------------------ |
| `pnpm dev`       | 開発サーバーを起動する。ファイルを保存すると画面に反映される |
| `pnpm build`     | 本番用にビルドする                                           |
| `pnpm start`     | ビルドした結果を起動する。先に `pnpm build` が必要           |
| `pnpm lint`      | ESLint でコードを調べる                                      |
| `pnpm fmt`       | oxfmt でファイルを整形する                                   |
| `pnpm fmt:check` | 整形が必要なファイルがあれば失敗する。ファイルは変えない     |
| `pnpm typecheck` | ルートの型を生成してから、`tsc --noEmit` で型を調べる        |
| `pnpm test`      | Vitest でテストを 1 回実行する                               |
| `pnpm check`     | `lint`、`fmt:check`、`typecheck`、`test` を順に実行する      |

コミットの前に `pnpm check` を実行します。

テストをファイルの保存のたびに実行したいときは、`pnpm exec vitest` を使います。

## ディレクトリ構成

```text
next/
├── app/
│   ├── layout.tsx           # 全ページ共通のレイアウト
│   ├── page.tsx             # トップページ。サーバーで Todo の一覧を取得する
│   ├── globals.css          # Tailwind CSS の読み込みと、色の変数
│   └── favicon.ico
├── components/
│   ├── todo-app.tsx         # Client Component。追加、完了の切り替え、削除
│   └── api-unavailable.tsx  # API に接続できないときの案内
├── lib/
│   └── api.ts               # API の型と関数（Todo、listTodos、createTodo など）
├── __tests__/
│   ├── api.test.ts          # lib/api.ts のテスト
│   └── todo-app.test.tsx    # components/todo-app.tsx のテスト
├── .vscode/
│   ├── settings.json        # 保存時の整形と ESLint の修正
│   ├── extensions.json      # おすすめの拡張機能
│   └── launch.json          # デバッグの構成
├── .env.example             # 環境変数の見本。.env.local にコピーして使う
├── next.config.ts           # Next.js の設定。/api/* の転送（rewrites）はここ
├── eslint.config.mjs        # ESLint の設定
├── .oxfmtrc.json            # oxfmt の設定
├── vitest.config.mts        # Vitest の設定
├── vitest.setup.ts          # テストのたびに、描画した DOM を片付ける
├── tsconfig.json            # TypeScript の設定。@/ はこのディレクトリを指す
├── pnpm-workspace.yaml      # pnpm の設定
├── .editorconfig            # 文字コード、改行、インデントの決まり
├── .gitattributes           # Git での改行の扱い（LF）
└── AGENTS.md                # create-next-app が生成したファイル
```

`node_modules/`、`.next/`、`next-env.d.ts`、`tsconfig.tsbuildinfo` は自動で作られます。Git には入れません。

`.env.local` も Git には入れません。`.gitignore` は、`.env.example` 以外の `.env*` を除外します。

## API との接続

ブラウザは FastAPI を直接呼びません。呼ぶのは Next.js のサーバーだけです。Next.js のサーバーが FastAPI を呼びます。

```text
Browser                Next.js server (:3000)               FastAPI (:8000)
   |                            |                                 |
   |-- GET / ------------------>|                                 |
   |                            |-- GET /todos ------------------>|  (1)
   |                            |<-- Todo[] ----------------------|
   |<-- HTML with the todos ----|                                 |
   |                            |                                 |
   |-- POST /api/todos -------->|                                 |
   |                            |-- POST /todos ----------------->|  (2)
   |                            |<-- 201 Todo --------------------|
   |<-- 201 Todo ---------------|                                 |
```

(1) 最初の一覧は、サーバーで作ります。`app/page.tsx` の `TodoList` は Server Component です。`lib/api.ts` の `listTodos()` で FastAPI から一覧を取得し、HTML にして返します。

(2) 追加、完了の切り替え、削除は、ブラウザから行います。`components/todo-app.tsx` は `/api/todos` のような URL を呼びます。`next.config.ts` の `rewrites` が、`/api/:path*` を `<API_URL>/:path*` に転送します。たとえば `/api/todos/1` は `<API_URL>/todos/1` になります。

この形には、次の利点があります。

- ブラウザから見ると、通信の相手は 1 つだけです。FastAPI に CORS の設定は要りません。
- FastAPI の場所はサーバーだけが知っています。ブラウザには渡りません。

呼び先を決めるのは、`lib/api.ts` の `baseUrl()` です。サーバーでは `API_URL` を返し、ブラウザでは `/api` を返します。

`API_URL` は環境変数です。`.env.local` に書きます。書かないときは `http://127.0.0.1:8000` になります。

```sh
# .env.local
API_URL=http://127.0.0.1:8000
```

最初の一覧はキャッシュしません。`app/page.tsx` の `<Suspense>` の内側は、リクエストのたびにサーバーで実行されます。`<Suspense>` の外側（見出しなど）は、ビルドのときに HTML になります。

`API_URL` には注意が 2 つあります。

- `API_URL` を変えたら、`pnpm dev` を再起動します。`rewrites` は、起動したときの値を使い続けます。
- `pnpm build` は、`rewrites` の転送先をビルドの結果に書き込みます。`pnpm start` のときに `API_URL` を変えても、`/api/*` の転送先は変わりません。本番用の `API_URL` は、ビルドのときにも設定します。

## ハンズオン

エディタを使って、このプロジェクトを順に見ていきます。エディタの操作は「定義へ移動」のような名前で書きます。キーの割り当ては [../README.md](../README.md) の表を見てください。

ここでは、next の隣に fastapi があるものとします。

### 1. 動かす

1. ターミナルを 2 つ開きます。1 つ目で API を起動します。

   ```sh
   cd ../fastapi && uv run fastapi dev
   ```

2. 2 つ目で `pnpm dev` を実行し、<http://localhost:3000> を開きます。
3. Todo を追加します。チェックを付けます。削除します。
4. Todo を 1 つ追加して、ページを再読み込みします。Todo は残っています。サーバーが作った HTML に入っているからです。
5. API を止めて、ページを再読み込みします。「The API is not reachable.」と出ます。
6. API をもう一度起動して、再読み込みします。一覧は空です。API はデータをメモリに持つので、止めると消えます。

### 2. リクエストをたどる

Todo を追加したとき、リクエストがどこを通るかを追います。

1. `components/todo-app.tsx` を開きます。`handleAdd` の中の `createTodo` で「定義へ移動」をします。`lib/api.ts` に移ります。
2. `createTodo` から `request`、`baseUrl` へと、同じように移動します。ブラウザでは `baseUrl()` が `/api` を返します。URL は `/api/todos` です。
3. `next.config.ts` を開き、`rewrites` を読みます。`/api/todos` は `<API_URL>/todos` に転送されます。
4. `../fastapi/src/todo_api/routers/todos.py` の `create_todo` が、このリクエストを受け取ります。
5. ブラウザの開発者ツールでネットワークのタブを開き、Todo を追加します。`POST` の宛先は `localhost:3000/api/todos` です。API のターミナルには `POST /todos -> 201` と出ます。
6. 同じリクエストを curl で送ります。そのあとページを再読み込みして、Todo が増えたことを確かめます。

   ```sh
   curl -X POST http://localhost:3000/api/todos \
     -H 'Content-Type: application/json' \
     -d '{"title": "curl から追加"}'
   ```

7. `lib/api.ts` の `listTodos` で「参照を検索」をします。`app/page.tsx` から呼ばれています。こちらはサーバーで動くので、`rewrites` を通りません。

### 3. 絞り込みを足す

API は、`GET /todos?done=false` で未完了の Todo だけを返します。`listTodos` からこれを使えるようにします。テストを先に書きます。

1. `__tests__/api.test.ts` の `describe("in the browser", ...)` の中に、テストを足します。

   ```ts
   test("listTodos can ask for todos that are not done", async () => {
     fetchMock.mockResolvedValue(Response.json([]));

     await listTodos({ done: false });

     expect(fetchMock).toHaveBeenCalledWith(
       "/api/todos?done=false",
       expect.anything(),
     );
   });
   ```

2. `pnpm test` を実行します。このテストは失敗します。期待した URL と実際の URL が出ます。
3. `lib/api.ts` の `listTodos` を変えます。

   ```ts
   export async function listTodos(
     filter: { done?: boolean } = {},
   ): Promise<Todo[]> {
     const query = filter.done === undefined ? "" : `?done=${filter.done}`;
     const res = await request(`/todos${query}`);
     return (await res.json()) as Todo[];
   }
   ```

4. `pnpm test` を実行します。今度は通ります。`pnpm check` も実行します。
5. `app/page.tsx` の `listTodos()` を `listTodos({ done: false })` に変えて、ページを再読み込みします。完了した Todo は、最初の一覧に出ません。確かめたら元に戻します。

### 4. テストを壊して直す

1. `components/todo-app.tsx` の `handleAdd` で、`title.trim()` を `title` に変えます。
2. `pnpm test` を実行します。`adds a todo` が失敗します。
3. 出力を読みます。期待した値は `"Walk"` で、実際の値は `"  Walk  "` です。失敗した行の番号も出ます。
4. `title.trim()` に戻して、`pnpm test` が通ることを確かめます。

### 5. サーバー側で止める

1. `pnpm dev` を止めます。API は動かしたままにします。
2. エディタで、デバッグの構成「Next.js: debug server-side」を開始します。
3. `app/page.tsx` の `todos = await listTodos();` の行にブレークポイントを置きます。
4. ブラウザで <http://localhost:3000> を再読み込みします。ブレークポイントで止まります。
5. 「ステップイン」で `listTodos`、`request`、`baseUrl` へと進みます。ここはサーバーなので、`typeof window` は `"undefined"` です。`baseUrl()` は `API_URL` を返します。
6. 「続行」で実行を再開します。ページが表示されます。

### 6. ブラウザ側で止める

1. ターミナルで `pnpm dev` を起動します。手順 5 のデバッグは終了しておきます。
2. デバッグの構成「Next.js: debug client-side」を開始します。新しいブラウザのウィンドウが開きます。
3. `components/todo-app.tsx` の `const trimmed = title.trim();` の行にブレークポイントを置きます。
4. 開いたウィンドウで Todo を追加します。ブレークポイントで止まります。
5. 「ステップイン」で `createTodo`、`request`、`baseUrl` へと進みます。今度はブラウザなので、`baseUrl()` は `/api` を返します。手順 5 と同じ関数が、別の結果を返します。

## デバッグ

デバッグの構成は `.vscode/launch.json` にあります。

| 構成                       | 内容                                                                         |
| -------------------------- | ---------------------------------------------------------------------------- |
| Next.js: debug server-side | `pnpm dev --inspect` を起動する。サーバーで動くコードで止められる            |
| Next.js: debug client-side | ブラウザを開く。ブラウザで動くコードで止められる。先に `pnpm dev` を起動する |
| Next.js: debug full stack  | サーバーとブラウザの両方を 1 回で起動する                                    |

サーバーで動くコードは、`app/page.tsx` と、そこから呼ばれる `lib/api.ts` です。ブラウザで動くコードは、`"use client"` で始まる `components/todo-app.tsx` と、そこから呼ばれる `lib/api.ts` です。

- client-side と full stack は Google Chrome を使います。Brave など、ほかの Chromium 系のブラウザを使う方法は、`launch.json` の中のコメントに書いてあります。
- 構成の URL は `http://localhost:3000` です。ポートを変えたときは、`launch.json` の `url` も変えます。
- `launch.json` はコメント付きの JSON です。ほかのエディタでも読み込めるように、コメントは行の先頭だけに書き、末尾のカンマは使っていません。

エディタのデバッガを使わない方法もあります。

- サーバー側: `pnpm dev --inspect` を実行し、Chrome 系のブラウザで `chrome://inspect` を開いて接続します。
- ブラウザ側: ブラウザの開発者ツールのソースのタブで、ブレークポイントを置きます。
- `console.log` も使えます。Server Component の出力は、`pnpm dev` のターミナルに出ます。Client Component の出力は、ブラウザのコンソールに出ます。

## 困ったとき

**ページに「The API is not reachable.」と出る**

API が動いていないか、`API_URL` が違います。次のコマンドで API を確かめます。

```sh
curl http://127.0.0.1:8000/health
```

**追加や削除をすると「API error: 500 Internal Server Error」と出る**

原因は上と同じです。`pnpm dev` のターミナルに `Failed to proxy ... ECONNREFUSED` と出ます。

**`.env.local` を変えたのに、`/api/*` の転送先が変わらない**

`pnpm dev` を再起動します。本番用のビルドでは、`pnpm build` からやり直します。「API との接続」の注意を見てください。

**`tsc --noEmit` が `Cannot find name 'LayoutProps'` で失敗する**

`pnpm typecheck` を使います。`LayoutProps` は Next.js が生成する型です。`pnpm typecheck` は、先に `next typegen` で型を生成します。

**エディタで保存しても整形されない**

`.vscode/extensions.json` の拡張機能を入れます。Oxc の拡張機能は `node_modules` の中の oxfmt を使うので、先に `pnpm install` が必要です。

**`pnpm install` で `deprecated eslint@9` という警告が出る**

`create-next-app` のテンプレートが ESLint 9 を指定しているためです。`pnpm lint` は動きます。

**ポート 3000 が使われている**

`pnpm dev --port 3001` のように、ポートを指定します。
