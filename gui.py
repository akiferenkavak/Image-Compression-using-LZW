import tkinter as tk
import os
from tkinter import filedialog, messagebox, scrolledtext
from PIL import Image, ImageTk
from project.LZW import LZWCoding
from project2.LZW import LZWCoding as LZWCoding2

class CompressionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Compression Tool")
        self.root.geometry("800x600")
        self.create_main_menu()

    def create_main_menu(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        label = tk.Label(self.root, text="Choose what to compress:", font=("Arial", 14))
        label.pack(pady=20)

        btn_text = tk.Button(self.root, text="Text", command=self.text_compression_menu, width=15, height=2)
        btn_text.pack(pady=10)

        btn_image = tk.Button(self.root, text="Image", command=self.image_compression_menu, width=15, height=2)
        btn_image.pack(pady=10)

    def text_compression_menu(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        label = tk.Label(self.root, text="Choose an action:", font=("Arial", 14))
        label.pack(pady=20)

        btn_select_txt = tk.Button(self.root, text="Select TXT File", command=self.select_txt_file, width=20, height=2)
        btn_select_txt.pack(pady=10)

        btn_select_bin = tk.Button(self.root, text="Select Compressed .bin File", command=self.select_bin_file, width=25, height=2)
        btn_select_bin.pack(pady=10)

        btn_back = tk.Button(self.root, text="Back to Main Menu", command=self.create_main_menu, width=20)
        btn_back.pack(pady=30)

    def select_txt_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            try:
                output_path = filedialog.asksaveasfilename(
                    defaultextension=".bin",
                    filetypes=[("Binary files", "*.bin")],
                    title="Save Compressed File As"
                )

                if output_path:
                    filename = os.path.splitext(os.path.basename(file_path))[0]
                    lzw = LZWCoding(filename, 'text', file_path, output_path)
                    compressed_path, compression_info = lzw.compress_text_file()

                    decompressed_path = os.path.splitext(output_path)[0] + "_decompressed.txt"
                    lzw.filepath = output_path
                    lzw.outputpath = decompressed_path
                    decompressed_file_path = lzw.decompress_text_file()

                    self.show_text_comparison(file_path, decompressed_file_path, compression_info)

            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {str(e)}")
                print(f"Error: {str(e)}")

    def show_text_comparison(self, original_path, decompressed_path, compression_info):
        for widget in self.root.winfo_children():
            widget.destroy()

        title_label = tk.Label(self.root, text="Text Compression Results", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)

        info_frame = tk.LabelFrame(self.root, text="Compression Statistics", font=("Arial", 12))
        info_frame.pack(padx=10, pady=10, fill=tk.X)

        for info in compression_info:
            info_label = tk.Label(info_frame, text=info, anchor="w")
            info_label.pack(padx=10, pady=2, fill=tk.X)

        files_frame = tk.Frame(self.root)
        files_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        original_frame = tk.LabelFrame(files_frame, text="Original File", font=("Arial", 12))
        original_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        decompressed_frame = tk.LabelFrame(files_frame, text="Decompressed File", font=("Arial", 12))
        decompressed_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

        original_text = scrolledtext.ScrolledText(original_frame, wrap=tk.WORD)
        original_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        decompressed_text = scrolledtext.ScrolledText(decompressed_frame, wrap=tk.WORD)
        decompressed_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        try:
            with open(original_path, 'r') as f:
                original_content = f.read()
                original_text.insert(tk.END, original_content)
                original_text.config(state=tk.DISABLED)

            with open(decompressed_path, 'r') as f:
                decompressed_content = f.read()
                decompressed_text.insert(tk.END, decompressed_content)
                decompressed_text.config(state=tk.DISABLED)

            if original_content == decompressed_content:
                status = "✓ Files match perfectly! Compression and decompression successful."
                status_color = "green"
            else:
                status = "⚠ Files do not match. There might be an issue with compression/decompression."
                status_color = "red"

            status_label = tk.Label(self.root, text=status, fg=status_color, font=("Arial", 12, "bold"))
            status_label.pack(pady=5)

        except Exception as e:
            messagebox.showerror("Error", f"Could not read files: {str(e)}")

        btn_back = tk.Button(self.root, text="Back to Main Menu", command=self.create_main_menu, width=20)
        btn_back.pack(pady=10)

    def select_bin_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Binary files", "*.bin")])
        if file_path:
            try:
                output_path = filedialog.asksaveasfilename(
                    defaultextension=".txt",
                    filetypes=[("Text files", "*.txt")],
                    title="Save Decompressed File As"
                )

                if output_path:
                    filename = os.path.splitext(os.path.basename(file_path))[0]
                    lzw = LZWCoding(filename, 'text', file_path, output_path)
                    lzw.decompress_text_file()

                    messagebox.showinfo("Success", f"File successfully decompressed to {output_path}")

            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def image_compression_menu(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        label = tk.Label(self.root, text="Choose Image Type:", font=("Arial", 14))
        label.pack(pady=20)

        btn_gray = tk.Button(self.root, text="Gray Scaled", command=lambda: self.image_options("gray"), width=15, height=2)
        btn_gray.pack(pady=10)

        btn_colored = tk.Button(self.root, text="Coloured", command=lambda: self.image_options("colored"), width=15, height=2)
        btn_colored.pack(pady=10)

        btn_back = tk.Button(self.root, text="Back to Main Menu", command=self.create_main_menu, width=20)
        btn_back.pack(pady=30)

    def image_options(self, mode):
            for widget in self.root.winfo_children():
                widget.destroy()

            label = tk.Label(self.root, text=f"Choose an option for {mode} image:", font=("Arial", 14))
            label.pack(pady=20)

            btn_diff = tk.Button(self.root, text="Difference Image", command=lambda: self.select_image(mode, "diff"), width=20, height=2)
            btn_diff.pack(pady=10)

            btn_gray_level = tk.Button(self.root, text="Gray Level", command=lambda: self.select_image(mode, "gray_level"), width=20, height=2)
            btn_gray_level.pack(pady=10)

            btn_back = tk.Button(self.root, text="Back", command=self.image_compression_menu, width=15)
            btn_back.pack(pady=30)

    def select_image(self, mode, option):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp")])
        if file_path:
            output_path = filedialog.asksaveasfilename(
                defaultextension=".bin",
                filetypes=[("Binary files", "*.bin")],
                title="Save Compressed File As"
            )

            if output_path:
                filename = os.path.splitext(os.path.basename(file_path))[0]

                try:
                    if mode == "gray":
                        lzw = LZWCoding2(filename, 'image', file_path, output_path)
                        compressed_path, compression_info = lzw.compress_image_file()
                        print("çalıştı")
                        print(f"Compressed Path: {compressed_path}, Compression Info: {compression_info}")

                        decompressed_path = os.path.splitext(output_path)[0] + "_decompressed.png"
                        lzw.filepath = output_path
                        lzw.outputpath = decompressed_path
                        decompressed_file_path = lzw.decompress_image_file()

                        self.show_image_comparison(file_path, decompressed_file_path, compression_info, mode)

                    elif mode == "colored":
                        lzw = LZWCoding2(filename, 'colored_image', file_path, output_path)
                        compressed_path, compression_info = lzw.compress_colored_image_file()

                        decompressed_path = os.path.splitext(output_path)[0] + "_decompressed.png"
                        lzw.filepath = output_path
                        lzw.outputpath = decompressed_path
                        decompressed_file_path = lzw.decompress_colored_image_file()

                        self.show_image_comparison(file_path, decompressed_file_path, compression_info, mode)

                except Exception as e:
                    messagebox.showerror("Error", f"An error occurred: {str(e)}")
                    print(f"Error: {str(e)}")

    def show_image_comparison(self, original_path, decompressed_path, compression_info, mode):
        for widget in self.root.winfo_children():
            widget.destroy()

        title_label = tk.Label(self.root, text="Image Compression Results", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)

        info_frame = tk.LabelFrame(self.root, text="Compression Statistics", font=("Arial", 12))
        info_frame.pack(padx=10, pady=10, fill=tk.X)

        for info in compression_info:
            info_label = tk.Label(info_frame, text=info, anchor="w")
            info_label.pack(padx=10, pady=2, fill=tk.X)

        files_frame = tk.Frame(self.root)
        files_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        original_frame = tk.LabelFrame(files_frame, text="Original Image", font=("Arial", 12))
        original_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        decompressed_frame = tk.LabelFrame(files_frame, text="Decompressed Image", font=("Arial", 12))
        decompressed_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

        try:
            if mode == "gray":
                original_image = Image.open(original_path).convert('L')
                decompressed_image = Image.open(decompressed_path).convert('L')
            else:
                original_image = Image.open(original_path).convert('RGB')
                decompressed_image = Image.open(decompressed_path).convert('RGB')

            original_image = original_image.resize((300, 300), Image.LANCZOS)
            original_image_tk = ImageTk.PhotoImage(original_image)

            original_image_label = tk.Label(original_frame, image=original_image_tk)
            original_image_label.image = original_image_tk
            original_image_label.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

            decompressed_image = decompressed_image.resize((300, 300), Image.LANCZOS)
            decompressed_image_tk = ImageTk.PhotoImage(decompressed_image)

            decompressed_image_label = tk.Label(decompressed_frame, image=decompressed_image_tk)
            decompressed_image_label.image = decompressed_image_tk
            decompressed_image_label.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

            if list(original_image.getdata()) == list(decompressed_image.getdata()):
                status = "✓ Images match perfectly! Compression and decompression successful."
                status_color = "green"
            else:
                status = "⚠ Images do not match. There might be an issue with compression/decompression."
                status_color = "red"

            status_label = tk.Label(self.root, text=status, fg=status_color, font=("Arial", 12, "bold"))
            status_label.pack(pady=5)

        except Exception as e:
            messagebox.showerror("Error", f"Could not read images: {str(e)}")
            print(f"Image error: {str(e)}")

        btn_back = tk.Button(self.root, text="Back to Main Menu", command=self.create_main_menu, width=20)
        btn_back.pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = CompressionApp(root)
    root.mainloop()