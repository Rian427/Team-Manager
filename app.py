import tkinter as tk
from tkinter import ttk, messagebox
from database import (
    get_user_by_username, create_user, get_all_positions, create_position,
    get_positions_with_higher_level_than, get_manageable_users_by_user,
    update_user_position, delete_user
)
import datetime


class TeamManagerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Team Manager")
        self.geometry("900x600")
        self.resizable(False, False)
        self.current_user = None

        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)
        self.frames = {}

        for F in (LoginFrame, DashboardFrame, PositionCreateFrame, UserCreateFrame, ManageUsersFrame):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("LoginFrame")

    def show_frame(self, name):
        frame = self.frames[name]
        if hasattr(frame, "refresh"):
            frame.refresh()
        frame.tkraise()


# ---------- Tela de Login ----------
class LoginFrame(ttk.Frame):
    def __init__(self, parent, controller: TeamManagerApp):
        super().__init__(parent)
        self.controller = controller

        title = ttk.Label(self, text="Login - Team Manager", font=("Helvetica", 18))
        title.pack(pady=20)

        frm = ttk.Frame(self)
        frm.pack(pady=10)

        ttk.Label(frm, text="Usuário:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.username_entry = ttk.Entry(frm, width=30)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frm, text="Senha:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.password_entry = ttk.Entry(frm, width=30, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=15)
        ttk.Button(btn_frame, text="Entrar", command=self.login).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="Sair", command=controller.quit).grid(row=0, column=1, padx=5)

    def login(self):
        username = self.username_entry.get().strip()
        senha = self.password_entry.get().strip()
        if not username or not senha:
            messagebox.showwarning("Aviso", "Preencha usuário e senha.")
            return
        user = get_user_by_username(username)
        if not user or user['password'] != senha:
            messagebox.showerror("Erro", "Usuário ou senha inválidos.")
            return
        self.controller.current_user = user
        messagebox.showinfo("Sucesso", f"Bem-vindo, {user['name']} ({user['position_name']})")
        self.controller.show_frame("DashboardFrame")


# ---------- Tela Principal ----------
class DashboardFrame(ttk.Frame):
    def __init__(self, parent, controller: TeamManagerApp):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text="Dashboard", font=("Helvetica", 16)).pack(pady=10)
        self.info_label = ttk.Label(self, text="", font=("Helvetica", 11))
        self.info_label.pack(pady=5)

        btns = ttk.Frame(self)
        btns.pack(pady=15)
        ttk.Button(btns, text="Cadastrar/Contratar", command=lambda: controller.show_frame("UserCreateFrame")).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(btns, text="Criar Cargo", command=lambda: controller.show_frame("PositionCreateFrame")).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(btns, text="Gerenciar Funcionários", command=lambda: controller.show_frame("ManageUsersFrame")).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(btns, text="Logout", command=self.logout).grid(row=0, column=3, padx=5, pady=5)

    def refresh(self):
        user = self.controller.current_user
        if user:
            text = f"Logado como: {user['name']} | Cargo: {user['position_name']} (Nível {user['position_level']})"
        else:
            text = "Nenhum usuário logado."
        self.info_label.config(text=text)

    def logout(self):
        self.controller.current_user = None
        self.controller.show_frame("LoginFrame")


# ---------- Criação de Cargo ----------
class PositionCreateFrame(ttk.Frame):
    def __init__(self, parent, controller: TeamManagerApp):
        super().__init__(parent)
        self.controller = controller
        ttk.Label(self, text="Criar Cargo", font=("Helvetica", 14)).pack(pady=10)

        frm = ttk.Frame(self)
        frm.pack(pady=8)

        ttk.Label(frm, text="Nome do Cargo:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.name_entry = ttk.Entry(frm, width=30)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frm, text="Nível (menor = mais poder):").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.level_spin = ttk.Spinbox(frm, from_=1, to=100, width=8)
        self.level_spin.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        btns = ttk.Frame(self)
        btns.pack(pady=12)
        ttk.Button(btns, text="Criar", command=self.create_position).grid(row=0, column=0, padx=6)
        ttk.Button(btns, text="Voltar", command=lambda: controller.show_frame("DashboardFrame")).grid(row=0, column=1, padx=6)

    def refresh(self):
        self.name_entry.delete(0, tk.END)
        self.level_spin.set(1)

    def create_position(self):
        user = self.controller.current_user
        if not user:
            messagebox.showerror("Erro", "Faça login primeiro.")
            return
        name = self.name_entry.get().strip()
        try:
            level = int(self.level_spin.get())
        except:
            messagebox.showerror("Erro", "Nível inválido.")
            return
        if not name:
            messagebox.showwarning("Aviso", "Informe o nome do cargo.")
            return
        if level <= user['position_level']:
            messagebox.showerror("Erro", "Você só pode criar cargos de nível maior (menos poder) que o seu.")
            return
        try:
            create_position(name, level)
            messagebox.showinfo("Sucesso", f"Cargo '{name}' criado com nível {level}.")
            self.name_entry.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao criar cargo: {e}")


# ---------- Cadastro / Contratação ----------
class UserCreateFrame(ttk.Frame):
    def __init__(self, parent, controller: TeamManagerApp):
        super().__init__(parent)
        self.controller = controller
        ttk.Label(self, text="Cadastro / Contratação", font=("Helvetica", 14)).pack(pady=10)

        frm = ttk.Frame(self)
        frm.pack(pady=5)

        ttk.Label(frm, text="Nome completo:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.name_entry = ttk.Entry(frm, width=40)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frm, text="Usuário (username):").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.username_entry = ttk.Entry(frm, width=30)
        self.username_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(frm, text="Data de nascimento (YYYY-MM-DD):").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.dn_entry = ttk.Entry(frm, width=20)
        self.dn_entry.grid(row=2, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(frm, text="Senha:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        self.password_entry = ttk.Entry(frm, width=30, show="*")
        self.password_entry.grid(row=3, column=1, padx=5, pady=5)

        ttk.Label(frm, text="Cargo a ser atribuído:").grid(row=4, column=0, sticky="e", padx=5, pady=5)
        self.position_combo = ttk.Combobox(frm, state="readonly")
        self.position_combo.grid(row=4, column=1, padx=5, pady=5)

        btns = ttk.Frame(self)
        btns.pack(pady=10)
        ttk.Button(btns, text="Cadastrar", command=self.create_user).grid(row=0, column=0, padx=6)
        ttk.Button(btns, text="Voltar", command=lambda: controller.show_frame("DashboardFrame")).grid(row=0, column=1, padx=6)

    def refresh(self):
        self.name_entry.delete(0, tk.END)
        self.username_entry.delete(0, tk.END)
        self.dn_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        user = self.controller.current_user
        if not user:
            self.position_combo['values'] = []
            return
        positions = get_positions_with_higher_level_than(user['position_level'])
        if not positions:
            self.position_combo['values'] = []
        else:
            self.position_combo['values'] = [f"{p['id']} - {p['name']} (Niv {p['level']})" for p in positions]
            self.position_combo.current(0)

    def create_user(self):
        user = self.controller.current_user
        if not user:
            messagebox.showerror("Erro", "Faça login primeiro.")
            return
        name = self.name_entry.get().strip()
        username = self.username_entry.get().strip()
        dn = self.dn_entry.get().strip() or None
        password = self.password_entry.get().strip()
        pos_sel = self.position_combo.get()
        if not (name and username and password and pos_sel):
            messagebox.showwarning("Aviso", "Preencha todos os campos e escolha um cargo.")
            return
        position_id = int(pos_sel.split(" - ")[0])
        try:
            create_user(name, username, dn, position_id, password)
            messagebox.showinfo("Sucesso", "Usuário cadastrado com sucesso.")
            self.refresh()
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao cadastrar: {e}")


# ---------- Gestão de Funcionários ----------
class ManageUsersFrame(ttk.Frame):
    def __init__(self, parent, controller: TeamManagerApp):
        super().__init__(parent)
        self.controller = controller
        ttk.Label(self, text="Gestão de Funcionários", font=("Helvetica", 14)).pack(pady=8)

        top = ttk.Frame(self)
        top.pack(fill="x", pady=5)
        ttk.Button(top, text="Voltar", command=lambda: controller.show_frame("DashboardFrame")).pack(side="left", padx=6)
        ttk.Button(top, text="Atualizar", command=self.refresh).pack(side="left", padx=6)

        self.tree = ttk.Treeview(self, columns=("id", "name", "username", "position", "level"), show="headings", height=18)
        for col, hd in [("id", "ID"), ("name", "Nome"), ("username", "Usuário"), ("position", "Cargo"), ("level", "Nível")]:
            self.tree.heading(col, text=hd)
            self.tree.column(col, width=120 if col == "name" else 80)
        self.tree.pack(padx=10, pady=8)

        btns = ttk.Frame(self)
        btns.pack(pady=8)
        ttk.Button(btns, text="Promover", command=self.promote).grid(row=0, column=0, padx=6)
        ttk.Button(btns, text="Rebaixar", command=self.rebaixar).grid(row=0, column=1, padx=6)
        ttk.Button(btns, text="Demitir", command=self.fire).grid(row=0, column=2, padx=6)

    def refresh(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        user = self.controller.current_user
        if not user:
            return
        rows = get_manageable_users_by_user(user['id'])
        for u in rows:
            self.tree.insert("", tk.END, values=(u['id'], u['name'], u['username'], u['position_name'], u['position_level']))

    def _get_selected_user(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione um usuário na lista.")
            return None
        vals = self.tree.item(sel[0], "values")
        return {"id": int(vals[0]), "name": vals[1], "username": vals[2], "position_name": vals[3], "position_level": int(vals[4])}

    def _choose_position_dialog(self, positions):
        d = tk.Toplevel(self)
        d.title("Escolher cargo")
        ttk.Label(d, text="Escolha o cargo a atribuir:").pack(pady=8)
        combo = ttk.Combobox(d, values=[f"{p['id']} - {p['name']} (Niv {p['level']})" for p in positions], state="readonly", width=40)
        combo.pack(pady=6, padx=8)
        result = {"choice": None}

        def ok():
            result["choice"] = combo.get()
            d.destroy()

        def cancel():
            d.destroy()

        btnf = ttk.Frame(d)
        btnf.pack(pady=8)
        ttk.Button(btnf, text="OK", command=ok).pack(side="left", padx=6)
        ttk.Button(btnf, text="Cancelar", command=cancel).pack(side="left", padx=6)
        d.grab_set()
        self.wait_window(d)
        return result["choice"]

    def promote(self):
        sel = self._get_selected_user()
        if not sel:
            return
        me = self.controller.current_user
        positions = get_positions_with_higher_level_than(me['position_level'])
        candidate = [p for p in positions if p['level'] < sel['position_level']]
        if not candidate:
            messagebox.showinfo("Info", "Nenhum cargo disponível para promover esse colaborador com suas permissões.")
            return
        choice = self._choose_position_dialog(candidate)
        if not choice:
            return
        new_position_id = int(choice.split(" - ")[0])
        update_user_position(sel['id'], new_position_id)
        messagebox.showinfo("Sucesso", f"{sel['name']} foi promovido.")
        self.refresh()

    def rebaixar(self):
        sel = self._get_selected_user()
        if not sel:
            return
        me = self.controller.current_user
        positions = get_positions_with_higher_level_than(me['position_level'])
        candidate = [p for p in positions if p['level'] > sel['position_level']]
        if not candidate:
            messagebox.showinfo("Info", "Nenhum cargo disponível para rebaixamento com suas permissões.")
            return
        choice = self._choose_position_dialog(candidate)
        if not choice:
            return
        new_position_id = int(choice.split(" - ")[0])
        update_user_position(sel['id'], new_position_id)
        messagebox.showinfo("Sucesso", f"{sel['name']} foi rebaixado.")
        self.refresh()

    def fire(self):
        sel = self._get_selected_user()
        if not sel:
            return
        me = self.controller.current_user
        if sel['position_level'] <= me['position_level']:
            messagebox.showerror("Erro", "Você não tem permissão para demitir esse usuário.")
            return
        if messagebox.askyesno("Confirmar", f"Confirma demitir {sel['name']}?"):
            delete_user(sel['id'])
            messagebox.showinfo("Sucesso", "Usuário demitido.")
            self.refresh()


if __name__ == "__main__":
    app = TeamManagerApp()
    app.mainloop()