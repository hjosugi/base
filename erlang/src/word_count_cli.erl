-module(word_count_cli).

-export([main/1]).

-spec main([string()]) -> no_return() | ok.
main(Arguments) ->
    case parse_args(Arguments, undefined, 10) of
        {ok, Path, Limit} -> run(Path, Limit);
        {error, Message} -> fail(Message)
    end.

-spec run(file:name_all(), non_neg_integer()) -> no_return() | ok.
run(Path, Limit) ->
    case file:read_file(Path) of
        {ok, Content} ->
            lists:foreach(
                fun({Word, Count}) -> io:format("~6B ~ts~n", [Count, Word]) end,
                word_count:top(unicode:characters_to_list(Content), Limit)
            );
        {error, Reason} ->
            fail(io_lib:format("~ts: ~ts", [Path, file:format_error(Reason)]))
    end.

-spec parse_args([string()], undefined | string(), non_neg_integer()) ->
    {ok, string(), non_neg_integer()} | {error, string()}.
parse_args([], undefined, _Limit) ->
    {error, "FILE is required"};
parse_args([], Path, Limit) ->
    {ok, Path, Limit};
parse_args(["-n", Value | Rest], Path, _Limit) ->
    case string:to_integer(Value) of
        {Limit, ""} when Limit >= 0 -> parse_args(Rest, Path, Limit);
        _ -> {error, "LIMIT must be a non-negative integer"}
    end;
parse_args(["-n"], _Path, _Limit) ->
    {error, "-n requires a number"};
parse_args([Path | Rest], undefined, Limit) ->
    parse_args(Rest, Path, Limit);
parse_args([_ | _], _Path, _Limit) ->
    {error, "only one FILE can be given"}.

-spec fail(unicode:chardata()) -> no_return().
fail(Message) ->
    io:format(standard_error, "word_count: ~ts~nUsage: word_count FILE [-n LIMIT]~n", [Message]),
    halt(1).
