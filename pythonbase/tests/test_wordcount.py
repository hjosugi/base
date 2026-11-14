import pytest

from pythonbase.wordcount import count_words, top_words


def test_count_ignores_case_and_punctuation() -> None:
    assert count_words("Tea, tea. TEA!") == {"tea": 3}


def test_apostrophe_stays_in_the_word() -> None:
    assert count_words("don't stop") == {"don't": 1, "stop": 1}


def test_top_words_orders_by_count_then_alphabet() -> None:
    assert top_words("b a c b a b", limit=2) == [("b", 3), ("a", 2)]


def test_top_words_of_empty_text() -> None:
    assert top_words("") == []


@pytest.mark.parametrize("limit", [0, -1])
def test_top_words_rejects_bad_limit(limit: int) -> None:
    with pytest.raises(ValueError, match="limit"):
        top_words("a", limit=limit)
