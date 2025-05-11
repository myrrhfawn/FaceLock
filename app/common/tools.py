import face_recognition


def prepare_image(image, encoding=False):
    if encoding:
        image = face_recognition.face_encodings(image)
    return image
