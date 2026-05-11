import os
import threading
import tkinter as tk
from tkinter import filedialog, ttk, messagebox

from dfs_engine import DFSEngine
from fault_tolerance import FaultToleranceMonitor


BG_DARK = "#1e1e2e"
BG_PANEL = "#2a2a3e"
BG_CARD = "#313147"
ACCENT = "#7c6af7"
ACCENT2 = "#5db8fe"
GREEN = "#50fa7b"
RED = "#ff5555"
TEXT_MAIN = "#f8f8f2"
TEXT_DIM = "#6272a4"


class DFSApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Distributed File System with Fault Tolerance")
        self.geometry("860x580")
        self.configure(bg=BG_DARK)
        self.resizable(False, False)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Treeview",
            background=BG_DARK,
            fieldbackground=BG_DARK,
            foreground=TEXT_MAIN,
            bordercolor=BG_PANEL,
            borderwidth=0,
        )
        style.configure(
            "Treeview.Heading",
            background=BG_PANEL,
            foreground=TEXT_MAIN,
            relief="flat",
        )
        style.map(
            "Treeview",
            background=[("selected", ACCENT)],
            foreground=[("selected", TEXT_MAIN)],
        )

        self.engine = DFSEngine()
        self.monitor = FaultToleranceMonitor(on_failure_callback=self._on_node_failure)
        self.monitor.start()

        self._build_ui()
        self._refresh_all()
        self.after(3000, self._refresh_loop)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self):
        title_bar = tk.Frame(self, bg=ACCENT, height=48)
        title_bar.pack(fill="x")
        title_label = tk.Label(
            title_bar,
            text="Distributed File System  |  3 Nodes  |  Replication x2",
            bg=ACCENT,
            fg=TEXT_MAIN,
            font=("Segoe UI", 13, "bold"),
        )
        title_label.pack(pady=10)

        container = tk.Frame(self, bg=BG_DARK)
        container.pack(fill="both", expand=True, padx=10, pady=10)

        left_panel = tk.Frame(container, bg=BG_PANEL, width=300, height=500)
        left_panel.pack(side="left", fill="y")
        left_panel.pack_propagate(False)

        right_panel = tk.Frame(container, bg=BG_DARK)
        right_panel.pack(side="right", fill="both", expand=True)

        self._build_node_panel(left_panel)
        self._build_file_ops_panel(right_panel)
        self._build_files_panel(right_panel)
        self._build_log_panel(right_panel)

    def _build_node_panel(self, parent):
        header = tk.Label(
            parent,
            text="Node Status",
            bg=BG_PANEL,
            fg=ACCENT2,
            font=("Segoe UI", 11, "bold"),
        )
        header.pack(anchor="w", padx=12, pady=(12, 6))

        self.node_rows = []
        for i in range(3):
            row = tk.Frame(parent, bg=BG_CARD, height=60)
            row.pack(fill="x", padx=10, pady=6)
            row.pack_propagate(False)

            dot = tk.Canvas(row, width=14, height=14, bg=BG_CARD, highlightthickness=0)
            dot.create_oval(2, 2, 12, 12, fill=GREEN, outline=GREEN)
            dot.pack(side="left", padx=10)

            labels = tk.Frame(row, bg=BG_CARD)
            labels.pack(side="left", fill="both", expand=True)
            status = tk.Label(
                labels,
                text=f"Node {i + 1} - ONLINE",
                bg=BG_CARD,
                fg=TEXT_MAIN,
                font=("Segoe UI", 10, "bold"),
            )
            status.pack(anchor="w")
            detail = tk.Label(
                labels,
                text="0 chunks | 0 KB",
                bg=BG_CARD,
                fg=TEXT_DIM,
                font=("Segoe UI", 9),
            )
            detail.pack(anchor="w")

            self.node_rows.append({"dot": dot, "status": status, "detail": detail})

        self.health_label = tk.Label(
            parent,
            text="All nodes healthy",
            bg=BG_PANEL,
            fg=GREEN,
            font=("Segoe UI", 10, "bold"),
        )
        self.health_label.pack(anchor="w", padx=12, pady=(10, 12))

    def _build_file_ops_panel(self, parent):
        panel = tk.Frame(parent, bg=BG_PANEL, height=120)
        panel.pack(fill="x", padx=10, pady=(0, 10))
        panel.pack_propagate(False)

        header = tk.Label(
            panel,
            text="File Operations",
            bg=BG_PANEL,
            fg=ACCENT2,
            font=("Segoe UI", 11, "bold"),
        )
        header.pack(anchor="w", padx=12, pady=(10, 6))

        btn_row = tk.Frame(panel, bg=BG_PANEL)
        btn_row.pack(anchor="w", padx=12)

        upload_btn = tk.Button(
            btn_row,
            text="Upload File",
            bg=ACCENT,
            fg=TEXT_MAIN,
            activebackground=ACCENT,
            activeforeground=TEXT_MAIN,
            relief="flat",
            command=self._upload_clicked,
            width=14,
        )
        upload_btn.pack(side="left", padx=(0, 8))

        download_btn = tk.Button(
            btn_row,
            text="Download File",
            bg=ACCENT2,
            fg=TEXT_MAIN,
            activebackground=ACCENT2,
            activeforeground=TEXT_MAIN,
            relief="flat",
            command=self._download_clicked,
            width=14,
        )
        download_btn.pack(side="left")

        self.progress = ttk.Progressbar(panel, length=350, mode="determinate", maximum=100)
        self.progress.pack(anchor="w", padx=12, pady=(8, 0))

        self.status_label = tk.Label(
            panel,
            text="Idle",
            bg=BG_PANEL,
            fg=TEXT_DIM,
            font=("Segoe UI", 9),
        )
        self.status_label.pack(anchor="w", padx=12, pady=(4, 8))

    def _build_files_panel(self, parent):
        panel = tk.Frame(parent, bg=BG_PANEL, height=210)
        panel.pack(fill="x", padx=10, pady=(0, 10))
        panel.pack_propagate(False)

        header = tk.Label(
            panel,
            text="Stored Files",
            bg=BG_PANEL,
            fg=ACCENT2,
            font=("Segoe UI", 11, "bold"),
        )
        header.pack(anchor="w", padx=12, pady=(10, 6))

        columns = ("filename", "size", "chunks", "status")
        self.tree = ttk.Treeview(panel, columns=columns, show="headings", height=6)
        self.tree.heading("filename", text="Filename")
        self.tree.heading("size", text="Size")
        self.tree.heading("chunks", text="Chunks")
        self.tree.heading("status", text="Status")
        self.tree.column("filename", width=180, anchor="w")
        self.tree.column("size", width=80, anchor="center")
        self.tree.column("chunks", width=70, anchor="center")
        self.tree.column("status", width=90, anchor="center")
        self.tree.pack(fill="x", padx=12, pady=(0, 10))

    def _build_log_panel(self, parent):
        panel = tk.Frame(parent, bg=BG_PANEL, height=150)
        panel.pack(fill="x", padx=10, pady=(0, 10))
        panel.pack_propagate(False)

        header = tk.Label(
            panel,
            text="Event Log",
            bg=BG_PANEL,
            fg=ACCENT2,
            font=("Segoe UI", 11, "bold"),
        )
        header.pack(anchor="w", padx=12, pady=(10, 6))

        self.log_text = tk.Text(
            panel,
            height=6,
            bg=BG_DARK,
            fg=GREEN,
            font=("Consolas", 9),
            relief="flat",
        )
        self.log_text.pack(fill="both", expand=True, padx=12, pady=(0, 10))
        self.log_text.config(state="disabled")

    def _set_status(self, text: str, color: str = TEXT_DIM) -> None:
        self.status_label.config(text=text, fg=color)

    def _set_progress(self, value: int) -> None:
        self.progress["value"] = max(0, min(100, value))

    def _reset_progress_later(self) -> None:
        self.after(2000, lambda: self._set_progress(0))

    def _upload_clicked(self):
        file_path = filedialog.askopenfilename()
        if not file_path:
            return

        def worker():
            self.after(0, lambda: self._set_status("Uploading...", ACCENT2))
            self.after(0, lambda: self._set_progress(15))
            try:
                self.engine.upload_file(file_path, self.monitor.get_failed_nodes())
                self.monitor.log_event(f"Uploaded {os.path.basename(file_path)}")
                self.after(0, lambda: self._set_status("Upload complete", GREEN))
            except Exception as e:
                self.monitor.log_event(f"Upload failed: {e}")
                self.after(0, lambda: self._set_status("Upload failed", RED))
            finally:
                self.after(0, lambda: self._set_progress(100))
                self.after(0, self._reset_progress_later)
                self.after(0, self._refresh_all)

        threading.Thread(target=worker, daemon=True).start()

    def _download_clicked(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("Download", "Select a file from the list first.")
            return

        file_name = self.tree.item(selection[0], "values")[0]
        output_dir = filedialog.askdirectory()
        if not output_dir:
            return

        def worker():
            self.after(0, lambda: self._set_status("Downloading...", ACCENT2))
            self.after(0, lambda: self._set_progress(15))
            success = self.engine.download_file(
                file_name, output_dir, self.monitor.get_failed_nodes()
            )
            if success:
                self.monitor.log_event(f"Downloaded {file_name}")
                self.after(0, lambda: self._set_status("Download complete", GREEN))
            else:
                self.monitor.log_event(f"Download failed for {file_name}")
                self.after(0, lambda: self._set_status("Download failed", RED))
            self.after(0, lambda: self._set_progress(100))
            self.after(0, self._reset_progress_later)
            self.after(0, self._refresh_all)

        threading.Thread(target=worker, daemon=True).start()

    def _on_node_failure(self, node_id: int) -> None:
        moved = self.engine.rereplicate(node_id, self.monitor.get_failed_nodes())
        self.monitor.log_event(f"Re-replicated {moved} chunk(s) after node {node_id + 1} failure")
        self.after(0, self._refresh_all)

    def _refresh_all(self):
        failed = self.monitor.get_failed_nodes()
        stats = self.engine.get_node_stats()

        for i, row in enumerate(self.node_rows):
            alive = i not in failed
            dot_color = GREEN if alive else RED
            row["dot"].delete("all")
            row["dot"].create_oval(2, 2, 12, 12, fill=dot_color, outline=dot_color)
            state_text = "ONLINE" if alive else "OFFLINE"
            row["status"].config(text=f"Node {i + 1} - {state_text}")
            row["detail"].config(
                text=f'{stats[i]["chunk_count"]} chunks | {stats[i]["total_size_kb"]} KB'
            )

        if failed:
            self.health_label.config(
                text=f"{len(failed)} node(s) offline", fg=RED
            )
        else:
            self.health_label.config(text="All nodes healthy", fg=GREEN)

        self._refresh_files()
        self._refresh_log()

    def _refresh_files(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        failed = set(self.monitor.get_failed_nodes())
        metadata = self.engine.get_all_files()
        for filename, meta in metadata.items():
            status = "Available"
            for chunk in meta["chunks"]:
                accessible = False
                for node_id in chunk["nodes"]:
                    if node_id in failed:
                        continue
                    node_dir = os.path.join(self.engine.base_dir, self.engine.nodes[node_id])
                    chunk_path = os.path.join(node_dir, chunk["chunk_id"])
                    if os.path.exists(chunk_path):
                        accessible = True
                        break
                if not accessible:
                    status = "Degraded"
                    break

            self.tree.insert(
                "",
                "end",
                values=(
                    filename,
                    f'{int(meta["file_size"] / 1024)} KB',
                    meta["num_chunks"],
                    status,
                ),
            )

    def _refresh_log(self):
        log_entries = self.monitor.get_log()[-30:]
        self.log_text.config(state="normal")
        self.log_text.delete("1.0", "end")
        for entry in log_entries:
            self.log_text.insert("end", entry + "\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    def _refresh_loop(self):
        self._refresh_all()
        self.after(3000, self._refresh_loop)

    def _on_close(self):
        self.monitor.stop()
        self.destroy()


if __name__ == "__main__":
    app = DFSApp()
    app.mainloop()
