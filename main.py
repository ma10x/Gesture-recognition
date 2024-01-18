# 导入opencv
import cv2
# mediapipe相关参数
import mediapipe as mp
import math
import random

# 初始化手势识别
mp_drawing = mp.solutions.drawing_utils  # 初始化Mediapipe库绘图工具
mp_drawing_styles = mp.solutions.drawing_styles  # 绘图样式
mp_hands = mp.solutions.hands  # 使用手部姿势估计模型

# 创建手部姿势估计对象，设置参数
hands = mp_hands.Hands(
    model_complexity=0,
    min_detection_confidence=0.5, min_tracking_confidence=0.5)

# 获取摄像头视频流
cap = cv2.VideoCapture(0)

# 获取画面的宽度和高度
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# 方块的相关参数
square_x = 300
square_y = 200
square_w = 70

target_x = 400
target_y = 100
target_w = 100
square_color = (255, 255, 0)
target_color = (0, 255, 255)

score = 0

L1 = 0
L2 = 0
on_squre = False

# 读取视频流
while True:
    # 获取视频流中的每一帧
    ret, frame = cap.read()

    # 对图像进行垂直翻转
    frame = cv2.flip(frame, 1)

    # mediapipe处理
    frame.flags.writeable = False
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame)
    frame.flags.writeable = True
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    # 检测到手势
    if results.multi_hand_landmarks:
        # 解析遍历每一双手
        for hand_landmarks in results.multi_hand_landmarks:
            # 画出21个关键点
            mp_drawing.draw_landmarks(
                frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                mp_drawing_styles.get_default_hand_landmarks_style(),
                mp_drawing_styles.get_default_hand_connections_style()
            )
            # 保存21个x，y坐标
            x_list = []  # x坐标列表
            y_list = []  # y坐标列表
            for landmark in hand_landmarks.landmark:  # 遍历21个关键点
                # 添加x坐标
                x_list.append(landmark.x)
                # 添加y坐标
                y_list.append(landmark.y)

            # 获取食指指尖
            index_finger_x = int(x_list[8] * width)  # 食指指尖x坐标
            index_finger_y = int(y_list[8] * height)  # 食指指尖y坐标

            # 获取拇指指尖坐标
            thumb_x = int(x_list[4] * width)  # 拇指指尖x坐标
            thumb_y = int(y_list[4] * height)  # 拇指指尖y坐标

            # 计算拇指指尖和食指指尖的距离
            finger_len = math.hypot((index_finger_x - thumb_x), (index_finger_y - thumb_y))  # 计算指尖距离

            print(finger_len)

            # 画一个圆来验证
            # cv2.circle(frame, (index_finger_x, index_finger_y), 20, (0, 0, 255), -1)
            # print(index_finger_x, index_finger_y)

            # 如果距离小于30算激活，否则取消激活
            if finger_len < 30:
                # 判断食指在不在方块上
                if (index_finger_x > square_x) and (index_finger_x <
                        (square_x + square_w)) and (index_finger_y > square_y) and \
                        (index_finger_y < (square_y + square_w)):
                    if on_squre == False:
                        # print('在方块上')
                        L1 = abs(index_finger_x - square_x)
                        L2 = abs(index_finger_y - square_y)
                        on_squre = True
                        square_color = (255, 0, 255)
                else:
                    # print('不在方块上')
                    pass
            else:
                # 取消激活
                on_squre = False
                square_color = (255, 255, 0)
            # 确保方块跟随手指移动
            if on_squre:
                square_x = index_finger_x - L1
                square_y = index_finger_y - L2

    # 画一方块
    # cv2.rectangle(frame, (square_x, square_y), (square_x+square_w,square_y+square_w),(255,0,0),-1)

    # 画一个半透明的方块
    overlay = frame.copy()
    cv2.rectangle(frame, (square_x, square_y), (square_x + square_w, square_y + square_w), square_color, -1)
    cv2.rectangle(frame, (target_x, target_y), (target_x + target_w, target_y + target_w), target_color, 2)
    frame = cv2.addWeighted(overlay, 0.5, frame, 0.5, 0)

    # 设置要显示的文本
    text = f"Score: {score}"
    # 选择字体和字号
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1
    font_thickness = 2
    # 选择文本位置
    text_position = (0, 25)
    # 选择文本颜色
    text_color = (255, 255, 0)
    # 在图像上绘制文本
    cv2.putText(frame, text, text_position, font, font_scale, text_color, font_thickness)

    if (square_x > target_x) and (square_x+square_w < target_x+target_w) and (square_y > target_y) and (square_y+square_w < target_y+target_w):
        score+=10
        target_x = random.randint(1, width-target_w)
        target_y = random.randint(1, height-target_w)


    # 显示图像
    cv2.imshow('Virtual grag', frame)

    # 按下esc键退出
    if cv2.waitKey(10) & 0xFF == 27:
        break

# 释放摄像头
cap.release()
# 关闭所有窗口
cv2.destroyAllWindows()