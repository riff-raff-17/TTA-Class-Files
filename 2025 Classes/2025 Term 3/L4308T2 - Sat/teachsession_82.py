import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

import ollama
from pypdf import PdfReader


# -----------------------------
# Core functions (from your CLI)
# -----------------------------
def load_pdf_text(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        # page.extract_text() can be None for image-only pages
        page_text = page.extract_text() or ""
        text += page_text + "\n"
    return text.strip()


def chunk_text(text, chunk_size=1000):
    chunks = []
    words = text.split()
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks


def ask_ollama(context_chunks, question, model_name="llama3.2"):
    context = "\n".join(context_chunks)
    prompt = f"""
You are a helpful assistant. Use the following text to answer the question.

Text:
{context}

Question: {question}
Answer in a short, clear sentence.
"""
    response = ollama.chat(model=model_name, messages=[
        {"role": "user", "content": prompt}
    ])
    return response["message"]["content"]


# -----------------------------
# Tkinter GUI
# -----------------------------
class PDFQAGui(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Ask My PDF (Ollama) — Tkinter")
        self.geometry("900x650")

        # State
        self.pdf_path = None
        self.pdf_text = ""
        self.chunks = []
        self.model_var = tk.StringVar(value="llama3.2")

        # --- Top controls: file + model + chunk size ---
        top_frame = ttk.Frame(self, padding=10)
        top_frame.pack(fill="x")

        btn_load = ttk.Button(top_frame, text="Open PDF…", command=self.load_pdf)
        btn_load.grid(row=0, column=0, padx=(0, 8), pady=4, sticky="w")

        ttk.Label(top_frame, text="Model:").grid(row=0, column=1, sticky="e")
        model_entry = ttk.Entry(top_frame, textvariable=self.model_var, width=18)
        model_entry.grid(row=0, column=2, padx=(6, 16), sticky="w")

        ttk.Label(top_frame, text="Chunk size (words):").grid(row=0, column=3, sticky="e")
        self.chunk_size_var = tk.IntVar(value=1000)
        chunk_spin = ttk.Spinbox(top_frame, from_=200, to=3000, increment=100,
                                 textvariable=self.chunk_size_var, width=8, command=self.rechunk_if_loaded)
        chunk_spin.grid(row=0, column=4, padx=(6, 0), sticky="w")

        self.status_var = tk.StringVar(value="Open a PDF to begin.")
        status = ttk.Label(top_frame, textvariable=self.status_var, foreground="#555")
        status.grid(row=1, column=0, columnspan=5, sticky="w", pady=(6, 0))

        # --- Middle: info + preview ---
        mid = ttk.Frame(self, padding=(10, 0, 10, 10))
        mid.pack(fill="both", expand=True)

        info_frame = ttk.Frame(mid)
        info_frame.pack(fill="x")
        self.info_var = tk.StringVar(value="No document loaded.")
        ttk.Label(info_frame, textvariable=self.info_var).pack(side="left")

        preview_label = ttk.Label(mid, text="Document preview (first ~2000 chars):")
        preview_label.pack(anchor="w", pady=(8, 4))
        self.preview = ScrolledText(mid, height=10, wrap="word")
        self.preview.pack(fill="both", expand=False)

        # --- Q&A area ---
        qa_frame = ttk.LabelFrame(self, text="Ask a question", padding=10)
        qa_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.question_entry = ttk.Entry(qa_frame)
        self.question_entry.pack(fill="x", padx=(0, 0))
        self.question_entry.bind("<Return>", lambda e: self.on_ask())

        ask_btn = ttk.Button(qa_frame, text="Ask", command=self.on_ask)
        ask_btn.pack(anchor="e", pady=6)

        ttk.Label(qa_frame, text="Answer:").pack(anchor="w")
        self.answer_box = ScrolledText(qa_frame, height=10, wrap="word")
        self.answer_box.pack(fill="both", expand=True)

    # -------------- UI callbacks --------------
    def load_pdf(self):
        path = filedialog.askopenfilename(
            title="Choose a PDF",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if not path:
            return
        self.pdf_path = path
        self.status_var.set("Loading PDF…")
        self.update_idletasks()

        try:
            self.pdf_text = load_pdf_text(self.pdf_path)
            if not self.pdf_text:
                messagebox.showwarning("No text found",
                                       "This PDF has no extractable text (maybe it's scanned).")
                self.status_var.set("No extractable text found.")
                return

            self.rechunk()
            self.populate_preview()

            self.info_var.set(
                f"Loaded: {self.pdf_path}  |  Chunks: {len(self.chunks)}  |  Chunk size: {self.chunk_size_var.get()} words"
            )
            self.status_var.set("PDF loaded. Enter a question below.")
        except Exception as e:
            messagebox.showerror("Error loading PDF", str(e))
            self.status_var.set("Failed to load PDF.")

    def rechunk_if_loaded(self):
        if self.pdf_text:
            self.rechunk()
            self.info_var.set(
                f"Loaded: {self.pdf_path}  |  Chunks: {len(self.chunks)}  |  Chunk size: {self.chunk_size_var.get()} words"
            )

    def rechunk(self):
        size = int(self.chunk_size_var.get())
        if size < 50:
            size = 50
            self.chunk_size_var.set(50)
        self.chunks = chunk_text(self.pdf_text, size)

    def populate_preview(self):
        self.preview.delete("1.0", "end")
        preview_text = self.pdf_text[:2000]
        if len(self.pdf_text) > 2000:
            preview_text += "\n...\n(truncated)"
        self.preview.insert("1.0", preview_text)
        self.preview.edit_modified(False)

    def on_ask(self):
        q = self.question_entry.get().strip()
        if not q:
            messagebox.showinfo("Question required", "Please type a question.")
            return
        if not self.chunks:
            messagebox.showinfo("No document", "Load a PDF first.")
            return

        self.answer_box.delete("1.0", "end")
        self.answer_box.insert("1.0", "Thinking with Ollama…")
        self.status_var.set("Querying Ollama…")
        self.disable_inputs()

        # Run the LLM call in a separate thread so the UI stays responsive
        t = threading.Thread(target=self._ask_thread, args=(q, self.model_var.get()), daemon=True)
        t.start()

    def _ask_thread(self, question, model_name):
        try:
            answer = ask_ollama(self.chunks, question, model_name=model_name)
        except Exception as e:
            answer = f"Error: {e}"
        # Safely update UI from main thread
        self.after(0, self._display_answer, answer)

    def _display_answer(self, answer: str):
        self.answer_box.delete("1.0", "end")
        self.answer_box.insert("1.0", answer)
        self.status_var.set("Ready.")
        self.enable_inputs()

    def disable_inputs(self):
        self.question_entry.config(state="disabled")

    def enable_inputs(self):
        self.question_entry.config(state="normal")


if __name__ == "__main__":
    app = PDFQAGui()
    app.mainloop()
