from engine.tracker import *


class Point:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __repr__():
        return f"Point({x}, {y})"


class DirectionTracker:
    end_point: Point = Point(335, 298)

    def __init__(self, people: int = 0):
        self.people: int = people
        self.pts = dict()
        self.ld = dict()
        self.rd = dict()
        self.status = dict()

    def dist_bt_twopts(self, curr: Point):
        return math.sqrt((self.end_point.x - curr.x) ** 2 + (self.end_point.y - curr.y) ** 2)

    def cal_only_ldist(self, i: int):
        curr = self.pts[i][0]
        self.ld[i] = self.dist_bt_twopts(curr)

    def update_dist(self, i: int):
        curr = self.pts[i][1]

        self.rd[i] = self.dist_bt_twopts(curr)
        if (self.ld[i] > self.rd[i]):
            print(f"{i} Entering")
            if (i not in self.status or (i in self.status and self.status[i] == False)):
                self.status[i] = True
                self.people += 1
        else:
            print(f"{i} Exiting")
            if (i not in self.status or (i in self.status and self.status[i] == True)):
                self.status[i] = False
                self.people -= 1
        self.ld[i] = self.rd[i]
        self.pts[i] = self.pts[i][1:]

    def update(self, point: list):
        x, y, w, h, i = point
        if i not in self.pts:
            self.pts[i] = [Point(x, y)]
            self.cal_only_ldist(i)
        else:
            self.pts[i].append(Point(x, y))
            self.update_dist(i)

#
# body_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_upperbody.xml")
# cap = cv2.VideoCapture('video4.mp4')
# tracker: EuclideanDistTracker = EuclideanDistTracker()
# dt: DirectionTracker = DirectionTracker(500)
#
# while True:
#     _, frame = cap.read()
#     # frame = cv2.resize(frame, (0 , 0), fx=0.5, fy=0.5)
#
#     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#     boxes = body_cascade.detectMultiScale(gray, 1.1, 3)
#     detections = []
#     for (x, y, w, h) in boxes:
#         cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
#         # cv2.circle(frame, ((x + w) - (w // 2), (y + h) - (h // 2)), 5, (0, 255, 0), -1)
#         detections.append([x, y, w, h])
#
#     points = tracker.update(detections)
#
#     for point in points:
#         p = dt.update(point)
#         x, y, w, h, i = point
#         cv2.putText(frame, str(i), (x, y - 15), cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 0), 1)
#         cv2.circle(frame, ((x + w) - (w // 2), (y + h) - (h // 2)), 5, (0, 0, 255), -1)
#
#     cv2.imshow("Frame", frame)
#
#     if (cv2.waitKey(30) == 27):
#         break
#
# print(f"Total people: {dt.people}")
# cap.release()
# cv2.destroyAllWindows()