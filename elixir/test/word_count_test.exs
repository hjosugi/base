defmodule WordCountTest do
  use ExUnit.Case, async: true

  test "count ignores case and punctuation" do
    assert WordCount.count("Elixir, elixir! Safe.") == %{"elixir" => 2, "safe" => 1}
  end

  test "top orders by count then word" do
    assert WordCount.top("pear apple pear banana apple", 2) == [{"apple", 2}, {"pear", 2}]
  end
end
