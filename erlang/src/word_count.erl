-module(word_count).

-export([count/1, top/2]).

-type count() :: {unicode:chardata(), non_neg_integer()}.
-export_type([count/0]).

-spec count(unicode:chardata()) -> [count()].
count(Text) ->
    Words = string:lexemes(string:lowercase(Text), separators()),
    maps:to_list(
        lists:foldl(
            fun(Word, Counts) -> maps:update_with(Word, fun(Value) -> Value + 1 end, 1, Counts) end,
            #{},
            Words
        )
    ).

-spec top(unicode:chardata(), non_neg_integer()) -> [count()].
top(Text, Limit) ->
    Ranked = lists:sort(fun rank_before/2, count(Text)),
    lists:sublist(Ranked, Limit).

-spec rank_before(count(), count()) -> boolean().
rank_before({WordA, CountA}, {WordB, CountB}) when CountA =:= CountB ->
    WordA =< WordB;
rank_before({_WordA, CountA}, {_WordB, CountB}) ->
    CountA > CountB.

-spec separators() -> nonempty_list(1..255).
separators() ->
    " \t\r\n.,!?;:\"()[]{}<>/\\|@#$%^&*_+=~`-".
