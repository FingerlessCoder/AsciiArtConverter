from PIL import Image

def image_to_ascii(image_path, width=100):
    img = Image.open(image_path).convert("L")
    
    # 保持原始调整因子 0.5
    aspect_ratio = img.height / img.width
    new_height = int(width * aspect_ratio * 0.5)
    img = img.resize((width, new_height))

    # 原始字符集（增加索引安全保护）
    ascii_chars = "@%#*+=-:. "
    
    # 修复原代码可能的索引越界问题
    pixel_to_char = lambda p: ascii_chars[min(int(p/255*(len(ascii_chars)-1)), len(ascii_chars)-1)]
    
    pixels = img.getdata()
    ascii_str = "".join(pixel_to_char(pixel) for pixel in pixels)
    
    ascii_lines = [ascii_str[i:i+width] for i in range(0, len(ascii_str), width)]
    return "\n".join(ascii_lines)

# 保持原始调用方式
if __name__ == "__main__":
    name = "gongyoo"
    image_path = name + ".jpg"
    
    # 保持原样输出到控制台和文件
    ascii_art = image_to_ascii(image_path, width=500)
    print(ascii_art)
    
    with open(name + ".txt", "w") as f:
        f.write(ascii_art)