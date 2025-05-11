import cv2
import face_recognition


def main(name):
    cap = cv2.VideoCapture(0)
    me = cv2.imread("faces/me.jpeg")
    me_rgb = cv2.cvtColor(me, cv2.COLOR_BGR2RGB)
    # print(f"me: {me_rgb}")
    me_rgb = cv2.rotate(me_rgb, cv2.ROTATE_90_CLOCKWISE)
    me_encode = face_recognition.face_encodings(me_rgb)[0]

    # print(f"me_en: {me_encode}")
    # show the image
    while True:
        res, image = cap.read()
        if res:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
            encode = face_recognition.face_encodings(image)
            loc = face_recognition.face_locations(image)
            print(f"loc: {loc}")
            if len(encode) > 0 and len(loc) > 0:
                result = face_recognition.compare_faces([me_encode], encode[0])
                y1, x1, y2, x2 = loc[0][0], loc[0][1], loc[0][2], loc[0][3]
                cv2.rectangle(image, (x1, y1), (x2, y2), (0, 0, 200), 4)
                print(f"face: {loc}, res: {result}")
            cv2.imshow("FaceLock", image)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    # save the image
    # cv2.imwrite("GeeksForGeeks.png", image)
    cv2.waitKey(0)
    cv2.destroyWindow("GeeksForGeeks")


if __name__ == "__main__":
    main("PyCharm")
