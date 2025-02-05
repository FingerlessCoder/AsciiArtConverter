import tkinter as tk
from tkinter import filedialog, ttk, messagebox, colorchooser
from PIL import Image, ImageFilter  # 导入 ImageFilter
import threading

class AsciiArtConverter:
    def __init__(self, master):
        self.master = master
        master.title("图片转ASCII工具")
        self.is_processing = False
        self.cancel_requested = False
        
        # 定义字符集（提前定义）
        self.basic_set = "@%#*+=-:. "   # 基础字符集
        self.inverse_set = ".:-=+*#%@"
        self.high_density_set = "@MBHENR#KWXDFPQASUZbdehx*8Gm&04LOVYkpq5Tagns69owz$CIu23Jcfry%1v7l+it[]{}?j|()=~!-/<>\"^_';,:`. "
        self.original_problem_set = "@W$9876543210?!abc;:+=-,._ "
        
        # 新增“盲文”选项
        self.braille_option = "盲文"
        
        self.create_widgets()
        self.image_path = ""
        self.ascii_art = ""
        
    def create_widgets(self):
        # 文件选择区域
        file_frame = ttk.LabelFrame(self.master, text="图片选择")
        file_frame.pack(padx=10, pady=5, fill="x")
        
        self.path_label = ttk.Label(file_frame, text="未选择文件")
        self.path_label.pack(side="left", padx=5)
        
        self.browse_btn = ttk.Button(file_frame, text="浏览...", command=self.select_file)
        self.browse_btn.pack(side="right", padx=5)
        
        # 参数设置区域
        param_frame = ttk.LabelFrame(self.master, text="转换参数")
        param_frame.pack(padx=10, pady=5, fill="x")
        
        ttk.Label(param_frame, text="输出宽度:").grid(row=0, column=0, sticky="w")
        self.width_entry = ttk.Entry(param_frame, width=10)
        self.width_entry.insert(0, "256")
        self.width_entry.grid(row=0, column=1, padx=5)
        
        ttk.Label(param_frame, text="高宽补偿:").grid(row=1, column=0, sticky="w")
        self.adj_scale = ttk.Scale(param_frame, from_=0.1, to=1.0, value=0.55)
        self.adj_scale.grid(row=1, column=1, sticky="we", padx=5)
        
        # 字符集选项：保留原有四种字符集，并添加“盲文”选项
        ttk.Label(param_frame, text="字符集:").grid(row=2, column=0, sticky="w")
        self.chars_combo = ttk.Combobox(param_frame, values=[
            self.basic_set, 
            self.inverse_set, 
            self.high_density_set, 
            self.original_problem_set,
            self.braille_option
        ])
        # 默认选择基础字符集
        self.chars_combo.set(self.basic_set)
        self.chars_combo.grid(row=2, column=1, sticky="we", padx=5)
        
        ttk.Label(param_frame, text="预览缩放:").grid(row=3, column=0, sticky="w")
        self.scale_slider = ttk.Scale(param_frame, from_=1, to=20, value=4, command=self._update_preview_font)
        self.scale_slider.grid(row=3, column=1, sticky="we", padx=5)
        
        # 操作按钮区域
        btn_frame = ttk.Frame(self.master)
        btn_frame.pack(pady=5)
        
        self.convert_btn = ttk.Button(btn_frame, text="生成", command=self._start_async_conversion)
        self.convert_btn.pack(side="left", padx=5)
        
        self.save_btn = ttk.Button(btn_frame, text="保存", command=self.save_file)
        self.save_btn.pack(side="left", padx=5)
        
        # 添加客制化按钮：设置背景色和文字颜色
        self.bg_color_btn = ttk.Button(btn_frame, text="设置背景色", command=self.choose_bg_color)
        self.bg_color_btn.pack(side="left", padx=5)
        
        self.text_color_btn = ttk.Button(btn_frame, text="设置文字颜色", command=self.choose_text_color)
        self.text_color_btn.pack(side="left", padx=5)
        
        # 结果显示区域
        result_frame = ttk.LabelFrame(self.master, text="预览 (建议使用等宽字体)")
        result_frame.pack(padx=10, pady=5, fill="both", expand=True)
        
        # 默认背景为白色，文字颜色为黑色
        self.result_text = tk.Text(result_frame, wrap="none", font=("Courier", 4), bg="white", fg="black")
        scroll_x = ttk.Scrollbar(result_frame, orient="horizontal", command=self.result_text.xview)
        scroll_y = ttk.Scrollbar(result_frame, orient="vertical", command=self.result_text.yview)
        self.result_text.configure(xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set)
        
        self.result_text.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns")
        scroll_x.grid(row=1, column=0, sticky="ew")
        result_frame.grid_rowconfigure(0, weight=1)
        result_frame.grid_columnconfigure(0, weight=1)
        
    def _update_preview_font(self, value):
        try:
            font_size = int(float(value))
            self.result_text.config(font=("Courier", font_size))
        except Exception:
            pass

    def choose_bg_color(self):
        # 使用颜色选择器
        color = colorchooser.askcolor(title="选择背景色")
        if color[1]:
            self.result_text.config(bg=color[1])
        
    def choose_text_color(self):
        # 使用颜色选择器
        color = colorchooser.askcolor(title="选择文字颜色")
        if color[1]:
            self.result_text.config(fg=color[1])
        
    def select_file(self):
        filetypes = (("图片文件", "*.jpg *.jpeg *.png"), ("所有文件", "*.*"))
        path = filedialog.askopenfilename(title="选择图片", filetypes=filetypes)
        if path:
            self.image_path = path
            self.path_label.config(text=path.split("/")[-1])

    def _start_async_conversion(self):
        if self.is_processing:
            messagebox.showinfo("提示", "已有任务正在运行")
            return

        self.is_processing = True
        self.cancel_requested = False
        for widget in [self.browse_btn, self.convert_btn, self.save_btn, self.bg_color_btn, self.text_color_btn]:
            widget.config(state="disabled")

        threading.Thread(target=self._async_generate, daemon=True).start()

    def _safe_gui_update(self, callback, *args):
        self.master.after(0, callback, *args)

    def _async_generate(self):
        try:
            width = int(self.width_entry.get())
            adjust_factor = self.adj_scale.get()
            ascii_chars = self.chars_combo.get()
            
            # 如果选择的是“盲文”，调用盲文转换方法
            if ascii_chars == self.braille_option:
                final_art = self.image_to_braille(width)
                self._safe_gui_update(self._update_final_result, final_art)
                return
            
            # 普通ASCII转换处理
            with Image.open(self.image_path) as img:
                # 转为灰度图并抗锯齿处理
                img = img.convert("L")
                aspect_ratio = img.height / img.width
                new_height = int(width * aspect_ratio * adjust_factor)
                img = img.resize((width, new_height), Image.LANCZOS)
                
                # 边缘增强处理
                img = img.filter(ImageFilter.EDGE_ENHANCE)
                
                pixel_access = img.load()
                gradient = len(ascii_chars)
                
                # 针对高密度和原问题字符集采用非线性映射（gamma校正）
                # gamma值可根据需要调整
                use_gamma = ascii_chars == self.high_density_set or ascii_chars == self.original_problem_set
                gamma = 0.7
                
                ascii_lines = []
                for y in range(new_height):
                    if self.cancel_requested:
                        self._safe_gui_update(lambda: messagebox.showinfo("提示", "已取消生成"))
                        break

                    self._safe_gui_update(self._update_progress, y+1, new_height)

                    line = []
                    for x in range(width):
                        p = pixel_access[x, y]
                        if use_gamma:
                            normalized = (p / 255) ** (1 / gamma)
                            index = min(int(normalized * (gradient - 1)), gradient - 1)
                        else:
                            index = min(int(p / 255 * (gradient - 1)), gradient - 1)
                        line.append(ascii_chars[index])
                    ascii_lines.append("".join(line))

                final_art = "\n".join(ascii_lines)
                self._safe_gui_update(self._update_final_result, final_art)

        except Exception as e:
            self._safe_gui_update(lambda: messagebox.showerror("转换错误", f"错误详情：{str(e)}"))
        finally:
            self._safe_gui_update(self._reset_ui_state)

    def _update_progress(self, current, total):
        if not hasattr(self, 'progress'):
            self.progress = ttk.Progressbar(self.master, mode='determinate')
            self.progress.pack(fill='x', pady=5)
        self.progress['maximum'] = total
        self.progress['value'] = current
        
        if not hasattr(self, 'status_label'):
            self.status_label = ttk.Label(self.master)
            self.status_label.pack()
        self.status_label.config(text=f"处理进度: {current}/{total} 行")

    def _update_final_result(self, art):
        self.ascii_art = art
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, art)

    def _reset_ui_state(self):
        self.is_processing = False
        for widget in [self.browse_btn, self.convert_btn, self.save_btn, self.bg_color_btn, self.text_color_btn]:
            widget.config(state="normal")
        if hasattr(self, 'progress'):
            self.progress.pack_forget()
            del self.progress
        if hasattr(self, 'status_label'):
            self.status_label.pack_forget()
            del self.status_label

    def save_file(self):
        if not self.ascii_art:
            messagebox.showwarning("警告", "请先生成ASCII内容")
            return
        
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        if path:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(self.ascii_art)
                messagebox.showinfo("保存成功", "文件已保存")
            except Exception as e:
                messagebox.showerror("保存失败", str(e))
    
    # 以下为盲文转换相关方法
    def pixel_to_braille(self, pixel_block):
        """
        将2x4像素块转换为对应的盲文字符
        """
        braille_base = 0x2800
        braille_map = [
            (0, 0), (1, 0), (0, 1), (1, 1),  # 左列：点1-4
            (0, 2), (1, 2), (0, 3), (1, 3)   # 右列：点5-8
        ]
        value = 0
        for i, (x, y) in enumerate(braille_map):
            if pixel_block[y][x] > 128:  # 阈值设为128
                value |= (1 << i)
        return chr(braille_base + value)
    
    # 盲文转换相关方法
    def image_to_braille(self, width=100):
        """
        将图片转换为盲文ASCII艺术。
        参数 width 为输出盲文字符的宽度，每个盲文字符代表2x4的像素块。
        """
        img = Image.open(self.image_path).convert("L")
        aspect_ratio = img.height / img.width
        new_height = int(width * aspect_ratio * self.adj_scale.get())  # 调整高度因子改为1.0
        # 盲文转换需要将图片尺寸调整为 (width*2, new_height*4)
        img = img.resize((width * 2, new_height * 4), Image.LANCZOS)
        
        pixels = img.load()
        braille_art = []
        for y in range(0, img.height, 4):
            line = []
            for x in range(0, img.width, 2):
                block = [
                    [pixels[x + dx, y + dy] if (x + dx < img.width and y + dy < img.height) else 0
                     for dx in range(2)]
                    for dy in range(4)
                ]
                line.append(self.pixel_to_braille(block))
            braille_art.append("".join(line))
        return "\n".join(braille_art)

if __name__ == "__main__":
    root = tk.Tk()
    app = AsciiArtConverter(root)
    root.geometry("800x600")
    root.mainloop()
