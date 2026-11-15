package wordcount

import (
	"sort"
	"strings"
	"unicode"
)

// Count returns case-insensitive word frequencies.
func Count(text string) map[string]int {
	words := strings.FieldsFunc(text, func(r rune) bool {
		return !unicode.IsLetter(r) && !unicode.IsNumber(r) && r != '\''
	})
	counts := make(map[string]int, len(words))
	for _, word := range words {
		counts[strings.ToLower(word)]++
	}
	return counts
}

// Top returns at most limit words ordered by count and then alphabetically.
func Top(text string, limit int) []Entry {
	entries := make([]Entry, 0, len(Count(text)))
	for word, count := range Count(text) {
		entries = append(entries, Entry{Word: word, Count: count})
	}
	sort.Slice(entries, func(i, j int) bool {
		if entries[i].Count == entries[j].Count {
			return entries[i].Word < entries[j].Word
		}
		return entries[i].Count > entries[j].Count
	})
	if limit < 0 {
		limit = 0
	}
	if limit < len(entries) {
		entries = entries[:limit]
	}
	return entries
}

// Entry is one word and its frequency.
type Entry struct {
	Word  string
	Count int
}
