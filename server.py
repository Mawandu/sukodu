# Fichier: server.py
import socket
import threading
from game_logic import Jeu

HOST = '0.0.0.0'  # Pour être accessible sur le réseau local
PORT = 65432
GRID_SIZE = 15

clients = []
joueurs_symboles = {}
partie = Jeu(taille=GRID_SIZE)
verrou = threading.Lock()
restart_votes = []

def envoyer_a_tous(message):
    for client in clients:
        client.sendall((message + '\n').encode())

def handle_client(conn, addr):
    global partie
    print(f"Nouvelle connexion de {addr}")
    
    try:
        with verrou:
            if len(clients) >= 2:
                conn.sendall("JOIN_ERR|Partie pleine.\n".encode())
                return
            
            clients.append(conn)
            symbole = 'X' if len(clients) == 1 else 'O'
            joueurs_symboles[conn] = symbole
            conn.sendall(f"JOIN_OK|{symbole}|Bienvenue Joueur {symbole}\n".encode())

        if len(clients) == 2:
            print("Deux joueurs connectés. La partie commence.")
            partie.reinitialiser()
            restart_votes.clear()
            envoyer_a_tous(f"GAME_START|{partie.tour_joueur}")
            
            joueur_qui_commence = next(c for c, s in joueurs_symboles.items() if s == partie.tour_joueur)
            joueur_qui_commence.sendall("YOUR_TURN|C'est a vous de jouer\n".encode())

        buffer = ""
        while True:
            data = conn.recv(1024).decode()
            if not data: break
            
            buffer += data
            while '\n' in buffer:
                message, buffer = buffer.split('\n', 1)
                commande, *params = message.strip().split('|')

                with verrou:
                    if commande == 'MOVE' and joueurs_symboles.get(conn) == partie.tour_joueur:
                        ligne, col = int(params[0]), int(params[1])
                        if partie.placer_pion(ligne, col):
                            envoyer_a_tous(f"UPDATE|{ligne}|{col}|{joueurs_symboles[conn]}")
                            statut = partie.get_statut()
                            if statut == 'VICTOIRE':
                                envoyer_a_tous(f"WIN|{partie.gagnant}")
                            elif statut == 'NUL':
                                envoyer_a_tous("DRAW")
                            else:
                                joueur_suivant = next(c for c in clients if c != conn)
                                joueur_suivant.sendall("YOUR_TURN|C'est a vous de jouer\n".encode())
                        else:
                            conn.sendall("INVALID_MOVE|Mouvement invalide\n".encode())
                    
                    elif commande == 'RESTART':
                        if conn not in restart_votes:
                            restart_votes.append(conn)
                        if len(restart_votes) == 2:
                            print("Redémarrage de la partie.")
                            partie.reinitialiser()
                            restart_votes.clear()
                            envoyer_a_tous(f"GAME_START|{partie.tour_joueur}")
                            joueur_qui_commence = next(c for c, s in joueurs_symboles.items() if s == partie.tour_joueur)
                            joueur_qui_commence.sendall("YOUR_TURN|C'est a vous de jouer\n".encode())
    finally:
        print(f"Déconnexion de {addr}")
        with verrou:
            if conn in clients:
                clients.remove(conn)
            joueurs_symboles.pop(conn, None)
            restart_votes.clear() # On nettoie les votes au cas où
            if len(clients) == 1:
                clients[0].sendall("OPPONENT_LEFT\n".encode())
        conn.close()

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        print(f"Le serveur écoute sur {HOST}:{PORT}")
        while True:
            conn, addr = server_socket.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()

if __name__ == "__main__":
    start_server()
