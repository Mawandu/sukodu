# Fichier: game_logic.py 

class Jeu:
    """
    Gère la logique du jeu de Carré (Gomoku).
    Version améliorée avec réinitialisation et historique des coups.
    """
    def __init__(self, taille=15):
        """
        Initialise le jeu.
        """
        self.taille = taille
        self.reinitialiser() # On utilise notre nouvelle méthode pour initialiser

    def reinitialiser(self):
        """
        Réinitialise la partie à son état initial pour permettre de rejouer.
        """
        self.grille = [[' ' for _ in range(self.taille)] for _ in range(self.taille)]
        self.tour_joueur = 'X'
        self.partie_terminee = False
        self.gagnant = None
        self.coups = 0
        self.historique = [] # BONUS : Pour la fonction "annuler"
        print("--- Nouvelle partie initialisée. ---")

    def get_statut(self):
        """
        Retourne le statut actuel de la partie.
        :return: Une chaîne de caractères: 'EN_COURS', 'VICTOIRE', 'NUL'.
        """
        if self.partie_terminee:
            return 'VICTOIRE' if self.gagnant else 'NUL'
        return 'EN_COURS'

    def placer_pion(self, ligne, col):
        """
        Tente de placer un pion sur la grille pour le joueur actuel.
        """
        if (0 <= ligne < self.taille and 
            0 <= col < self.taille and 
            self.grille[ligne][col] == ' ' and 
            not self.partie_terminee):
            
            joueur_actuel = self.tour_joueur
            self.grille[ligne][col] = joueur_actuel
            self.coups += 1
            self.historique.append((ligne, col)) # On sauvegarde le coup

            if self.verifier_victoire(ligne, col):
                self.partie_terminee = True
                self.gagnant = joueur_actuel
            elif self.verifier_match_nul():
                self.partie_terminee = True

            self.tour_joueur = 'O' if joueur_actuel == 'X' else 'X'
            return True
        return False

    def annuler_dernier_coup(self):
        """
        BONUS : Annule le dernier coup joué.
        """
        if not self.historique:
            print("Aucun coup à annuler.")
            return False

        # On ne peut pas annuler un coup si la partie est déjà finie
        if self.partie_terminee:
            self.partie_terminee = False
            self.gagnant = None
        
        # Récupérer et effacer le dernier coup
        ligne, col = self.historique.pop()
        self.grille[ligne][col] = ' '
        self.coups -= 1
        
        # Rétablir le tour du joueur précédent
        self.tour_joueur = 'O' if self.tour_joueur == 'X' else 'X'
        print(f"Le coup en ({ligne}, {col}) a été annulé.")
        return True

    def verifier_victoire(self, ligne, col):
        """
        Vérifie si le dernier coup est un coup gagnant. (Inchangé)
        """
        symbole = self.grille[ligne][col]
        for dr, dc in [(0, 1), (1, 0), (1, 1), (1, -1)]:
            compteur = 1
            for i in range(1, 5):
                r, c = ligne + i * dr, col + i * dc
                if 0 <= r < self.taille and 0 <= c < self.taille and self.grille[r][c] == symbole:
                    compteur += 1
                else:
                    break
            for i in range(1, 5):
                r, c = ligne - i * dr, col - i * dc
                if 0 <= r < self.taille and 0 <= c < self.taille and self.grille[r][c] == symbole:
                    compteur += 1
                else:
                    break
            if compteur >= 5:
                return True
        return False

    def verifier_match_nul(self):
        return self.coups == self.taille * self.taille

    def afficher_grille(self):
        for ligne in self.grille:
            print('|' + '|'.join(ligne) + '|')


# --- Section de test améliorée ---
if __name__ == "__main__":
    jeu_test = Jeu(taille=5)
    
    print(f"Statut du jeu: {jeu_test.get_statut()}")
    
    # Jouer quelques coups
    jeu_test.placer_pion(2, 2) # X
    jeu_test.placer_pion(1, 1) # O
    jeu_test.placer_pion(2, 3) # X
    
    print("\nGrille après 3 coups:")
    jeu_test.afficher_grille()

    # Test de la fonction Annuler
    print("\n--- Test de la fonction Annuler ---")
    jeu_test.annuler_dernier_coup()
    print("Grille après avoir annulé le dernier coup:")
    jeu_test.afficher_grille()
    print(f"C'est maintenant au tour du joueur: {jeu_test.tour_joueur}")

    # Test de la réinitialisation
    print("\n--- Test de la réinitialisation ---")
    jeu_test.placer_pion(0,0) # X
    jeu_test.placer_pion(0,1) # O
    jeu_test.reinitialiser()
    print("Grille après réinitialisation:")
    jeu_test.afficher_grille()
    print(f"Statut du jeu: {jeu_test.get_statut()}")
    print(f"C'est maintenant au tour du joueur: {jeu_test.tour_joueur}")
