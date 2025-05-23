import random
from time import *
import tkinter as tk
import os
import copy
import chess
import chess.engine
import threading
import socket
import concurrent.futures

plateau = [[[" ", ""] for _ in range(8)] for _ in range(8)]
for i, piece in enumerate(["T", "C", "F", "D", "R", "F", "C", "T"]):
    plateau[0][i] = [piece, "N"]
    plateau[7][i] = [piece, "B"]
for i in range(8):
    plateau[1][i] = ["P", "N"]
    plateau[6][i] = ["P", "B"]



def draw_plateau(plateau):
    for i in range(8):
        print(plateau[i])


class NetworkChess:
    def __init__(self, is_host, host_ip=None, port=5000):
        self.is_host = is_host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if is_host:
            self.sock.bind(('', port))
            self.sock.listen(1)
            print("En attente d'un joueur...")
            self.conn, _ = self.sock.accept()
            print("Joueur connecté !")
        else:
            self.sock.connect((host_ip, port))
            self.conn = self.sock

    def send_move(self, move):
        # move doit être une chaîne (ex: "e2e4" ou indices)
        self.conn.sendall(move.encode())

    def receive_move(self):
        data = self.conn.recv(1024)
        return data.decode()

    def close(self):
        self.conn.close()
        self.sock.close()


class AfficheurEchiquier:
    def __init__(self):
        self._dernier_score = 0
        self.x_offset = 40  # Largeur de la barre d'évaluation
        self.root = tk.Tk()
        self.root.title("Échiquier")
        self.root.configure(bg="#312e2b")  # Fond noir pour la fenêtre
        self.board_size = 728
        self.case_size = 91
        self.canvas = tk.Canvas(
            self.root,
            width=self.board_size + 300 + self.x_offset,
            height=self.board_size,
            bg="#312e2b",                # <-- Ajoute ce paramètre
            highlightthickness=0       # <-- Enlève la bordure grise
        )
        self.canvas.pack()
        self.images = {}
        self.fond_img = tk.PhotoImage(file=os.path.join("Pieces", "200.png"))
        self.canvas.create_image(self.x_offset, 0, image=self.fond_img, anchor=tk.NW)
        self.correspondance = {
            "P": "p", "T": "r", "C": "n",
            "F": "b", "D": "q", "R": "k"
        }
        espacement_total = self.board_size - (self.case_size * 8)
        espacement = espacement_total // 7
        self.positions = [0]
        self._clicked = tk.BooleanVar()
        self.sens = "B"  # "B" = blancs en bas, "N" = noirs en bas
        self.positions_x = [self.x_offset]
        for _ in range(1, 8):
            self.positions_x.append(self.positions_x[-1] + self.case_size + espacement)

        self.positions_y = [0]
        for _ in range(1, 8):
            self.positions_y.append(self.positions_y[-1] + self.case_size + espacement)
        # --- AJOUT DU BOUTON POUR TOURNER LE PLATEAU---
        
        self.bouton_tourner = tk.Button(
            self.root, text="Tourner le plateau", command=self.tourner_plateau,
            bg="#312e2b", fg="white", activebackground="gray20", activeforeground="white"
        )
        self.bouton_tourner.pack(side=tk.RIGHT, padx=10, pady=10)

        self.auto_rotate = tk.BooleanVar(value=False)
        self.check_auto_rotate = tk.Checkbutton(
            self.root, text="Rotation automatique", variable=self.auto_rotate,
            bg="#312e2b", fg="white", selectcolor="#312e2b", activebackground="gray20", activeforeground="white"
        )
        self.check_auto_rotate.pack(side=tk.RIGHT, padx=10, pady=10)

    def afficher_barre_eval(self, score):
        self._dernier_score = score  # mémorise le dernier score
        self.canvas.delete("evalbar")
        max_score = 10
        min_score = -10
        score_aff = max(min(score / 100, max_score), min_score)  # centipions -> pions
        h_total = self.board_size
        y_blanc = int(h_total * (0.5 - score_aff / (2 * max_score)))
        #y_noir = h_total - y_blanc
        x = 0
        w = self.x_offset
        # Barre blanche (en haut si score négatif)
        self.canvas.create_rectangle(x, 0, x + w, y_blanc, fill="#222", outline="", tags="evalbar")
        # Barre noire (en bas si score positif)
        self.canvas.create_rectangle(x, y_blanc, x + w, h_total, fill="#f0f0f0", outline="", tags="evalbar")
        # Ligne centrale
        self.canvas.create_line(x, h_total // 2, x + w, h_total // 2, fill="#888", width=2, tags="evalbar")

        # Affichage du score sur la barre, aux extrémités
        eval_text = f"{abs(score_aff):.2f}"
        if score_aff >= 0:
            # Score positif : en bas, texte noir
            self.canvas.create_text(
                x + w // 2, h_total - 10, text=eval_text, fill="#222", font=("Arial", 8, "bold"),
                anchor="s", tags="evalbar"
            )
        else:
            # Score négatif : en haut, texte blanc
            self.canvas.create_text(
                x + w // 2, 10, text=eval_text, fill="#f0f0f0", font=("Arial", 8, "bold"),
                anchor="n", tags="evalbar"
            )
   
    def tourner_plateau(self):
        self.sens = "N" if self.sens == "B" else "B"
        # Il faut réafficher le plateau avec les bonnes listes (à adapter selon ton code principal)
        # Exemple générique :
        self.afficher_plateau(plateau, liste_blanc, liste_noire, None, None, last_two_cases[0][0], last_two_cases[0][1], last_two_cases[1][0], last_two_cases[1][1])
    

    def afficher_plateau(self, plateau, liste_blanc, liste_noire, colorier_x=None, colorier_y=None, colorier_x2=None, colorier_y2=None, colorier_x3=None, colorier_y3=None):
        self.canvas.delete("pieces")
        self.canvas.delete("ui")
        self.canvas.create_image(self.x_offset, 0, image=self.fond_img, anchor=tk.NW)
        
        for i in range(8):
            for j in range(8):
                # Inversion des coordonnées si sens == "N"
                if self.sens == "B":
                    row, col = i, j
                else:
                    row, col = 7 - i, 7 - j

                x = self.positions_x[col]
                y = self.positions_y[row]

                # Coloration des cases sélectionnées (adapter aussi)
                def rotate(x, y):
                    if self.sens == "B":
                        return x, y
                    else:
                        return 7 - x, 7 - y

                rx1, ry1 = rotate(colorier_x, colorier_y) if colorier_x is not None and colorier_y is not None else (None, None)
                rx2, ry2 = rotate(colorier_x2, colorier_y2) if colorier_x2 is not None and colorier_y2 is not None else (None, None)
                rx3, ry3 = rotate(colorier_x3, colorier_y3) if colorier_x3 is not None and colorier_y3 is not None else (None, None)

                if (col == rx1 and row == ry1) or (col == rx2 and row == ry2) or (col == rx3 and row == ry3):
                    color = "#f3f68a" if (row + col) % 2 == 0 else "#b8ca4c"
                    self.canvas.create_rectangle(x, y, x + self.case_size, y + self.case_size, fill=color, outline=color)

                piece, couleur = plateau[i][j]
                if piece != " ":
                    prefix = "w" if couleur == "B" else "b"
                    suffix = self.correspondance[piece]
                    nom_fichier = f"{prefix}{suffix}.png"
                    chemin_image = os.path.join("Pieces", nom_fichier)
                    if nom_fichier not in self.images:
                        self.images[nom_fichier] = tk.PhotoImage(file=chemin_image)
                    self.canvas.create_image(x, y, image=self.images[nom_fichier], anchor=tk.NW, tags="pieces")

        self.afficher_captures(liste_blanc, liste_noire)
        self.afficher_barre_eval(self._dernier_score)
 
    def afficher_captures(self, liste_blanc, liste_noire):
        # Valeurs des pièces pour le calcul du score
        liste_total = {"P": 8, "C": 2, "F": 2, "T": 2, "D": 1, "R":1}
        liste_blanc_prise = {"P": 0, "C": 0, "F": 0, "T": 0, "D": 0 ,"R":0}
        liste_noire_prise = {"P": 0, "C": 0, "F": 0, "T": 0, "D": 0 ,"R":0}
        for piece in ["D", "T", "F", "C", "P"]:
            liste_blanc_prise[piece] = liste_total[piece] - liste_blanc[piece]
            liste_noire_prise[piece] = liste_total[piece] - liste_noire[piece]

        valeurs = {"P": 1, "C": 3, "F": 3, "T": 5, "D": 9}

        def pieces_en_texte(liste, couleur):
            lettre_to_caracteres_blanc = {"P":"♙", "C":"♘", "F":"♗", "T":"♖", "D":"♕"}
            lettre_to_caracteres_noire = {"P":"♟", "C":"♞", "F":"♝", "T":"♜", "D":"♛"}
            texte = ""
            for piece in ["P", "C", "F", "T", "D"]:
                if couleur == 0:
                    if piece == "P" and liste[piece]>2:
                        texte += "♟* " + str(liste[piece]) + " "
                    else:
                        texte += lettre_to_caracteres_noire[piece] * liste[piece]
                else:
                    if piece == "P" and liste[piece]>2:
                        texte += "♙* " + str(liste[piece]) + " "
                    else:
                        texte += lettre_to_caracteres_blanc[piece] * liste[piece]
            return texte

        def calcul_score(liste1, liste2):
            score1 = sum(valeurs[p] * liste1[p] for p in valeurs)
            score2 = sum(valeurs[p] * liste2[p] for p in valeurs)
            return score1 - score2

        # Coordonnées d'affichage
        x_text = self.board_size + 20
        y_blanc = 50
        y_noir = 200

        # Texte pièces capturées
        blanc_txt = pieces_en_texte(liste_blanc_prise, 0)
        noir_txt = pieces_en_texte(liste_noire_prise, 1)

        # Calcul score
        score_blanc = calcul_score(liste_blanc_prise, liste_noire_prise)
        score_noir = -score_blanc

        # Affichage
        self.canvas.create_text(x_text + self.x_offset, y_blanc, anchor="nw", text="⚫ Noirs ont pris :", font=("Arial", 12), tags="ui", fill="white")
        self.canvas.create_text(x_text + self.x_offset, y_blanc + 20, anchor="nw", text=blanc_txt or "—", font=("Arial", 16), tags="ui", fill="white")
        if score_blanc > 0:
            self.canvas.create_text(x_text + self.x_offset + 230, y_blanc + 20, anchor="nw", text=f"+{score_blanc}", font=("Arial", 14), fill="white", tags="ui", )

        self.canvas.create_text(x_text + self.x_offset, y_noir, anchor="nw", text="⚪ Blancs ont pris :", font=("Arial", 12), tags="ui", fill="white")
        self.canvas.create_text(x_text + self.x_offset, y_noir + 20, anchor="nw", text=noir_txt or "—", font=("Arial", 16), tags="ui", fill="white")
        if score_noir > 0:
            self.canvas.create_text(x_text + self.x_offset + 230, y_noir + 20, anchor="nw", text=f"+{score_noir}", font=("Arial", 14), tags="ui", fill="white")

    def attendre_click_case(self):
        self.click_coord = None
        self._clicked.set(False)
        self.root.bind("<Button-1>", self._on_click)
        self.root.wait_variable(self._clicked) 
        return self.click_coord  # retourne un tuple (x_case, y_case)

    def _on_click(self, event):
        # N'accepte le clic que si c'est sur le canvas (pas sur un bouton)
        if event.widget != self.canvas:
            return
        x_pixel = event.x
        y_pixel = event.y
        if x_pixel < self.x_offset:
            return
        plateau_max_x = self.positions_x[-1] + self.case_size
        plateau_max_y = self.positions_y[-1] + self.case_size
        if x_pixel >= plateau_max_x or y_pixel >= plateau_max_y:
            return

        col = None
        row = None
        for i, pos_x in enumerate(self.positions_x):
            if x_pixel < pos_x + self.case_size:
                col = i
                break
        for j, pos_y in enumerate(self.positions_y):
            if y_pixel < pos_y + self.case_size:
                row = j
                break
        if col is None or row is None:
            return

        if self.sens == "B":
            x_case, y_case = col, row
        else:
            x_case, y_case = 7 - col, 7 - row

        self.click_coord = (x_case, y_case)
        self.root.unbind("<Button-1>")
        self._clicked.set(True)

    def afficher_dot(self, plateau, n_case_1, l_case_1, joueur, is_en_passant_possible, en_passant_collone, is_rock_possible):
        legal_cases_no_echecs_liste_copy = liste_moov(plateau, n_case_1, l_case_1, joueur, is_en_passant_possible, en_passant_collone, is_rock_possible)
        for legals_cases in legal_cases_no_echecs_liste_copy:
            # Appliquer la rotation comme dans afficher_plateau
            if self.sens == "B":
                row, col = legals_cases  # ligne, colonne
            else:
                row, col = 7 - legals_cases[0], 7 - legals_cases[1]
            x = self.positions_x[col]
            y = self.positions_y[row]
            if plateau[legals_cases[0]][legals_cases[1]] == [" ", ""]:
                nom_fichier = "dot.png"
            else:
                nom_fichier = "prise.png"
            chemin_image = os.path.join("Pieces", nom_fichier)
            if nom_fichier not in self.images:
                self.images[nom_fichier] = tk.PhotoImage(file=chemin_image)
            self.canvas.create_image(x, y, image=self.images[nom_fichier], anchor=tk.NW, tags="pieces")

    def afficher_resultat_fin_partie(self, plateau, resultat, joueur, sens_affichage=None):
        """
        Affiche une image de victoire, défaite ou match nul en haut à droite des rois.
        - resultat : 0 = victoire, 1 = match nul
        - sens_affichage : "B" ou "N" (pour forcer l'orientation d'affichage)
        """
        def _afficher_images():
            roi_blanc_pos = None
            roi_noir_pos = None

            for i in range(8):
                for j in range(8):
                    piece, couleur = plateau[i][j]
                    if piece == "R":
                        if couleur == "B":
                            roi_blanc_pos = (i, j)
                        elif couleur == "N":
                            roi_noir_pos = (i, j)

            if roi_blanc_pos is None or roi_noir_pos is None:
                print("Erreur : roi blanc ou noir introuvable.")
                return

            noms = ["gagnant.png", "perdant.png", "nul - Copie.png"]
            for nom in noms:
                chemin = os.path.join("Pieces", nom)
                if nom not in self.images:
                    try:
                        self.images[nom] = tk.PhotoImage(file=chemin)
                    except Exception as e:
                        print(f"Erreur chargement {nom} :", e)
                        return

            # Fonction pour tourner les coordonnées selon le sens voulu
            def rotate(i, j, sens):
                if sens == "B":
                    return i, j
                else:
                    return 7 - i, 7 - j

            sens = sens_affichage if sens_affichage is not None else self.sens

            if resultat == 1:
                for (i, j) in [roi_blanc_pos, roi_noir_pos]:
                    ri, rj = rotate(i, j, sens)
                    x = self.positions_x[rj] + self.case_size * 0.5
                    y = self.positions_y[ri] - self.case_size * 0.5
                    if y < 0:
                        y = -26
                    if x > 682:
                        x = 664
                    self.canvas.create_image(x, y, image=self.images["nul - Copie.png"], anchor=tk.NW, tags="resultat")
            else:
                gagnant = joueur
                perdant = "N" if joueur == "B" else "B"
                positions = {"B": roi_blanc_pos, "N": roi_noir_pos}
                for nom_image, couleur in [("gagnant.png", gagnant), ("perdant.png", perdant)]:
                    i, j = positions[couleur]
                    ri, rj = rotate(i, j, sens)
                    # Correction : vérifie que ri et rj sont dans [0, 7]
                    print(positions, rj, ri)
                    x = self.positions_x[rj] + self.case_size * 0.5
                    y = self.positions_y[ri] - self.case_size * 0.5
                    if y < 0:
                        y = -26
                    if x > 682:
                        x = 664
                    self.canvas.create_image(x, y, image=self.images[nom_image], anchor=tk.NW, tags="resultat")

        self.root.after(100, _afficher_images)
    def promotion(self, couleur):
        choix_var = tk.StringVar()

        # Nouvelle fenêtre popup
        popup = tk.Toplevel(self.root)
        popup.title("Choisissez une pièce pour la promotion")
        popup.transient(self.root)
        popup.grab_set()  # bloque la fenêtre principale

        # Charger les images des pièces
        pieces = {
            "D": "q",
            "T": "r",
            "F": "b",
            "C": "n"
        }
        images = {}

        for code, suffixe in pieces.items():
            prefixe = "w" if couleur == "B" else "b"
            chemin = os.path.join("Pieces", f"{prefixe}{suffixe}.png")
            images[code] = tk.PhotoImage(file=chemin)

        # Fonction de sélection
        def choisir_piece(code):
            choix_var.set(code)
            popup.destroy()

        # Afficher les boutons avec images
        for i, (code, image) in enumerate(images.items()):
            bouton = tk.Button(popup, image=image, command=lambda c=code: choisir_piece(c))
            bouton.image = image  # pour éviter que l'image soit supprimée par le garbage collector
            bouton.grid(row=0, column=i, padx=10, pady=10)

        # Attente du choix
        self.root.wait_variable(choix_var)
        return choix_var.get()


    def lancer(self):
        self.root.mainloop()

def choisir_mode():
    accueil = tk.Tk()
    accueil.title("Choix du mode")
    mode_var = tk.StringVar(value="1v1")
    couleur_var = tk.StringVar(value="B")
    temps_var = tk.StringVar(value="0.1")
    temps_b_var = tk.StringVar(value="0.1")
    temps_n_var = tk.StringVar(value="0.1")
    online_host_var = tk.StringVar(value="host")
    online_couleur_var = tk.StringVar(value="B")
    ip_var = tk.StringVar(value="192.168.1.80")

    def choisir(val):
        mode_var.set(val)
        if val == "1v1":
            frame_couleur.pack_forget()
            frame_temps.pack_forget()
            frame_temps_sf.pack_forget()
            frame_online.pack_forget()
            accueil.destroy()
        elif val == "ordi":
            frame_couleur.pack(pady=10)
            frame_temps.pack(pady=10)
            frame_temps_sf.pack_forget()
            frame_online.pack_forget()
        elif val == "mon_ia":
            frame_couleur.pack(pady=10)
            frame_temps.pack_forget()
            frame_temps_sf.pack_forget()
            frame_online.pack_forget()
        elif val == "sf_vs_sf":
            frame_couleur.pack_forget()
            frame_temps.pack_forget()
            frame_temps_sf.pack(pady=10)
            frame_online.pack_forget()
        elif val == "online":
            frame_online.pack(pady=10)
            frame_couleur.pack_forget()
            frame_temps.pack_forget()
            frame_temps_sf.pack_forget()
            # Désactive le choix de couleur si on veut rejoindre
            if online_host_var.get() == "join":
                radio_online_blanc.config(state=tk.DISABLED)
                radio_online_noir.config(state=tk.DISABLED)
            else:
                radio_online_blanc.config(state=tk.NORMAL)
                radio_online_noir.config(state=tk.NORMAL)
    def on_online_host_change(*args):
        if online_host_var.get() == "join":
            radio_online_blanc.config(state=tk.DISABLED)
            radio_online_noir.config(state=tk.DISABLED)
        else:
            radio_online_blanc.config(state=tk.NORMAL)
            radio_online_noir.config(state=tk.NORMAL)

    online_host_var.trace("w", on_online_host_change)
    def valider():
        accueil.destroy()

    label = tk.Label(accueil, text="Choisissez un mode de jeu :", font=("Arial", 16))
    label.pack(padx=20, pady=20)

    bouton_1v1 = tk.Button(accueil, text="1v1 (deux joueurs)", width=25, command=lambda: choisir("1v1"))
    bouton_1v1.pack(pady=10)

    bouton_ordi = tk.Button(accueil, text="Contre Stockfish", width=25, command=lambda: choisir("ordi"))
    bouton_ordi.pack(pady=10)

    bouton_ia = tk.Button(accueil, text="Contre mon IA", width=25, command=lambda: choisir("mon_ia"))
    bouton_ia.pack(pady=10)

    bouton_sf_vs_sf = tk.Button(accueil, text="Stockfish vs Stockfish", width=25, command=lambda: choisir("sf_vs_sf"))
    bouton_sf_vs_sf.pack(pady=10)

    bouton_online = tk.Button(accueil, text="Jouer en ligne (ami)", width=25, command=lambda: choisir("online"))
    bouton_online.pack(pady=10)

    # Choix de la couleur (caché par défaut)
    frame_couleur = tk.Frame(accueil)
    label_couleur = tk.Label(frame_couleur, text="Vous jouez :", font=("Arial", 12))
    label_couleur.pack(side=tk.LEFT)
    radio_blanc = tk.Radiobutton(frame_couleur, text="Blancs", variable=couleur_var, value="B")
    radio_blanc.pack(side=tk.LEFT, padx=5)
    radio_noir = tk.Radiobutton(frame_couleur, text="Noirs", variable=couleur_var, value="N")
    radio_noir.pack(side=tk.LEFT, padx=5)

    # Champ pour le temps de réflexion (mode ordi)
    frame_temps = tk.Frame(accueil)
    label_temps = tk.Label(frame_temps, text="Temps de réflexion de Stockfish (secondes) :")
    label_temps.pack(side=tk.LEFT)
    entry_temps = tk.Entry(frame_temps, textvariable=temps_var, width=5)
    entry_temps.pack(side=tk.LEFT, padx=5)

    # Champs pour Stockfish vs Stockfish
    frame_temps_sf = tk.Frame(accueil)
    label_temps_b = tk.Label(frame_temps_sf, text="Temps Stockfish Blancs (s) :")
    label_temps_b.pack(side=tk.LEFT)
    entry_temps_b = tk.Entry(frame_temps_sf, textvariable=temps_b_var, width=5)
    entry_temps_b.pack(side=tk.LEFT, padx=5)
    label_temps_n = tk.Label(frame_temps_sf, text="Temps Stockfish Noirs (s) :")
    label_temps_n.pack(side=tk.LEFT)
    entry_temps_n = tk.Entry(frame_temps_sf, textvariable=temps_n_var, width=5)
    entry_temps_n.pack(side=tk.LEFT, padx=5)

    # Frame pour le mode online
    frame_online = tk.Frame(accueil)
    label_online = tk.Label(frame_online, text="Mode en ligne :")
    label_online.pack()
    radio_host = tk.Radiobutton(frame_online, text="Héberger la partie", variable=online_host_var, value="host")
    radio_host.pack(anchor=tk.W)
    radio_join = tk.Radiobutton(frame_online, text="Rejoindre une partie", variable=online_host_var, value="join")
    radio_join.pack(anchor=tk.W)
    label_online_couleur = tk.Label(frame_online, text="Votre couleur (si hôte) :")
    label_online_couleur.pack()
    radio_online_blanc = tk.Radiobutton(frame_online, text="Blancs", variable=online_couleur_var, value="B")
    radio_online_blanc.pack(anchor=tk.W)
    radio_online_noir = tk.Radiobutton(frame_online, text="Noirs", variable=online_couleur_var, value="N")
    radio_online_noir.pack(anchor=tk.W)
    label_ip = tk.Label(frame_online, text="Adresse IP de l'hôte (si rejoindre) :")
    label_ip.pack()
    entry_ip = tk.Entry(frame_online, textvariable=ip_var, width=20)
    entry_ip.pack()

    bouton_valider = tk.Button(accueil, text="Valider", command=valider)
    bouton_valider.pack(pady=20)

    accueil.mainloop()
    # Retourne les infos nécessaires pour le mode online
    return (mode_var.get(), couleur_var.get(), float(temps_var.get()), float(temps_b_var.get()), float(temps_n_var.get()),
            online_host_var.get(), online_couleur_var.get(), ip_var.get())

def is_legal_pion(plateau,n_case_1,l_case_1,n_case_2,l_case_2,is_en_passant_possible,en_passant_collone):
    if plateau[n_case_1][l_case_1][1]=="B": #Pion blanc
        
            
        if n_case_1-n_case_2==1 and l_case_1==l_case_2: #Avance d'un case
            if plateau[n_case_2][l_case_2][0]!=" ": #Case suivant pleine
                return False
        elif n_case_2==4 and l_case_1==l_case_2 and n_case_1==6: #Avance de 2 cases
            if not (plateau[n_case_2][l_case_2][0]==" "  and plateau[n_case_2+1][l_case_2][0]==" "): #Case suivant et celle d'après pleine
                return False
        elif n_case_1-n_case_2==1 and (l_case_2-l_case_1==1 or l_case_2-l_case_1==-1): #Si le pion va en diagonal
               
            if (is_en_passant_possible and n_case_1==3 and l_case_2 == en_passant_collone): #En passant
                return True
                
            elif plateau[n_case_2][l_case_2][0]==" ": #Case en diagonal vide
                return False
                
        else:
            return False
              

    else: #pion noir
       
            
        if n_case_2-n_case_1==1 and l_case_1==l_case_2: #Avance d'un case
            if not plateau[n_case_2][l_case_2][0]==" ": #Case suivant pleine
                return False
        elif n_case_2-n_case_1==2 and l_case_1==l_case_2: #Avance de 2 cases
            if not (plateau[n_case_2][l_case_2][0]==" "  and plateau[n_case_2-1][l_case_2][0]==" "): #Case suivant et celle d'après pleine
                return False
        elif n_case_2-n_case_1==1 and (l_case_2-l_case_1==1 or l_case_2-l_case_1==-1): #Si le pion va en diagonal
            if (is_en_passant_possible and n_case_1==4 and l_case_2 == en_passant_collone): #En passant
                return True
            
            elif plateau[n_case_2][l_case_2][0]==" ": #Case en diagonal vide
                return False 
        else:
                return False

    return True 

def is_legal_tour(plateau,n_case_1,l_case_1,n_case_2,l_case_2):
    
    if n_case_1 == n_case_2:
        cases = plateau[n_case_1][min(l_case_1, l_case_2) + 1:max(l_case_1, l_case_2)]
    elif l_case_1 == l_case_2:
        cases = [plateau[i][l_case_1] for i in range(min(n_case_1, n_case_2) + 1, max(n_case_1, n_case_2))]
    else:
        return False

    return all(case[0] == " " for case in cases)


def is_legal_fou(plateau,n_case_1,l_case_1,n_case_2,l_case_2):
    

    if abs(n_case_1 - n_case_2) != abs(l_case_1 - l_case_2):
        return False  # Vérifie si le mouvement est bien en diagonale

    # Détermine la direction du déplacement
    step_n = 1 if n_case_2 > n_case_1 else -1
    step_l = 1 if l_case_2 > l_case_1 else -1

    # Vérifie s'il y a des pièces sur le chemin
    return all(
        plateau[n_case_1 + i * step_n][l_case_1 + i * step_l][0] == " "
        for i in range(1, abs(n_case_1 - n_case_2))
    )


def is_legal_roi(plateau,n_case_1,l_case_1,n_case_2,l_case_2,joueur,is_rock_possible):
    if joueur=="B":
        if is_rock_possible[3]==True and l_case_1-l_case_2==2 and n_case_2==7 and plateau[7][l_case_1-1][0]==" " and plateau[7][l_case_1-2][0]==" " and plateau[7][l_case_1-3][0]==" ":
            
            return True 
        if is_rock_possible[2]==True and l_case_2-l_case_1==2 and n_case_2==7 and plateau[7][l_case_1+1][0]==" " and plateau[7][l_case_1+2][0]==" ":
            
            return True 

    else:
        if is_rock_possible[0]==True and l_case_1-l_case_2==2 and n_case_2==0 and plateau[0][l_case_1-1][0]==" " and plateau[0][l_case_1-2][0]==" " and plateau[0][l_case_1-3][0]==" ":
            
            return True 
        if is_rock_possible[1]==True and l_case_2-l_case_1==2 and n_case_2==0 and plateau[0][l_case_1+1][0]==" " and plateau[0][l_case_1+2][0]==" ":
            
            return True 

    if abs(n_case_1-n_case_2)>1 or abs(l_case_1-l_case_2)>1:
        return False

def is_legal_cavalier(n_case_1,l_case_1,n_case_2,l_case_2):
    if not((abs(n_case_2-n_case_1)==2 and abs(l_case_2-l_case_1)==1) or (abs(n_case_2-n_case_1)==1 and abs(l_case_2-l_case_1)==2)):
        return False

def is_legal(plateau,n_case_1,l_case_1,n_case_2,l_case_2,joueur,is_en_passant_possible,en_passant_collone,is_rock_possible,check_eat):
  
    if (plateau[n_case_1][l_case_1][0]==" ") or (plateau[n_case_1][l_case_1][1]==plateau[n_case_2][l_case_2][1]) or (plateau[n_case_1][l_case_1][1]!=joueur) or (n_case_1==n_case_2 and l_case_1==l_case_2) or ((not check_eat) and plateau[n_case_2][l_case_2][0] != " ") or (plateau[n_case_1][l_case_1][0]=="P" and is_legal_pion(plateau,n_case_1,l_case_1,n_case_2,l_case_2,is_en_passant_possible,en_passant_collone)==False) or (plateau[n_case_1][l_case_1][0]=="T" and is_legal_tour(plateau,n_case_1,l_case_1,n_case_2,l_case_2)==False) or (plateau[n_case_1][l_case_1][0]=="F" and is_legal_fou(plateau,n_case_1,l_case_1,n_case_2,l_case_2)==False) or (plateau[n_case_1][l_case_1][0]=="D" and is_legal_tour(plateau,n_case_1,l_case_1,n_case_2,l_case_2)==False and is_legal_fou(plateau,n_case_1,l_case_1,n_case_2,l_case_2)==False) or (plateau[n_case_1][l_case_1][0]=="R" and is_legal_roi(plateau,n_case_1,l_case_1,n_case_2,l_case_2,joueur,is_rock_possible)==False) or (plateau[n_case_1][l_case_1][0]=="C" and is_legal_cavalier(n_case_1,l_case_1,n_case_2,l_case_2)==False):
      return False
    return True      



def move(plateau,x_case,y_case,second_time,n_case_1,l_case_1,joueur,is_en_passant_possible,en_passant_collone,is_rock_possible):

    
    legal_cases_no_echecs_liste_copy = liste_moov(plateau,n_case_1,l_case_1,joueur,is_en_passant_possible,en_passant_collone,is_rock_possible)
    
    good_second_selected_case = False


    while good_second_selected_case == False:
        #x_case = int(input("x_case : "))
        #y_case = int(input("y_case : "))
        x_case, y_case = afficheur.attendre_click_case()
        



        if second_time==True:
            for legals_cases in legal_cases_no_echecs_liste_copy:
                pass #Afficher les cases possibles 
            if [y_case,x_case] in legal_cases_no_echecs_liste_copy or [y_case,x_case] == [n_case_1,l_case_1] or plateau[y_case][x_case][1] == joueur:
                good_second_selected_case = True
            else:
                good_second_selected_case = False
        else:
            good_second_selected_case = True
    return x_case,y_case,legal_cases_no_echecs_liste_copy





def is_echecs(plateau,joueur,is_en_passant_possible,en_passant_collone,is_rock_possible, invert_joueur = False):
    if invert_joueur == True:
        if joueur == "N":
            joueur = "B"
        else:
            joueur ="N"

    for i in range(8):
        for j in range(8):
            if plateau[i][j][0] == "R" and plateau[i][j][1] != joueur:
                coord_roi=[i,j]

    for i in range(8):
        for j in range(8):
            if is_legal(plateau,i,j,coord_roi[0],coord_roi[1],joueur,is_en_passant_possible,en_passant_collone,is_rock_possible,True) == True:
                return True
    return False


def liste_moov(plateau,n_case_1,l_case_1,joueur,is_en_passant_possible,en_passant_collone,is_rock_possible):
    legal_cases_no_echecs_liste = []
    for i in range(8):
        for j in range(8):
            if is_legal(plateau,n_case_1,l_case_1,i,j,joueur,is_en_passant_possible,en_passant_collone,is_rock_possible,True):
                legal_cases_no_echecs_liste.append([i,j])
    

    legal_cases_no_echecs_liste_copy = [row[:] for row in legal_cases_no_echecs_liste]
    if plateau[n_case_1][l_case_1] == ["R",joueur] and is_echecs(plateau,joueur,is_en_passant_possible,en_passant_collone,is_rock_possible):
        for legals_cases in legal_cases_no_echecs_liste_copy:
            if legals_cases[1] == l_case_1+2 or legals_cases[1] == l_case_1-2:
                legal_cases_no_echecs_liste.remove(legals_cases)
            
            

    for legals_cases in legal_cases_no_echecs_liste:

        plateau_temp = [row[:] for row in plateau]


        if is_en_passant_possible == True and n_case_1==3 and legals_cases[1] == en_passant_collone and plateau_temp[n_case_1][l_case_1][0]=="P" and joueur == "B":
            plateau_temp[n_case_1][legals_cases[1]]=[" ",""]
        if is_en_passant_possible == True and n_case_1==4 and legals_cases[1] == en_passant_collone and plateau_temp[n_case_1][l_case_1][0]=="P" and joueur == "N":
            plateau_temp[n_case_1][legals_cases[1]]=[" ",""]
        
        if joueur == "B":
           
            if plateau_temp[n_case_1][l_case_1][0]=="R" and l_case_1-legals_cases[1]==2:
                plateau_temp[7][0]=[" ",""]
                plateau_temp[7][3]=["T","B"]

            if plateau_temp[n_case_1][l_case_1][0]=="R" and legals_cases[1]-l_case_1==2:
                plateau_temp[7][7]=[" ",""]
                plateau_temp[7][5]=["T","B"]

        else:
        
            if plateau_temp[n_case_1][l_case_1][0]=="R" and l_case_1-legals_cases[1]==2:
                plateau_temp[0][0]=[" ",""]
                plateau_temp[0][3]=["T","N"]

            if plateau_temp[n_case_1][l_case_1][0]=="R" and legals_cases[1]-l_case_1==2:
                plateau_temp[0][7]=[" ",""]
                plateau_temp[0][5]=["T","N"]
                

        plateau_temp[legals_cases[0]][legals_cases[1]]=plateau_temp[n_case_1][l_case_1]
        plateau_temp[n_case_1][l_case_1]=[" ",""]

        invert_joueur = joueur
        if invert_joueur == "N":
            invert_joueur = "B"
        else:
            invert_joueur = "N"
        
        if is_echecs(plateau_temp,invert_joueur,is_en_passant_possible,en_passant_collone,is_rock_possible):
             
            if legals_cases in legal_cases_no_echecs_liste_copy:
                legal_cases_no_echecs_liste_copy.remove(legals_cases)

            if plateau[n_case_1][l_case_1] == ["R",joueur]:
                if [legals_cases[0],legals_cases[1]-1] in legal_cases_no_echecs_liste_copy and n_case_1 == legals_cases[0]:
                    legal_cases_no_echecs_liste_copy.remove([legals_cases[0],legals_cases[1]-1])
                if [legals_cases[0],legals_cases[1]+1] in legal_cases_no_echecs_liste_copy and n_case_1 == legals_cases[0]:
                    legal_cases_no_echecs_liste_copy.remove([legals_cases[0],legals_cases[1]+1])


    return legal_cases_no_echecs_liste_copy

def can_moov(plateau,joueur,is_en_passant_possible,en_passant_collone,is_rock_possible):
    liste_pieces_joueur = []
    for i in range(8):
        for j in range(8):
            if plateau[i][j][1] == joueur:
                liste_pieces_joueur.append([i,j])
    for pieces in liste_pieces_joueur:
        if liste_moov(plateau,pieces[0],pieces[1],joueur,is_en_passant_possible,en_passant_collone,is_rock_possible) != []:
            return True
    return False

def est_nulle_par_manque_de_materiel(liste_blanc, liste_noire):
    if liste_blanc == {"R": 1, "D": 0, "P": 0, "F": 0, "C": 0, "T": 0} and \
       liste_noire == {"R": 1, "D": 0, "P": 0, "F": 0, "C": 0, "T": 0}:
        return True

    if (liste_blanc == {"R": 1, "D": 0, "P": 0, "F": 1, "C": 0, "T": 0} and liste_noire == {"R": 1, "D": 0, "P": 0, "F": 0, "C": 0, "T": 0}) or \
       (liste_noire == {"R": 1, "D": 0, "P": 0, "F": 1, "C": 0, "T": 0} and liste_blanc == {"R": 1, "D": 0, "P": 0, "F": 0, "C": 0, "T": 0}):
        return True

    if (liste_blanc == {"R": 1, "D": 0, "P": 0, "F": 0, "C": 1, "T": 0} and liste_noire == {"R": 1, "D": 0, "P": 0, "F": 0, "C": 0, "T": 0}) or \
       (liste_noire == {"R": 1, "D": 0, "P": 0, "F": 0, "C": 1, "T": 0} and liste_blanc == {"R": 1, "D": 0, "P": 0, "F": 0, "C": 0, "T": 0}):
        return True

    if liste_blanc["F"] == 1 and liste_noire["F"] == 1 and sum(liste_blanc.values()) == 2 and sum(liste_noire.values()) == 2:
        return True  

    return False

def plateau_to_fen(plateau, joueur, is_rock_possible, is_en_passant_possible, en_passant_collone):
    # Pièces
    pieces = {"P":"P", "T":"R", "C":"N", "F":"B", "D":"Q", "R":"K"}
    rows = []
    for i in range(8):
        row = ""
        empty = 0
        for j in range(8):
            piece, couleur = plateau[i][j]
            if piece == " ":
                empty += 1
            else:
                if empty > 0:
                    row += str(empty)
                    empty = 0
                symbol = pieces.get(piece, "")
                if couleur == "N":
                    symbol = symbol.lower()
                row += symbol
        if empty > 0:
            row += str(empty)
        rows.append(row)
    fen_rows = "/".join(rows)

    # Joueur
    fen_joueur = "w" if joueur == "B" else "b"

    # Roque
    roque = ""
    if is_rock_possible[2]:  # bas à droite (blancs roque roi)
        roque += "K"
    if is_rock_possible[3]:  # bas à gauche (blancs roque dame)
        roque += "Q"
    if is_rock_possible[0]:  # haut à gauche (noirs roque dame)
        roque += "q"
    if is_rock_possible[1]:  # haut à droite (noirs roque roi)
        roque += "k"
    if roque == "":
        roque = "-"

    # Prise en passant
    if is_en_passant_possible:
        # Trouver la rangée et colonne de la case en passant
        # Pour les blancs, le pion noir vient de jouer de la 6 à la 4 (ligne 3 à 5 en index python)
        # Pour les noirs, le pion blanc vient de jouer de la 1 à la 3 (ligne 4 à 2 en index python)
        if joueur == "B":
            row = 3  # ligne 4 en notation échiquier
        else:
            row = 4  # ligne 3 en notation échiquier
        col = en_passant_collone
        # Conversion colonne/ligne vers notation échiquier
        file = chr(ord('a') + col)
        rank = str(8 - row)
        en_passant = file + rank
    else:
        en_passant = "-"

    # Les deux derniers champs (demi-coup, numéro du coup) sont mis à 0 et 1 par défaut
    fen = f"{fen_rows} {fen_joueur} {roque} {en_passant} 0 1"
    return fen

def get_stockfish_eval(board, engine, temps=0.3):
    # board : objet chess.Board (python-chess)
    info = engine.analyse(board, chess.engine.Limit(time=temps))
    score = info["score"].white().score(mate_score=10000)
    # score > 0 : avantage blanc, score < 0 : avantage noir
    return score

def on_close():
    global end_game, engine
    end_game = True
    try:
        engine.quit()
    except Exception:
        pass
    afficheur.root.destroy()


def analyse_continue(afficheur, engine):
    print("Thread analyse_continue lancé")
    def worker():
        global plateau, joueur, is_rock_possible, is_en_passant_possible, en_passant_collone, end_game
        while not end_game:
            try:
                """if not hasattr(engine, "process") or engine.process is None:
                    break"""
                fen = plateau_to_fen(plateau, joueur, is_rock_possible, is_en_passant_possible, en_passant_collone)
                board = chess.Board(fen)
                info = engine.analyse(board, chess.engine.Limit(time=0.2))
                score = info["score"].white().score(mate_score=10000)
                afficheur.root.after(0, afficheur.afficher_barre_eval, score)
            except Exception as e:
                print("Erreur dans analyse_continue :", e)
                break
            sleep(0.3)
    threading.Thread(target=worker, daemon=True).start()
   


def jouer_tour():
    global end_game, joueur, first_play, last_two_cases, liste_plateaux
    global is_en_passant_possible, en_passant_collone, is_rock_possible
    global liste_blanc, liste_noire
    global x_case, y_case, n_case_1, l_case_1, n_case_2, l_case_2
    global mode_jeu, couleur_joueur
    global temps_stockfish, temps_sf_b, temps_sf_n
    global engine
    global afficheur
    global temps


    if end_game:
        return
    fen = plateau_to_fen(plateau, joueur, is_rock_possible, is_en_passant_possible, en_passant_collone)
    board = chess.Board(fen)
    #score = get_stockfish_eval(board, engine, temps=0.05)
    #afficheur.afficher_barre_eval(score)
        
    if mode_jeu == "sf_vs_sf":
        recommencer = True
        while recommencer:
            # Détermine le temps selon le joueur
            if joueur == "B":
                temps = temps_sf_b
            else:
                temps = temps_sf_n

            if first_play:
                afficheur.afficher_plateau(plateau, liste_blanc, liste_noire)
            else:
                afficheur.afficher_plateau(plateau, liste_blanc, liste_noire, None, None, last_two_cases[0][0], last_two_cases[0][1], last_two_cases[1][0], last_two_cases[1][1])

            fen = plateau_to_fen(plateau, joueur, is_rock_possible, is_en_passant_possible, en_passant_collone)
            board = chess.Board(fen)
            afficheur.root.update_idletasks()
            afficheur.root.update()
            recommencer = False
            try:
                result = engine.play(board, chess.engine.Limit(time=temps))
            except concurrent.futures.CancelledError:
                recommencer = True
                print("Coup annulé, réessayer")
            if not recommencer:
                uci_move = result.move
                depart_i = 7 - chess.square_rank(uci_move.from_square)
                depart_j = chess.square_file(uci_move.from_square)
                arrivee_i = 7 - chess.square_rank(uci_move.to_square)
                arrivee_j = chess.square_file(uci_move.to_square)

                x_case, y_case = depart_j, depart_i
                n_case_1, l_case_1 = depart_i, depart_j
                n_case_2, l_case_2 = arrivee_i, arrivee_j


    elif mode_jeu == "ordi" and joueur != couleur_joueur:
        recommencer = True
        while recommencer:
            if first_play:
                afficheur.afficher_plateau(plateau,liste_blanc, liste_noire)
            else:
                afficheur.afficher_plateau(plateau,liste_blanc, liste_noire, None, None, last_two_cases[0][0], last_two_cases[0][1], last_two_cases[1][0], last_two_cases[1][1])

            fen = plateau_to_fen(plateau, joueur, is_rock_possible, is_en_passant_possible, en_passant_collone)
            board = chess.Board(fen)
            afficheur.root.update_idletasks()
            afficheur.root.update()
            recommencer = False
            try:
                result = engine.play(board, chess.engine.Limit(time=temps_stockfish))
            except concurrent.futures.CancelledError:
                recommencer = True
                print("Coup annulé, réessayer")
            if not recommencer:
                uci_move = result.move
                # Conversion UCI vers indices de ton plateau
                depart_i = 7 - chess.square_rank(uci_move.from_square)
                depart_j = chess.square_file(uci_move.from_square)
                arrivee_i = 7 - chess.square_rank(uci_move.to_square)
                arrivee_j = chess.square_file(uci_move.to_square)

                x_case, y_case = depart_j, depart_i
                n_case_1, l_case_1 = depart_i, depart_j
                n_case_2, l_case_2 = arrivee_i, arrivee_j   


    elif mode_jeu == "mon_ia" and joueur != couleur_joueur:
        if first_play:
            afficheur.afficher_plateau(plateau,liste_blanc, liste_noire)
        else:
            afficheur.afficher_plateau(plateau,liste_blanc, liste_noire, None, None, last_two_cases[0][0], last_two_cases[0][1], last_two_cases[1][0], last_two_cases[1][1])

        # L'ordinateur joue un coup random pour les noirs
        coups_possibles = []
        for i in range(8):
            for j in range(8):
                if plateau[i][j][1] == joueur:
                    moves = liste_moov(plateau, i, j, joueur, is_en_passant_possible, en_passant_collone, is_rock_possible)
                    for move1 in moves:
                        coups_possibles.append((i, j, move1[0], move1[1]))
        if coups_possibles:
            depart_i, depart_j, arrivee_i, arrivee_j = random.choice(coups_possibles)
            # Simule le clic sur la pièce puis sur la destination
            x_case, y_case = depart_j, depart_i
            n_case_1, l_case_1 = depart_i, depart_j
            n_case_2, l_case_2 = arrivee_i, arrivee_j
            
    elif mode_jeu == "1v1" or mode_jeu == "ordi" and joueur == couleur_joueur or mode_jeu == "mon_ia" and joueur == couleur_joueur:
        good_second_case = False
        while good_second_case == False:

            
            
            if joueur=="B":
                print("Au blancs de jouer")
            else:
                print("Au noirs de jouer")

            good_selected_case=False
            while not good_selected_case:
                if first_play:
                    afficheur.afficher_plateau(plateau,liste_blanc, liste_noire)
                else:
                    afficheur.afficher_plateau(plateau,liste_blanc, liste_noire, None, None, last_two_cases[0][0], last_two_cases[0][1], last_two_cases[1][0], last_two_cases[1][1])

                
                result=move(plateau,x_case,y_case,False,0,0,joueur,is_en_passant_possible,en_passant_collone,is_rock_possible)    
            
                y_case,n_case_1 = result[1],result[1]
                x_case,l_case_1 = result[0],result[0]
                
                

                if plateau[n_case_1][l_case_1][0] != " " and plateau[n_case_1][l_case_1][1]==joueur:
                    good_selected_case = True
                print("case séléctioné : ",x_case," ",y_case)

                if first_play:
                    afficheur.afficher_plateau(plateau,liste_blanc, liste_noire, x_case, y_case)
                else:
                    if plateau[x_case][y_case][1] == joueur:
                        afficheur.afficher_plateau(plateau,liste_blanc, liste_noire, x_case, y_case, last_two_cases[0][0], last_two_cases[0][1], last_two_cases[1][0], last_two_cases[1][1])
                    else:
                        afficheur.afficher_plateau(plateau,liste_blanc, liste_noire, None, None, last_two_cases[0][0], last_two_cases[0][1], last_two_cases[1][0], last_two_cases[1][1])

            selected_same_color = True
            while selected_same_color == True:
                if first_play:
                    afficheur.afficher_plateau(plateau,liste_blanc, liste_noire, x_case, y_case)
                else:
                    afficheur.afficher_plateau(plateau,liste_blanc, liste_noire, x_case, y_case, last_two_cases[0][0], last_two_cases[0][1], last_two_cases[1][0], last_two_cases[1][1])

                afficheur.afficher_dot(plateau,n_case_1,l_case_1,joueur,is_en_passant_possible,en_passant_collone,is_rock_possible)


                result=move(plateau,x_case,y_case,True,n_case_1,l_case_1,joueur,is_en_passant_possible,en_passant_collone,is_rock_possible)    
                
                y_case,n_case_2 = result[1],result[1]
                x_case,l_case_2 = result[0],result[0]
                legal_cases_no_echecs_liste_copy = result[2]



                if plateau[y_case][x_case][1] != joueur or [y_case,x_case] == [n_case_1,l_case_1]:   
                    selected_same_color = False
                else:
            
                    n_case_1 = y_case
                    l_case_1 = x_case

                for i in legal_cases_no_echecs_liste_copy:
                    if i == [y_case,x_case]:
                        good_second_case = True
                        

            if first_play:
                afficheur.afficher_plateau(plateau,liste_blanc, liste_noire, x_case, y_case)
            else:
                afficheur.afficher_plateau(plateau,liste_blanc, liste_noire, x_case, y_case, last_two_cases[0][0], last_two_cases[0][1], last_two_cases[1][0], last_two_cases[1][1])

    elif mode_jeu == "online":
        afficheur.sens = couleur_joueur
        afficheur.afficher_plateau(plateau, liste_blanc, liste_noire)
        afficheur.root.update_idletasks()
        afficheur.root.update()
        print("joueur, couleur_joueur: ", joueur, couleur_joueur)
        mon_tour = (joueur == couleur_joueur)#couleur_joueur_online
        if mon_tour:
            # Joueur local joue
            good_second_case = False
            while not good_second_case:
                if joueur == "B":
                    print("À toi (blancs)")
                else:
                    print("À toi (noirs)")
                good_selected_case = False
                while not good_selected_case:
                    if first_play:
                        afficheur.afficher_plateau(plateau, liste_blanc, liste_noire)
                    else:
                        afficheur.afficher_plateau(plateau, liste_blanc, liste_noire, None, None, last_two_cases[0][0], last_two_cases[0][1], last_two_cases[1][0], last_two_cases[1][1])
                    result = move(plateau, x_case, y_case, False, 0, 0, joueur, is_en_passant_possible, en_passant_collone, is_rock_possible)
                    y_case, n_case_1 = result[1], result[1]
                    x_case, l_case_1 = result[0], result[0]
                    if plateau[n_case_1][l_case_1][0] != " " and plateau[n_case_1][l_case_1][1] == joueur:
                        good_selected_case = True
                selected_same_color = True
                while selected_same_color:
                    if first_play:
                        afficheur.afficher_plateau(plateau, liste_blanc, liste_noire, x_case, y_case)
                    else:
                        afficheur.afficher_plateau(plateau, liste_blanc, liste_noire, x_case, y_case, last_two_cases[0][0], last_two_cases[0][1], last_two_cases[1][0], last_two_cases[1][1])
                    afficheur.afficher_dot(plateau, n_case_1, l_case_1, joueur, is_en_passant_possible, en_passant_collone, is_rock_possible)
                    result = move(plateau, x_case, y_case, True, n_case_1, l_case_1, joueur, is_en_passant_possible, en_passant_collone, is_rock_possible)
                    y_case, n_case_2 = result[1], result[1]
                    x_case, l_case_2 = result[0], result[0]
                    legal_cases_no_echecs_liste_copy = result[2]
                    if plateau[y_case][x_case][1] != joueur or [y_case, x_case] == [n_case_1, l_case_1]:
                        selected_same_color = False
                    else:
                        n_case_1 = y_case
                        l_case_1 = x_case
                    for i in legal_cases_no_echecs_liste_copy:
                        if i == [y_case, x_case]:
                            good_second_case = True
            # Envoie le coup au format "n_case_1,l_case_1,n_case_2,l_case_2"
            """move_str = f"{n_case_1},{l_case_1},{n_case_2},{l_case_2}"
            net.send_move(move_str)"""
        else:
            print("En attente du coup de l'adversaire...")
            move_str = net.receive_move()
            n_case_1, l_case_1, n_case_2, l_case_2 = map(int, move_str.split(","))
            x_case, y_case = l_case_2, n_case_2

        

    if (is_en_passant_possible == True and n_case_1==3 and l_case_2 == en_passant_collone and plateau[n_case_1][l_case_1][0]=="P" and joueur == "B") or (is_en_passant_possible == True and n_case_1==4 and l_case_2 == en_passant_collone and plateau[n_case_1][l_case_1][0]=="P" and joueur == "N"):
        plateau[n_case_1][l_case_2]=[" ",""]
        
        
    
    if joueur == "B":
        if plateau[n_case_1][l_case_1][0]=="P" and n_case_1-n_case_2==2:    #En passant
            is_en_passant_possible = True
            en_passant_collone = l_case_1
        else:
            is_en_passant_possible = False

        if plateau[n_case_1][l_case_1][0]=="R": #Rock
            is_rock_possible[2] = False
            is_rock_possible[3] = False

        if (plateau[n_case_1][l_case_1][0]=="R"and n_case_1==7 and l_case_1==0) or n_case_2==7 and l_case_2==0:
            is_rock_possible[3] = False

        if (plateau[n_case_1][l_case_1][0]=="R"and n_case_1==7 and l_case_1==7) or n_case_2==7 and l_case_2==7:
            is_rock_possible[2] = False

        if plateau[n_case_1][l_case_1][0]=="R" and l_case_1-l_case_2==2:
            plateau[7][0]=[" ",""]
            plateau[7][3]=["T","B"]

        if plateau[n_case_1][l_case_1][0]=="R" and l_case_2-l_case_1==2:
            plateau[7][7]=[" ",""]
            plateau[7][5]=["T","B"]

    else:
        if plateau[n_case_1][l_case_1][0]=="P" and n_case_2-n_case_1==2:
            is_en_passant_possible = True
            en_passant_collone = l_case_1
        else:
            is_en_passant_possible = False

        if plateau[n_case_1][l_case_1][0]=="R": #Rock
            is_rock_possible[0] = False
            is_rock_possible[1] = False
        if (plateau[n_case_1][l_case_1][0]=="R"and n_case_1==0 and l_case_1==0) or n_case_2==0 and l_case_2==0:
            is_rock_possible[0] = False
        if (plateau[n_case_1][l_case_1][0]=="R"and n_case_1==0 and l_case_1==7) or n_case_2==0 and l_case_2==7:
            is_rock_possible[1] = False

        if plateau[n_case_1][l_case_1][0]=="R" and l_case_1-l_case_2==2:
            plateau[0][0]=[" ",""]
            plateau[0][3]=["T","N"]

        if plateau[n_case_1][l_case_1][0]=="R" and l_case_2-l_case_1==2:
            plateau[0][7]=[" ",""]
            plateau[0][5]=["T","N"]


    plateau[n_case_2][l_case_2]=plateau[n_case_1][l_case_1]
    plateau[n_case_1][l_case_1]=[" ",""]
    
    promotion_piece = None
    if mode_jeu in ("ordi", "sf_vs_sf") and joueur != couleur_joueur and 'uci_move' in locals():
        if uci_move.promotion:
            mapping = {1: "C", 2: "F", 3: "T", 4: "D"}
            promotion_piece = mapping.get(uci_move.promotion, "D")
    # Promotion IA Stockfish
    if plateau[0][l_case_2][0] == "P" or plateau[7][l_case_2][0] == "P":
        if mode_jeu in ("ordi", "sf_vs_sf", "mon_ia") and joueur != couleur_joueur:
            if promotion_piece:
                plateau[n_case_2][l_case_2] = [promotion_piece, joueur]
            else:
                plateau[n_case_2][l_case_2] = ["D", joueur]
        else:
            plateau[n_case_2][l_case_2] = [afficheur.promotion(joueur), joueur]

    if joueur=="B":
        joueur="N"
    else:
        joueur="B"
    if afficheur.auto_rotate.get():
        afficheur.sens = joueur
    liste_plateaux.append(copy.deepcopy(plateau))
    last_two_cases = [[l_case_1,n_case_1],[l_case_2,n_case_2]]
    if can_moov(plateau,joueur,is_en_passant_possible,en_passant_collone,is_rock_possible) == True:
        
        if is_echecs(plateau, joueur, is_en_passant_possible, en_passant_collone, is_rock_possible, True):
            print("échecs")
     
        pass
    else:
        if is_echecs(plateau, joueur, is_en_passant_possible, en_passant_collone, is_rock_possible, True):
            print("Victoire")
            if joueur == "N":
                
                print("des blancs")
                if not afficheur.auto_rotate.get():
                    afficheur.sens = couleur_joueur
                    afficheur.afficher_plateau(plateau, liste_blanc, liste_noire, None, None, last_two_cases[0][0], last_two_cases[0][1], last_two_cases[1][0], last_two_cases[1][1])
                    afficheur.afficher_resultat_fin_partie(plateau, resultat=0, joueur="B", sens_affichage = couleur_joueur)
                else:
                    afficheur.sens = "B"
                    afficheur.afficher_plateau(plateau, liste_blanc, liste_noire, None, None, last_two_cases[0][0], last_two_cases[0][1], last_two_cases[1][0], last_two_cases[1][1])
                    afficheur.afficher_resultat_fin_partie(plateau, resultat=0, joueur="B", sens_affichage = "B")
            else:
                print("des noirs")
                if not afficheur.auto_rotate.get():
                    afficheur.sens = couleur_joueur
                    afficheur.afficher_plateau(plateau, liste_blanc, liste_noire, None, None, last_two_cases[0][0], last_two_cases[0][1], last_two_cases[1][0], last_two_cases[1][1])
                    afficheur.afficher_resultat_fin_partie(plateau, resultat=0, joueur="N", sens_affichage = couleur_joueur)
                else:
                    afficheur.sens = "N"
                    afficheur.afficher_plateau(plateau, liste_blanc, liste_noire, None, None, last_two_cases[0][0], last_two_cases[0][1], last_two_cases[1][0], last_two_cases[1][1])
                    afficheur.afficher_resultat_fin_partie(plateau, resultat=0, joueur="N", sens_affichage = "N")
        else:
            afficheur.sens = "N" if joueur == "B" else "B"
            print("nul")
            afficheur.afficher_plateau(plateau, liste_blanc, liste_noire, None, None, last_two_cases[0][0], last_two_cases[0][1], last_two_cases[1][0], last_two_cases[1][1])
            afficheur.afficher_resultat_fin_partie(plateau, resultat=1, joueur=None)
        
        end_game = True

    liste_blanc={"R":0,"D":0,"P":0,"F":0,"C":0,"T":0}
    liste_noire={"R":0,"D":0,"P":0,"F":0,"C":0,"T":0}
    for rows in plateau:
        for cases in rows:
            if cases[1] == "B":
                liste_blanc[cases[0]] += 1
            if cases[1] == "N":
                liste_noire[cases[0]] += 1
   
    if est_nulle_par_manque_de_materiel(liste_blanc,liste_noire):
        end_game = True
        print("nul")
        afficheur.sens = "N" if joueur == "B" else "B"
        afficheur.afficher_plateau(plateau, liste_blanc, liste_noire, None, None, last_two_cases[0][0], last_two_cases[0][1], last_two_cases[1][0], last_two_cases[1][1])
        afficheur.afficher_resultat_fin_partie(plateau, resultat=1, joueur=None)
    if liste_plateaux.count(plateau) == 3:
        if afficheur.auto_rotate.get():
            afficheur.sens = "N" if joueur == "B" else "B"
        afficheur.afficher_plateau(plateau, liste_blanc, liste_noire, None, None, last_two_cases[0][0], last_two_cases[0][1], last_two_cases[1][0], last_two_cases[1][1])
        afficheur.afficher_resultat_fin_partie(plateau, resultat=1, joueur=None)
        end_game = True
        print("nul")

    if not afficheur.auto_rotate.get():
        afficheur.sens = couleur_joueur
    
    if mode_jeu == "online":
        if mon_tour:
            afficheur.afficher_plateau(plateau, liste_blanc, liste_noire, None, None, last_two_cases[0][0], last_two_cases[0][1], last_two_cases[1][0], last_two_cases[1][1])
            move_str = f"{n_case_1},{l_case_1},{n_case_2},{l_case_2}"
            net.send_move(move_str)
    first_play = False
    afficheur.root.after(10, jouer_tour)
 

mode_jeu, couleur_joueur, temps_stockfish, temps_sf_b, temps_sf_n, online_host, online_couleur, ip_ami = choisir_mode()

print("temps_sf_b", temps_sf_b)
print("temps_sf_n", temps_sf_n)
print("online_couleur", online_couleur)
if mode_jeu == "online":
    is_host = (online_host == "host")
    if is_host:
        couleur_joueur_online = online_couleur

    else:
        # Le client prend TOUJOURS l'opposé de la couleur choisie par le host

        couleur_joueur = "B" if online_couleur == "N" else "N"
        
        # Et on ignore la valeur du menu côté client !
        #print("Couleur choisie par le host :", couleur_joueur_online)
        print("couleur_joueur :", couleur_joueur)
    net = NetworkChess(is_host, ip_ami if not is_host else None)

else:
    net = None
    couleur_joueur_online = None
if mode_jeu == "sf_vs_sf":
    joueur = "B"
elif mode_jeu == "ordi":
    joueur = "B"  # pour que ce soit le joueur humain qui commence
elif mode_jeu == "online":
    joueur = "B"
else:
    joueur = "B"




x_case = 0
y_case = 0
is_en_passant_possible = False
en_passant_collone = 0
is_rock_possible = [True,True,True,True]    #haut à gauche/haut à droite/bas à droite/bas à gauche
legal_cases_no_echecs_liste_copy=[]
draw_plateau(plateau)
afficheur = AfficheurEchiquier()
if mode_jeu in ("ordi", "sf_vs_sf"):
    afficheur.auto_rotate.set(False)
    afficheur.sens = couleur_joueur
liste_blanc={"R":1,"D":1,"P":8,"F":2,"C":2,"T":2}
liste_noire={"R":1,"D":1,"P":8,"F":2,"C":2,"T":2}
afficheur.afficher_plateau(plateau, liste_blanc, liste_noire)
end_game = False
last_two_cases = [[0,0],[0,0]]
first_play = True
liste_plateaux = []
liste_plateaux.append(copy.deepcopy(plateau))
engine = chess.engine.SimpleEngine.popen_uci("stockfish/stockfish-windows-x86-64-avx2.exe") 



def start_threads():
    analyse_continue(afficheur, engine)
    jouer_tour()

afficheur.root.after(200, start_threads)
afficheur.root.protocol("WM_DELETE_WINDOW", on_close)
afficheur.lancer()


afficheur.afficher_plateau(plateau,liste_blanc, liste_noire, None, None, last_two_cases[0][0], last_two_cases[0][1], last_two_cases[1][0], last_two_cases[1][1])
x_case, y_case = afficheur.attendre_click_case()