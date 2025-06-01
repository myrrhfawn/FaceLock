import os

import face_recognition


def prepare_image(image, encoding=False):
    """Prepares an image for face recognition."""
    if encoding:
        image = face_recognition.face_encodings(image)
    return image


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
