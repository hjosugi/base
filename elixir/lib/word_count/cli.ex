defmodule WordCount.CLI do
  @moduledoc false

  @spec main([String.t()]) :: no_return() | :ok
  def main(arguments) do
    with {options, [path], []} <-
           OptionParser.parse(arguments, strict: [limit: :integer], aliases: [n: :limit]),
         limit when is_integer(limit) and limit >= 0 <- Keyword.get(options, :limit, 10),
         {:ok, text} <- File.read(path) do
      text
      |> WordCount.top(limit)
      |> Enum.each(fn {word, count} ->
        IO.puts("#{String.pad_leading(Integer.to_string(count), 6)} #{word}")
      end)
    else
      {:error, reason} -> fail(:file.format_error(reason))
      _ -> fail("Usage: word_count FILE [-n LIMIT]")
    end
  end

  defp fail(message) do
    IO.puts(:stderr, "word_count: #{message}")
    System.halt(1)
  end
end
