import threading
import openpyxl
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import traceback
import pandas as pd
import logging
from setup import get_driver
from main import process_row


class Logger(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.textbox = tk.Text(self, width=130, height=50, state="disabled")
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.textbox.yview)
        self.textbox.config(yscrollcommand=self.scrollbar.set)
        self.textbox.tag_config("info")
        self.textbox.tag_config("error", foreground="red")
        self.textbox.pack(side="left", fill="y")
        self.scrollbar.pack(side="right", fill="y")

    def log_text(self, text: str, tag: str) -> None:
        self.textbox.config(state="normal")
        self.textbox.insert("end", f"{text}\n", tag)
        self.textbox.config(state="disabled")
        self.textbox.see(tk.END)

    def info(self, text: str) -> None:
        self.log_text(text, "info")

    def error(self, text: str) -> None:
        self.log_text(text, "error")


class TextHandler(logging.Handler):
    """A custom logging handler that sends log messages to a Tkinter Text widget."""

    def __init__(self, logger_widget):
        super().__init__()
        self.logger_widget = logger_widget

    def emit(self, record):
        msg = self.format(record)
        tag = "info" if record.levelno < logging.ERROR else "error"
        self.logger_widget.log_text(msg, tag)


class ExcelProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Fastpeoplesearch scraper")

        # Title
        self.title_label = tk.Label(root, text="Fastpeoplesearch scraper", font=("Arial", 24))
        self.title_label.pack(pady=10)

        # Input for source Excel file
        self.source_label = tk.Label(root, text="Select Source Excel File:")
        self.source_label.pack(pady=5)
        self.source_entry = tk.Entry(root, width=60)
        self.source_entry.pack(pady=5)
        self.source_button = tk.Button(root, text="Browse", command=self.browse_source_file)
        self.source_button.pack(pady=5)

        # Input for destination Excel file
        self.dest_label = tk.Label(root, text="Select Destination Excel File:")
        self.dest_label.pack(pady=5)
        self.dest_entry = tk.Entry(root, width=60)
        self.dest_entry.pack(pady=5)
        self.dest_button = tk.Button(root, text="Browse", command=self.browse_dest_file)
        self.dest_button.pack(pady=5)

        # Submit button
        self.submit_button = tk.Button(root, text="Submit", command=self.process_excel)
        self.submit_button.pack(pady=20)

        # Progress bar
        self.progress = ttk.Progressbar(root, orient='horizontal', length=800, mode='determinate')
        self.progress.pack(pady=10)

        # Progress label
        self.progress_label = tk.Label(root, text="")
        self.progress_label.pack(pady=5)

        # Logging area
        self.logger_frame = Logger(root)
        self.logger_frame.pack(pady=10)

        # Configure logger
        self.logger = logging.getLogger('ExcelProcessor')
        self.logger.setLevel(logging.DEBUG)

        # Create a file handler and set its level to DEBUG
        file_handler = logging.FileHandler('logs.log')
        file_handler.setLevel(logging.DEBUG)

        # Create a logging format
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        # Set the formatter for the handler
        file_handler.setFormatter(formatter)

        # Add the file handler to the logger
        self.logger.addHandler(file_handler)

        # Create a custom handler for displaying logs in the UI
        ui_handler = TextHandler(self.logger_frame)
        ui_handler.setLevel(logging.DEBUG)
        ui_handler.setFormatter(formatter)
        self.logger.addHandler(ui_handler)

    def browse_source_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
        if file_path:
            self.source_entry.delete(0, tk.END)
            self.source_entry.insert(0, file_path)

    def browse_dest_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx *.xls")])
        if file_path:
            self.dest_entry.delete(0, tk.END)
            self.dest_entry.insert(0, file_path)

    def process_excel(self):
        source_file = self.source_entry.get()
        dest_file = self.dest_entry.get()

        if not source_file or not dest_file:
            messagebox.showerror("Error", "Please select both source and destination files")
            return

        threading.Thread(target=self.process_excel_thread, args=(source_file, dest_file)).start()

    def process_excel_thread(self, source_file, dest_file):
        try:
            self.submit_button.config(state='disabled')
            self.progress['value'] = 0
            self.progress_label.config(text="0% (0/0)")
            self.logger.info("Starting Excel processing...")

            # Read the source Excel file
            df = pd.read_excel(source_file)
            total_rows = len(df)
            self.logger.info(f"Total rows to process: {total_rows}")
            df.columns = ["EMAIL"]
            with get_driver() as driver:
                for index, row in df.iloc[299:].iterrows():
                    df = process_row(row, dest_file, driver, self.logger)
                    def show_try_again_popup():
                        result = messagebox.askretrycancel("Error", "Updating excel could not be possible. Please close the file if you are viewing")
                        return result

                    while True:
                        try:
                            df.to_excel(dest_file, index=False)
                            break
                        except:
                            if not show_try_again_popup():
                                continue
                    progress_percentage = (index + 1) / total_rows * 100
                    self.progress['value'] = progress_percentage
                    self.progress_label.config(text=f"{progress_percentage:.2f}% ({index + 1}/{total_rows})")
                    self.root.update_idletasks()

            self.logger.info("Excel processing completed.")
            messagebox.showinfo("Info", "Excel processing completed successfully.")
        except Exception as e:
            self.logger.error("Error occurred: %s", str(e))
            self.logger.error(traceback.format_exc())
            messagebox.showerror("Error", str(e))
        finally:
            self.submit_button.config(state='normal')
            self.progress['value'] = 100
            self.progress_label.config(text=f"100% ({total_rows}/{total_rows})")
            self.root.quit()  # Close the program after completion


if __name__ == "__main__":
    root = tk.Tk()
    app = ExcelProcessorApp(root)
    root.mainloop()
