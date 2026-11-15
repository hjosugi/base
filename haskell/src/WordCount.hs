module WordCount
  ( countWords
  , topWords
  )
where

import Data.Char (isAlphaNum, toLower)
import Data.List (group, sort, sortBy)
import Data.Ord (Down (Down), comparing)

countWords :: String -> [(String, Int)]
countWords = map toCount . group . sort . words . map normalize
 where
  normalize character
    | isAlphaNum character || character == '\'' = toLower character
    | otherwise = ' '
  toCount [] = error "Data.List.group never creates an empty group"
  toCount grouped@(word : _) = (word, length grouped)

topWords :: Int -> String -> [(String, Int)]
topWords limit = take (max 0 limit) . sortBy ranking . countWords
 where
  ranking = comparing (\(word, count) -> (Down count, word))
