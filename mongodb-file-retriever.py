import os
import threading
from pymongo import MongoClient
import gridfs
from bson import ObjectId
import customtkinter as ctk
from tkinter import ttk, filedialog, messagebox, Menu

class DatabaseManager:
    def __init__(self, uri='mongodb://localhost:27017/'):
        self.uri = uri
        self.client = MongoClient(uri)
        self.update_database_list()

    def update_database_list(self):
        try:
            self.db_names = self.client.list_database_names()
        except Exception as e:
            self.db_names = []
            # Notify GUI about the error
            raise RuntimeError(f"Error updating database list: {e}")

    def get_collection_names(self, db_name):
        try:
            db = self.client[db_name]
            return db.list_collection_names()
        except Exception as e:
            # Notify GUI about the error
            raise RuntimeError(f"Error updating collection list: {e}")

    def update_uri(self, new_uri):
        try:
            self.client = MongoClient(new_uri)
            self.update_database_list()
            self.uri = new_uri
        except Exception as e:
            # Notify GUI about the error
            raise RuntimeError(f"Error updating URI: {e}")

class FileRetrieverUI:
    def __init__(self, root, db_manager):
        self.root = root
        self.db_manager = db_manager
        self.root.title("MongoDB File Retriever")
        self.root.geometry("800x600")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.create_widgets()
        self.initialize_db_and_collections()

    def create_widgets(self):
        # URI input
        uri_frame = ctk.CTkFrame(self.root)
        uri_frame.pack(pady=10, padx=20, fill="x")

        uri_label = ctk.CTkLabel(uri_frame, text="MongoDB URI:")
        uri_label.grid(row=0, column=0, padx=10, sticky="w")

        self.uri_var = ctk.StringVar(value='mongodb://localhost:27017/')
        self.uri_entry = ctk.CTkEntry(uri_frame, textvariable=self.uri_var, width=300)
        self.uri_entry.grid(row=0, column=1, padx=10, sticky="w")
        self.uri_entry.bind("<Return>", self.on_uri_change)  # Bind Enter key to update URI

        # Database selection
        db_frame = ctk.CTkFrame(self.root)
        db_frame.pack(pady=10, padx=20, fill="x")

        db_label = ctk.CTkLabel(db_frame, text="Select Database:")
        db_label.grid(row=0, column=0, padx=10, sticky="w")

        self.db_var = ctk.StringVar()
        self.db_combo = ctk.CTkComboBox(db_frame, variable=self.db_var, values=[], width=150, command=self.load_collections)
        self.db_combo.grid(row=0, column=1, padx=10, sticky="w")

        # Collection selection
        collection_frame = ctk.CTkFrame(self.root)
        collection_frame.pack(pady=10, padx=20, fill="x")

        collection_label = ctk.CTkLabel(collection_frame, text="Select Collection:")
        collection_label.grid(row=0, column=0, padx=10, sticky="w")

        self.collection_var = ctk.StringVar()
        self.collection_combo = ctk.CTkComboBox(collection_frame, variable=self.collection_var, width=150)
        self.collection_combo.grid(row=0, column=1, padx=10, sticky="w")

        # File ID input
        file_id_frame = ctk.CTkFrame(self.root)
        file_id_frame.pack(pady=10, padx=20, fill="x")

        file_id_label = ctk.CTkLabel(file_id_frame, text="Enter File ID:")
        file_id_label.grid(row=0, column=0, padx=10, sticky="w")

        self.file_id_entry = ctk.CTkEntry(file_id_frame, width=200)
        self.file_id_entry.grid(row=0, column=1, padx=10, sticky="w")

        # Output directory selection
        output_dir_frame = ctk.CTkFrame(self.root)
        output_dir_frame.pack(pady=10, padx=20, fill="x")

        output_dir_label = ctk.CTkLabel(output_dir_frame, text="Output Directory:")
        output_dir_label.grid(row=0, column=0, padx=10, sticky="w")

        self.output_dir_var = ctk.StringVar()
        self.output_dir_entry = ctk.CTkEntry(output_dir_frame, textvariable=self.output_dir_var, width=200)
        self.output_dir_entry.grid(row=0, column=1, padx=10, sticky="w")

        self.browse_button = ctk.CTkButton(output_dir_frame, text="Browse", command=self.browse_output_directory, width=80)
        self.browse_button.grid(row=0, column=2, padx=10, sticky="w")

        # Retrieve button
        self.retrieve_button = ctk.CTkButton(self.root, text="Retrieve File(s)", command=self.retrieve_files)
        self.retrieve_button.pack(pady=10)

        # List files button
        self.list_files_button = ctk.CTkButton(self.root, text="List Files", command=self.list_files)
        self.list_files_button.pack(pady=10)

        # Treeview for displaying file list and metadata
        self.tree_frame = ctk.CTkFrame(self.root)
        self.tree_frame.pack(pady=10, padx=20, fill="both", expand=True)

        style = ttk.Style()
        style.configure("Treeview", background="gray15", foreground="white", fieldbackground="gray15", rowheight=25)
        style.map('Treeview', background=[('selected', 'gray25')])

        self.tree = ttk.Treeview(self.tree_frame, columns=("Select", "File ID", "Filename", "Size (KB)", "Tag"), show="headings", selectmode="extended")
        self.tree.heading("Select", text="Select")
        self.tree.heading("File ID", text="File ID")
        self.tree.heading("Filename", text="Filename")
        self.tree.heading("Size (KB)", text="Size (KB)")
        self.tree.heading("Tag", text="Tag")
        self.tree.column("Select", width=50)
        self.tree.pack(fill="both", expand=True)

        # Status bar for total and selected items
        self.status_bar = ctk.CTkLabel(self.root, text="Total items: 0 | Selected items: 0")
        self.status_bar.pack(side="bottom", fill="x")

        # Bind right-click event to show context menu
        self.tree.bind("<Button-3>", self.show_tree_menu)
        # Bind left-click event to toggle checkboxes
        self.tree.bind("<Button-1>", self.toggle_checkbox, add="+")
        # Bind selection event to update status bar
        self.tree.bind("<<TreeviewSelect>>", self.update_status_bar)

        # Create right-click context menu for copying
        self.tree_menu = Menu(self.root, tearoff=0)
        self.tree_menu.add_command(label="Copy File ID", command=self.copy_file_id)
        self.tree_menu.add_command(label="Copy Filename", command=self.copy_filename)

    def initialize_db_and_collections(self):
        """ Initialize database and collection lists based on the current URI. """
        self.update_database_list()

    def update_database_list(self):
        """ Asynchronously update the database and collection lists. """
        threading.Thread(target=self._update_database_list).start()

    def _update_database_list(self):
        """ Update the database list on a separate thread. """
        try:
            self.db_manager.update_database_list()
            databases = self.db_manager.db_names
            self.root.after(0, self._populate_databases, databases)
        except RuntimeError as e:
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))

    def _populate_databases(self, databases):
        """ Populate database drop-down list and reset default value. """
        self.db_combo.configure(values=databases)
        self.db_var.set("")  # Reset database selection

        # Clear the collection list as the database selection is reset
        self.collection_combo.configure(values=[])
        self.collection_var.set("")

    def on_uri_change(self, event=None):
        """ Handle URI changes when Enter key is pressed. """
        new_uri = self.uri_var.get()
        try:
            self.db_manager.update_uri(new_uri)
            self.update_database_list()
        except RuntimeError as e:
            messagebox.showerror("Error", f"Failed to connect to the URI: {e}")

    def load_collections(self, event=None):
        """ Load collections based on the selected database. """
        db_name = self.db_var.get()
        try:
            collections = self.db_manager.get_collection_names(db_name)
            self.collection_combo.configure(values=collections)
            self.collection_var.set("")  # Reset collection selection
        except RuntimeError as e:
            messagebox.showerror("Error", f"Failed to load collections: {e}")

    def browse_output_directory(self):
        """ Open file dialog to select output directory. """
        directory = filedialog.askdirectory()
        if directory:
            self.output_dir_var.set(directory)

    def retrieve_files(self):
        """ Retrieve selected files from MongoDB and save to output directory. """
        db_name = self.db_var.get()
        collection_name = self.collection_var.get()
        output_dir = self.output_dir_var.get()

        selected_items = self.tree.get_children()  # Get all items since there's no checkbox to select
        if not selected_items:
            messagebox.showerror("Error", "No files to retrieve.")
            return

        try:
            db = self.db_manager.client[db_name]
            fs = gridfs.GridFS(db, collection=collection_name)
            os.makedirs(output_dir, exist_ok=True)

            for item in selected_items:
                file_id = self.tree.item(item)["values"][1]
                file_document = fs.find_one({"_id": ObjectId(file_id)})
                if not file_document:
                    messagebox.showerror("Error", f"No file found with ID: {file_id}")
                    continue

                file_data = fs.get(ObjectId(file_id)).read()
                file_name = file_document.filename
                output_path = os.path.join(output_dir, file_name)

                with open(output_path, 'wb') as file:
                    file.write(file_data)

            messagebox.showinfo("Success", f"Selected files retrieved and saved to: {output_dir}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def list_files(self):
        """ List files in the selected database and collection. """
        db_name = self.db_var.get()
        collection_name = self.collection_var.get()

        if not all([db_name, collection_name]):
            messagebox.showerror("Error", "Please select both database and collection.")
            return

        try:
            db = self.db_manager.client[db_name]
            fs = gridfs.GridFS(db, collection=collection_name)
            self.tree.delete(*self.tree.get_children())  # Clear the treeview

            files_cursor = db[collection_name + ".files"].find({})
            for file in files_cursor:
                file_id = str(file["_id"])
                filename = file.get("filename", "N/A")
                length = file.get("length", 0)
                size_kb = round(length / 1024, 2)
                tag = file.get("tag", "N/A")
                self.tree.insert("", "end", values=("☐", file_id, filename, size_kb, tag))

            self.update_status_bar()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def show_tree_menu(self, event):
        """ Show context menu on right-click. """
        try:
            self.tree_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.tree_menu.grab_release()

    def toggle_checkbox(self, event):
        """ Toggle checkbox selection on left-click. """
        item = self.tree.identify_row(event.y)
        if item:
            current_value = self.tree.set(item, "Select")
            new_value = "✓" if current_value == "☐" else "☐"
            self.tree.set(item, "Select", new_value)
            self.update_status_bar()

    def copy_file_id(self):
        """ Copy file ID of the selected item to clipboard. """
        selected_item = self.tree.focus()
        if selected_item:
            file_id = self.tree.item(selected_item)["values"][1]
            self.root.clipboard_clear()
            self.root.clipboard_append(file_id)
            messagebox.showinfo("Copied", "File ID copied to clipboard.")

    def copy_filename(self):
        """ Copy filename of the selected item to clipboard. """
        selected_item = self.tree.focus()
        if selected_item:
            filename = self.tree.item(selected_item)["values"][2]
            self.root.clipboard_clear()
            self.root.clipboard_append(filename)
            messagebox.showinfo("Copied", "Filename copied to clipboard.")

    def update_status_bar(self, event=None):
        """ Update the status bar with the number of items and selected items. """
        total_items = len(self.tree.get_children())
        selected_items = len([item for item in self.tree.get_children() if self.tree.set(item, "Select") == "✓"])
        total_text = "item" if total_items == 1 else "items"
        selected_text = "item selected" if selected_items == 1 else "items selected"
        self.status_bar.configure(text=f"{total_items} {total_text}    {selected_items} {selected_text}")

if __name__ == "__main__":
    root = ctk.CTk()
    db_manager = DatabaseManager()
    app = FileRetrieverUI(root, db_manager)
    root.mainloop()
