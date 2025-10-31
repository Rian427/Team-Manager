import tkinter as tk

class TeamManagerApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Team Manager")
        self.geometry("500x400")
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

        tk.Button(self, text="Entrar",
                  command=master.show_menu).pack(pady=15)


class MenuFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        tk.Label(self, text="Menu Principal", font=("Arial", 18, "bold")).pack(pady=20)

        tk.Button(self, text="Cadastro de Funcionário",
                  width=25, command=master.show_cadastro).pack(pady=5)

        tk.Button(self, text="Criação de Cargo",
                  width=25, command=master.show_criar_cargo).pack(pady=5)

        tk.Button(self, text="Gestão de Funcionários",
                  width=25, command=master.show_gestao).pack(pady=5)

        tk.Button(self, text="Sair",
                  width=25, command=master.show_login).pack(pady=20)


class CadastroFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        tk.Label(self, text="Cadastro de Funcionário", font=("Arial", 16, "bold")).pack(pady=15)

        tk.Label(self, text="Nome completo").pack()
        tk.Entry(self).pack()

        tk.Label(self, text="Cargo").pack()
        tk.Entry(self).pack()

        tk.Label(self, text="Data de nascimento").pack()
        tk.Entry(self).pack()

        tk.Label(self, text="Senha").pack()
        tk.Entry(self, show="*").pack()

        tk.Button(self, text="Voltar",
                  command=master.show_menu).pack(pady=15)


class CriarCargoFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        tk.Label(self, text="Criação de Cargo", font=("Arial", 16, "bold")).pack(pady=20)

        tk.Label(self, text="Nome do cargo").pack()
        tk.Entry(self).pack()

        tk.Button(self, text="Voltar",
                  command=master.show_menu).pack(pady=15)


class GestaoFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        tk.Label(self, text="Gestão de Funcionários", font=("Arial", 16, "bold")).pack(pady=20)

        tk.Label(self, text="(Área para listagem de funcionários futuramente)").pack(pady=10)

        tk.Button(self, text="Voltar",
                  command=master.show_menu).pack(pady=15)


if __name__ == "__main__":
    app = TeamManagerApp()
    app.mainloop()
