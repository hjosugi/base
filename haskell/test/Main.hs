module Main (main) where

import Control.Monad (unless)
import WordCount (countWords, topWords)

main :: IO ()
main = do
  assertEqual
    "countWords ignores case and punctuation"
    [("haskell", 2), ("safe", 1)]
    (countWords "Haskell, haskell! Safe.")
  assertEqual
    "topWords orders by count then word"
    [("apple", 2), ("pear", 2)]
    (topWords 2 "pear apple pear banana apple")

assertEqual :: (Eq a, Show a) => String -> a -> a -> IO ()
assertEqual label expected actual =
  unless (expected == actual) $
    fail (label <> ": expected " <> show expected <> ", got " <> show actual)
