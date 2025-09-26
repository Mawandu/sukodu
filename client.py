# Fichier: client.py 
import socket
import threading
import tkinter as tk
from tkinter import messagebox, simpledialog
import queue
from game_logic import Jeu

GRID_SIZE = 15
PORT = 65432

class GameGUI(tk.Frame):
    def __init__(self, master, mode, server_ip=None):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        self.master = master
        self.master.title("Jeu de Carré")
        
        self.mode = mode
        self.create_widgets()

        if self.mode == "Réseau":
            self.init_network_mode(server_ip)
        else: # Mode IA
            self.init_ai_mode()

    def create_widgets(self):
        # Cette méthode est identique à la version précédente
        grid_frame = tk.Frame(self)
        grid_frame.pack(pady=10, padx=10)
        
        self.buttons = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                button = tk.Button(grid_frame, text=' ', width=2, height=1, font=('Arial', 12), command=lambda r=r, c=c: self.on_grid_click(r, c))
                button.grid(row=r, column=c)
                self.buttons[r][c] = button
            
        self.info_label = tk.Label(self, text="Bienvenue !", font=('Arial', 14))
        self.info_label.pack(pady=10)

        control_frame = tk.Frame(self)
        control_frame.pack(pady=10)

        self.restart_button = tk.Button(control_frame, text="Recommencer", font=('Arial', 12), command=self.request_restart)
        self.restart_button.pack(side=tk.LEFT, padx=10)

        quit_button = tk.Button(control_frame, text="Quitter", font=('Arial', 12), command=self.on_closing)
        quit_button.pack(side=tk.LEFT, padx=10)

    # --- Initialisation des modes ---
    def init_network_mode(self, server_ip):
        self.my_symbol = None
        self.is_my_turn = False
        self.message_queue = queue.Queue()
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect_to_server(server_ip)

    def init_ai_mode(self):
        self.jeu_local = Jeu(taille=GRID_SIZE)
        self.info_label.config(text="Vous êtes 'X'. À vous de jouer.")
        self.restart_button.config(command=self.reset_ai_game)

    def reset_ai_game(self):
        self.jeu_local.reinitialiser()
        self.clear_board()
        self.info_label.config(text="Vous êtes 'X'. À vous de jouer.")

    # --- Logique de clic ---
    def on_grid_click(self, r, c):
        if self.mode == "Réseau":
            if self.is_my_turn and self.buttons[r][c]['text'] == ' ':
                self.send_message(f"MOVE|{r}|{c}\n")
                self.is_my_turn = False
                self.info_label.config(text="Tour de l'adversaire...")
        else: # Mode IA
            if not self.jeu_local.partie_terminee and self.buttons[r][c]['text'] == ' ':
                self.jeu_local.placer_pion(r, c)
                self.update_board(r, c, 'X')
                if self.jeu_local.partie_terminee:
                    self.handle_local_game_over()
                else:
                    self.info_label.config(text="L'IA réfléchit...")
                    self.master.after(500, self.make_ai_move)

    # --- Méthodes Réseau ---
    def connect_to_server(self, server_ip):
        try:
            self.client_socket.connect((server_ip, PORT))
            self.info_label.config(text="Connecté. En attente d'un autre joueur...")
            
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.daemon = True
            receive_thread.start()

            self.master.after(100, self.process_queue)
            self.send_message(f"JOIN|Joueur\n")
        except Exception as e:
            messagebox.showerror("Erreur de connexion", f"Impossible de se connecter au serveur:\n{e}")
            self.on_closing()
    
    def receive_messages(self):
        buffer = ""
        while True:
            try:
                data = self.client_socket.recv(1024).decode()
                if not data: break
                buffer += data
                while '\n' in buffer:
                    message, buffer = buffer.split('\n', 1)
                    if message: self.message_queue.put(message)
            except: break
        self.message_queue.put("SERVER_DOWN")

    def process_queue(self):
        try:
            message = self.message_queue.get_nowait()
            self.handle_server_message(message.strip())
        except queue.Empty:
            pass
        finally:
            self.master.after(100, self.process_queue)

    def handle_server_message(self, message):
        parts = message.split('|')
        command = parts[0]

        if command == "JOIN_OK":
            self.my_symbol = parts[1]
            self.master.title(f"Jeu de Carré - Joueur {self.my_symbol}")
        elif command == "GAME_START":
            self.clear_board()
            self.info_label.config(text=f"La partie commence ! Tour de '{parts[1]}'")
        elif command == "YOUR_TURN":
            self.is_my_turn = True
            self.info_label.config(text="C'est votre tour !")
        elif command == "UPDATE":
            r, c, symbol = int(parts[1]), int(parts[2]), parts[3]
            self.update_board(r, c, symbol)
        elif command == "WIN":
            self.is_my_turn = False
            messagebox.showinfo("Partie terminée", f"Le joueur '{parts[1]}' a gagné !")
        elif command == "DRAW":
            self.is_my_turn = False
            messagebox.showinfo("Partie terminée", "Match nul !")
        elif command == "OPPONENT_LEFT":
            messagebox.showinfo("Info", "Votre adversaire a quitté la partie.")
        elif "SERVER_DOWN" in command:
            messagebox.showerror("Erreur", "Connexion au serveur perdue.")
            self.on_closing()

    # --- Méthodes IA ---
    def make_ai_move(self):
        if self.jeu_local.partie_terminee: return
        move = self.find_best_move()
        if move:
            r, c = move
            self.jeu_local.placer_pion(r, c)
            self.update_board(r, c, 'O')
            if self.jeu_local.partie_terminee:
                self.handle_local_game_over()
            else:
                self.info_label.config(text="Vous êtes 'X'. À vous de jouer.")

    def find_best_move(self):
        # Cette logique est identique à la version précédente
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if self.jeu_local.grille[r][c] == ' ':
                    self.jeu_local.grille[r][c] = 'O';
                    if self.jeu_local.verifier_victoire(r, c):
                        self.jeu_local.grille[r][c] = ' '
                        return (r, c)
                    self.jeu_local.grille[r][c] = ' '
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if self.jeu_local.grille[r][c] == ' ':
                    self.jeu_local.grille[r][c] = 'X';
                    if self.jeu_local.verifier_victoire(r, c):
                        self.jeu_local.grille[r][c] = ' '
                        return (r, c)
                    self.jeu_local.grille[r][c] = ' '
        if self.jeu_local.grille[GRID_SIZE // 2][GRID_SIZE // 2] == ' ':
            return (GRID_SIZE // 2, GRID_SIZE // 2)
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if self.jeu_local.grille[r][c] == ' ':
                    return (r, c)
        return None
    
    def handle_local_game_over(self):
        winner = self.jeu_local.gagnant
        if winner:
            messagebox.showinfo("Partie terminée", f"Le joueur '{winner}' a gagné !")
        else:
            messagebox.showinfo("Partie terminée", "Match nul !")

    # --- Utilitaires ---
    def update_board(self, r, c, symbol):
        color = 'blue' if symbol == 'X' else 'red'
        self.buttons[r][c].config(text=symbol, state=tk.DISABLED, disabledforeground=color)

    def clear_board(self):
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                self.buttons[r][c].config(text=' ', state=tk.NORMAL)
    
    def request_restart(self):
        if self.mode == "Réseau":
            self.send_message("RESTART\n")
            self.info_label.config(text="Demande de redémarrage envoyée...")
        else:
            self.reset_ai_game()
    
    def send_message(self, message):
        if hasattr(self, 'client_socket'):
            self.client_socket.sendall(message.encode())

    def on_closing(self):
        if self.mode == "Réseau" and hasattr(self, 'client_socket'):
            try:
                self.client_socket.close()
            except:
                pass
        self.master.destroy()

# --- Classe principale de lancement ---
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sukodu - Lancement")
        self.geometry("300x150")
        
        tk.Label(self, text="Comment voulez-vous jouer ?").pack(padx=20, pady=10)
        
        tk.Button(self, text="Jouer en Réseau", command=self.start_network_game).pack(fill="x", padx=20, pady=5)
        tk.Button(self, text="Jouer contre l'IA", command=self.start_ai_game).pack(fill="x", padx=20, pady=5)

    def clear_window(self):
        for widget in self.winfo_children():
            widget.destroy()

    def start_network_game(self):
        server_ip = simpledialog.askstring("Adresse du Serveur", "Entrez l'adresse IP du serveur:", parent=self)
        if server_ip:
            self.clear_window()
            self.geometry("") # Reset geometry to fit the game board
            game = GameGUI(self, mode="Réseau", server_ip=server_ip)
            self.protocol("WM_DELETE_WINDOW", game.on_closing)

    def start_ai_game(self):
        self.clear_window()
        self.geometry("") # Reset geometry to fit the game board
        game = GameGUI(self, mode="IA")
        self.protocol("WM_DELETE_WINDOW", game.on_closing)

if __name__ == "__main__":
    app = App()
    app.mainloop()
