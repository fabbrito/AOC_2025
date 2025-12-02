import logging

from .parse_txt import separator_parser, simple_txt_parser


def setup_logger(level=logging.INFO, format="%(levelname)s: %(message)s"):
  logging.basicConfig(level=level, format=format)


__all__ = ["simple_txt_parser", "setup_logger", "separator_parser"]
