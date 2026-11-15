FROM erlang:29.1.2-slim

ARG STARTER_REBAR3_VERSION=3.28.0
ARG STARTER_REBAR3_SHA256=5a28b1cca082d3b023ec0f5df9d9f9d52557036c6f2a21c1ffa11b93a984dd42
RUN apt-get update && \
    apt-get install --yes --no-install-recommends ca-certificates curl && \
    rm -rf /var/lib/apt/lists/* && \
    curl -fsSL "https://github.com/erlang/rebar3/releases/download/${STARTER_REBAR3_VERSION}/rebar3" \
      -o /usr/local/bin/rebar3 && \
    printf '%s  /usr/local/bin/rebar3\n' "$STARTER_REBAR3_SHA256" | sha256sum --check --strict - && \
    chmod +x /usr/local/bin/rebar3 && \
    rebar3 version | grep -F "$STARTER_REBAR3_VERSION"

WORKDIR /app
COPY rebar.config ./
COPY src ./src
COPY test ./test
COPY README.md ./
RUN rebar3 do compile, eunit, escriptize

ENTRYPOINT ["/app/_build/default/bin/word_count"]
CMD ["README.md", "-n", "5"]
