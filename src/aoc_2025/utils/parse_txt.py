from pathlib import Path
from typing import Callable, TypeVar, overload

T = TypeVar("T")


def separator_parser(text: str, separator: str = ",") -> list[str]:
  """
  Parse a string by splitting on a separator and stripping whitespace from each part.
  Filters out empty strings after stripping.

  Args:
      text: The string to parse.
      separator: The separator to split on (default: ",").

  Returns:
      List of non-empty stripped strings.
  """
  return [item.strip() for item in text.split(separator) if item.strip()]


@overload
def simple_txt_parser(file_path: Path, parser: Callable[[str], T]) -> list[T]: ...
@overload
def simple_txt_parser(file_path: Path, parser: None = None) -> list[str]: ...
def simple_txt_parser(file_path: Path, parser: Callable[[str], T] | None = None) -> list[T] | list[str]:
  """
  Parse a text file into a list of lines, optionally applying a parser function to each line.

  Args:
      file_path: Path to the text file.
      parser: Optional callable to apply to each line. If None, returns stripped lines.

  Returns:
      List of parsed lines or stripped strings.

  Raises:
      FileNotFoundError: If the file does not exist.
  """
  if not file_path.exists():
    raise FileNotFoundError(f"The file {file_path} does not exist.")

  with file_path.open("r", encoding="utf-8") as file:
    lines = [line.strip() for line in file]

  return [parser(line) for line in lines] if parser is not None else lines
