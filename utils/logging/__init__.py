import logging
import re
import sys

from utils.logging import format, palette

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(message)s')

replacements = {
    # AI Clients
    'Plugin': f'{format.color(palette.material.yellow)}Plugin{format.reset()}',
    'Chat AI': f'{format.color(palette.material.cyan)}Chat AI{format.reset()}',
    'Speech AI': f'{format.color(palette.material.cyan)}Speech AI{format.reset()}',
    'Transcribe AI': f'{format.color(palette.material.cyan)}Transcribe AI{format.reset()}',
    # Usage
    'Usage': f'{format.color(palette.material.pink)}Usage{format.reset()}',
    '[0-9]+ tokens': f'{format.color(palette.material.purple)}\\g<0>{format.reset()}',
    '[0-9]+ words': f'{format.color(palette.material.purple)}\\g<0>{format.reset()}',
    # input.py
    'input.py': f'{format.color(palette.material.orange)}input.py{format.reset()}',
    'Recording': f'{format.color(palette.material.red)}Recording{format.reset()}',
    # Characters
    '\(([^\)]+?)\)': f'{format.color(palette.material.blue)}(\\g<1>){format.reset()}',
}


class Log:
    @staticmethod
    def info(message):
        for pattern, replacement in replacements.items():
            message = re.sub(pattern, replacement, message)

        logging.info(message)

    @staticmethod
    def warning(message):
        for pattern, replacement in replacements.items():
            message = re.sub(pattern, replacement, message)

        logging.warning(message)

    @staticmethod
    def error(message):
        for pattern, replacement in replacements.items():
            message = re.sub(pattern, replacement, message)

        logging.error(message)


log = Log()
