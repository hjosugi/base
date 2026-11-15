use std::collections::HashMap;

/// Count words case-insensitively. Letters, numbers, and apostrophes are kept.
#[must_use]
pub fn count_words(text: &str) -> HashMap<String, usize> {
    text.split(|character: char| !character.is_alphanumeric() && character != '\'')
        .filter(|word| !word.is_empty())
        .map(str::to_lowercase)
        .fold(HashMap::new(), |mut counts, word| {
            *counts.entry(word).or_default() += 1;
            counts
        })
}

/// Return the most common words, ordered by count and then alphabetically.
#[must_use]
pub fn top_words(text: &str, limit: usize) -> Vec<(String, usize)> {
    let mut counts: Vec<_> = count_words(text).into_iter().collect();
    counts.sort_unstable_by(|(word_a, count_a), (word_b, count_b)| {
        count_b.cmp(count_a).then_with(|| word_a.cmp(word_b))
    });
    counts.truncate(limit);
    counts
}

#[cfg(test)]
mod tests {
    use super::{count_words, top_words};

    #[test]
    fn counts_case_insensitively() {
        let counts = count_words("Rust, rust! Safe.");
        assert_eq!(counts.get("rust"), Some(&2));
        assert_eq!(counts.get("safe"), Some(&1));
    }

    #[test]
    fn orders_by_count_then_word() {
        assert_eq!(
            top_words("pear apple pear banana apple", 2),
            vec![("apple".into(), 2), ("pear".into(), 2)]
        );
    }
}
