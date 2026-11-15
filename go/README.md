# go

Go の CLI スターターです。Go 1.27.4、標準の gofmt / vet / test、gopls、Delve、golangci-lint を使います。サンプルは外部依存のない word-count CLI です。

## セットアップ

| 方法                              | コマンド                        |
| --------------------------------- | ------------------------------- |
| 公式配布                          | Go 1.27.4 を入れて `go version` |
| mise                              | `mise install`                  |
| Nix（リポジトリ内）               | `nix develop ..#go`             |
| Docker (`golang:1.27.4-bookworm`) | `docker build -t go-starter .`  |

```sh
go run ./cmd/wordcount -n 5 README.md
gofmt -w .
go vet ./...
go test -race ./...
```

まとめて確認するときは、ルートから `task check:go` を実行します。Docker では `docker run --rm go-starter` を使います。

## Neovim (LazyVim)

`:LazyExtras` で `lang.go`、`dap.core`、`test.core` を有効にします。gopls、gofumpt、goimports、golangci-lint、Delve、neotest-golang が入ります。`<leader>tt` でテスト、`<leader>td` でテストのデバッグ、`<leader>dc` で `.vscode/launch.json` の構成を開始できます。

## コピー後に変えるもの

- `go.mod` の `module example.com/wordcount`
- `cmd/wordcount/main.go` の import path
- コマンド名と `.vscode/launch.json`

`go mod tidy` と `go test ./...` を実行してから使い始めます。
