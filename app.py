from __future__ import annotations

import argparse
import os
import platform
import queue
import subprocess
import sys
import threading
import traceback
from pathlib import Path
from typing import Callable, Dict

import fitz
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

APP_VERSION = "1.1.0"
DEFAULT_DPI = 200
SUPPORTED_DPI = (150, 200, 300)

LANG_DISPLAY = {
    "zh": "中文",
    "en": "English",
    "ms": "Bahasa Melayu",
}
DISPLAY_TO_LANG = {value: key for key, value in LANG_DISPLAY.items()}

I18N: Dict[str, Dict[str, str]] = {
    "zh": {
        "title": "PDF Flatten 工具",
        "header": "PDF Flatten 工具",
        "subheader": "支持单个或批量导入 PDF，强力 flatten 后导出到新的文件或文件夹。",
        "language": "语言",
        "source_pdf": "原始 PDF",
        "output_pdf": "导出位置",
        "browse": "浏览 / 多选",
        "save_as": "选择保存位置",
        "dpi": "输出清晰度 (DPI)",
        "start": "开始 Flatten",
        "working": "处理中...",
        "ready": "就绪",
        "progress_wait": "等待开始",
        "progress_done": "完成",
        "note": "可单个处理，也可一次多选多个 PDF 批量处理。\n单个文件可另存为单个 PDF；多文件会输出到你选择的文件夹内。\n建议 200 DPI。150 DPI 文件较小；300 DPI 更清晰，但文件会更大。",
        "hint_source": "请选择一个或多个要 flatten 的 PDF 文件。",
        "hint_output": "单个文件可选择输出 PDF；多文件请选择输出文件夹。",
        "select_input_first": "请先选择原始 PDF。",
        "warn_title": "提示",
        "error_title": "错误",
        "done_title": "完成",
        "select_input": "请先选择一个或多个原始 PDF 文件。",
        "select_output": "请先选择导出 PDF 路径或导出文件夹。",
        "same_path": "导出路径不能与原始 PDF 相同，请选择新的文件名。",
        "file_exists": "目标文件已存在，是否覆盖？",
        "folder_exists_files": "输出文件夹内已有同名文件，是否继续并覆盖重名文件？",
        "start_status": "开始处理：{name}",
        "batch_start_status": "开始批量处理：共 {count} 个文件",
        "page_progress": "正在处理第 {current}/{total} 页",
        "file_progress": "正在处理文件 {current}/{total}：{name}",
        "file_page_progress": "文件 {file_current}/{file_total}：{name} | 第 {page_current}/{page_total} 页",
        "done_status": "处理完成：{path}",
        "batch_done_status": "批量处理完成：输出文件夹 {path}",
        "done_message": "PDF flatten 已完成。\n\n输出文件：\n{path}",
        "batch_done_message": "批量 flatten 已完成。\n\n输出文件夹：\n{path}",
        "failed_status": "处理失败",
        "failed_message": "处理 PDF 时出错：\n\n{error}",
        "pick_input_title": "选择一个或多个原始 PDF",
        "pick_output_title": "选择导出 PDF",
        "pick_output_dir_title": "选择导出文件夹",
        "pdf_filter": "PDF 文件",
        "all_files": "所有文件",
        "default_output_suffix": "_flattened",
        "mode": "处理方式",
        "mode_value": "强力 Flatten（图像化，推荐）",
        "open_folder": "打开输出文件夹",
        "open_folder_failed": "无法打开输出文件夹。",
        "selected_files": "已选 {count} 个文件",
        "single_file": "单个文件",
        "batch_files": "批量文件",
        "cli_done": "已完成：{path}",
        "cli_progress": "第 {current}/{total} 页",
        "password_error": "暂不支持需要密码才能打开的 PDF。",
    },
    "en": {
        "title": "PDF Flatten Tool",
        "header": "PDF Flatten Tool",
        "subheader": "Import one or many PDFs, strongly flatten them, then export to a new file or folder.",
        "language": "Language",
        "source_pdf": "Source PDF",
        "output_pdf": "Export Location",
        "browse": "Browse / Multi-select",
        "save_as": "Choose Save Location",
        "dpi": "Output DPI",
        "start": "Start Flatten",
        "working": "Processing...",
        "ready": "Ready",
        "progress_wait": "Waiting to start",
        "progress_done": "Done",
        "note": "You can process one PDF or batch-process multiple PDFs at once.\nSingle-file mode saves one PDF; multi-file mode exports all results into a folder.\n200 DPI is recommended. 150 DPI gives a smaller file; 300 DPI is sharper but larger.",
        "hint_source": "Choose one or more PDFs to flatten.",
        "hint_output": "For one file, choose an output PDF. For multiple files, choose an output folder.",
        "select_input_first": "Please choose source PDFs first.",
        "warn_title": "Notice",
        "error_title": "Error",
        "done_title": "Completed",
        "select_input": "Please choose one or more source PDF files.",
        "select_output": "Please choose an output PDF path or output folder.",
        "same_path": "The output path cannot be the same as the source PDF. Please choose a different filename.",
        "file_exists": "The target file already exists. Overwrite it?",
        "folder_exists_files": "Some output files already exist in the selected folder. Continue and overwrite duplicates?",
        "start_status": "Started: {name}",
        "batch_start_status": "Batch started: {count} files",
        "page_progress": "Processing page {current}/{total}",
        "file_progress": "Processing file {current}/{total}: {name}",
        "file_page_progress": "File {file_current}/{file_total}: {name} | Page {page_current}/{page_total}",
        "done_status": "Completed: {path}",
        "batch_done_status": "Batch completed: output folder {path}",
        "done_message": "PDF flattening is complete.\n\nOutput file:\n{path}",
        "batch_done_message": "Batch PDF flattening is complete.\n\nOutput folder:\n{path}",
        "failed_status": "Processing failed",
        "failed_message": "An error occurred while processing the PDF:\n\n{error}",
        "pick_input_title": "Choose one or more source PDFs",
        "pick_output_title": "Choose Output PDF",
        "pick_output_dir_title": "Choose Output Folder",
        "pdf_filter": "PDF files",
        "all_files": "All files",
        "default_output_suffix": "_flattened",
        "mode": "Mode",
        "mode_value": "Strong Flatten (image-based, recommended)",
        "open_folder": "Open Output Folder",
        "open_folder_failed": "Unable to open the output folder.",
        "selected_files": "{count} files selected",
        "single_file": "Single file",
        "batch_files": "Batch files",
        "cli_done": "Completed: {path}",
        "cli_progress": "Page {current}/{total}",
        "password_error": "Password-protected PDFs are not supported in this version.",
    },
    "ms": {
        "title": "Alat Flatten PDF",
        "header": "Alat Flatten PDF",
        "subheader": "Import satu atau banyak PDF, flatten dengan kuat, kemudian eksport ke fail atau folder baharu.",
        "language": "Bahasa",
        "source_pdf": "PDF Asal",
        "output_pdf": "Lokasi Eksport",
        "browse": "Semak Imbas / Pilih Banyak",
        "save_as": "Pilih Lokasi Simpan",
        "dpi": "DPI Output",
        "start": "Mula Flatten",
        "working": "Sedang diproses...",
        "ready": "Sedia",
        "progress_wait": "Menunggu untuk bermula",
        "progress_done": "Selesai",
        "note": "Anda boleh proses satu PDF atau banyak PDF sekali gus.\nMod satu fail simpan satu PDF; mod berbilang fail eksport semua hasil ke dalam satu folder.\n200 DPI disyorkan. 150 DPI menghasilkan fail lebih kecil; 300 DPI lebih tajam tetapi lebih besar.",
        "hint_source": "Pilih satu atau lebih fail PDF untuk di-flatten.",
        "hint_output": "Untuk satu fail, pilih output PDF. Untuk banyak fail, pilih folder output.",
        "select_input_first": "Sila pilih PDF asal dahulu.",
        "warn_title": "Makluman",
        "error_title": "Ralat",
        "done_title": "Selesai",
        "select_input": "Sila pilih satu atau lebih fail PDF asal.",
        "select_output": "Sila pilih laluan PDF output atau folder output.",
        "same_path": "Laluan output tidak boleh sama dengan PDF asal. Sila pilih nama fail lain.",
        "file_exists": "Fail sasaran sudah wujud. Tulis ganti?",
        "folder_exists_files": "Ada fail output dengan nama sama dalam folder itu. Teruskan dan tulis ganti fail yang sama nama?",
        "start_status": "Mula: {name}",
        "batch_start_status": "Batch bermula: {count} fail",
        "page_progress": "Memproses halaman {current}/{total}",
        "file_progress": "Memproses fail {current}/{total}: {name}",
        "file_page_progress": "Fail {file_current}/{file_total}: {name} | Halaman {page_current}/{page_total}",
        "done_status": "Selesai: {path}",
        "batch_done_status": "Batch selesai: folder output {path}",
        "done_message": "Flatten PDF telah selesai.\n\nFail output:\n{path}",
        "batch_done_message": "Batch flatten PDF telah selesai.\n\nFolder output:\n{path}",
        "failed_status": "Pemprosesan gagal",
        "failed_message": "Ralat berlaku semasa memproses PDF:\n\n{error}",
        "pick_input_title": "Pilih satu atau lebih PDF asal",
        "pick_output_title": "Pilih PDF Output",
        "pick_output_dir_title": "Pilih Folder Output",
        "pdf_filter": "Fail PDF",
        "all_files": "Semua fail",
        "default_output_suffix": "_flattened",
        "mode": "Mod",
        "mode_value": "Strong Flatten (berasaskan imej, disyorkan)",
        "open_folder": "Buka Folder Output",
        "open_folder_failed": "Tidak dapat membuka folder output.",
        "selected_files": "{count} fail dipilih",
        "single_file": "Satu fail",
        "batch_files": "Fail berbilang",
        "cli_done": "Selesai: {path}",
        "cli_progress": "Halaman {current}/{total}",
        "password_error": "PDF yang memerlukan kata laluan belum disokong dalam versi ini.",
    },
}


def flatten_pdf(
    input_path: str,
    output_path: str,
    dpi: int = DEFAULT_DPI,
    progress_callback: Callable[[int, int], None] | None = None,
) -> None:
    if dpi <= 0:
        raise ValueError("DPI must be a positive integer.")

    src = None
    dst = None
    try:
        src = fitz.open(input_path)
        if src.needs_pass:
            raise ValueError("PASSWORD_REQUIRED")

        total = len(src)
        if total == 0:
            raise ValueError("The input PDF has no pages.")

        dst = fitz.open()
        matrix = fitz.Matrix(dpi / 72.0, dpi / 72.0)

        for index, page in enumerate(src, start=1):
            rect = page.rect
            pix = page.get_pixmap(matrix=matrix, alpha=False)
            new_page = dst.new_page(width=rect.width, height=rect.height)
            new_page.insert_image(new_page.rect, pixmap=pix, keep_proportion=False, overlay=True)
            pix = None

            if progress_callback is not None:
                progress_callback(index, total)

        metadata = src.metadata or {}
        metadata["producer"] = f"PDF Flatten Tool {APP_VERSION}"
        metadata["creator"] = "PDF Flatten Tool"
        dst.set_metadata(metadata)
        dst.save(output_path, deflate=True, garbage=4)
    finally:
        if dst is not None:
            dst.close()
        if src is not None:
            src.close()


class PDFFlattenApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.lang = tk.StringVar(value="zh")
        self.input_var = tk.StringVar()
        self.output_var = tk.StringVar()
        self.dpi_var = tk.StringVar(value=str(DEFAULT_DPI))
        self.status_var = tk.StringVar()
        self.progress_label_var = tk.StringVar()
        self.mode_var = tk.StringVar()
        self.queue: queue.Queue[tuple] = queue.Queue()
        self.processing = False
        self.last_output_path: str | None = None
        self.selected_inputs: list[str] = []

        self._build_style()
        self._build_ui()
        self._apply_language()
        self._set_app_icon()

    def t(self, key: str, **kwargs) -> str:
        text = I18N[self.lang.get()][key]
        return text.format(**kwargs) if kwargs else text

    def _build_style(self) -> None:
        self.root.title("PDF Flatten Tool")
        self.root.geometry("900x500")
        self.root.minsize(820, 460)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        style = ttk.Style()
        try:
            if "vista" in style.theme_names():
                style.theme_use("vista")
            elif "clam" in style.theme_names():
                style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("Card.TFrame", padding=18)
        style.configure("Header.TLabel", font=("Arial", 18, "bold"))
        style.configure("SubHeader.TLabel", font=("Arial", 10))
        style.configure("Hint.TLabel", font=("Arial", 9))
        style.configure("Primary.TButton", padding=(12, 8))

    def _build_ui(self) -> None:
        container = ttk.Frame(self.root, style="Card.TFrame")
        container.grid(row=0, column=0, sticky="nsew")
        for col in range(3):
            container.columnconfigure(col, weight=1 if col == 1 else 0)
        container.rowconfigure(8, weight=1)

        self.header_label = ttk.Label(container, style="Header.TLabel")
        self.header_label.grid(row=0, column=0, sticky="w")

        self.lang_label = ttk.Label(container)
        self.lang_label.grid(row=0, column=1, sticky="e", padx=(0, 8))

        self.lang_combo = ttk.Combobox(
            container,
            state="readonly",
            width=16,
            values=[LANG_DISPLAY["zh"], LANG_DISPLAY["en"], LANG_DISPLAY["ms"]],
        )
        self.lang_combo.grid(row=0, column=2, sticky="e")
        self.lang_combo.set(LANG_DISPLAY[self.lang.get()])
        self.lang_combo.bind("<<ComboboxSelected>>", self._on_language_changed)

        self.subheader_label = ttk.Label(container, style="SubHeader.TLabel")
        self.subheader_label.grid(row=1, column=0, columnspan=3, sticky="w", pady=(6, 16))

        self.source_label = ttk.Label(container)
        self.source_label.grid(row=2, column=0, sticky="w", pady=(2, 8))

        self.input_entry = ttk.Entry(container, textvariable=self.input_var)
        self.input_entry.grid(row=2, column=1, sticky="ew", padx=(10, 10), pady=(2, 8))

        self.browse_button = ttk.Button(container, command=self.choose_input)
        self.browse_button.grid(row=2, column=2, sticky="ew", pady=(2, 8))

        self.output_label = ttk.Label(container)
        self.output_label.grid(row=3, column=0, sticky="w", pady=(2, 8))

        self.output_entry = ttk.Entry(container, textvariable=self.output_var)
        self.output_entry.grid(row=3, column=1, sticky="ew", padx=(10, 10), pady=(2, 8))

        self.save_as_button = ttk.Button(container, command=self.choose_output)
        self.save_as_button.grid(row=3, column=2, sticky="ew", pady=(2, 8))

        options_frame = ttk.Frame(container)
        options_frame.grid(row=4, column=0, columnspan=3, sticky="ew", pady=(8, 10))
        options_frame.columnconfigure(1, weight=1)
        options_frame.columnconfigure(3, weight=1)

        self.dpi_label = ttk.Label(options_frame)
        self.dpi_label.grid(row=0, column=0, sticky="w")

        self.dpi_combo = ttk.Combobox(
            options_frame,
            textvariable=self.dpi_var,
            state="readonly",
            width=12,
            values=[str(value) for value in SUPPORTED_DPI],
        )
        self.dpi_combo.grid(row=0, column=1, sticky="w", padx=(10, 20))

        self.mode_label = ttk.Label(options_frame)
        self.mode_label.grid(row=0, column=2, sticky="w")

        self.mode_value_label = ttk.Label(options_frame, textvariable=self.mode_var)
        self.mode_value_label.grid(row=0, column=3, sticky="w", padx=(10, 0))

        action_frame = ttk.Frame(container)
        action_frame.grid(row=5, column=0, columnspan=3, sticky="ew", pady=(8, 10))
        action_frame.columnconfigure(0, weight=0)
        action_frame.columnconfigure(1, weight=1)
        action_frame.columnconfigure(2, weight=0)

        self.start_button = ttk.Button(action_frame, style="Primary.TButton", command=self.start_processing)
        self.start_button.grid(row=0, column=0, sticky="w")

        self.progress = ttk.Progressbar(action_frame, mode="determinate")
        self.progress.grid(row=0, column=1, sticky="ew", padx=(16, 16))

        self.open_folder_button = ttk.Button(action_frame, command=self.open_output_folder)
        self.open_folder_button.grid(row=0, column=2, sticky="e")

        self.progress_label = ttk.Label(container, textvariable=self.progress_label_var)
        self.progress_label.grid(row=6, column=0, columnspan=3, sticky="w", pady=(0, 8))

        self.status_label = ttk.Label(container, textvariable=self.status_var)
        self.status_label.grid(row=7, column=0, columnspan=3, sticky="w", pady=(0, 10))

        self.note_label = ttk.Label(container, style="Hint.TLabel", justify="left", wraplength=830)
        self.note_label.grid(row=8, column=0, columnspan=3, sticky="nw")

    def _apply_language(self) -> None:
        self.root.title(self.t("title"))
        self.header_label.configure(text=self.t("header"))
        self.subheader_label.configure(text=self.t("subheader"))
        self.lang_label.configure(text=self.t("language"))
        self.source_label.configure(text=self.t("source_pdf"))
        self.output_label.configure(text=self.t("output_pdf"))
        self.browse_button.configure(text=self.t("browse"))
        self.save_as_button.configure(text=self.t("save_as"))
        self.dpi_label.configure(text=self.t("dpi"))
        self.mode_label.configure(text=self.t("mode"))
        self.mode_var.set(self.t("mode_value"))
        self.start_button.configure(text=self.t("start"))
        self.open_folder_button.configure(text=self.t("open_folder"))
        self.note_label.configure(text=self.t("note"))

        if not self.selected_inputs:
            self.status_var.set(self.t("hint_source"))
        if not self.output_var.get():
            self.progress_label_var.set(self.t("progress_wait"))
        if not self.processing and self.last_output_path is None:
            self.progress_label_var.set(self.t("progress_wait"))

    def _set_app_icon(self) -> None:
        base = Path(__file__).resolve().parent
        icon_png = base / "app_icon.png"
        if not icon_png.exists():
            return
        try:
            self.icon_image = tk.PhotoImage(file=str(icon_png))
            self.root.iconphoto(True, self.icon_image)
        except Exception:
            pass

    def _on_language_changed(self, event: object | None = None) -> None:
        selected = self.lang_combo.get()
        lang_code = DISPLAY_TO_LANG.get(selected, "zh")
        self.lang.set(lang_code)
        self._apply_language()
        if self.selected_inputs:
            self._refresh_input_display()

    def choose_input(self) -> None:
        filetypes = [
            (self.t("pdf_filter"), "*.pdf"),
            (self.t("all_files"), "*.*"),
        ]
        paths = filedialog.askopenfilenames(title=self.t("pick_input_title"), filetypes=filetypes)
        if not paths:
            return
        self.selected_inputs = list(paths)
        self._refresh_input_display()

        if len(self.selected_inputs) == 1 and not self.output_var.get():
            self.output_var.set(self._suggest_output_path(self.selected_inputs[0]))
        elif len(self.selected_inputs) > 1:
            common_dir = str(Path(self.selected_inputs[0]).resolve().parent)
            if not self.output_var.get() or self.output_var.get().lower().endswith('.pdf'):
                self.output_var.set(common_dir)

    def _refresh_input_display(self) -> None:
        if not self.selected_inputs:
            self.input_var.set("")
            return
        if len(self.selected_inputs) == 1:
            path = self.selected_inputs[0]
            self.input_var.set(path)
            self.status_var.set(self.t("start_status", name=Path(path).name))
        else:
            first_name = Path(self.selected_inputs[0]).name
            self.input_var.set(f"{self.t('selected_files', count=len(self.selected_inputs))} | {first_name} ...")
            self.status_var.set(self.t("batch_start_status", count=len(self.selected_inputs)))

    def choose_output(self) -> None:
        count = len(self.selected_inputs)
        if count <= 1:
            source = self.selected_inputs[0] if self.selected_inputs else self.input_var.get().strip()
            initial = self._suggest_output_path(source) if source else "flattened.pdf"
            filetypes = [(self.t("pdf_filter"), "*.pdf")]
            path = filedialog.asksaveasfilename(
                title=self.t("pick_output_title"),
                defaultextension=".pdf",
                filetypes=filetypes,
                initialfile=Path(initial).name,
                initialdir=str(Path(initial).parent),
            )
        else:
            initial_dir = self.output_var.get().strip() or str(Path(self.selected_inputs[0]).resolve().parent)
            path = filedialog.askdirectory(
                title=self.t("pick_output_dir_title"),
                initialdir=initial_dir,
                mustexist=False,
            )
        if not path:
            return
        self.output_var.set(path)
        self.status_var.set(self.t("hint_output"))

    def _suggest_output_path(self, input_path: str) -> str:
        if not input_path:
            return "flattened.pdf"
        path = Path(input_path)
        suffix = self.t("default_output_suffix")
        return str(path.with_name(f"{path.stem}{suffix}.pdf"))

    def _build_batch_output_path(self, input_path: str, output_dir: str) -> str:
        path = Path(input_path)
        suffix = self.t("default_output_suffix")
        return str(Path(output_dir) / f"{path.stem}{suffix}.pdf")

    def start_processing(self) -> None:
        if self.processing:
            return

        if not self.selected_inputs:
            input_path_text = self.input_var.get().strip()
            if input_path_text:
                self.selected_inputs = [input_path_text]

        if not self.selected_inputs:
            messagebox.showwarning(self.t("warn_title"), self.t("select_input"))
            return

        output_path = self.output_var.get().strip()
        if not output_path:
            messagebox.showwarning(self.t("warn_title"), self.t("select_output"))
            return

        single_mode = len(self.selected_inputs) == 1

        if single_mode:
            input_path = self.selected_inputs[0]
            try:
                if Path(input_path).resolve() == Path(output_path).resolve():
                    messagebox.showwarning(self.t("warn_title"), self.t("same_path"))
                    return
            except Exception:
                pass

            if Path(output_path).exists():
                overwrite = messagebox.askyesno(self.t("warn_title"), self.t("file_exists"))
                if not overwrite:
                    return
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        else:
            out_dir = Path(output_path)
            out_dir.mkdir(parents=True, exist_ok=True)
            existing = [
                self._build_batch_output_path(src, output_path)
                for src in self.selected_inputs
                if Path(self._build_batch_output_path(src, output_path)).exists()
            ]
            if existing:
                overwrite = messagebox.askyesno(self.t("warn_title"), self.t("folder_exists_files"))
                if not overwrite:
                    return

        try:
            dpi = int(self.dpi_var.get())
        except ValueError:
            dpi = DEFAULT_DPI
            self.dpi_var.set(str(dpi))

        self.processing = True
        self.last_output_path = output_path
        self.progress.configure(value=0, maximum=100)
        if single_mode:
            self.status_var.set(self.t("start_status", name=Path(self.selected_inputs[0]).name))
        else:
            self.status_var.set(self.t("batch_start_status", count=len(self.selected_inputs)))
        self.progress_label_var.set(self.t("working"))
        self._set_controls_enabled(False)

        worker = threading.Thread(
            target=self._worker,
            args=(list(self.selected_inputs), output_path, dpi),
            daemon=True,
        )
        worker.start()
        self.root.after(100, self._poll_queue)

    def _worker(self, input_paths: list[str], output_target: str, dpi: int) -> None:
        try:
            total_files = len(input_paths)
            single_mode = total_files == 1

            for file_index, input_path in enumerate(input_paths, start=1):
                output_path = output_target if single_mode else self._build_batch_output_path(input_path, output_target)
                self.queue.put(("file", file_index, total_files, Path(input_path).name))
                flatten_pdf(
                    input_path,
                    output_path,
                    dpi,
                    progress_callback=lambda current, total, fi=file_index, ft=total_files, name=Path(input_path).name: self.queue.put((
                        "progress", fi, ft, name, current, total
                    )),
                )
            self.queue.put(("done", output_target, single_mode))
        except Exception as exc:
            trace = traceback.format_exc()
            self.queue.put(("error", exc, trace))

    def _poll_queue(self) -> None:
        try:
            while True:
                item = self.queue.get_nowait()
                kind = item[0]
                if kind == "file":
                    _, current, total, name = item
                    self.status_var.set(self.t("file_progress", current=current, total=total, name=name))
                elif kind == "progress":
                    _, file_current, file_total, name, page_current, page_total = item
                    overall = ((file_current - 1) + (page_current / page_total if page_total else 0)) / file_total * 100
                    self.progress.configure(value=overall)
                    if file_total == 1:
                        self.progress_label_var.set(self.t("page_progress", current=page_current, total=page_total))
                    else:
                        self.progress_label_var.set(
                            self.t(
                                "file_page_progress",
                                file_current=file_current,
                                file_total=file_total,
                                name=name,
                                page_current=page_current,
                                page_total=page_total,
                            )
                        )
                elif kind == "done":
                    _, output_target, single_mode = item
                    self.processing = False
                    self.progress.configure(value=100)
                    self.progress_label_var.set(self.t("progress_done"))
                    self._set_controls_enabled(True)
                    if single_mode:
                        self.status_var.set(self.t("done_status", path=output_target))
                        messagebox.showinfo(self.t("done_title"), self.t("done_message", path=output_target))
                    else:
                        self.status_var.set(self.t("batch_done_status", path=output_target))
                        messagebox.showinfo(self.t("done_title"), self.t("batch_done_message", path=output_target))
                elif kind == "error":
                    _, exc, trace = item
                    self.processing = False
                    self.progress.configure(value=0)
                    self.progress_label_var.set(self.t("failed_status"))
                    self.status_var.set(self.t("failed_status"))
                    self._set_controls_enabled(True)
                    error_text = self._human_error(exc)
                    print(trace, file=sys.stderr)
                    messagebox.showerror(self.t("error_title"), self.t("failed_message", error=error_text))
        except queue.Empty:
            pass

        if self.processing:
            self.root.after(100, self._poll_queue)

    def _human_error(self, exc: Exception) -> str:
        if str(exc) == "PASSWORD_REQUIRED":
            return self.t("password_error")
        return str(exc)

    def _set_controls_enabled(self, enabled: bool) -> None:
        state = "normal" if enabled else "disabled"
        combo_state = "readonly" if enabled else "disabled"

        self.input_entry.configure(state=state)
        self.output_entry.configure(state=state)
        self.browse_button.configure(state=state)
        self.save_as_button.configure(state=state)
        self.start_button.configure(state=state)
        self.open_folder_button.configure(state=state if self.last_output_path else "disabled")
        self.dpi_combo.configure(state=combo_state)
        self.lang_combo.configure(state=combo_state)

    def open_output_folder(self) -> None:
        target = self.last_output_path or self.output_var.get().strip()
        if not target:
            return
        path = Path(target).resolve()
        folder = path if path.is_dir() else path.parent
        try:
            if platform.system() == "Windows":
                os.startfile(str(folder))  # type: ignore[attr-defined]
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", str(folder)])
            else:
                subprocess.Popen(["xdg-open", str(folder)])
        except Exception:
            messagebox.showerror(self.t("error_title"), self.t("open_folder_failed"))



def run_gui() -> int:
    root = tk.Tk()
    app = PDFFlattenApp(root)
    app._set_controls_enabled(True)
    root.mainloop()
    return 0



def run_cli(input_path: str, output_path: str, dpi: int, lang: str = "en") -> int:
    if lang not in I18N:
        lang = "en"

    def progress(current: int, total: int) -> None:
        print(I18N[lang]["cli_progress"].format(current=current, total=total))

    try:
        flatten_pdf(input_path, output_path, dpi=dpi, progress_callback=progress)
    except Exception as exc:
        msg = I18N[lang]["password_error"] if str(exc) == "PASSWORD_REQUIRED" else str(exc)
        print(msg, file=sys.stderr)
        return 1

    print(I18N[lang]["cli_done"].format(path=output_path))
    return 0



def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Strong PDF flatten tool with GUI and CLI modes.")
    parser.add_argument("--cli", action="store_true", help="Run in command-line mode.")
    parser.add_argument("--input", help="Source PDF path for CLI mode.")
    parser.add_argument("--output", help="Output PDF path for CLI mode.")
    parser.add_argument("--dpi", type=int, default=DEFAULT_DPI, help="Output DPI. Default: 200")
    parser.add_argument("--lang", choices=["zh", "en", "ms"], default="en", help="CLI language.")
    return parser



def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.cli:
        if not args.input or not args.output:
            parser.error("--input and --output are required in --cli mode.")
        return run_cli(args.input, args.output, args.dpi, args.lang)

    return run_gui()


if __name__ == "__main__":
    raise SystemExit(main())
