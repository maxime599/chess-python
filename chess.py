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




"""
def draw_matrice(matrice,coord_x,coord_y,taille,color,draw_color_0):
    palette_blanc={0:0,1:0,2:219,3:199,4:176,5:168,6:138}
    palette_noire={0:0,1:0,2:90,3:74,4:59,5:42,6:24}


    for i in range(len(matrice)):
        for j in range(len(matrice[0])):
            if not matrice[i][j] == 0 or draw_color_0 == True:

                if color == "B":
                    c = palette_blanc[matrice[i][j]]
                    fill_rect(j*taille+coord_x,i*taille+coord_y,taille,taille,(c,c,c))

                else:
                    c = palette_noire[matrice[i][j]]
                    fill_rect(j*taille+coord_x,i*taille+coord_y,taille,taille,(c,c,c))"""


def draw_plateau(plateau):
    for i in range(8):
        print(plateau[i])



class AfficheurEchiquier:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Échiquier")
        self.board_size = 728
        self.case_size = 91
        self.canvas = tk.Canvas(self.root, width=self.board_size, height=self.board_size)
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
        

    

    def afficher_plateau(self, plateau, colorier_x=None, colorier_y=None, colorier_x2=None, colorier_y2=None, colorier_x3=None, colorier_y3=None):
        self.canvas.delete("pieces")  # Supprimer les anciennes pièces

        # Redessiner le fond du plateau
        self.canvas.create_image(0, 0, image=self.fond_img, anchor=tk.NW)

        for i in range(8):
            for j in range(8):
                x = self.positions[j]
                y = self.positions[i]

                # Vérifier si on doit colorier cette case
                if (colorier_x == j and colorier_y == i) or (colorier_x2 == j and colorier_y2 == i) or (colorier_x3 == j and colorier_y3 == i):
                    # Couleur de fond en fonction de la couleur originale de la case
                    if (i + j) % 2 == 0:
                        color = "#f3f68a"  # case blanche modifiée
                    else:
                        color = "#b8ca4c"  # case noire modifiée
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
        - joueur : "B" ou "N"
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


    def lancer(self):
        self.root.mainloop()

"""
def draw_plateau(plateau,x_case,y_case,pion,tour,cavalier,fou,roi,dame):
    
    for i in range(8):
        for j in range(8):
            draw_case_back(i,j)
            draw_case_piece(plateau,i,j,pion,tour,cavalier,fou,roi,dame)
    draw_selection_generic(x_case, y_case, 27)

def draw_case_back(i,j):
    if i%2 == j%2:
        c = (255,255,255)
    else:
        c = (75,115,153)
    fill_rect(2+(i*27),2+(j*27),27,27,c)

def draw_case_piece(plateau,j,i,pion,tour,cavalier,fou,roi,dame):
    pieces = {"P":pion,"T":tour,"C":cavalier,"F":fou,"R":roi,"D":dame}
    if plateau[i][j][0] != " ":
        draw_matrice(pieces[plateau[i][j][0]],2+(j*27),2+(i*27),2,plateau[i][j][1],False)"""
    



"""def draw_selection_generic(x, y, size, offset_x=2, offset_y=2):
    red = (255, 0, 0)
    fill_rect(offset_x + (x * size), offset_y + (y * size), size, 1, red)
    fill_rect(offset_x + (x * size) + (size - 1), offset_y + (y * size), 1, size, red)
    fill_rect(offset_x + (x * size), offset_y + (y * size) + (size - 1), size, 1, red)
    fill_rect(offset_x + (x * size), offset_y + (y * size), 1, size, red)

"""
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





"""def move(plateau,x_case,y_case,pion,tour,cavalier,fou,roi,dame,second_time,n_case_1,l_case_1,joueur,is_en_passant_possible,en_passant_collone,is_rock_possible):
    draw_case_back(x_case,y_case)
    draw_case_piece(plateau,x_case,y_case,pion,tour,cavalier,fou,roi,dame)
    draw_selection_generic(x_case, y_case, 27)
    
    
    legal_cases_no_echecs_liste_copy = liste_moov(plateau,n_case_1,l_case_1,joueur,is_en_passant_possible,en_passant_collone,is_rock_possible)
    
    good_second_selected_case = True


    while not ((keydown(KEY_OK) == True or keydown(KEY_EXE) == True) and good_second_selected_case == True):
        if (keydown(KEY_RIGHT) and x_case<7) or (keydown(KEY_DOWN) and y_case<7) or (keydown(KEY_LEFT) and x_case>0) or (keydown(KEY_UP) and y_case>0):
            
            mouvements = {
            KEY_RIGHT: (1, 0),
            KEY_LEFT: (-1, 0),
            KEY_UP: (0, -1),
            KEY_DOWN: (0, 1)
                            }

            for key, (dx, dy) in mouvements.items():
                if keydown(key) and 0 <= x_case + dx < 8 and 0 <= y_case + dy < 8:
                    draw_case_back(x_case,y_case)
                    draw_case_piece(plateau,x_case,y_case,pion,tour,cavalier,fou,roi,dame)
                    x_case += dx
                    y_case += dy
                    break   
   
          
            draw_selection_generic(x_case, y_case, 27)
            sleep(0.1)

        if second_time==True:
            draw_selection_generic(l_case_1, n_case_1, 27)
            for legals_cases in legal_cases_no_echecs_liste_copy:
                fill_rect(2+legals_cases[1]*27+12,2+legals_cases[0]*27+12,3,3,(0,255,0))
            if [y_case,x_case] in legal_cases_no_echecs_liste_copy or [y_case,x_case] == [n_case_1,l_case_1] or plateau[y_case][x_case][1] == joueur:
                good_second_selected_case = True
            else:
                good_second_selected_case = False
    return x_case,y_case,legal_cases_no_echecs_liste_copy"""


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

def promotion():
    piece = input("rang dans les pieces ['D','F','T','C']  :")

    pieces = ["D","F","T","C"]

    return pieces[piece]
    
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




"""fill_rect(0,0,500,500,(50,50,50))
"""
joueur="B"
x_case = 0
y_case = 0
is_en_passant_possible = False
en_passant_collone = 0
is_rock_possible = [True,True,True,True]    #haut à gauche/haut à droite/bas à droite/bas à gauche
legal_cases_no_echecs_liste_copy=[]
"""draw_plateau(plateau,x_case,y_case,pion,tour,cavalier,fou,roi,dame)
"""
draw_plateau(plateau)
afficheur = AfficheurEchiquier()
afficheur.afficher_plateau(plateau)
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
            """draw_string("Blanc",248,3,(255,255,255),(50,50,50))"""
        else:
            print("Au noirs de jouer")
            """draw_string("Noir  ",248,3,(255,255,255),(50,50,50))"""

        good_selected_case=False
        while not good_selected_case:
            if first_play:
                afficheur.afficher_plateau(plateau)
            else:
                afficheur.afficher_plateau(plateau, None, None, last_two_cases[0][0], last_two_cases[0][1], last_two_cases[1][0], last_two_cases[1][1])

            
            
            result=move(plateau,x_case,y_case,False,0,0,joueur,is_en_passant_possible,en_passant_collone,is_rock_possible)    
        
            y_case,n_case_1 = result[1],result[1]
            x_case,l_case_1 = result[0],result[0]
            
            

            if plateau[n_case_1][l_case_1][0] != " " and plateau[n_case_1][l_case_1][1]==joueur:
                good_selected_case = True
            print("case séléctioné : ",x_case," ",y_case)

            if first_play:
                afficheur.afficher_plateau(plateau, x_case, y_case)
            else:
                if plateau[x_case][y_case][1] == joueur:
                    afficheur.afficher_plateau(plateau, x_case, y_case, last_two_cases[0][0], last_two_cases[0][1], last_two_cases[1][0], last_two_cases[1][1])
                else:
                    afficheur.afficher_plateau(plateau, None, None, last_two_cases[0][0], last_two_cases[0][1], last_two_cases[1][0], last_two_cases[1][1])

        selected_same_color = True
        while selected_same_color == True:
            if first_play:
                afficheur.afficher_plateau(plateau, x_case, y_case)
            else:
                afficheur.afficher_plateau(plateau, x_case, y_case, last_two_cases[0][0], last_two_cases[0][1], last_two_cases[1][0], last_two_cases[1][1])

            afficheur.afficher_dot(plateau,n_case_1,l_case_1,joueur,is_en_passant_possible,en_passant_collone,is_rock_possible)


            result=move(plateau,x_case,y_case,True,n_case_1,l_case_1,joueur,is_en_passant_possible,en_passant_collone,is_rock_possible)    
            
            y_case,n_case_2 = result[1],result[1]
            x_case,l_case_2 = result[0],result[0]
            legal_cases_no_echecs_liste_copy = result[2]

            """while keydown(KEY_OK) == True or keydown(KEY_EXE) == True:
                pass"""

            if plateau[y_case][x_case][1] != joueur or [y_case,x_case] == [n_case_1,l_case_1]:   
                selected_same_color = False
            else:
                """draw_case_back(l_case_1,n_case_1)
                draw_case_piece(plateau,l_case_1,n_case_1,pion,tour,cavalier,fou,roi,dame)"""
                n_case_1 = y_case
                l_case_1 = x_case

            for i in legal_cases_no_echecs_liste_copy:
                if i == [y_case,x_case]:
                    good_second_case = True
                    

            """    draw_case_back(i[1],i[0])
                draw_case_piece(plateau,i[1],i[0],pion,tour,cavalier,fou,roi,dame)
            draw_case_back(l_case_1,n_case_1)
            draw_case_piece(plateau,l_case_1,n_case_1,pion,tour,cavalier,fou,roi,dame)"""
        if first_play:
            afficheur.afficher_plateau(plateau, x_case, y_case)
        else:
            afficheur.afficher_plateau(plateau, x_case, y_case, last_two_cases[0][0], last_two_cases[0][1], last_two_cases[1][0], last_two_cases[1][1])

    

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
        """draw_plateau(plateau,x_case,y_case,pion,tour,cavalier,fou,roi,dame)"""
        plateau[n_case_2][l_case_2] = promotion(joueur)
        """fill_rect(235,75,70,70,(50,50,50))"""

    if joueur=="B":
        joueur="N"
    else:
        joueur="B"

    liste_plateaux.append(copy.deepcopy(plateau))
    if can_moov(plateau,joueur,is_en_passant_possible,en_passant_collone,is_rock_possible) == True:
        
        if is_echecs(plateau, joueur, is_en_passant_possible, en_passant_collone, is_rock_possible, True):
            """draw_string("échecs",238,50,(255,255,255),(50,50,50))"""
            print("échecs")
                
        """else:
            draw_string("            ",233,50,(255,255,255),(50,50,50))"""
        pass
    else:
        if is_echecs(plateau, joueur, is_en_passant_possible, en_passant_collone, is_rock_possible, True):
            print("Victoire")
            """draw_string("Victoire",230,50,(255,255,255),(50,50,50))"""
            if joueur == "N":
                """draw_string("des blancs",220,70,(255,255,255),(50,50,50))"""
                print("des blancs")
                afficheur.afficher_resultat_fin_partie(plateau, resultat=0, joueur="B")
            else:
                """draw_string("des noirs",227,70,(255,255,255),(50,50,50))"""
                print("des noirs")
                afficheur.afficher_resultat_fin_partie(plateau, resultat=0, joueur="N")
        else:
            print("nul")
            """draw_string("Nul",238,50,(255,255,255),(50,50,50))"""
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
        """draw_string("Nul",238,50,(255,255,255),(50,50,50))"""
    if liste_plateaux.count(plateau) == 3:
        afficheur.afficher_resultat_fin_partie(plateau, resultat=1, joueur=None)
        end_game = True
        print("nul")

    """draw_plateau(plateau,x_case,y_case,pion,tour,cavalier,fou,roi,dame)"""
   
    last_two_cases = [[l_case_1,n_case_1],[l_case_2,n_case_2]]
    
    first_play = False
    
    
afficheur.afficher_plateau(plateau)
x_case, y_case = afficheur.attendre_click_case()
