{
  description = "Development shells for the starter projects";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
        shell = packages: pkgs.mkShell { inherit packages; };
        beam = pkgs.beam29Packages;
      in
      {
        devShells = {
          default = shell [ pkgs.go-task pkgs.git ];

          python = shell [ pkgs.python315 pkgs.uv ];
          fastapi = shell [ pkgs.python315 pkgs.uv ];
          react = shell [ pkgs.nodejs_26 pkgs.pnpm ];
          next = shell [ pkgs.nodejs_26 pkgs.pnpm ];

          haskell = shell [
            pkgs.haskell.compiler.ghc9141
            pkgs.cabal-install
            pkgs.haskell-language-server
            pkgs.fourmolu
            pkgs.hlint
          ];

          rust = shell [
            pkgs.rustc
            pkgs.cargo
            pkgs.clippy
            pkgs.rustfmt
            pkgs.rust-analyzer
          ];

          go = shell [
            pkgs.go_1_27
            pkgs.gopls
            pkgs.gofumpt
            pkgs.golangci-lint
            pkgs.delve
          ];

          erlang = shell [
            beam.erlang
            beam.rebar3
            pkgs.erlfmt
            pkgs.erlang-language-platform
          ];

          elixir = shell [
            beam.erlang
            beam.elixir_1_20
            beam.rebar3
            beam.elixir-ls
          ];
        };
      });
}
