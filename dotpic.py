from PIL import Image

# 定义盲文点阵映射
def pixel_to_braille(pixel_block):
    braille_base = 0x2800
    braille_map = [
        (0, 0), (1, 0), (0, 1), (1, 1),  # 左列：点1-4
        (0, 2), (1, 2), (0, 3), (1, 3)   # 右列：点5-8
    ]
    value = 0
    for i, (x, y) in enumerate(braille_map):
        if pixel_block[y][x] > 128:  # 设置一个阈值，控制点是否激活
            value |= (1 << i)
    return chr(braille_base + value)

# 将图片转换为盲文ASCII艺术
def image_to_braille(image_path, width=100):
    img = Image.open(image_path).convert("L")  # 转为灰度图
    aspect_ratio = img.height / img.width
    new_height = int(width * aspect_ratio * 0.5)  # 调整高度比

    # 调整图像大小，适应盲文字符的点阵（每字符表示2x4像素）
    img = img.resize((width * 2, new_height * 4))

    # 获取像素数据并划分为 2x4 的小块
    pixels = img.load()
    braille_art = []
    for y in range(0, img.height, 4):  # 每4行
        line = []
        for x in range(0, img.width, 2):  # 每2列
            block = [[pixels[x + dx, y + dy] if x + dx < img.width and y + dy < img.height else 0
                      for dx in range(2)] for dy in range(4)]
            line.append(pixel_to_braille(block))
        braille_art.append("".join(line))
    return "\n".join(braille_art)

# 主程序
if __name__ == "__main__":
    # 输入图片路径
    name="gongyoo"
    image_path = name+".jpg"  # 替换为你的图片文件路径
    braille_ascii_art = image_to_braille(image_path, width=100)

    # 输出盲文ASCII艺术
    print(braille_ascii_art)

    # 保存到文本文件
    with open(name+"_braille.txt", "w", encoding="utf-8") as f:
        f.write(braille_ascii_art)
