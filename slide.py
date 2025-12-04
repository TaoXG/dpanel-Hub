import base64
from PIL import Image, ImageFilter
from io import BytesIO
from bottle import post, run, request

def read_base64_image(base64_str: str):
    # 注意：这里是英文 in，不是中文“在”
    if ',' in base64_str:
        base64_str = base64_str.split(',')[1]
    image_data = base64.b64decode(base64_str)
    return Image.open(BytesIO(image_data)).convert('RGB')

def find_slide_distance(bg_base64: str, front_base64: str) -> int:
    # 读取图片
    bg = read_base64_image(bg_base64)
    slider = read_base64_image(front_base64)
    
    # 边缘检测
    bg_gray = bg.convert('L').filter(ImageFilter.GaussianBlur(radius=1)).filter(ImageFilter.FIND_EDGES)
    slider_gray = slider.convert('L').filter(ImageFilter.GaussianBlur(radius=1)).filter(ImageFilter.FIND_EDGES)
    
    # 模板匹配（纯PIL实现）
    bg_w, bg_h = bg_gray.size
    slider_w, slider_h = slider_gray.size
    max_corr = -1
    best_x = 0
    
    for x in range(bg_w - slider_w + 1):
        # 截取窗口
        window = bg_gray.crop((x, 0, x+slider_w, slider_h))
        # 计算像素相似度
        corr = sum(abs(a - b) for a, b in zip(window.getdata(), slider_gray.getdata()))
        corr = 1 - (corr / (slider_w * slider_h * 255))  # 归一化
        if corr > max_corr:
            max_corr = corr
            best_x = x
    
    return best_x, bg, (best_x, 0), (slider_h, slider_w)

@post('/')
def index():
    try:
        body = request.json
        x, _, _, _ = find_slide_distance(body['bg'], body['front'])
        return {'code': 0, 'result': x}
    except Exception as e:
        return {'code': 400, 'msg': str(e)}

# 启动服务（确保端口和Docker暴露的一致）
run(host='0.0.0.0', port=3001)
