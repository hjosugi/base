package wordcount

import (
	"reflect"
	"testing"
)

func TestCountIgnoresCaseAndPunctuation(t *testing.T) {
	t.Parallel()
	got := Count("Go, go! Safe.")
	if got["go"] != 2 || got["safe"] != 1 {
		t.Fatalf("Count() = %#v", got)
	}
}

func TestTopOrdersByCountThenWord(t *testing.T) {
	t.Parallel()
	want := []Entry{{Word: "apple", Count: 2}, {Word: "pear", Count: 2}}
	if got := Top("pear apple pear banana apple", 2); !reflect.DeepEqual(got, want) {
		t.Fatalf("Top() = %#v, want %#v", got, want)
	}
}
