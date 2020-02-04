import cv2
import platform
import time
import numpy as np


if 'Darwin' == platform.system():
    # Mac
    cap = cv2.VideoCapture(0)
else:
    pass


def dHash(door=12, maxFps=1000):
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    # cv2.imshow('HH', frame)
    start = time.time()
    fps = 0
    last = False
    while 1:
        _ret, frame = cap.read()
        frame = cv2.resize(frame, (9, 8))
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        ret = []
        # print(np.mean(frame))

        # cv2.imshow('HH', frame)
        for row in range(8):
            for col in range(8):
                ret.append(frame[row][col] > frame[row][col + 1])
                # ret.append(frame[row][col] > np.mean(frame))
        x = 0
        if not last:
            last = ret
        else:
            for i in range(64):
                if last[i] != ret[i]:
                    x += 1
            if x > door:
                last = ret
                print(time.ctime() + '\t' + str(x))

        # print(''.join([str(i) for i in ret]) + '\t' + info)
            
        # dst = cv2.bilateralFilter(frame, 0, 15, 5)
        # cv2.imshow('HH', dst)        
        fps += 1
        if cv2.waitKey(1) & 0xff == ord('q') or fps >= maxFps:
            break
    print(f'总共 {fps} 帧，平均 FPS = {fps/(time.time()-start):.0f}')
    cap.release()
    cv2.destroyAllWindows()


dHash(door=15, maxFps=1000)