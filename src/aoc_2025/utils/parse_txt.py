from pathlib import Path


def simple_txt_parser(file_path: Path) -> list[str]:
  if not file_path.exists():
    raise FileNotFoundError(f"The file {file_path} does not exist.")
  with file_path.open("r", encoding="utf-8") as file:
    return [line.strip() for line in file.readlines()]
