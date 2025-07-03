#!/usr/bin/env python3
"""
Book Highlights GUI

A simple GUI to tie together summarization and flashcard creation.
"""

import tkinter as tk
from tkinter import ttk
from helpers.config_helper import load_config, save_config, ensure_save_directory
from tkinter import messagebox, filedialog
import threading
from helpers.amazon_helper import KindleHighlightsExtractor
from helpers.llm_helper import LLMSummarizer
from helpers.markdown_helper import save_comprehensive_markdown
import os
import json
import re
import requests
from pathlib import Path
from typing import List, Dict, Optional
from helpers.models import Book, Highlight
from helpers.anki_helper import AnkiFlashcardCreator

class BookHighlightsApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Book Highlights Toolkit")
        self.geometry("500x500")
        self.resizable(False, False)
        self.config_data = load_config()
        self._create_homepage()

    def _create_homepage(self):
        for widget in self.winfo_children():
            widget.destroy()

        title_label = ttk.Label(self, text="Book Highlights Toolkit", font=("Helvetica", 18, "bold"))
        title_label.pack(pady=(40, 20))

        btn_summarize = ttk.Button(self, text="Summarize Book", width=25, command=self._summarize_book_workflow)
        btn_summarize.pack(pady=10)

        btn_flashcard = ttk.Button(self, text="Create Flashcard", width=25, command=self._create_flashcard_workflow)
        btn_flashcard.pack(pady=10)

        btn_settings = ttk.Button(self, text="Settings", width=25, command=self._open_settings)
        btn_settings.pack(pady=10)

    def _summarize_book_workflow(self):
        for widget in self.winfo_children():
            widget.destroy()

        label = ttk.Label(self, text="Summarize Book Workflow", font=("Helvetica", 16, "bold"))
        label.pack(pady=(20, 10))

        instructions = ttk.Label(self, text="Step 1: Login to your Amazon account to access your Kindle books.", wraplength=400)
        instructions.pack(pady=(10, 20))

        btn_login = ttk.Button(self, text="Start Amazon Login", command=self._start_amazon_login)
        btn_login.pack(pady=10)

        btn_cancel = ttk.Button(self, text="Cancel", command=self._create_homepage)
        btn_cancel.pack(pady=10)

        self.progress_label = ttk.Label(self, text="")
        self.progress_label.pack(pady=10)

    def _start_amazon_login(self):
        self.progress_label.config(text="Launching browser for Amazon login...")
        self.update_idletasks()
        threading.Thread(target=self._amazon_login_thread, daemon=True).start()

    def _amazon_login_thread(self):
        try:
            self.extractor = KindleHighlightsExtractor()
            self.extractor.setup_driver()
            self.extractor.launch_amazon_notebook()
            logged_in = self.extractor.wait_for_login()
            if not logged_in:
                self._show_error("Login failed or timed out.")
                return
            self._show_book_selection()
        except Exception as e:
            self._show_error(f"Error during Amazon login: {e}")

    def _show_book_selection(self):
        def gui():
            for widget in self.winfo_children():
                widget.destroy()
            label = ttk.Label(self, text="Select Books to Summarize", font=("Helvetica", 16, "bold"))
            label.pack(pady=(20, 10))
            instructions = ttk.Label(self, text="Step 2: Select one or more books to summarize.", wraplength=400)
            instructions.pack(pady=(0, 10))
            # Fetch books
            books = self.extractor.get_available_books()
            if not books:
                ttk.Label(self, text="No books found.").pack(pady=20)
                ttk.Button(self, text="Back", command=self._create_homepage).pack(pady=10)
                return
            # Scrollable frame for book checkboxes
            frame = ttk.Frame(self)
            frame.pack(pady=10, padx=20, fill='both', expand=True)
            canvas = tk.Canvas(frame, height=250)
            scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)
            scrollable_frame.bind(
                "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            # Book checkboxes
            self.book_vars = []
            self.books = books
            for i, book in enumerate(books):
                var = tk.BooleanVar()
                cb = ttk.Checkbutton(scrollable_frame, text=f"{book.title} by {book.author}", variable=var)
                cb.pack(anchor='w', pady=2)
                self.book_vars.append(var)
            # Summarize button
            btn_summarize = ttk.Button(self, text="Summarize Selected", command=self._summarize_selected_books)
            btn_summarize.pack(pady=10)
            btn_cancel = ttk.Button(self, text="Cancel", command=self._create_homepage)
            btn_cancel.pack(pady=5)
            # Progress bar and label
            self.progress_label = ttk.Label(self, text="")
            self.progress_label.pack(pady=5)
            self.progress_bar = ttk.Progressbar(self, mode='determinate', length=300)
            self.progress_bar.pack(pady=5)
        self.after(0, gui)

    def _summarize_selected_books(self):
        selected_books = [book for book, var in zip(self.books, self.book_vars) if var.get()]
        if not selected_books:
            self.progress_label.config(text="Please select at least one book.")
            return
        self.progress_label.config(text="Starting summarization...")
        self.progress_bar['maximum'] = len(selected_books)
        self.progress_bar['value'] = 0
        self.update_idletasks()
        threading.Thread(target=self._summarize_books_thread, args=(selected_books,), daemon=True).start()

    def _summarize_books_thread(self, selected_books):
        try:
            summarizer = LLMSummarizer()
            for idx, book in enumerate(selected_books, 1):
                self._update_progress(f"Processing '{book.title}' ({idx}/{len(selected_books)})...", idx)
                self._update_progress(f"Extracting highlights for '{book.title}'...", idx)
                highlights = self.extractor.extract_highlights_from_book(book)
                if not highlights:
                    self._update_progress(f"No highlights found for '{book.title}'. Skipping.", idx)
                    continue
                self._update_progress(f"Summarizing '{book.title}'...", idx)
                summary_data = summarizer.summarize_highlights(highlights, book)
                save_comprehensive_markdown(book, highlights, summary_data, self.config_data['save_location'])
                if summary_data:
                    self._update_progress(f"Saved summary for '{book.title}'.", idx)
                else:
                    self._update_progress(f"Failed to summarize '{book.title}'.", idx)
            self._update_progress("Closing browser...", len(selected_books))
            if hasattr(self, 'extractor') and hasattr(self.extractor, 'driver'):
                self.extractor.driver.quit()
            self._update_progress("All selected books processed successfully!", len(selected_books))
            self.after(0, lambda: self._show_done_page())
        except Exception as e:
            if hasattr(self, 'extractor') and hasattr(self.extractor, 'driver'):
                try:
                    self.extractor.driver.quit()
                except:
                    pass
            self._show_error(f"Error during summarization: {e}")

    def _update_progress(self, msg, current_book=None):
        def gui():
            if hasattr(self, 'progress_label'):
                self.progress_label.config(text=msg)
            if hasattr(self, 'progress_bar') and current_book is not None:
                self.progress_bar['value'] = current_book
        self.after(0, gui)

    def _show_done_page(self):
        for widget in self.winfo_children():
            widget.destroy()
        label = ttk.Label(self, text="Summarization Complete!", font=("Helvetica", 16, "bold"))
        label.pack(pady=(40, 20))
        ttk.Button(self, text="Back to Home", command=self._create_homepage).pack(pady=20)

    def _show_error(self, msg):
        def gui():
            for widget in self.winfo_children():
                widget.destroy()
            label = ttk.Label(self, text="Error", font=("Helvetica", 16, "bold"), foreground="red")
            label.pack(pady=(40, 10))
            ttk.Label(self, text=msg, wraplength=400, foreground="red").pack(pady=10)
            ttk.Button(self, text="Back to Home", command=self._create_homepage).pack(pady=20)
        self.after(0, gui)

    def _open_settings(self):
        for widget in self.winfo_children():
            widget.destroy()

        def choose_directory():
            dir_selected = filedialog.askdirectory(initialdir=self.config_data['save_location'])
            if dir_selected:
                entry_save_location.delete(0, tk.END)
                entry_save_location.insert(0, dir_selected)

        # Title
        title_label = ttk.Label(self, text="Settings", font=("Helvetica", 16, "bold"))
        title_label.pack(pady=(20, 10))

        # Save Location
        frame_save = ttk.Frame(self)
        frame_save.pack(pady=5, fill='x', padx=40)
        ttk.Label(frame_save, text="Save Location:").pack(side='left')
        entry_save_location = ttk.Entry(frame_save, width=28)
        entry_save_location.pack(side='left', padx=(5, 0))
        entry_save_location.insert(0, self.config_data['save_location'])
        btn_browse = ttk.Button(frame_save, text="Browse", command=choose_directory)
        btn_browse.pack(side='left', padx=(5, 0))

        # OpenAI API Key
        frame_key = ttk.Frame(self)
        frame_key.pack(pady=5, fill='x', padx=40)
        ttk.Label(frame_key, text="OpenAI API Key:").pack(side='left')
        entry_api_key = ttk.Entry(frame_key, width=32, show='*')
        entry_api_key.pack(side='left', padx=(5, 0))
        entry_api_key.insert(0, self.config_data['openai_api_key'])

        # OpenAI Model
        frame_model = ttk.Frame(self)
        frame_model.pack(pady=5, fill='x', padx=40)
        ttk.Label(frame_model, text="OpenAI Model:").pack(side='left')
        entry_model = ttk.Entry(frame_model, width=32)
        entry_model.pack(side='left', padx=(5, 0))
        entry_model.insert(0, self.config_data['openai_model'])

        # Save and Cancel buttons
        frame_buttons = ttk.Frame(self)
        frame_buttons.pack(pady=20)
        def save_settings():
            self.config_data['save_location'] = entry_save_location.get().strip()
            self.config_data['openai_api_key'] = entry_api_key.get().strip()
            self.config_data['openai_model'] = entry_model.get().strip()
            save_config(self.config_data)
            messagebox.showinfo("Settings Saved", "Settings have been saved successfully.")
            self._create_homepage()
        btn_save = ttk.Button(frame_buttons, text="Save", command=save_settings)
        btn_save.pack(side='left', padx=10)
        btn_cancel = ttk.Button(frame_buttons, text="Cancel", command=self._create_homepage)
        btn_cancel.pack(side='left', padx=10)

    def _create_flashcard_workflow(self):
        for widget in self.winfo_children():
            widget.destroy()

        label = ttk.Label(self, text="Create Anki Flashcards", font=("Helvetica", 16, "bold"))
        label.pack(pady=(20, 10))

        instructions = ttk.Label(self, text="Select one or more summarized books to create Anki flashcards.", wraplength=400)
        instructions.pack(pady=(10, 20))

        # Use AnkiFlashcardCreator to find markdown files
        self.anki_creator = AnkiFlashcardCreator()
        md_files = self.anki_creator.find_markdown_files()
        if not md_files:
            ttk.Label(self, text="No summarized books found.", foreground="red").pack(pady=20)
            ttk.Label(self, text=f"Save directory: {self.config_data['save_location']}", font=("Helvetica", 10)).pack(pady=5)
            ttk.Button(self, text="Back to Home", command=self._create_homepage).pack(pady=20)
            return

        # Create scrollable frame for file selection
        frame = ttk.Frame(self)
        frame.pack(pady=10, padx=20, fill='both', expand=True)
        canvas = tk.Canvas(frame, height=250)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # File checkboxes
        self.file_vars = []
        self.md_files = md_files
        for i, file_path in enumerate(md_files):
            var = tk.BooleanVar()
            filename = file_path.name
            title = filename.replace('-complete.md', '').replace('_', ' ')
            cb = ttk.Checkbutton(scrollable_frame, text=title, variable=var)
            cb.pack(anchor='w', pady=2)
            self.file_vars.append(var)

        btn_create = ttk.Button(self, text="Create Flashcards", command=self._create_selected_flashcards)
        btn_create.pack(pady=10)
        btn_cancel = ttk.Button(self, text="Cancel", command=self._create_homepage)
        btn_cancel.pack(pady=5)

        self.progress_label = ttk.Label(self, text="")
        self.progress_label.pack(pady=5)
        self.progress_bar = ttk.Progressbar(self, mode='determinate', length=300)
        self.progress_bar.pack(pady=5)

    def _create_selected_flashcards(self):
        selected_files = [file_path for file_path, var in zip(self.md_files, self.file_vars) if var.get()]
        if not selected_files:
            self.progress_label.config(text="Please select at least one book.")
            return
        self.progress_label.config(text="Starting flashcard creation...")
        self.progress_bar['maximum'] = len(selected_files)
        self.progress_bar['value'] = 0
        self.update_idletasks()
        threading.Thread(target=self._create_flashcards_thread, args=(selected_files,), daemon=True).start()

    def _create_flashcards_thread(self, selected_files):
        try:
            # Use AnkiFlashcardCreator for all Anki operations
            creator = self.anki_creator
            self._update_progress("Testing AnkiConnect connection...", 0)
            if not creator.test_anki_connect():
                self._show_error("AnkiConnect is not available. Please make sure Anki is running and the AnkiConnect addon is installed.")
                return
            deck_name = creator.DEFAULT_DECK_NAME if hasattr(creator, 'DEFAULT_DECK_NAME') else "Kindle Highlights"
            self._update_progress("Creating Anki deck...", 0)
            if not creator.create_deck(deck_name):
                self._show_error("Failed to create Anki deck.")
                return
            for idx, file_path in enumerate(selected_files, 1):
                filename = file_path.name
                title = filename.replace('-complete.md', '').replace('_', ' ')
                self._update_progress(f"Processing '{title}' ({idx}/{len(selected_files)})...", idx)
                book_data = creator.parse_markdown_file(file_path)
                if not book_data:
                    self._update_progress(f"Failed to parse '{title}'. Skipping.", idx)
                    continue
                if creator.create_flashcards_from_book(book_data):
                    self._update_progress(f"Created flashcard for '{title}'.", idx)
                else:
                    self._update_progress(f"Failed to create flashcard for '{title}'.", idx)
            self._update_progress("All flashcards created successfully!", len(selected_files))
            self.after(0, lambda: self._show_flashcard_done_page())
        except Exception as e:
            self._show_error(f"Error during flashcard creation: {e}")

    def _show_flashcard_done_page(self):
        """Show completion page for flashcard creation."""
        for widget in self.winfo_children():
            widget.destroy()
        label = ttk.Label(self, text="Flashcards Created!", font=("Helvetica", 16, "bold"))
        label.pack(pady=(40, 20))
        ttk.Label(self, text="Your Anki flashcards have been created successfully.", wraplength=400).pack(pady=10)
        ttk.Label(self, text="Open Anki to review your new flashcards.", wraplength=400).pack(pady=10)
        ttk.Button(self, text="Back to Home", command=self._create_homepage).pack(pady=20)

if __name__ == "__main__":
    app = BookHighlightsApp()
    app.mainloop() 