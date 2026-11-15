-module(word_count_tests).

-include_lib("eunit/include/eunit.hrl").

count_ignores_case_and_punctuation_test() ->
    ?assertEqual(
        [{"erlang", 2}, {"safe", 1}], lists:sort(word_count:count("Erlang, erlang! Safe."))
    ).

top_orders_by_count_then_word_test() ->
    ?assertEqual(
        [{"apple", 2}, {"pear", 2}],
        word_count:top("pear apple pear banana apple", 2)
    ).
