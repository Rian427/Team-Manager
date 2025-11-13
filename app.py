import tkinter as tk

# Data

USUARIOS = {"admin": "123"}
CARGOS = ["CEO", "Gerente", "Assistente"]
FUNCIONARIOS = [
    {"nome": "Lucas Goulart", "cargo": "CEO", "nascimento": "10/02/1980"}
]

# App

class TeamManagerApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Team Manager")
        self.geometry("550x420")
        self.resizable(False, False)

        self.current_frame = None
        self.show_login()

    def switch_frame(self, frame_class):
        if self.current_frame is not None:
            self.current_frame.destroy()
        self.current_frame = frame_class(self)
        self.current_frame.pack(fill="both", expand=True)

    def show_login(self):
        self.switch_frame(LoginFrame)

    def show_menu(self):
        self.switch_frame(MenuFrame)

    def show_cadastro(self):
        self.switch_frame(CadastroFrame)

    def show_criar_cargo(self):
        self.switch_frame(CriarCargoFrame)

    def show_gestao(self):
        self.switch_frame(GestaoFrame)

# Screens

class LoginFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        tk.Label(self, text="Login", font=("Arial", 18, "bold")).pack(pady=20)

        tk.Label(self, text="Usuário").pack()
        self.entry_user = tk.Entry(self)
        self.entry_user.pack()

        tk.Label(self, text="Senha").pack()
        self.entry_pass = tk.Entry(self, show="*")
        self.entry_pass.pack()

        enter_action = lambda event=None: self.try_login(master)

        tk.Button(self, text="Entrar",
                  command=lambda: self.try_login(master)).pack(pady=15)

        self.entry_user.bind("<Return>", enter_action)
        self.entry_pass.bind("<Return>", enter_action)

    def try_login(self, master):
        user = self.entry_user.get()
        pwd = self.entry_pass.get()

        if user in USUARIOS and USUARIOS[user] == pwd:
            master.show_menu()
        else:
            tk.Label(self, text="Credenciais inválidas.", fg="red").pack()


class MenuFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        tk.Label(self, text="Menu Principal", font=("Arial", 18, "bold")).pack(pady=20)

        tk.Button(self, text="Cadastro de Funcionário", width=30,
                  command=master.show_cadastro).pack(pady=5)

        tk.Button(self, text="Criação de Cargo", width=30,
                  command=master.show_criar_cargo).pack(pady=5)

        tk.Button(self, text="Gestão de Funcionários", width=30,
                  command=master.show_gestao).pack(pady=5)

        tk.Button(self, text="Sair", width=30,
                  command=master.show_login).pack(pady=20)


class CadastroFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        tk.Label(self, text="Cadastro de Funcionário", font=("Arial", 16, "bold")).pack(pady=15)

        tk.Label(self, text="Nome completo").pack()
        self.nome = tk.Entry(self)
        self.nome.pack()

        tk.Label(self, text="Cargo").pack()
        self.cargo = tk.Entry(self)
        self.cargo.pack()

        tk.Label(self, text="Data de nascimento").pack()
        self.nascimento = tk.Entry(self)
        self.nascimento.pack()

        tk.Button(self, text="Cadastrar", command=self.cadastrar).pack(pady=10)

        tk.Button(self, text="Voltar", command=master.show_menu).pack()

        self.bind_all("<Return>", lambda event: self.cadastrar())

    def cadastrar(self):
        nome = self.nome.get()
        cargo = self.cargo.get()
        nasc = self.nascimento.get()

        if nome and cargo and nasc:
            FUNCIONARIOS.append({
                "nome": nome,
                "cargo": cargo,
                "nascimento": nasc
            })

            tk.Label(self, text="Funcionário cadastrado!", fg="green").pack()
        else:
            tk.Label(self, text="Preencha todos os campos!", fg="red").pack()


class CriarCargoFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        tk.Label(self, text="Criação de Cargo", font=("Arial", 16, "bold")).pack(pady=20)

        tk.Label(self, text="Nome do novo cargo").pack()
        self.cargo = tk.Entry(self)
        self.cargo.pack()

        tk.Button(self, text="Criar Cargo", command=self.criar).pack(pady=10)

        tk.Button(self, text="Voltar", command=master.show_menu).pack()

        self.bind_all("<Return>", lambda event: self.criar())

    def criar(self):
        nome = self.cargo.get()

        if nome and nome not in CARGOS:
            CARGOS.append(nome)
            tk.Label(self, text="Cargo criado!", fg="green").pack()
        else:
            tk.Label(self, text="Cargo inválido ou já existente.", fg="red").pack()


class GestaoFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        tk.Label(self, text="Gestão de Funcionários", font=("Arial", 16, "bold")).pack(pady=20)

        box = tk.Frame(self)
        box.pack()

        for f in FUNCIONARIOS:
            tk.Label(box, text=f"{f['nome']} | {f['cargo']} | {f['nascimento']}").pack()

        tk.Button(self, text="Voltar", command=master.show_menu).pack(pady=15)


# Execution

if __name__ == "__main__":
    app = TeamManagerApp()
    app.mainloop()