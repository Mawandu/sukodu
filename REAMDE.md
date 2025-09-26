# Sukodu - Jeu de Carré en Réseau

Bienvenue sur Sukodu, une implémentation en Python du classique "Jeu de Carré" (aussi connu sous le nom de Gomoku ou 5 en ligne). Ce projet a été développé dans le but de mettre en pratique la conception de protocoles et la programmation réseau.

Il permet de jouer à deux en réseau local ou seul contre une intelligence artificielle simple.

## ✨ Fonctionnalités

* **Jeu de Carré classique** : Alignez 5 de vos symboles pour gagner.
* **Mode multijoueur** : Jouez contre un ami sur le même réseau WiFi.
* **Mode solo** : Entraînez-vous contre une intelligence artificielle basique.
* **Interface graphique** : Une interface simple et intuitive construite avec Tkinter.
* **Protocole réseau personnalisé** : Le jeu utilise un protocole TCP simple conçu spécifiquement pour ce projet.

## ⚙️ Prérequis

* **Python 3.x**

Toutes les bibliothèques nécessaires (`socket`, `threading`, `tkinter`) sont incluses dans l'installation standard de Python.

## 🚀 Installation & Lancement

Suivez ces étapes pour lancer le jeu.

1.  **Cloner le Dépôt**
    Clonez ce projet sur votre machine locale :
    ```bash
    git clone [https://github.com/Mawandu/sukodu.git](https://github.com/Mawandu/sukodu.git)
    cd sukodu
    ```

2.  **Créer un Environnement Virtuel** (Recommandé)
    ```bash
    python3 -m venv env
    source env/bin/activate
    ```
    Sur Windows, utilisez `env\Scripts\activate`.

3.  **Lancer le Jeu**
    Il suffit de lancer le fichier `client.py`. Une fenêtre s'ouvrira pour vous demander de choisir un mode de jeu.
    ```bash
    python3 client.py
    ```

## 🌐 Comment Jouer en Réseau ?

Pour jouer à deux sur le même réseau WiFi, il faut un **Hôte** (qui lance le serveur) et un **Client** (qui rejoint la partie).

#### **🖥️ Pour le Joueur 1 (Hôte)**

1.  **Lancez le serveur** dans un premier terminal. Il se mettra en attente de joueurs.
    ```bash
    python3 server.py
    ```
2.  **Trouvez votre adresse IP locale** (par exemple `192.168.1.42`).
    * Sur Windows : `ipconfig` dans `cmd`.
    * Sur macOS/Linux : `ifconfig` ou `ip a` dans le terminal.
3.  **Communiquez cette adresse IP** au Joueur 2.
4.  **Lancez votre client** en exécutant `python3 client.py`, choisissez "Jouer en Réseau" et entrez votre propre adresse IP.

#### **➡️ Pour le Joueur 2 (Client)**

1.  **Lancez le client** en exécutant `python3 client.py`.
2.  Choisissez "Jouer en Réseau".
3.  **Entrez l'adresse IP** que le Joueur 1 vous a donnée.
4.  La partie commence dès que vous êtes connecté !

---
