FROM erlang:29.1.2-slim

RUN rebar3 version | grep -F '3.28.0'

WORKDIR /app
COPY rebar.config ./
COPY src ./src
COPY test ./test
COPY README.md ./
RUN rebar3 do compile, eunit, escriptize

ENTRYPOINT ["/app/_build/default/bin/word_count"]
CMD ["README.md", "-n", "5"]
