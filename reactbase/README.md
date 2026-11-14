# reactbase

React (Vite) のスタータープロジェクトです。このディレクトリをコピーして、新しいプロジェクトを始めます。Vite の `react-ts` テンプレートに、フォーマッタ、テスト、エディタの設定、小さな Todo 画面を足しています。Todo 画面は [fastapibase](../fastapibase) の API を使います。

| 項目           | 内容                                         | バージョン             |
| -------------- | -------------------------------------------- | ---------------------- |
| ビルドツール   | Vite、@vitejs/plugin-react                   | 8.3.8、6.3.0           |
| UI             | React、React DOM                             | 19.3.1                 |
| 言語           | TypeScript（ネイティブ版）                   | 7.0.2                  |
| リンタ         | Oxlint                                       | 1.93.0                 |
| フォーマッタ   | oxfmt                                        | 0.78.0                 |
| テスト         | Vitest、jsdom                                | 5.1.0、31.0.1          |
| テスト         | @testing-library/react、user-event、jest-dom | 16.3.3、14.6.10、7.0.1 |
| パッケージ管理 | pnpm                                         | 12.19.0                |
| 実行環境       | Node.js                                      | 26.13.1 で確認         |

ほかのパッケージのバージョンは `pnpm-lock.yaml` にあります。

## 使い方

```sh
# 1. このディレクトリをコピーする
cp -r reactbase /path/to/my-app
cd /path/to/my-app

# 2. パッケージを入れる
pnpm install

# 3. 開発サーバーを起動する
pnpm dev
```

ブラウザで <http://localhost:5173> を開きます。

Todo 画面は API を使います。別のターミナルで [fastapibase](../fastapibase) を起動します。

```sh
cd ../fastapibase && uv run fastapi dev
```

API が動いていなくても、画面は表示されます。そのときは、API の起動方法が画面に出ます。

API の場所を変えるときは、`.env.example` を `.env.local` にコピーして `API_URL` を書き換えます。

コピーしたあとに、次の 2 つを自分のプロジェクトに合わせて変えます。

- `package.json` の `name`
- `index.html` の `<title>`

`node_modules` と `dist` がすでにある場合は、コピーに含めません。コピー先で `pnpm install` をやり直します。

## コマンド

| コマンド          | 内容                                                |
| ----------------- | --------------------------------------------------- |
| `pnpm dev`        | 開発サーバー（<http://localhost:5173>、HMR あり）   |
| `pnpm build`      | 型チェックをしてから `dist/` に本番用ファイルを作る |
| `pnpm preview`    | `dist/` の中身を手元で配信して確認する              |
| `pnpm lint`       | Oxlint（設定は `.oxlintrc.json`）                   |
| `pnpm fmt`        | oxfmt で整形する（設定は `.oxfmtrc.json`）          |
| `pnpm fmt:check`  | 整形されているかだけを調べる                        |
| `pnpm typecheck`  | `tsc -b`（プロジェクト全体の型チェック）            |
| `pnpm test`       | Vitest を 1 回実行する                              |
| `pnpm test:watch` | Vitest を watch モードで動かす                      |
| `pnpm check`      | lint、fmt:check、typecheck、test を順に実行する     |

コミットの前に `pnpm check` を実行します。

## ディレクトリ構成

```
reactbase/
├── index.html
├── vite.config.ts          開発サーバーのプロキシと Vitest の設定
├── .oxlintrc.json          lint のルール
├── .oxfmtrc.json           整形のルール（シングルクォート、セミコロンなし）
├── .env.example            .env.local にコピーして使う
├── tsconfig*.json
├── .vscode/
│   ├── settings.json       保存時の整形と lint の修正
│   ├── launch.json         ブラウザと Vitest のデバッグ
│   ├── tasks.json          dev server / check
│   └── extensions.json     必要な拡張機能
└── src/
    ├── main.tsx            エントリポイント
    ├── App.tsx             画面全体
    ├── api.ts              API の型と呼び出し
    ├── useTodos.ts         Todo の状態と SSE（カスタムフック）
    ├── components/
    │   ├── TodoForm.tsx
    │   └── TodoList.tsx
    ├── api.test.ts
    ├── App.test.tsx
    └── test/setup.ts       各テストの前後に動く準備
```

## API との接続

ブラウザは Vite の開発サーバーだけと通信します。`/api` で始まるリクエストは、開発サーバーが API に転送します。

```
ブラウザ ── GET /api/todos ──> Vite (localhost:5173) ── GET /todos ──> FastAPI (127.0.0.1:8000)
```

- 転送の設定は `vite.config.ts` の `server.proxy` にあります。`/api` を外してから転送します。
- ブラウザから見ると通信先は 1 つです。そのため、API 側に CORS の設定はいりません。
- 画面は SSE（`/api/todos/events`）もつないでいます。別のタブや `curl` で Todo を変えると、画面にすぐ反映されます。右上の表示が `live` なら接続中です。
- このプロキシは開発サーバーだけの機能です。本番では、Web サーバー（Nginx など）で `/api` を API に転送します。

## ハンズオン

エディタの操作は [ルートの README のショートカット早見表](../README.md#5-ショートカット早見表) を見てください。

### 1. 動かす

1. ターミナルを 2 つ開きます。1 つ目で `cd ../fastapibase && uv run fastapi dev`、2 つ目で `pnpm dev` を実行します。
2. <http://localhost:5173> を開いて、Todo を 1 つ足します。
3. 3 つ目のターミナルから API を直接呼びます。画面を触らなくても、一覧に出ます。

```sh
curl -X POST localhost:8000/todos -H 'content-type: application/json' -d '{"title":"from curl"}'
```

### 2. 呼び出しをたどる

「Add」を押してから API に届くまでを、「定義へ移動」でたどります。

1. `src/components/TodoForm.tsx` の `onAdd` にカーソルを置き、「参照を表示」で使われている場所を見ます。
2. `src/App.tsx` の `add` から「定義へ移動」をします。`src/useTodos.ts` に移ります。
3. `createTodo` から「定義へ移動」をします。`src/api.ts` に移ります。ここで `fetch` を呼んでいます。

### 3. 保存時の整形と lint を見る

1. `src/App.tsx` のどこかの `'` を `"` に変え、行末に `;` を足して保存します。元に戻れば、整形が動いています。
2. `App` 関数の中に次の 1 行を足します。フックを条件の中で呼んでいるので、Oxlint がエラーを出します。

```tsx
if (live) useTodos()
```

3. 足した行を消します。

### 4. テストを壊して直す

1. `pnpm test:watch` を実行します。
2. `src/components/TodoForm.tsx` の `title.trim()` を `title` に変えて保存します。テストは通ったままです。空白だけの入力を調べるテストがないからです。
3. `src/App.test.tsx` に、空白だけを入力すると「Add」が押せないことを調べるテストを足します。テストが失敗します。

```tsx
it('does not accept a blank title', async () => {
  vi.stubGlobal(
    'fetch',
    vi.fn(async () => jsonResponse([])),
  )
  const user = userEvent.setup()

  render(<App />)
  await user.type(await screen.findByLabelText('New todo'), '   ')

  expect(screen.getByRole('button', { name: 'Add' })).toBeDisabled()
})
```

4. `title.trim()` に戻します。テストが通ります。

### 5. ブラウザ側で止める

1. `pnpm dev` を動かしたままにします。
2. `src/useTodos.ts` の `const todo = await createTodo(title)` の行にブレークポイントを置きます。
3. デバッグ構成「Browser: debug app (Chrome)」を開始します。Chrome がなく Brave がある場合は「Browser: debug app (Brave)」を使います。
4. 開いたブラウザで Todo を足します。エディタで止まります。`title` の値を見ます。

### 6. テストをデバッガで動かす

1. `src/api.ts` の `const res = await fetch(API_BASE + path, init)` の行にブレークポイントを置きます。
2. `src/api.test.ts` を開いて、デバッグ構成「Vitest: current file」を開始します。
3. 止まったら `path` の値を見ます。

## デバッグ

デバッグ構成は `.vscode/launch.json` にあります。VS Code でも Neovim (nvim-dap) でも同じファイルを使います。

| 構成                        | 使う場面                                             |
| --------------------------- | ---------------------------------------------------- |
| Browser: debug app (Chrome) | 画面のコードを止める。先に `pnpm dev` を起動しておく |
| Browser: debug app (Brave)  | 上と同じ。Linux の Brave（`/usr/bin/brave`）を使う   |
| Vitest: current file        | 開いているテストファイルをデバッガ付きで実行する     |

ブラウザの開発者ツールだけでも止められます。Sources タブで `src/` のファイルを開いて、行番号を押します。

## 困ったとき

- **`Cannot reach the API` と出る**: fastapibase が動いていません。`cd ../fastapibase && uv run fastapi dev` を実行します。
- **保存しても整形されない (VS Code)**: Oxc 拡張機能（`oxc.oxc-vscode`）が入っているか確認します。
- **保存しても整形されない (Neovim)**: `:LazyFormatInfo` で、いま使われるフォーマッタを確認します。
- **ポート 5173 が使用中**: 別の `pnpm dev` が残っています。止めてから起動し直します。
- **`pnpm typecheck` では出る型エラーがエディタに出ない**: エディタはいま開いているファイルしか調べません。プロジェクト全体は `pnpm typecheck` で調べます。
