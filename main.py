import json
import os
import random
import string
import tkinter as tk
from tkinter import messagebox, ttk

DATA_FILE = "passwords.json"


def load_vault():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}


def save_vault(vault):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(vault, f, indent=4, ensure_ascii=False)


class PasswordManagerApp:

    def __init__(self, root):
        self.root = root
        self.root.title("PassGuard - Générateur de Mots de Passe")
        self.root.geometry("500x480")
        self.root.resizable(False, False)

        self.vault = load_vault()

        # Section Génération
        gen_frame = ttk.LabelFrame(self.root, text="Générateur", padding=10)
        gen_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(gen_frame, text="Service / Application:").grid(
            row=0, column=0, sticky="w", padx=5, pady=5
        )
        self.service_entry = ttk.Entry(gen_frame, width=25)
        self.service_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(gen_frame, text="Longueur:").grid(
            row=1, column=0, sticky="w", padx=5, pady=5
        )
        self.length_spinbox = ttk.Spinbox(gen_frame, from_=8, to=32, width=5)
        self.length_spinbox.set(14)
        self.length_spinbox.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        self.symbols_var = tk.BooleanVar(value=True)
        self.symbols_check = ttk.Checkbutton(
            gen_frame, text="Inclure des symboles (!@#$)", variable=self.symbols_var
        )
        self.symbols_check.grid(
            row=2, column=0, columnspan=2, sticky="w", padx=5, pady=2
        )

        generate_btn = ttk.Button(
            gen_frame, text="Générer & Enregistrer", command=self.generate_password
        )
        generate_btn.grid(
            row=3, column=0, columnspan=2, pady=10, sticky="ew"
        )

        ttk.Label(gen_frame, text="Mot de passe généré:").grid(
            row=4, column=0, sticky="w", padx=5, pady=5
        )
        self.password_entry = ttk.Entry(gen_frame, width=25)
        self.password_entry.grid(row=4, column=1, padx=5, pady=5)

        copy_btn = ttk.Button(
            gen_frame, text="Copier", command=self.copy_to_clipboard
        )
        copy_btn.grid(row=4, column=2, padx=5, pady=5)

        # Section Coffre-fort
        vault_frame = ttk.LabelFrame(
            self.root, text="Mots de Passe Enregistrés", padding=10
        )
        vault_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("service", "password")
        self.tree = ttk.Treeview(
            vault_frame, columns=columns, show="headings", height=6
        )
        self.tree.heading("service", text="Service")
        self.tree.heading("password", text="Mot de passe")

        self.tree.column("service", width=200)
        self.tree.column("password", width=220)
        self.tree.pack(fill="both", expand=True)

        delete_btn = ttk.Button(
            vault_frame, text="Supprimer l'entrée", command=self.delete_entry
        )
        delete_btn.pack(anchor="e", pady=5)

        self.refresh_vault()

    def generate_password(self):
        service = self.service_entry.get().strip()
        if not service:
            messagebox.showwarning(
                "Champ manquant", "Entrez le nom du service."
            )
            return

        length = int(self.length_spinbox.get())
        chars = string.ascii_letters + string.digits
        if self.symbols_var.get():
            chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"

        password = "".join(random.choice(chars) for _ in range(length))

        self.password_entry.delete(0, tk.END)
        self.password_entry.insert(0, password)

        self.vault[service] = password
        save_vault(self.vault)
        self.refresh_vault()

    def copy_to_clipboard(self):
        pwd = self.password_entry.get()
        if pwd:
            self.root.clipboard_clear()
            self.root.clipboard_append(pwd)
            messagebox.showinfo("Copié", "Mot de passe copié dans le presse-papier !")

    def delete_entry(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showinfo("Information", "Sélectionnez un service à supprimer.")
            return

        service = self.tree.item(selected_item[0])["values"][0]
        if service in self.vault:
            del self.vault[service]
            save_vault(self.vault)
            self.refresh_vault()

    def refresh_vault(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for service, pwd in self.vault.items():
            self.tree.insert("", tk.END, values=(service, pwd))


if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordManagerApp(root)
    root.mainloop()
