import os
import shutil
import webbrowser
from tkinter import filedialog, messagebox, Toplevel, Label
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from PIL import Image
import json
import threading

class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.show)
        self.widget.bind("<Leave>", self.hide)

    def show(self, event=None):
        x = y = 0
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25

        self.tooltip = Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")

        label = Label(self.tooltip, text=self.text, background="#ffffff", relief="solid", borderwidth=1)
        label.pack(ipadx=1)

    def hide(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

class ImageSorterApp:
    def __init__(self, master):
        self.master = master
        master.title("Image Sorter Pro")
        master.geometry("660x780")
        master.resizable(False, False)


        self.style = ttk.Style("darkly")
        self.style.configure("TButton", font=("Helvetica", 10))
        self.style.configure("TLabel", font=("Helvetica", 10))
        self.style.configure("TCheckbutton", font=("Helvetica", 10))
        self.style.configure("TRadiobutton", font=("Helvetica", 10))

        self.create_widgets()
        self.operations_log = []

    def create_widgets(self):
        main_frame = ttk.Frame(self.master, padding="20 20 20 0")
        main_frame.pack(fill=BOTH, expand=YES)

        self.create_folder_inputs(main_frame)
        self.create_options(main_frame)
        self.create_buttons(main_frame)
        self.create_log_window(main_frame)
        self.create_progress_bar(main_frame)
        self.setup_support_button()

    def create_folder_inputs(self, parent):
        ttk.Label(parent, text="Input Folder:").grid(row=0, column=0, sticky=W, padx=5, pady=5)
        self.input_entry = ttk.Entry(parent, width=50)
        self.input_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(parent, text="Browse", command=self.browse_input).grid(row=0, column=2, padx=5, pady=5)

        ttk.Label(parent, text="Output Folder:").grid(row=1, column=0, sticky=W, padx=5, pady=5)
        self.output_entry = ttk.Entry(parent, width=50)
        self.output_entry.grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(parent, text="Browse", command=self.browse_output).grid(row=1, column=2, padx=5, pady=5)

    def create_options(self, parent):
        options_frame = ttk.LabelFrame(parent, text="Options", padding=10)
        options_frame.grid(row=2, column=0, columnspan=3, sticky=EW, padx=5, pady=10)

        self.include_subfolders = ttk.IntVar(value=0)
        ttk.Checkbutton(options_frame, text="Include subfolders", variable=self.include_subfolders).pack(anchor=W)

        self.min_size = ttk.IntVar(value=0)
        size_frame = ttk.Frame(options_frame)
        size_frame.pack(fill=X, expand=YES, pady=5)
        ttk.Label(size_frame, text="Minimum file size (KB):").pack(side=LEFT)
        ttk.Entry(size_frame, textvariable=self.min_size, width=10).pack(side=LEFT, padx=5)

        self.move_files = ttk.IntVar(value=1)
        ttk.Checkbutton(options_frame, text="Move files (uncheck to copy)", variable=self.move_files).pack(anchor=W)

        self.sort_by = ttk.StringVar(value="dimensions")
        ttk.Label(options_frame, text="Sort by:").pack(anchor=W, pady=(10, 0))
        ttk.Radiobutton(options_frame, text="Exact Dimensions", variable=self.sort_by, value="dimensions").pack(anchor=W)
        ttk.Radiobutton(options_frame, text="Dimension Ranges", variable=self.sort_by, value="ranges").pack(anchor=W)
        ttk.Radiobutton(options_frame, text="Aspect Ratio", variable=self.sort_by, value="ratio").pack(anchor=W)
        ttk.Radiobutton(options_frame, text="File Type", variable=self.sort_by, value="filetype").pack(anchor=W)

        ranges_frame = ttk.Frame(options_frame)
        ranges_frame.pack(fill=X, expand=YES, pady=5)
        ttk.Label(ranges_frame, text="Dimension ranges (pixels):").pack(anchor=W)
        self.ranges_entry = ttk.Entry(ranges_frame, width=50)
        self.ranges_entry.pack(fill=X, expand=YES, pady=5)
        self.ranges_entry.insert(0, "0-1000, 1001-2000, 2001-3000, 3001-4000, 4001-5000, 5001-6000, 6001-7000, 7001-8000, 8001-9000, 9001+")

        # Add width/height range option
        self.use_width = ttk.IntVar(value=1)
        ttk.Radiobutton(options_frame, text="Use Width for Ranges", variable=self.use_width, value=1).pack(anchor=W)
        ttk.Radiobutton(options_frame, text="Use Height for Ranges", variable=self.use_width, value=0).pack(anchor=W)

    def create_buttons(self, parent):
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=3, column=0, columnspan=3, pady=10)
        ttk.Button(button_frame, text="Sort Images", command=self.start_sorting).pack(side=LEFT, padx=5)
        ttk.Button(button_frame, text="Rollback", command=self.start_rollback).pack(side=LEFT, padx=5)
        ttk.Button(button_frame, text="Clear Log", command=self.clear_log).pack(side=LEFT, padx=5)

    def create_log_window(self, parent):
        self.log = ttk.Text(parent, height=10, width=80)
        self.log.grid(row=4, column=0, columnspan=3, padx=5, pady=5)

    def create_progress_bar(self, parent):
        self.progress = ttk.DoubleVar()
        self.progress_bar = ttk.Progressbar(parent, variable=self.progress, maximum=100)
        self.progress_bar.grid(row=5, column=0, columnspan=3, sticky=EW, padx=5, pady=5)

    def setup_support_button(self):
        support_button = ttk.Button(self.master, text="Support Me", style="Link.TButton",
                                    command=lambda: webbrowser.open("https://buymeacoffee.com/milky99"))
        support_button.pack(side=BOTTOM, anchor=SE, padx=10, pady=10)
        Tooltip(support_button, "Support the developer")

    def browse_input(self):
        folder = filedialog.askdirectory()
        self.input_entry.delete(0, ttk.END)
        self.input_entry.insert(0, folder)

    def browse_output(self):
        folder = filedialog.askdirectory()
        self.output_entry.delete(0, ttk.END)
        self.output_entry.insert(0, folder)

    def parse_ranges(self, ranges_str):
        ranges = []
        for r in ranges_str.split(','):
            r = r.strip()
            if '-' in r:
                start, end = map(int, r.split('-'))
                ranges.append((start, end))
            elif '+' in r:
                start = int(r.rstrip('+'))
                ranges.append((start, float('inf')))
        return sorted(ranges, key=lambda x: x[0])

    def get_range_folder(self, size, ranges):
        for start, end in ranges:
            if start <= size < end:
                return f"{start}-{end if end != float('inf') else '+'}"
        return "Other"

    def start_sorting(self):
        threading.Thread(target=self.sort_images, daemon=True).start()

    def sort_images(self):
        input_folder = self.input_entry.get()
        output_folder = self.output_entry.get()
        include_subfolders = self.include_subfolders.get()
        min_size = self.min_size.get() * 1024  # Convert KB to bytes
        move_files = self.move_files.get()
        sort_by = self.sort_by.get()
        use_width = self.use_width.get()

        if not input_folder or not output_folder:
            messagebox.showerror("Error", "Please select both input and output folders.")
            return

        self.operations_log = []
        self.progress.set(0)
        self.log.delete(1.0, ttk.END)

        total_files = sum([len(files) for _, _, files in os.walk(input_folder)])
        processed_files = 0

        ranges = self.parse_ranges(self.ranges_entry.get()) if sort_by == "ranges" else None

        for root, _, files in os.walk(input_folder):
            if not include_subfolders and root != input_folder:
                continue

            for file in files:
                file_path = os.path.join(root, file)
                if os.path.getsize(file_path) < min_size:
                    continue

                try:
                    with Image.open(file_path) as img:
                        width, height = img.size
                except IOError:
                    continue  # Not an image file

                if sort_by == "dimensions":
                    folder_name = f"{width}x{height}"
                elif sort_by == "ranges":
                    dimension = width if use_width else height
                    folder_name = self.get_range_folder(dimension, ranges)
                elif sort_by == "ratio":
                    ratio = width / height
                    folder_name = f"ratio_{ratio:.2f}"
                elif sort_by == "filetype":
                    folder_name = os.path.splitext(file)[1][1:].upper()  # Get file extension without the dot
                else:
                    folder_name = "Unsorted"

                output_path = os.path.join(output_folder, folder_name)
                os.makedirs(output_path, exist_ok=True)

                new_file_path = os.path.join(output_path, file)
                new_file_path = self.rename_image(new_file_path)

                if move_files:
                    shutil.move(file_path, new_file_path)
                    operation = "moved"
                else:
                    shutil.copy2(file_path, new_file_path)
                    operation = "copied"

                self.operations_log.append({"source": file_path, "destination": new_file_path, "operation": operation})
                self.log.insert(ttk.END, f"{operation.capitalize()}: {file} to {folder_name}\n")
                self.log.see(ttk.END)

                processed_files += 1
                self.progress.set((processed_files / total_files) * 100)
                self.master.update_idletasks()

        self.save_operations_log()
        messagebox.showinfo("Complete", "Image sorting completed.")

    def start_rollback(self):
        threading.Thread(target=self.rollback, daemon=True).start()

    def rollback(self):
        if not self.operations_log:
            try:
                with open("operations_log.json", "r") as f:
                    self.operations_log = json.load(f)
            except FileNotFoundError:
                messagebox.showerror("Error", "No operations to rollback.")
                return

        self.progress.set(0)
        self.log.delete(1.0, ttk.END)
        total_operations = len(self.operations_log)

        for i, operation in enumerate(reversed(self.operations_log)):
            source = operation["source"]
            destination = operation["destination"]
            if operation["operation"] == "moved":
                if os.path.exists(destination):
                    shutil.move(destination, source)
                    self.log.insert(ttk.END, f"Rolled back: {destination} to {source}\n")
            elif operation["operation"] == "copied":
                if os.path.exists(destination):
                    os.remove(destination)
                    self.log.insert(ttk.END, f"Deleted copy: {destination}\n")
            
            self.log.see(ttk.END)
            self.progress.set(((i + 1) / total_operations) * 100)
            self.master.update_idletasks()

        self.remove_empty_folders(self.output_entry.get())
        self.remove_empty_folders(self.input_entry.get())
        self.operations_log = []
        self.save_operations_log()
        messagebox.showinfo("Complete", "Rollback completed and empty folders removed from both input and output directories.")

    def remove_empty_folders(self, path):
        for root, dirs, files in os.walk(path, topdown=False):
            for dir in dirs:
                dir_path = os.path.join(root, dir)
                if not os.listdir(dir_path):
                    os.rmdir(dir_path)
                    self.log.insert(ttk.END, f"Removed empty folder: {dir_path}\n")
                    self.log.see(ttk.END)

    def rename_image(self, file_path):
        base, extension = os.path.splitext(file_path)
        counter = 1
        while os.path.exists(file_path):
            file_path = f"{base}_{counter}{extension}"
            counter += 1
        return file_path

    def save_operations_log(self):
        with open("operations_log.json", "w") as f:
            json.dump(self.operations_log, f)
    def clear_log(self):
        self.log.delete(1.0, ttk.END)

if __name__ == "__main__":
    root = ttk.Window()
    app = ImageSorterApp(root)
    root.mainloop()