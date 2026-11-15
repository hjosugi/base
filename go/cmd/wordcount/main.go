package main

import (
	"flag"
	"fmt"
	"os"

	"example.com/wordcount"
)

func run() error {
	limit := flag.Int("n", 10, "number of words to show")
	flag.Parse()
	if flag.NArg() != 1 {
		return fmt.Errorf("usage: wordcount [-n LIMIT] FILE")
	}
	text, err := os.ReadFile(flag.Arg(0))
	if err != nil {
		return fmt.Errorf("read %s: %w", flag.Arg(0), err)
	}
	for _, entry := range wordcount.Top(string(text), *limit) {
		fmt.Printf("%6d %s\n", entry.Count, entry.Word)
	}
	return nil
}

func main() {
	if err := run(); err != nil {
		fmt.Fprintf(os.Stderr, "wordcount: %v\n", err)
		os.Exit(1)
	}
}
