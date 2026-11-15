FROM haskell:9.14.1-slim-bookworm

ARG CABAL_VERSION=3.18.2.0
RUN apt-get update && \
    apt-get install --yes --no-install-recommends ca-certificates curl xz-utils && \
    rm -rf /var/lib/apt/lists/*
RUN set -eux; \
    architecture="$(dpkg --print-architecture)"; \
    case "$architecture" in \
      amd64) cabal_arch="x86_64" ;; \
      arm64) cabal_arch="aarch64" ;; \
      *) echo "unsupported architecture: $architecture" >&2; exit 1 ;; \
    esac; \
    archive="cabal-install-${CABAL_VERSION}-${cabal_arch}-linux-unknown.tar.xz"; \
    base_url="https://downloads.haskell.org/~cabal/cabal-install-${CABAL_VERSION}"; \
    curl -fsSLO "${base_url}/${archive}"; \
    curl -fsSLO "${base_url}/SHA256SUMS"; \
    grep " ${archive}$" SHA256SUMS | sha256sum --check --strict -; \
    tar -xJf "$archive"; \
    install -m 0755 cabal /usr/local/bin/cabal; \
    rm -f "$archive" SHA256SUMS cabal; \
    test "$(cabal --numeric-version)" = "$CABAL_VERSION"

WORKDIR /app
COPY cabal.project word-count.cabal ./
COPY src ./src
COPY app ./app
COPY test ./test
COPY README.md ./
RUN cabal test all

ENTRYPOINT ["cabal", "run", "word-count", "--"]
CMD ["README.md", "-n", "5"]
