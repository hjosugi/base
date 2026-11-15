FROM elixir:1.20.5-otp-29-slim

RUN elixir --version | grep -F 'Elixir 1.20.5' && \
    erl -noshell -eval 'io:format("~s", [erlang:system_info(otp_release)]), halt().' | grep -F '29'

WORKDIR /app
COPY mix.exs .formatter.exs ./
COPY lib ./lib
COPY test ./test
COPY README.md ./
RUN mix do format --check-formatted, compile --warnings-as-errors, test, escript.build

ENTRYPOINT ["/app/word_count"]
CMD ["README.md", "-n", "5"]
