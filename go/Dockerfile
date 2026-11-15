FROM golang:1.27.4-bookworm AS build

WORKDIR /src
COPY go.mod ./
COPY . .
RUN go test ./... && CGO_ENABLED=0 go build -trimpath -o /wordcount ./cmd/wordcount

FROM scratch
WORKDIR /app
COPY --from=build /wordcount /usr/local/bin/wordcount
COPY README.md ./
USER 65532:65532
ENTRYPOINT ["wordcount"]
CMD ["-n", "5", "README.md"]
