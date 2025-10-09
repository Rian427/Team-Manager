# app.py
import tkinter as tk
from tkinter import ttk, messagebox
from database import (
  get_user_by_username, create_user, get_all_roles, create_role,
  get_roles_with_higher_nivel_than, get_manageable_users_by_user,
  update_user_cargo, delete_user
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

    for F in (LoginFrame, DashboardFrame, RoleCreateFrame, UserCreateFrame, ManageUsersFrame):
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
      if not user or user['senha'] != senha:
        messagebox.showerror("Erro", "Usuário ou senha inválidos.")
        return
      self.controller.current_user = user
      messagebox.showinfo("Sucesso", f"Bem-vindo, {user['nome']} ({user['cargo_nome']})")
      self.controller.show_frame("DashboardFrame")

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
    ttk.Button(btns, text="Criar Cargo", command=lambda: controller.show_frame("RoleCreateFrame")).grid(row=0, column=1, padx=5, pady=5)
    ttk.Button(btns, text="Gerenciar Funcionários", command=lambda: controller.show_frame("ManageUsersFrame")).grid(row=0, column=2, padx=5, pady=5)
    ttk.Button(btns, text="Logout", command=self.logout).grid(row=0, column=3, padx=5, pady=5)

  def refresh(self):
    user = self.controller.current_user
    if user:
      text = f"Logado como: {user['nome']} | Cargo: {user['cargo_nome']} (Nível {user['cargo_nivel']})"
    else:
      text = "Nenhum usuário logado."
    self.info_label.config(text=text)

  def logout(self):
    self.controller.current_user = None
    self.controller.show_frame("LoginFrame")

class RoleCreateFrame(ttk.Frame):
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
    self.nivel_spin = ttk.Spinbox(frm, from_=1, to=100, width=8)
    self.nivel_spin.grid(row=1, column=1, sticky="w", padx=5, pady=5)

    btns = ttk.Frame(self)
    btns.pack(pady=12)
    ttk.Button(btns, text="Criar", command=self.create_role).grid(row=0, column=0, padx=6)
    ttk.Button(btns, text="Voltar", command=lambda: controller.show_frame("DashboardFrame")).grid(row=0, column=1, padx=6)

  def refresh(self):
    # apenas limpar entradas
    self.name_entry.delete(0, tk.END)
    self.nivel_spin.set(1)

  def create_role(self):
    user = self.controller.current_user
    if not user:
      messagebox.showerror("Erro", "Faça login primeiro.")
      return
    # apenas permitir criação se o nível do novo cargo for maior (menos poder) que o do criador
    nome = self.name_entry.get().strip()
    try:
      nivel = int(self.nivel_spin.get())
    except:
      messagebox.showerror("Erro", "Nível inválido.")
      return
    if not nome:
      messagebox.showwarning("Aviso", "Informe o nome do cargo.")
      return
    # permissões: só pode criar cargos com nivel > seu_nivel
    if nivel <= user['cargo_nivel']:
      messagebox.showerror("Erro", "Você só pode criar cargos de nível maior (menos poder) que o seu.")
      return
    try:
      create_role(nome, nivel)
      messagebox.showinfo("Sucesso", f"Cargo '{nome}' criado com nível {nivel}.")
      self.name_entry.delete(0, tk.END)
    except Exception as e:
      messagebox.showerror("Erro", f"Falha ao criar cargo: {e}")

class UserCreateFrame(ttk.Frame):
  def __init__(self, parent, controller: TeamManagerApp):
    super().__init__(parent)
    self.controller = controller
    ttk.Label(self, text="Cadastro / Contratação", font=("Helvetica", 14)).pack(pady=10)

    frm = ttk.Frame(self)
    frm.pack(pady=5)

    ttk.Label(frm, text="Nome completo:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
    self.nome_entry = ttk.Entry(frm, width=40)
    self.nome_entry.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(frm, text="Usuário (username):").grid(row=1, column=0, sticky="e", padx=5, pady=5)
    self.username_entry = ttk.Entry(frm, width=30)
    self.username_entry.grid(row=1, column=1, padx=5, pady=5)

    ttk.Label(frm, text="Data de nascimento (YYYY-MM-DD):").grid(row=2, column=0, sticky="e", padx=5, pady=5)
    self.dn_entry = ttk.Entry(frm, width=20)
    self.dn_entry.grid(row=2, column=1, sticky="w", padx=5, pady=5)

    ttk.Label(frm, text="Senha:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
    self.senha_entry = ttk.Entry(frm, width=30, show="*")
    self.senha_entry.grid(row=3, column=1, padx=5, pady=5)

    ttk.Label(frm, text="Cargo a ser atribuído:").grid(row=4, column=0, sticky="e", padx=5, pady=5)
    self.role_combo = ttk.Combobox(frm, state="readonly")
    self.role_combo.grid(row=4, column=1, padx=5, pady=5)

    btns = ttk.Frame(self)
    btns.pack(pady=10)
    ttk.Button(btns, text="Cadastrar", command=self.create_user).grid(row=0, column=0, padx=6)
    ttk.Button(btns, text="Voltar", command=lambda: controller.show_frame("DashboardFrame")).grid(row=0, column=1, padx=6)

  def refresh(self):
    # carregar cargos que o usuário logado pode criar/atribuir (nivel maior que o do logado)
    self.nome_entry.delete(0, tk.END)
    self.username_entry.delete(0, tk.END)
    self.dn_entry.delete(0, tk.END)
    self.senha_entry.delete(0, tk.END)
    user = self.controller.current_user
    if not user:
        self.role_combo['values'] = []
        return
    roles = get_roles_with_higher_nivel_than(user['cargo_nivel'])
    if not roles:
        self.role_combo['values'] = []
    else:
        self.role_combo['values'] = [f"{r['id']} - {r['nome']} (Niv {r['nivel']})" for r in roles]
        self.role_combo.current(0)

  def create_user(self):
    user = self.controller.current_user
    if not user:
      messagebox.showerror("Erro", "Faça login primeiro.")
      return
    nome = self.nome_entry.get().strip()
    username = self.username_entry.get().strip()
    dn = self.dn_entry.get().strip() or None
    senha = self.senha_entry.get().strip()
    role_sel = self.role_combo.get()
    if not (nome and username and senha and role_sel):
      messagebox.showwarning("Aviso", "Preencha todos os campos e escolha um cargo.")
      return
    # extrair cargo_id de "id - nome"
    cargo_id = int(role_sel.split(" - ")[0])
    try:
      create_user(nome, username, dn, cargo_id, senha)
      messagebox.showinfo("Sucesso", "Usuário cadastrado com sucesso.")
      # limpar
      self.nome_entry.delete(0, tk.END)
      self.username_entry.delete(0, tk.END)
      self.dn_entry.delete(0, tk.END)
      self.senha_entry.delete(0, tk.END)
      self.role_combo.set('')
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

    self.tree = ttk.Treeview(self, columns=("id", "nome", "username", "cargo", "nivel"), show="headings", height=18)
    for col, hd in [("id", "ID"), ("nome", "Nome"), ("username", "Usuário"), ("cargo", "Cargo"), ("nivel", "Nível")]:
      self.tree.heading(col, text=hd)
      self.tree.column(col, width=120 if col == "nome" else 80)
    self.tree.pack(padx=10, pady=8)

    btns = ttk.Frame(self)
    btns.pack(pady=8)
    ttk.Button(btns, text="Promover (atribuir cargo)", command=self.promote).grid(row=0, column=0, padx=6)
    ttk.Button(btns, text="Rebaixar (atribuir cargo)", command=self.rebaixar).grid(row=0, column=1, padx=6)
    ttk.Button(btns, text="Demitir", command=self.fire).grid(row=0, column=2, padx=6)

  def refresh(self):
    # listar usuários que o logado pode gerenciar
    for r in self.tree.get_children():
      self.tree.delete(r)
    user = self.controller.current_user
    if not user:
      return
    rows = get_manageable_users_by_user(user['id'])
    for u in rows:
      self.tree.insert("", tk.END, values=(u['id'], u['nome'], u['username'], u['cargo_nome'], u['cargo_nivel']))

  def _get_selected_user(self):
    sel = self.tree.selection()
    if not sel:
      messagebox.showwarning("Aviso", "Selecione um usuário na lista.")
      return None
    vals = self.tree.item(sel[0], "values")
    return {"id": int(vals[0]), "nome": vals[1], "username": vals[2], "cargo_nome": vals[3], "cargo_nivel": int(vals[4])}

  def _choose_role_dialog(self, roles):
    # roles: lista de dicts com id,nome,nivel
    d = tk.Toplevel(self)
    d.title("Escolher cargo")
    ttk.Label(d, text="Escolha o cargo a atribuir:").pack(pady=8)
    combo = ttk.Combobox(d, values=[f"{r['id']} - {r['nome']} (Niv {r['nivel']})" for r in roles], state="readonly", width=40)
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
    # quem pode ser atribuido: cargos com nivel < user's current sel level? For promotion, choose cargos with nivel < sel.cargo_nivel but still > me.cargo_nivel
    # Em regra: você só pode atribuir cargos com nivel > meu_nivel (menos poder que eu). Porém promoção significa reduzir o nivel do colaborador (mais poder).
    # Para simplificar: o logado pode atribuir qualquer cargo cujo nivel seja maior que seu nivel (menos poder que o logado).
    roles = get_roles_with_higher_nivel_than(me['cargo_nivel'])
    # Para promover, selecionar entre todos cargos que tenham nivel < sel['cargo_nivel'] (mais poder que actual do sel) AND nivel > me['cargo_nivel']
    candidate = [r for r in roles if r['nivel'] < sel['cargo_nivel']]
    if not candidate:
      messagebox.showinfo("Info", "Nenhum cargo disponível para promover esse colaborador com suas permissões.")
      return
    choice = self._choose_role_dialog(candidate)
    if not choice:
      return
    new_cargo_id = int(choice.split(" - ")[0])
    update_user_cargo(sel['id'], new_cargo_id)
    messagebox.showinfo("Sucesso", f"{sel['nome']} foi promovido.")
    self.refresh()

  def rebaixar(self):
    sel = self._get_selected_user()
    if not sel:
      return
    me = self.controller.current_user
    # Rebaixar -> atribuir cargo de nível maior (menos poder) que o atual do selecionado, mas ainda maior que meu_nivel
    roles = get_roles_with_higher_nivel_than(me['cargo_nivel'])  # cargos que posso criar/atribuir
    candidate = [r for r in roles if r['nivel'] > sel['cargo_nivel']]
    if not candidate:
      messagebox.showinfo("Info", "Nenhum cargo disponível para rebaixamento com suas permissões.")
      return
    choice = self._choose_role_dialog(candidate)
    if not choice:
      return
    new_cargo_id = int(choice.split(" - ")[0])
    update_user_cargo(sel['id'], new_cargo_id)
    messagebox.showinfo("Sucesso", f"{sel['nome']} foi rebaixado.")
    self.refresh()

  def fire(self):
    sel = self._get_selected_user()
    if not sel:
      return
    me = self.controller.current_user
    # Só pode demitir se o cargo do selecionado tiver nivel > meu nivel
    if sel['cargo_nivel'] <= me['cargo_nivel']:
      messagebox.showerror("Erro", "Você não tem permissão para demitir esse usuário.")
      return
    if messagebox.askyesno("Confirmar", f"Confirma demitir {sel['nome']}?"):
      delete_user(sel['id'])
      messagebox.showinfo("Sucesso", "Usuário demitido.")
      self.refresh()

if __name__ == "__main__":
  app = TeamManagerApp()
  app.mainloop()