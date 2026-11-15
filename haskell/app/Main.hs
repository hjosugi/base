module Main (main) where

import System.Environment (getArgs, getProgName)
import System.Exit (die)
import Text.Printf (printf)
import WordCount (topWords)

main :: IO ()
main = do
  program <- getProgName
  arguments <- getArgs
  (path, limit) <- either (die . usage program) pure (parseArgs arguments)
  content <- readFile path
  mapM_ (\(word, count) -> printf "%6d %s\n" count word) (topWords limit content)

usage :: String -> String -> String
usage program message = message <> "\nUsage: " <> program <> " FILE [-n LIMIT]"

parseArgs :: [String] -> Either String (FilePath, Int)
parseArgs = go Nothing 10
 where
  go path limit [] = maybe (Left "FILE is required") (\file -> Right (file, limit)) path
  go path _limit ("-n" : value : rest) = do
    limit <- parseLimit value
    go path limit rest
  go _path _limit ["-n"] = Left "-n requires a number"
  go Nothing limit (file : rest) = go (Just file) limit rest
  go (Just _) _limit (_ : _) = Left "only one FILE can be given"

parseLimit :: String -> Either String Int
parseLimit value = case reads value of
  [(limit, "")] | limit >= 0 -> Right limit
  _ -> Left "LIMIT must be a non-negative integer"
