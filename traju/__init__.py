"""Top-level package for traju."""

__author__ = 'Vsevolod O. Shegolev'
__email__ = 'v.sheg@icloud.com'
__version__ = '0.1.0'

from sys import stdout
import logging

# level will be overwritten if `-y` is specified
logging.basicConfig(level=logging.INFO)  # root logger
