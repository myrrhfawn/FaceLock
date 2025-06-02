import os
import sys


def get_app_path():
    """
    Returns the absolute path to the application directory.
    """
    if getattr(sys, "frozen", False):
        # PyInstaller-режим
        return sys._MEIPASS if hasattr(sys, "_MEIPASS") else os.getcwd()
    else:
        return os.getcwd()


def replace_file_extension(file_path: str, new_extension: str) -> str:
    """
    Replaces the extension of a file with the specified new extension.

    :param file_path: The original file path (e.g. 'data/file.txt')
    :param new_extension: The new extension (e.g. 'bin' or '.bin')
    :return: File path with the new extension (e.g. 'data/file.bin')
    """
    base, _ = os.path.splitext(file_path)
    if not new_extension.startswith("."):
        new_extension = "." + new_extension
    return base + new_extension
