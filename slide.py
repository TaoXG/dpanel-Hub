import base64
import numpy as np
from PIL import Image, ImageFilter
from io import BytesIO
from bottle import post, run, request

def read_base64_image(base64_str: str):
    if ',' in base64_str:
        base64_str = base64_str.split(',')[1]
    image_data = base64.b64decode(base64_str)
    # 用PIL读取图片并转为numpy数组（BGR格式，对齐原OpenCV逻辑）
    img = Image.open(BytesIO(image_data))。convert('RGB')
    img_np = np.array(img)
    return img_np[:, :, ::-1]  # RGB转BGR

def edge_detection(img_np):
    """纯PIL实现边缘检测（替代Canny）"""
    # 转为PIL图片（BGR转RGB）
    img = Image.fromarray(img_np[:, :, ::-1])
    # 灰度化 + 高斯模糊 + 边缘检测
    img_gray = img.convert('L')
    img_blur = img_gray.filter(ImageFilter.GaussianBlur(radius=1))
    img_edge = img_blur.filter(ImageFilter.FIND_EDGES)
    # 转回numpy数组
    return np.array(img_edge)

def match_template(bg_edge, slider_edge):
    """纯numpy实现模板匹配（替代cv2.matchTemplate）"""
    bg_h, bg_w = bg_edge.shape
    slider_h, slider_w = slider_edge.shape
    
    # 滑动窗口计算相似度（归一化相关系数）
    max_val = -1
    max_loc = (0, 0)
    
    # 只在X轴滑动（滑块匹配只需要横向找位置）
    for x in range(bg_w - slider_w + 1):
        # 截取窗口
        window = bg_edge[:, x:x+slider_w]
        # 计算归一化相关系数
        corr = np.sum((window - window.mean()) * (slider_edge - slider_edge.mean()))
        corr /= (np.std(window) * np.std(slider_edge) * slider_h * slider_w + 1e-8)
        if corr > max_val:
            max_val = corr
            max_loc = (x, 0)
    
    return max_val, max_loc

def find_slide_distance(bg_base64: str, front_base64: str) -> int:
    # 读取图片
    bg = read_base64_image(bg_base64)
    slider = read_base64_image(front_base64)

    # 边缘检测（替代Canny）
    bg_edge = edge_detection(bg)
    slider_edge = edge_detection(slider)

    # 模板匹配
    max_val, max_loc = match_template(bg_edge, slider_edge)

    x = max_loc[0]  # 缺口 X 坐标
    return x, bg, max_loc, slider_edge.shape

@post('/')
def index():
    try:
        body = request.json
        x, bg, max_loc, shape = find_slide_distance(body['bg'], body['front'])
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
