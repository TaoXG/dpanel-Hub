import base64
import cv2
import numpy as np
from bottle import post, run, request


def read_base64_image(base64_str: str):
    if ',' in base64_str:
        base64_str = base64_str.split(',')[1]
    image_data = base64.b64decode(base64_str)
    np_arr = np.frombuffer(image_data, np.uint8)
    return cv2.imdecode(np_arr, cv2.IMREAD_COLOR)


def find_slide_distance(bg_base64: str, front_base64: str) -> int:
    # 读取图片
    bg = read_base64_image(bg_base64)
    slider = read_base64_image(front_base64)

    # 转灰度
    bg_gray = cv2.cvtColor(bg, cv2.COLOR_BGR2GRAY)
    slider_gray = cv2.cvtColor(slider, cv2.COLOR_BGR2GRAY)

    # 1️⃣ 高斯模糊去噪（减少背景噪点干扰）
    bg_gray = cv2.GaussianBlur(bg_gray, (3, 3), 0)
    slider_gray = cv2.GaussianBlur(slider_gray, (3, 3), 0)

    # 2️⃣ Canny 边缘检测（增强结构特征）
    bg_edge = cv2.Canny(bg_gray, 100, 200)
    slider_edge = cv2.Canny(slider_gray, 100, 200)

    # 3️⃣ 模板匹配
    result = cv2.matchTemplate(bg_edge, slider_edge, cv2.TM_CCOEFF_NORMED)

    # 匹配最高分的位置
    _, max_val, _, max_loc = cv2.minMaxLoc(result)

    x = max_loc[0]  # 缺口 X 坐标

    return x, bg,  max_loc, slider_edge.shape


@post('/')
def index():
    try:
        body = request.json
        x, bg, max_loc, shape = find_slide_distance(body['bg'], body['front'])

        # # 可视化调试（可选）
        # h, w = shape
        # cv2.rectangle(bg, max_loc, (max_loc[0] + w, max_loc[1] + h), (0, 0, 255), 2)
        # cv2.imshow("Match Result", bg)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        return {
            'code': 0,
            'result': x
        }
    except Exception as e:
        return {
            'code': 400,
            'msg': str(e),
        }


run(host='0.0.0.0', port=3001)
