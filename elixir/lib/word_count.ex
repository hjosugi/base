defmodule WordCount do
  @moduledoc "Case-insensitive word counting."

  @word ~r/[\p{L}\p{N}']+/u

  @spec count(String.t()) :: %{String.t() => non_neg_integer()}
  def count(text) do
    @word
    |> Regex.scan(text, capture: :first)
    |> List.flatten()
    |> Enum.map(&String.downcase/1)
    |> Enum.frequencies()
  end

  @spec top(String.t(), non_neg_integer()) :: [{String.t(), non_neg_integer()}]
  def top(text, limit) do
    text
    |> count()
    |> Enum.sort_by(fn {word, count} -> {-count, word} end)
    |> Enum.take(limit)
  end
end
