from pathlib import Path
import json
import csv



#La classe Compte
class Compte(object):
    
    def setnumero(self, value:int):
        self.__numero=value 
    def getnumero(self)->int:
        return self.__numero 

    def setproprietaire(self, value:str):
        self.__proprietaire=value 
    def getproprietaire(self)->str:
        return self.__proprietaire 
    
    def getsolde(self)->float:
        return self.__solde

    def __init__(self,num=0, prop='', solde=0):
        #initialisation des attributs
        self.setnumero(num) 
        self.setproprietaire(prop)
        self.__solde=max(solde,0) 

    def deposer(self, montant:float)->float:
        self.__solde+=montant 
        return self.__solde
    
    def retirer(self, montant:float)->float:
        #verifier si le solde est suffisant avant de retirer
        if self.__solde>=montant:
            self.__solde-=montant 
            return self.__solde
        else:
            raise ValueError("Le solde est insuffisant")

    @classmethod
    def converttolist(cls, valeur:object)->list:
        #liste vide pour mettre les valeurs
        liste:list=[]
        for valeur in valeur.__dict__.values(): #parcourir et ajouter les valeurs du dictionnaire a la liste
            liste.append(valeur)
        return liste

    @classmethod
    def createfromlist(cls,valeur:list[str])->object:
        compte:Compte=cls(int(valeur[0]),valeur[1],valeur[2])
        return compte

    @classmethod
    def converttodict(cls, valeur:object)->dict:
        return valeur.__dict__

    @classmethod
    def createfromdict(cls,valeur:dict[str])->object:
        compte:Compte=Compte()
        for key,value in valeur.items():
            if key in compte.__dict__.keys():
                compte.__setattr__(key,value)         
        return compte 

#La classe JSONSerialiseur
class JSONSerialiseur(object):

    def __init__(self, filename:str):
        self.filename=filename 
    
    @property
    def filename(self)->str:
        return self.__filename

    @filename.setter
    def filename(self, value:str):
        self.__filename=value 

    def serialiser(self, valeurs:list[Compte])->None:
        #ouvrir le fichier (creer le stream)
        path:Path=Path(self.filename)
        stream=path.open('w')
        #verifier si c'est un fichier
        if path.is_file():
            
            #serialiser la valeur vers le fichier
            json.dump(valeurs,stream, indent=4,separators=(',',':'),default=Compte.converttodict)
            #fermer le stream
            stream.flush()
            stream.close()
        else:
            raise Exception('fichier incorrect')

    def deserialiser(self)->list[Compte]:
        #ouvrir le fichier (creer le stream)
        path:Path=Path(self.filename)
        #verifier s'il existe et que c'est un file
        #verifier si le fichier existe
        if path.is_file() and path.exists():
            stream=path.open('r') 
            #deserialiser le fichier vers un objet liste de compte
            listecompte:list[Compte]=json.load(stream,object_hook=Compte.createfromdict)
        
            #fermer le stream
            stream.close()
            #retourner le resultat
            return listecompte 
        else:
            #sinon exception s'il existe pas
            raise Exception('fichier inexistant')

#La classe CSVSerialiseur
class CSVSerialiseur(object):
    def __init__(self, filename:str):
        self.filename=filename 
    
    @property
    def filename(self)->str:
        return self.__filename

    @filename.setter
    def filename(self, value:str):
        self.__filename=value 
            
    def serialiser(self, valeur:list[Compte],header:list[str])->None:
        #ouvrir le fichier (creer le stream)
        path:Path=Path(self.filename)
        stream=path.open('w',newline='')
        #verifier si le chemin represente un fichier
        if path.is_file():
            #creation du flux pour la serialisation en csv
            streamcsv=csv.writer(stream,dialect='excel',
                                 quoting=csv.QUOTE_NONNUMERIC,
                                 quotechar='\'')
            #ecrire le header
            streamcsv.writerow(header)
            #serialiser la liste des objets a travers le streamcsv
            for element in valeur:
                streamcsv.writerow(Compte.converttolist(element))

            # fermer le stream d'ecriture
            stream.flush()
            stream.close()
        else:
            #mettre une exception si ce n'est pas un fichier
            raise Exception('fichier incorrect')

    def deserialiser(self)->list[Compte]:
        #ouvrir le fichier (creer le stream)
        path:Path=Path(self.filename)
        if path.exists():
            stream=path.open('r',newline='') 
            #creation du flux pour la deserialisation le csv en objet
            streamcsv=csv.reader(stream,dialect='excel',
                                 quoting=csv.QUOTE_NONNUMERIC,
                                 quotechar='\'')
            #deserialiser le csv en objet
            #lire l'en-tete
            streamcsv.__next__()
            #lire les datas
            listecomptes:list[Compte]=[]
            for element in streamcsv:
                #transformer une liste en compte
                compte:Compte=Compte.createfromlist(element)
                #ajouter le compte a la liste
                listecomptes.append(compte)
            #fermer le stream
            stream.close()
            return listecomptes
        else:
            raise Exception('fichier inexistant')

#La classe Banque
class Banque(object):
    def __init__(self):
        self.listecomptes=[]

    @property
    def listecomptes(self)->list[Compte]:
        return self.__listecomptes 

    @listecomptes.setter
    def listecomptes(self,value:list[Compte]):
        self.__listecomptes=value 

    def rechercher(self,numcompte:int)->Compte: 
        for element in self.listecomptes:
            if element.getnumero()==numcompte:
                return element
        return None 

    def ajouter(self,valeur:Compte)->None:
        #verifier si le compte n'Existe pas deja
        compte:Compte=self.rechercher(valeur.getnumero())
        if compte is None:
            self.listecomptes.append(valeur) 
        else:
            raise ValueError("Le compte existe deja") 
    
    def deposer(self, numcompte:int, montant:float)->float:
        compte:Compte=self.rechercher(numcompte)
        if compte is not None:
            nouvesolde:float= compte.deposer(montant)
            return nouvesolde 
        else:
            raise ValueError("Compte inexistant") 

    def retirer(self, numcompte:int, montant:float)->float:
        compte:Compte=self.rechercher(numcompte)
        if compte is not None:
            try:
                nouvesolde:float= compte.retirer(montant)
                return nouvesolde 
            except ValueError as ex:
                raise ValueError(ex.args[0])
        else:
            raise ValueError("Compte inexistant") 

#La classe BanqueUI
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
from tkinter.constants import END

class BanqueUI:
    def __init__(self, top=None):
        '''This class configures and populates the toplevel window.
           top is the toplevel containing window.'''

        top.geometry("600x450+660+210")
        top.minsize(148, 1)
        top.maxsize(1924, 1055)
        top.resizable(1,  1)
        top.title("Toplevel 0")
        top.configure(background="#d9d9d9")

        self.banque=Banque() # la creation d'un objet banque
       
        self.top = top
        self.typefichier = tk.StringVar(value='csv')
       
        self.TNotebook1 = ttk.Notebook(self.top)
        self.TNotebook1.place(relx=0.0, rely=0.0, relheight=1.002
                , relwidth=1.007)
        self.TNotebook1.configure(takefocus="")
        self.TabBanque = tk.Frame(self.TNotebook1)
        self.TNotebook1.add(self.TabBanque, padding=3)
        self.TNotebook1.tab(0, text='''Banque''', compound="left"
                ,underline='''-1''', )
        self.TabBanque.configure(background="#8080ff")
        self.TabBanque.configure(highlightbackground="#d9d9d9")
        self.TabBanque.configure(highlightcolor="black")
        self.TabCompte = tk.Frame(self.TNotebook1)
        self.TNotebook1.add(self.TabCompte, padding=3)
        self.TNotebook1.tab(1, text='''Compte''', compound="left"
                ,underline='''-1''', )
        self.TabCompte.configure(background="#80ffff")
        self.TabCompte.configure(highlightbackground="#d9d9d9")
        self.TabCompte.configure(highlightcolor="black")
        self.TabTransaction = tk.Frame(self.TNotebook1)
        self.TNotebook1.add(self.TabTransaction, padding=3)
        self.TNotebook1.tab(2, text='''Transaction''', compound="left"
                ,underline='''-1''', )
        self.TabTransaction.configure(background="#ff80c0")
        self.TabTransaction.configure(highlightbackground="#d9d9d9")
        self.TabTransaction.configure(highlightcolor="black")
        self.Label1 = tk.Label(self.TabBanque)
        self.Label1.place(relx=0.067, rely=0.167, height=46, width=142)
        self.Label1.configure(anchor='w')
        self.Label1.configure(background="#d9d9d9")
        self.Label1.configure(compound='left')
        self.Label1.configure(disabledforeground="#a3a3a3")
        self.Label1.configure(font="-family {Segoe UI} -size 12 -weight bold")
        self.Label1.configure(foreground="#000000")
        self.Label1.configure(text='''Fichier :''')
        self.txtChemin = tk.Entry(self.TabBanque)
        self.txtChemin.place(relx=0.35, rely=0.167, height=44, relwidth=0.623)
        self.txtChemin.configure(background="white")
        self.txtChemin.configure(disabledforeground="#a3a3a3")
        self.txtChemin.configure(font="TkFixedFont")
        self.txtChemin.configure(foreground="#000000")
        self.txtChemin.configure(insertbackground="black")
        self.btnDeSerialiser = tk.Button(self.TabBanque)
        self.btnDeSerialiser.place(relx=0.067, rely=0.69, height=63, width=206)
        self.btnDeSerialiser.configure(activebackground="beige")
        self.btnDeSerialiser.configure(activeforeground="black")
        self.btnDeSerialiser.configure(background="#d9d9d9")
        self.btnDeSerialiser.configure(compound='left')
        self.btnDeSerialiser.configure(disabledforeground="#a3a3a3")
        self.btnDeSerialiser.configure(font="-family {Segoe UI} -size 12 -weight bold")
        self.btnDeSerialiser.configure(foreground="#000000")
        self.btnDeSerialiser.configure(highlightbackground="#d9d9d9")
        self.btnDeSerialiser.configure(highlightcolor="black")
        self.btnDeSerialiser.configure(pady="0")
        self.btnDeSerialiser.configure(text='''Deseriliser''')
        self.btnSerialiser = tk.Button(self.TabBanque)
        self.btnSerialiser.place(relx=0.55, rely=0.69, height=63, width=206)
        self.btnSerialiser.configure(activebackground="beige")
        self.btnSerialiser.configure(activeforeground="black")
        self.btnSerialiser.configure(background="#d9d9d9")
        self.btnSerialiser.configure(compound='left')
        self.btnSerialiser.configure(disabledforeground="#a3a3a3")
        self.btnSerialiser.configure(font="-family {Segoe UI} -size 12 -weight bold")
        self.btnSerialiser.configure(foreground="#000000")
        self.btnSerialiser.configure(highlightbackground="#d9d9d9")
        self.btnSerialiser.configure(highlightcolor="black")
        self.btnSerialiser.configure(pady="0")
        self.btnSerialiser.configure(text='''Serialiser''')
        self.rdtypecsv = tk.Radiobutton(self.TabBanque)
        self.rdtypecsv.place(relx=0.233, rely=0.333, relheight=0.121
                , relwidth=0.163)
        self.rdtypecsv.configure(activebackground="beige")
        self.rdtypecsv.configure(activeforeground="black")
        self.rdtypecsv.configure(anchor='w')
        self.rdtypecsv.configure(background="#d9d9d9")
        self.rdtypecsv.configure(compound='left')
        self.rdtypecsv.configure(disabledforeground="#a3a3a3")
        self.rdtypecsv.configure(font="-family {Segoe UI} -size 12 -weight bold")
        self.rdtypecsv.configure(foreground="#000000")
        self.rdtypecsv.configure(highlightbackground="#d9d9d9")
        self.rdtypecsv.configure(highlightcolor="black")
        self.rdtypecsv.configure(justify='left')
        self.rdtypecsv.configure(selectcolor="#d9d9d9")
        self.rdtypecsv.configure(text='''CSV''')
        self.rdtypecsv.configure(value='csv')
        self.rdtypecsv.configure(variable=self.typefichier)
        self.rbtypejson = tk.Radiobutton(self.TabBanque)
        self.rbtypejson.place(relx=0.517, rely=0.333, relheight=0.121
                , relwidth=0.163)
        self.rbtypejson.configure(activebackground="beige")
        self.rbtypejson.configure(activeforeground="black")
        self.rbtypejson.configure(anchor='w')
        self.rbtypejson.configure(background="#d9d9d9")
        self.rbtypejson.configure(compound='left')
        self.rbtypejson.configure(disabledforeground="#a3a3a3")
        self.rbtypejson.configure(font="-family {Segoe UI} -size 12 -weight bold")
        self.rbtypejson.configure(foreground="#000000")
        self.rbtypejson.configure(highlightbackground="#d9d9d9")
        self.rbtypejson.configure(highlightcolor="black")
        self.rbtypejson.configure(justify='left')
        self.rbtypejson.configure(selectcolor="#d9d9d9")
        self.rbtypejson.configure(text='''JSON''')
        self.rbtypejson.configure(value='json')
        self.rbtypejson.configure(variable=self.typefichier)
        self.Label2 = tk.Label(self.TabCompte)
        self.Label2.place(relx=0.1, rely=0.143, height=46, width=142)
        self.Label2.configure(anchor='w')
        self.Label2.configure(background="#d9d9d9")
        self.Label2.configure(compound='left')
        self.Label2.configure(disabledforeground="#a3a3a3")
        self.Label2.configure(font="-family {Segoe UI} -size 12 -weight bold")
        self.Label2.configure(foreground="#000000")
        self.Label2.configure(text='''Numero :''')
        self.Label3 = tk.Label(self.TabCompte)
        self.Label3.place(relx=0.1, rely=0.333, height=46, width=142)
        self.Label3.configure(anchor='w')
        self.Label3.configure(background="#d9d9d9")
        self.Label3.configure(compound='left')
        self.Label3.configure(disabledforeground="#a3a3a3")
        self.Label3.configure(font="-family {Segoe UI} -size 12 -weight bold")
        self.Label3.configure(foreground="#000000")
        self.Label3.configure(text='''Proprietaire :''')
        self.Label4 = tk.Label(self.TabCompte)
        self.Label4.place(relx=0.1, rely=0.524, height=46, width=142)
        self.Label4.configure(anchor='w')
        self.Label4.configure(background="#d9d9d9")
        self.Label4.configure(compound='left')
        self.Label4.configure(disabledforeground="#a3a3a3")
        self.Label4.configure(font="-family {Segoe UI} -size 12 -weight bold")
        self.Label4.configure(foreground="#000000")
        self.Label4.configure(text='''Solde :''')
        self.btnajoutercompte = tk.Button(self.TabCompte)
        self.btnajoutercompte.place(relx=0.217, rely=0.738, height=53, width=146)

        self.btnajoutercompte.configure(activebackground="beige")
        self.btnajoutercompte.configure(activeforeground="black")
        self.btnajoutercompte.configure(background="#d9d9d9")
        self.btnajoutercompte.configure(compound='left')
        self.btnajoutercompte.configure(disabledforeground="#a3a3a3")
        self.btnajoutercompte.configure(font="-family {Segoe UI} -size 12 -weight bold")
        self.btnajoutercompte.configure(foreground="#000000")
        self.btnajoutercompte.configure(highlightbackground="#d9d9d9")
        self.btnajoutercompte.configure(highlightcolor="black")
        self.btnajoutercompte.configure(pady="0")
        self.btnajoutercompte.configure(text='''Ajouter''')
        self.txtnumero = tk.Entry(self.TabCompte)
        self.txtnumero.place(relx=0.4, rely=0.143, height=44, relwidth=0.24)
        self.txtnumero.configure(background="white")
        self.txtnumero.configure(disabledforeground="#a3a3a3")
        self.txtnumero.configure(font="TkFixedFont")
        self.txtnumero.configure(foreground="#000000")
        self.txtnumero.configure(insertbackground="black")
        self.txtpro = tk.Entry(self.TabCompte)
        self.txtpro.place(relx=0.4, rely=0.333, height=44, relwidth=0.54)
        self.txtpro.configure(background="white")
        self.txtpro.configure(disabledforeground="#a3a3a3")
        self.txtpro.configure(font="TkFixedFont")
        self.txtpro.configure(foreground="#000000")
        self.txtpro.configure(insertbackground="black")
        self.txtsolde = tk.Entry(self.TabCompte)
        self.txtsolde.place(relx=0.4, rely=0.524, height=44, relwidth=0.257)
        self.txtsolde.configure(background="white")
        self.txtsolde.configure(disabledforeground="#a3a3a3")
        self.txtsolde.configure(font="TkFixedFont")
        self.txtsolde.configure(foreground="#000000")
        self.txtsolde.configure(insertbackground="black")
        self.btnrecherchercompte = tk.Button(self.TabCompte)
        self.btnrecherchercompte.place(relx=0.567, rely=0.738, height=53
                , width=146)
        self.btnrecherchercompte.configure(activebackground="beige")
        self.btnrecherchercompte.configure(activeforeground="black")
        self.btnrecherchercompte.configure(background="#d9d9d9")
        self.btnrecherchercompte.configure(compound='left')
        self.btnrecherchercompte.configure(disabledforeground="#a3a3a3")
        self.btnrecherchercompte.configure(font="-family {Segoe UI} -size 12 -weight bold")
        self.btnrecherchercompte.configure(foreground="#000000")
        self.btnrecherchercompte.configure(highlightbackground="#d9d9d9")
        self.btnrecherchercompte.configure(highlightcolor="black")
        self.btnrecherchercompte.configure(pady="0")
        self.btnrecherchercompte.configure(text='''Rechercher''')
        self.Label5 = tk.Label(self.TabTransaction)
        self.Label5.place(relx=0.083, rely=0.119, height=46, width=182)
        self.Label5.configure(anchor='w')
        self.Label5.configure(background="#d9d9d9")
        self.Label5.configure(compound='left')
        self.Label5.configure(disabledforeground="#a3a3a3")
        self.Label5.configure(font="-family {Segoe UI} -size 12 -weight bold")
        self.Label5.configure(foreground="#000000")
        self.Label5.configure(text='''Numero compte :''')
        self.Label6 = tk.Label(self.TabTransaction)
        self.Label6.place(relx=0.083, rely=0.31, height=46, width=182)
        self.Label6.configure(anchor='w')
        self.Label6.configure(background="#d9d9d9")
        self.Label6.configure(compound='left')
        self.Label6.configure(disabledforeground="#a3a3a3")
        self.Label6.configure(font="-family {Segoe UI} -size 12 -weight bold")
        self.Label6.configure(foreground="#000000")
        self.Label6.configure(text='''Montant :''')
        self.txtcomptetrans = tk.Entry(self.TabTransaction)
        self.txtcomptetrans.place(relx=0.433, rely=0.119, height=44
                , relwidth=0.273)
        self.txtcomptetrans.configure(background="white")
        self.txtcomptetrans.configure(disabledforeground="#a3a3a3")
        self.txtcomptetrans.configure(font="-family {Courier New} -size 12 -weight bold")
        self.txtcomptetrans.configure(foreground="#000000")
        self.txtcomptetrans.configure(insertbackground="black")
        self.txtmontanttrans = tk.Entry(self.TabTransaction)
        self.txtmontanttrans.place(relx=0.433, rely=0.31, height=44
                , relwidth=0.34)
        self.txtmontanttrans.configure(background="white")
        self.txtmontanttrans.configure(disabledforeground="#a3a3a3")
        self.txtmontanttrans.configure(font="-family {Courier New} -size 12 -weight bold")
        self.txtmontanttrans.configure(foreground="#000000")
        self.txtmontanttrans.configure(insertbackground="black")
        self.btndeposer = tk.Button(self.TabTransaction)
        self.btndeposer.place(relx=0.133, rely=0.714, height=53, width=156)
        self.btndeposer.configure(activebackground="beige")
        self.btndeposer.configure(activeforeground="black")
        self.btndeposer.configure(background="#d9d9d9")
        self.btndeposer.configure(compound='left')
        self.btndeposer.configure(disabledforeground="#a3a3a3")
        self.btndeposer.configure(font="-family {Segoe UI} -size 12 -weight bold")
        self.btndeposer.configure(foreground="#000000")
        self.btndeposer.configure(highlightbackground="#d9d9d9")
        self.btndeposer.configure(highlightcolor="black")
        self.btndeposer.configure(pady="0")
        self.btndeposer.configure(text='''Deposer''')
        self.btnretirer = tk.Button(self.TabTransaction)
        self.btnretirer.place(relx=0.45, rely=0.714, height=53, width=156)
        self.btnretirer.configure(activebackground="beige")
        self.btnretirer.configure(activeforeground="black")
        self.btnretirer.configure(background="#d9d9d9")
        self.btnretirer.configure(compound='left')
        self.btnretirer.configure(disabledforeground="#a3a3a3")
        self.btnretirer.configure(font="-family {Segoe UI} -size 12 -weight bold")
        self.btnretirer.configure(foreground="#000000")
        self.btnretirer.configure(highlightbackground="#d9d9d9")
        self.btnretirer.configure(highlightcolor="black")
        self.btnretirer.configure(pady="0")
        self.btnretirer.configure(text='''Retirer''')
        self.Label7 = tk.Label(self.TabTransaction)
        self.Label7.place(relx=0.15, rely=0.5, height=56, width=342)
        self.Label7.configure(anchor='w')
        self.Label7.configure(background="#d9d9d9")
        self.Label7.configure(compound='left')
        self.Label7.configure(disabledforeground="#a3a3a3")
        self.Label7.configure(font="-family {Segoe UI} -size 12 -weight bold")
        self.Label7.configure(foreground="#000000")
        self.Label7.configure(text='''Nouv. solde : ''')
        
        #La gestion des evenements
        self.btnSerialiser.configure(command=self.btnserialiser_click)
        self.btnDeSerialiser.configure(command=self.btndeserialiser_click)
        self.btnajoutercompte.configure(command=self.btnajoutercompte_click) 
        self.btnrecherchercompte.configure(command=self.btnrecherchercompte_click)
        self.btndeposer.configure(command=self.btndeposer_click)
        self.btnretirer.configure(command=self.btnretirer_click)

    def btnserialiser_click(self,*args):
        if self.txtChemin.get().__len__()>0:
            try:
                #verifier le type de serialsiation chosit : csv ou json
                if self.typefichier.get()=='csv':
                    csvserialiseur:CSVSerialiseur=CSVSerialiseur(self.txtChemin.get())
                    csvserialiseur.serialiser(self.banque.listecomptes)
                else:
                    jsonserialiseur:JSONSerialiseur=JSONSerialiseur(self.txtChemin.get())
                    jsonserialiseur.serialiser(self.banque.listecomptes)
            except Exception as ex:
                messagebox.showerror('Erreurs',ex.args[0])
        else:
            messagebox.showinfo('Erreurs','le nom du fichier est vide')

    def btndeserialiser_click(self,*args):
        if self.txtChemin.get().__len__()>0:
            try:
                #verifier le type de deserialsiation chosit : csv ou json
                if self.typefichier.get()=='csv':
                    csvserialiseur:CSVSerialiseur=CSVSerialiseur(self.txtChemin.get())
                    self.banque.listecomptes=csvserialiseur.deserialiser()
                else:
                    jsonserialiseur:JSONSerialiseur=JSONSerialiseur(self.txtChemin.get())
                    self.banque.listecomptes=jsonserialiseur.deserialiser()
            except Exception as ex:
                messagebox.showerror('Erreurs',ex.args[0])
        else:
            messagebox.showinfo('Erreurs','le nom du fichier est vide')        
    
    def btnajoutercompte_click(self,*args):
        try:
            numero:int=int(self.txtnumero.get())
            prop:str=self.txtpro.get()
            solde:float=float(self.txtsolde.get())
            compte:Compte=Compte(numero,prop,solde)
            self.banque.ajouter(compte)
            messagebox.showinfo('Infos','compte ajoute avec succes')
        except ValueError as ex:
            messagebox.showerror('Erreur',ex.args[0])

    def btnrecherchercompte_click(self,*args):
        if self.txtnumero.get().__len__()>0:
            try:
                numero:int=int(self.txtnumero.get())
                compte:Compte=self.banque.rechercher(numero)
                if compte is not None:
                    #afficher les informations du compte
                    #vider les textbox
                    self.txtpro.delete(0,END) 
                    self.txtsolde.delete(0,END)
                    #remplir les textbox
                    self.txtpro.insert(0,compte.getproprietaire())
                    self.txtsolde.insert(0,compte.getnumero())                    
                else:
                    messagebox.showerror('Erreur','compte inexistant') 
            except ValueError as ex:
                messagebox.showerror('Erreur',ex.args[0]) 
        else:
            messagebox.showerror('Erreur','le textbox numero est vide') 

    def btndeposer_click(self,*args):
        #verifier si les deux textbox sont pleins
        if self.txtnumero.get().__len__()>0 and self.txtmontanttrans.get().__len__()>0:
            try:
                numero:int=int(self.txtcomptetrans.get())
                montant:float=float(self.txtmontanttrans.get())
                compte:Compte=self.banque.rechercher(numero)
                nouvsolde=self.banque.deposer(numero,montant)
                self.Label7.configure(text='Nouv. solde :'+str(nouvsolde))
            except ValueError as ex:
                messagebox.showerror('Erreur',ex.args[0]) 
        else:
            messagebox.showerror('Erreur','l\'un des textbox est vide') 

    def btnretirer_click(self,*args):
        if self.txtnumero.get().__len__()>0 and self.txtmontanttrans.get().__len__()>0:
            try:
                numero:int=int(self.txtcomptetrans.get())
                montant:float=float(self.txtmontanttrans.get())
                compte:Compte=self.banque.rechercher(numero)
                nouvsolde=self.banque.retirer(numero,montant)
                #afficher le nouveau solde
                self.Label7.configure(text='Nouv. solde :'+str(nouvsolde))

            except ValueError as ex:
                messagebox.showerror('Erreur',ex.args[0]) 
        else:
            messagebox.showerror('Erreur','l\'un des textbox est vide') 

    @classmethod
    def start_up(cls):
        root=tk.Tk()
        banqueui=cls(root) # ou BanqueUI(root)
        root.mainloop()

if __name__ == '__main__':
    BanqueUI.start_up()
