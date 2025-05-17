from math import *
from time import *
import tkinter as tk
import os
import copy



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



class AfficheurEchiquier:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Échiquier")
        self.board_size = 728
        self.case_size = 91
        self.canvas = tk.Canvas(self.root, width=self.board_size+300, height=self.board_size)
        self.canvas.pack()
        self.images = {}
        self.fond_img = tk.PhotoImage(file=os.path.join("Pieces", "200.png"))
        self.canvas.create_image(0, 0, image=self.fond_img, anchor=tk.NW)
        self.correspondance = {
            "P": "p", "T": "r", "C": "n",
            "F": "b", "D": "q", "R": "k"
        }
        espacement_total = self.board_size - (self.case_size * 8)
        espacement = espacement_total // 7
        self.positions = [0]
        self._clicked = tk.BooleanVar()
        for _ in range(1, 8):
            self.positions.append(self.positions[-1] + self.case_size + espacement)
        

    

    def afficher_plateau(self, plateau, liste_blanc, liste_noire, colorier_x=None, colorier_y=None, colorier_x2=None, colorier_y2=None, colorier_x3=None, colorier_y3=None):

        self.canvas.delete("pieces")  # Supprimer les anciennes pièces
        self.canvas.delete("ui")      # Supprimer les anciens textes UI

        # Redessiner le fond du plateau
        self.canvas.create_image(0, 0, image=self.fond_img, anchor=tk.NW)

        # Affichage des pièces sur le plateau
        for i in range(8):
            for j in range(8):
                x = self.positions[j]
                y = self.positions[i]

                # Vérifie si la case doit être coloriée
                if (colorier_x == j and colorier_y == i) or \
                (colorier_x2 == j and colorier_y2 == i) or \
                (colorier_x3 == j and colorier_y3 == i):
                    if (i + j) % 2 == 0:
                        color = "#f3f68a"
                    else:
                        color = "#b8ca4c"
                    self.canvas.create_rectangle(x, y, x + self.case_size, y + self.case_size, fill=color, outline=color)

                # Affichage de la pièce
                piece, couleur = plateau[i][j]
                if piece != " ":
                    prefix = "w" if couleur == "B" else "b"
                    suffix = self.correspondance[piece]
                    nom_fichier = f"{prefix}{suffix}.png"
                    chemin_image = os.path.join("Pieces", nom_fichier)
                    if nom_fichier not in self.images:
                        self.images[nom_fichier] = tk.PhotoImage(file=chemin_image)
                    self.canvas.create_image(x, y, image=self.images[nom_fichier], anchor=tk.NW, tags="pieces")

        # Ajout des prises et score à droite
        self.afficher_captures(liste_blanc, liste_noire)


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
        self.canvas.create_text(x_text, y_blanc, anchor="nw", text="⚪ Blancs ont pris :", font=("Arial", 12), tags="ui")
        self.canvas.create_text(x_text, y_blanc + 20, anchor="nw", text=blanc_txt or "—", font=("Arial", 16), tags="ui")
        if score_blanc > 0:
            self.canvas.create_text(x_text + 230, y_blanc + 20, anchor="nw", text=f"+{score_blanc}", font=("Arial", 14), fill="green", tags="ui")

        self.canvas.create_text(x_text, y_noir, anchor="nw", text="⚫ Noirs ont pris :", font=("Arial", 12), tags="ui")
        self.canvas.create_text(x_text, y_noir + 20, anchor="nw", text=noir_txt or "—", font=("Arial", 16), tags="ui")
        if score_noir > 0:
            self.canvas.create_text(x_text + 230, y_noir + 20, anchor="nw", text=f"+{score_noir}", font=("Arial", 14), fill="green", tags="ui")

    def attendre_click_case(self):
        self.click_coord = None
        self._clicked.set(False)
        self.root.bind("<Button-1>", self._on_click)
        self.root.wait_variable(self._clicked) 
        return self.click_coord  # retourne un tuple (x_case, y_case)

    def _on_click(self, event):
        x_pixel = event.x
        y_pixel = event.y

        # Taille réelle du plateau (en pixels)
        plateau_max_x = self.positions[-1] + self.case_size
        plateau_max_y = self.positions[-1] + self.case_size

        # Ignorer le clic si hors du plateau
        if x_pixel >= plateau_max_x or y_pixel >= plateau_max_y:
            return  # clic ignoré

        # Trouver la colonne (x_case)
        for i, pos_x in enumerate(self.positions):
            if x_pixel < pos_x + self.case_size:
                x_case = i
                break

        # Trouver la ligne (y_case)
        for j, pos_y in enumerate(self.positions):
            if y_pixel < pos_y + self.case_size:
                y_case = j
                break

        self.click_coord = (x_case, y_case)
        self.root.unbind("<Button-1>")
        self._clicked.set(True)


    def afficher_dot(self, plateau,n_case_1,l_case_1,joueur,is_en_passant_possible,en_passant_collone,is_rock_possible):
    
        legal_cases_no_echecs_liste_copy = liste_moov(plateau,n_case_1,l_case_1,joueur,is_en_passant_possible,en_passant_collone,is_rock_possible)
        for legals_cases in legal_cases_no_echecs_liste_copy:
            row, col = legals_cases  # ligne, colonne
            x = self.positions[col]
            y = self.positions[row]
            if plateau[legals_cases[0]][legals_cases[1]] == [" ",""]:
                nom_fichier = "dot.png"
            else:
                nom_fichier = "prise.png"
            chemin_image = os.path.join("Pieces", nom_fichier)
            if nom_fichier not in self.images:
                self.images[nom_fichier] = tk.PhotoImage(file=chemin_image)
            self.canvas.create_image(x, y, image=self.images[nom_fichier], anchor=tk.NW, tags="pieces")

    def afficher_resultat_fin_partie(self, plateau, resultat, joueur):
        """
        Affiche une image de victoire, défaite ou match nul en haut à droite des rois.
        - resultat : 0 = victoire, 1 = match nul
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

            if resultat == 1:
                for (i, j) in [roi_blanc_pos, roi_noir_pos]:
                    x = self.positions[j] + self.case_size * 0.5
                    y = self.positions[i] - self.case_size * 0.5
                    if y<0:
                        y=-26
                    if x>682:
                        x=664
                    self.canvas.create_image(x, y, image=self.images["nul - Copie.png"], anchor=tk.NW, tags="resultat")
            else:
                gagnant = joueur
                perdant = "N" if joueur == "B" else "B"
                positions = {"B": roi_blanc_pos, "N": roi_noir_pos}
                for nom_image, couleur in [("gagnant.png", gagnant), ("perdant.png", perdant)]:
                    i, j = positions[couleur]
                    x = self.positions[j] + self.case_size * 0.5
                    y = self.positions[i] - self.case_size * 0.5
                    if y<0:
                        y=-26
                    if x>682:
                        x=664
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


joueur="B"
x_case = 0
y_case = 0
is_en_passant_possible = False
en_passant_collone = 0
is_rock_possible = [True,True,True,True]    #haut à gauche/haut à droite/bas à droite/bas à gauche
legal_cases_no_echecs_liste_copy=[]
draw_plateau(plateau)
afficheur = AfficheurEchiquier()
liste_blanc={"R":1,"D":1,"P":8,"F":2,"C":2,"T":2}
liste_noire={"R":1,"D":1,"P":8,"F":2,"C":2,"T":2}
afficheur.afficher_plateau(plateau, liste_blanc, liste_noire)
end_game = False
last_two_cases = [[0,0],[0,0]]
first_play = True
liste_plateaux = []
liste_plateaux.append(copy.deepcopy(plateau))




while end_game == False:
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
    
    if plateau[0][l_case_2][0] == "P" or plateau[7][l_case_2][0] == "P":
        plateau[n_case_2][l_case_2] = [afficheur.promotion(joueur),joueur]

    if joueur=="B":
        joueur="N"
    else:
        joueur="B"

    liste_plateaux.append(copy.deepcopy(plateau))
    if can_moov(plateau,joueur,is_en_passant_possible,en_passant_collone,is_rock_possible) == True:
        
        if is_echecs(plateau, joueur, is_en_passant_possible, en_passant_collone, is_rock_possible, True):
            print("échecs")
     
        pass
    else:
        if is_echecs(plateau, joueur, is_en_passant_possible, en_passant_collone, is_rock_possible, True):
            print("Victoire")
            if joueur == "N":
                print("des blancs")
                afficheur.afficher_resultat_fin_partie(plateau, resultat=0, joueur="B")
            else:
                print("des noirs")
                afficheur.afficher_resultat_fin_partie(plateau, resultat=0, joueur="N")
        else:
            print("nul")
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
        afficheur.afficher_resultat_fin_partie(plateau, resultat=1, joueur=None)
    if liste_plateaux.count(plateau) == 3:
        afficheur.afficher_resultat_fin_partie(plateau, resultat=1, joueur=None)
        end_game = True
        print("nul")

   
    last_two_cases = [[l_case_1,n_case_1],[l_case_2,n_case_2]]
    
    first_play = False
    
    
afficheur.afficher_plateau(plateau,liste_blanc, liste_noire)
x_case, y_case = afficheur.attendre_click_case()
