#!/usr/bin/env python
# coding=utf8

import codecs
import sqlite3
import sys
import os, inspect

def strlist(l):
    return u"[{0}]".format(u", ".join(unicode(x) for x in l))


"""
class Pied:
    def __init__(self, voyelle, position):
        self.voyelle = voyelle
        self.position = position
        self.consonnes = u""
    
    def ajouteConsonne(self, c):
        self.consonnes += c
    
    def __str__(self):
        return u"[{0}:{1} {2}]".format(self.position, self.voyelle, self.consonnes)
    
    def __repr__(self):
        return self.__str__()
"""

class Pied:
    def __init__(self, voyelle):
        self.voyelle = voyelle
        self.consonnes = u""
        self.longueur = 0
    
    def ajouteConsonne(self, c):
        self.consonnes += c
    
    def lesConsonnes(self):
        conso = ""
        for c in self.consonnes:
            if c in "bcdfghjklmnpqrstvwxz":
                conso += c
        return conso
    
    def __str__(self):
        if self.longueur == 2:
            marque = "_"
        else:
            marque = ""
        return u"{0}{1}{2}".format(self.voyelle, marque, self.consonnes)
    
    def __repr__(self):
        return self.__str__()



class TypeVers:
    def __init__(self, abbr, motif_pieds):
        self.motif_pieds = motif_pieds
        self.abbr = abbr
        
    def scande(self, quantites):
        return self.scande_rec([], "", quantites, self.motif_pieds)
    
    def scande_rec(self, gauche, gauche_pieds, quantites, motif_droite):
        #print u"scande_rec({0}, {1})".format(quantites, strlist(motif_droite))
        if motif_droite == []:
            if quantites == []:
                #print "==> return fini: {0}".format(gauche)
                return [ (gauche, gauche_pieds) ]
            else:
                return None
        else:
            pied = motif_droite[0]
            reste_motif = motif_droite[1:]
            possibilites_pied = pied.scande(quantites)
            
            #print "=> {0}".format(strlist(possibilites_pied))
            
            possibilites = []
            for (sp, spn, r) in possibilites_pied:
                scansions = self.scande_rec(gauche + sp, gauche_pieds + spn, r, reste_motif)
                #if scansions_reste == True:
                #    possibilites += [ sp ]
                if scansions != None:
                    possibilites += scansions

            #print "==> {0}".format(possibilites)
            return possibilites
                        

        
    

class TypePiedAbstrait:
    pass

class ChoixPied(TypePiedAbstrait):
    def __init__(self, choix):
        self.choix = choix
        
    def scande(self, quantites):
        #print "s.c => {0}".format(self.choix)
        possibilites = []
        for c in self.choix:
            scande_c = c.scande(quantites)
            possibilites += scande_c
        return possibilites
        
    def __str__(self):
        return u"(OU {0})".format(strlist(self.choix))

class TypePied(TypePiedAbstrait):
    def __init__(self, motif, nom):
        self.motif = motif
        self.nom = nom
    
    def longueur(self):
        return len(self.motif)
    
    def scande(self, quantites):
        #print u"TypePied.scande({0}, {1})".format(self.motif, quantites)

        # si pas assez de pieds, alors aucune solution d'emblée
        if len(quantites) < len(self.motif):
            return []

        reste = quantites[ len(self.motif) : ]
        
        for i in range( len(self.motif) ):
            if self.motif[i] != 0 and quantites[i] != 0 and quantites[i] != self.motif[i]:
                return []
        return [ (self.motif, self.nom, reste) ]
    
    def __str__(self):
        return self.nom
    

P_DACTYLE = TypePied([2, 1, 1], u'd')
P_TROCHEE = TypePied([2, 1], u't')
P_SPONDEE = TypePied([2, 2], u's')
P_IAMBE = TypePied([1, 2], u'i')
P_ANAPESTE = TypePied([1, 1, 2], u'a')
P_TRIBRAQUE = TypePied([1, 1, 1], u'3')
P_PROCELEUSMATIQUE = TypePied([1, 1, 1, 1], u'p')  # procéleusmatique
P_INDIF_TROCHEE_SPONDEE = TypePied([2, 0], u't/s')

V_HEXAMETRE = TypeVers("hd", [
    ChoixPied([P_DACTYLE, P_SPONDEE]),
    ChoixPied([P_DACTYLE, P_SPONDEE]),
    ChoixPied([P_DACTYLE, P_SPONDEE]),
    ChoixPied([P_DACTYLE, P_SPONDEE]),
    ChoixPied([P_DACTYLE, P_SPONDEE]),
    P_INDIF_TROCHEE_SPONDEE
])

# "hexamètre dactylique / pentamètre dactylique" (on peut pour simplifier
# l'appeler "distique élégiaque"), et voici le schéma du pentamètre :
# longue brève brève / longue brève brève / longue isolée obligatoire //
# longue brève brève / longue brève brève / voyelle finale indifférente.
# Aux deux premiers pieds les dactyles peuvent être remplacés par des
# spondées , ou inversement.

V_PENTAMETRE = TypeVers("pd", [
    ChoixPied([P_DACTYLE, P_SPONDEE]),
    ChoixPied([P_DACTYLE, P_SPONDEE]),
    TypePied([2], u'-'),
    P_DACTYLE,
    P_DACTYLE,
    TypePied([0], u'*')
])

V_SENAIRE_IAMBIQUE = TypeVers("si", [
    P_IAMBE,
    P_IAMBE,
    P_IAMBE,
    P_IAMBE,
    P_IAMBE,
    ChoixPied([P_IAMBE, P_DACTYLE])
])

# "hendécasyllabe phalécien" (chez Catulle, entre autres) comporte un spondée, un 
# dactyle et trois trochées.
V_HENDECASYLLABE_PHALECIEN = TypeVers("hp", [
    P_SPONDEE,
    P_DACTYLE,
    P_TROCHEE,
    P_TROCHEE,
    P_INDIF_TROCHEE_SPONDEE,
])

# Le "sénaire iambique" se termine lui aussi par une syllabe indifférente,
# et quand on le trouve ce n'est pas en alternance avec un autre mètre.
# Son principe de base est le suivant : brève longue / brève longue /
# brève longue / brève longue / brève longue / brève indifférente Aux cinq
# premiers pieds, le iambe peut être remplacé par un dactyle, un spondée,
# un anapeste (brève brève longue), un tribraque (brève brève brève). Le
# sixième et dernier pied est le seul fiable : brève + indifférente = un
# douzième de certitude ! Au premier pied même, parfois, on peut trouver
# un procéleusmatique (brève brève brève brève)

V_SENAIRE_IAMBIQUE = TypeVers("si", [
    ChoixPied([P_IAMBE, P_DACTYLE, P_SPONDEE, P_ANAPESTE, P_TRIBRAQUE, P_PROCELEUSMATIQUE]),
    ChoixPied([P_IAMBE, P_DACTYLE, P_SPONDEE, P_ANAPESTE, P_TRIBRAQUE]),
    ChoixPied([P_IAMBE, P_DACTYLE, P_SPONDEE, P_ANAPESTE, P_TRIBRAQUE]),
    ChoixPied([P_IAMBE, P_DACTYLE, P_SPONDEE, P_ANAPESTE, P_TRIBRAQUE]),
    ChoixPied([P_IAMBE, P_DACTYLE, P_SPONDEE, P_ANAPESTE, P_TRIBRAQUE]),
    TypePied([1, 0], u'.*')    
])

def voyelle(c):
    return c in u"aeiouyæœαε"

# normalise :
# - convertit tout en minuscules
# - retire les éventuelles marques de scansion déjà présentes
def normalise(vers):
    vers = vers.lower()     # minuscules
    
    # retrait marques de scansion
    resultat = u""
    for c in vers:
        if c in u"ăā": c = u"a"
        elif c in u"ēĕ": c = u"e"
        elif c in u"īĭ": c = u"i"
        elif c in u"ōŏ": c = u"o"
        elif c in u"ūŭ": c = u"u"
        elif c in u"ǣ": c = u"ae"
        elif c in u"æ": c = u"ae"
        elif c in u"œ": c = u"oe"
        elif not (c.isalpha() or c == " "): continue   # u"/,?;.:«»()'"
        
        resultat += c
    
    return resultat

# si un mot se termine par une voyelle, et si le mot suivant commence par
# une voyelle, alors on supprime la voyelle finale du premier mot
"""
def applique_elisions(vers):
    resultat = u""
    
    for i in range(0, len(vers)-2):
        if voyelle(vers[i]) and vers[i+1] == u" " and voyelle(vers[i+2]):
            continue
        resultat += vers[i]
        
    resultat += vers[-2:]
    
    return resultat
"""


# remplace les diphtongues par des voyelles uniques
# qv devient qu
"""
def remplace_diphtongues(vers):
    return vers.replace(u"qu", u"q").replace(u" iu", u" ju").replace(u"ae", u"æ").replace(u"eu", u"ε").replace(u"au", u"α").replace(u"oe", u"œ")
    
def diphtongue(c):
    return c in u"æœαε"
"""


"""
def decoupe_pieds(vers):
    vers += u"#"
    pieds = [Pied(None, None)]
    for i in range(len(vers)):
        c = vers[i]
        if voyelle(c) or c == u"#":
            pieds += [Pied(c, i)]
        elif c != " ":
            pieds[-1].ajouteConsonne(c)
    return pieds[1:-1]
"""


def decoupe_pieds(vers):
    pieds = [Pied(None)]
    debut = u"##"
    
    diphtongues = ["ae", "oe", "eu", "au"]
    
    for c in vers:
        if c == '_':
            pieds[-1].longueur = 2
        elif c == ' ':
            pieds[-1].ajouteConsonne(" ")
        elif voyelle(c):
            # diphtongue ?
            # TODO: à améliorer - il faudrait aussi vérifier que la voyelle courante
            # n'a pas de marque de longueur
            if pieds[-1].longueur == 0 and debut[-1] + c in diphtongues:
                pieds[-1].voyelle += c
                pieds[-1].longueur = 2
            # suit q ?
            elif debut[-1] + c == "qu":
                pieds[-1].ajouteConsonne(c)
            # en tête de mot avec élision ?
            elif voyelle(debut[-2]) and debut[-1] == " ":
                pieds[-1].ajouteConsonne(c)
            # "vraie" voyelle ?
            else:
                pieds += [Pied(c)]
        else:
            pieds[-1].ajouteConsonne(c)
        
        if c != '_':
            debut += c
    
    return pieds


    

"""
def quantites_evidentes(pieds):
    resultat = []
    for p in pieds:
        q = 0
        # une voyelle suivie de 2 consonnes (ou plus) est allongée, mais pas 
        # systématiquement si sur les 2, la 2e est un r ou un l
        if len(p.consonnes) == 2 and not p.consonnes[1] in "rl":
            q = 2
        elif len(p.consonnes) > 2:
            q = 2
        if diphtongue(p.voyelle):
            q = 2
        resultat += [q]
    return resultat
"""

def applique_allongements(pieds):
    for p in pieds[1:]:
        if p.longueur == 0:
            conso = p.lesConsonnes()
            if len(conso) == 2 and not conso[1] in "rl":
                p.longueur = 2
            if len(conso) > 2:
                p.longueur = 2


def quantites_apriori(pieds):
    return map(lambda p: p.longueur, pieds[1:])


"""
def formate_scansion(vers, pieds, quantites):
    for i in range(len(pieds)-1, -1, -1):
        if quantites[i] > 0:   # si une quantité a été affectée
            if quantites[i] == 1:
                c = u"\u0306"
            elif quantites[i] == 2:
                c = u"\u0304"
            vers = vers[:pieds[i].position+1] + c + vers[pieds[i].position+1:]
    return vers
"""

marqueurs_quantites = {
    0: u"",
    1: u"\u0306",
    2: u"\u0304",
}

def formate_scansion(texte, pieds, quantites, mode):
    if mode == "txt":
        res = pieds[0].consonnes
        for i in range(1,(len(pieds))):
            res += pieds[i].voyelle
            res += marqueurs_quantites[quantites[i-1]]
            res += pieds[i].consonnes
            if i != len(pieds)-1:
                res += "/ "
        return u"{0}\t\t{1}\n".format(texte, res)
        
    elif mode == "html":
        h = u'<td rowspan="2">{0}</td>'.format(texte)
        h += u'<td></td>'       # * len(pieds[0].consonnes)
        b =  u'<td>{0}</td>'.format(pieds[0].consonnes)
        #'<td>' + '</td><td>'.join(pieds[0].consonnes) + '</td>'
        
        for i in range(1, len(pieds)):
            if quantites[i-1] == 1:
                symbole = u"˘"
            elif quantites[i-1] == 2:
                symbole = u"–"
            else:
                symbole = u""
            
            if pieds[i].longueur != 0:
                cls = u'class="apriori"'
            else:
                cls = ""
            
            h += u'<td {1}>{0}</td>'.format(symbole, cls)
            b += u'<td>{0}</td>'.format(pieds[i].voyelle)
            #h += u'<td colspan="{0}">{1}</td>'.format(len(pieds[i].voyelle), symbole)
            #b += '<td>' + '</td><td>'.join(pieds[i].voyelle) + '</td>'
            
            h += u'<td></td>'
            b += u'<td>{0}</td>'.format(pieds[i].consonnes)

            #h += u'<td></td>' * len(pieds[i].consonnes)
            #b += '<td>' + '</td><td>'.join(pieds[i].consonnes) + '</td>'
            
            if i != len(pieds)-1:
                h += u'<td></td>'
                b += u'<td>/</td>'
        
        return u'<table><tr>{0}</tr>\n       <tr>{1}</tr></table>\n'.format(h, b)


enclitiques = ["que", "ne", "ve"]

class Dictionnaire:
    def __init__(self):
        path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        self.conn = sqlite3.connect(path + '/mots.sqlite')
        self.conn.row_factory = sqlite3.Row
    
    def cherche(self, mot):
        c = self.conn.cursor()
        c.execute("SELECT longueurs from mots WHERE mot=?", (mot,))
        for r in c:
            return r["longueurs"]
        for e in enclitiques:
            if mot.endswith(e):
                r = self.cherche(mot[:-len(e)])
                if r != None:
                    return r + e
                else:
                    return None



def recherche_dictionnaire(vers):
    dic = Dictionnaire()
    debug = []
    non_trouves = []
    res = []
    for mot in vers.split():
        l = dic.cherche(mot)
        if l == None:
            debug += ["???"]
            non_trouves += [mot]
            res += [mot]
        else:
            debug += [l]
            res += [l]
    #print u"Recherche dans le dictionnaire: " + u" ".join(debug)
    res = u" ".join(res)
    return (res, non_trouves)



''' DUPLICAT
def decoupe_pieds2(vers):
    pieds = [Pied2(None)]
    debut = u"##"
    
    diphtongues = ["ae", "oe", "eu", "au"]
    
    for c in vers:
        if c == '_':
            pieds[-1].longueur = 2
        elif c == ' ':
            pieds[-1].ajouteConsonne(" ")
        elif voyelle(c):
            # diphtongue ?
            if debut[-1] + c in diphtongues:
                pieds[-1].voyelle += c
            # suit q ?
            elif debut[-1] + c == "qu":
                pieds[-1].ajouteConsonne(c)
            # en tête de mot avec élision ?
            elif voyelle(debut[-2]) and debut[-1] == " ":
                pieds[-1].ajouteConsonne(c)
            # "vraie" voyelle ?
            else:
                pieds += [Pied2(c)]
        else:
            pieds[-1].ajouteConsonne(c)
        
        if c != '_':
            debut += c
    
    return pieds[1:]
'''

def par(texte, mode):
    if mode == "txt":
        return texte
    else:
        return u"<p>{0}</p>".format(texte)

def scande(vers, type_vers, mode = "txt"):
    txt = u""
    #print( u"Entrée :    {0}".format(vers) )
    
    versNormalise = normalise(vers)
    #print( u"Normalisé : {0}".format(versNormalise) )

    (versPondere, non_trouves) = recherche_dictionnaire(versNormalise)
    if len(non_trouves) > 0:
        txt += par(u"Mots absents du dictionnaire : {0}\n".format(u", ".join(non_trouves)), mode)
    
    pieds = decoupe_pieds(versPondere)

    applique_allongements(pieds)
    
    quantites = quantites_apriori(pieds)
    
    res_quantites_apriori = formate_scansion(u"Quantités a priori", pieds, quantites, mode)
    if mode == "txt":
        txt += res_quantites_apriori
    
    #print( u"Longueurs : {0}".format(res) )
    
    possibilites = type_vers.scande( quantites )
    
    if possibilites == None or possibilites == []:
        if mode == "html":
            txt += res_quantites_apriori
        return (False, txt + par(u"Pas de solution trouvée", mode) )
    else:
        for (p, forme_vers) in possibilites:
            res = formate_scansion(u"{0:10}".format(forme_vers), pieds, p, mode)
            #print( u"Possibilité :  {0}\t\t{1}".format(res, forme_vers) )
            #txt += u"hello\n"
            txt += res
        return (True, txt)
    

def forme_hdsi(l):
    if l % 2 == 0:
        return V_HEXAMETRE
    else:
        return V_SENAIRE_IAMBIQUE

def forme_distique_elegiaque(l):
    if l % 2 == 0:
        return V_HEXAMETRE
    else:
        return V_PENTAMETRE

types = {
    "hdpd": forme_distique_elegiaque,
    "hdsi": forme_hdsi,
    "hd": (lambda(k): V_HEXAMETRE),
    "si": (lambda(k): V_SENAIRE_IAMBIQUE),
    "hp": (lambda(k): V_HENDECASYLLABE_PHALECIEN),
}

def scande_texte(type, lignes, mode="txt"):
    if not type in types:
        yield par( u"Type inconnu: " + type, mode )
        return
    
    schema_fun = types[type]
    i=0
    succes = 0
    for l in lignes:
        if mode=="html": yield(u'<div class="vers">')
        l = l.strip()
        type_vers = schema_fun(i)
        yield par( u"[{0}] {1}".format(type_vers.abbr, l), mode )
        (ok, msg) = scande(l, type_vers, mode)
        yield msg
        if ok:
            succes += 1
        i += 1
        if mode=="html": yield(u'</div>')
        yield ""

    yield par( u"Solutions trouvées dans {0} cas sur {1}".format(succes, i), mode )


def main():
    # vers d'Horace...
    #scande(u"Āltĕră /jām tĕrĭ/tūr bēl/līs cī/vīlĭbŭs /ǣtas", V_HEXAMETRE)
    
    #scande(u"sŭīs ĕt īpsă Rōmă vīrĭbūs rŭīt", V_SENAIRE_IAMBIQUE)
    
    #f = codecs.open("horace_brut.txt", "r", encoding="utf-8")
    #f = codecs.open("catulle_hendecasyllabe_phalecien.txt", "r", encoding="utf-8")
    #f = codecs.open("distique_elegiaque.txt", "r", encoding="utf-8")
    
    #f = codecs.open("ovide_metamorphoses.txt", "r", encoding="utf-8")
    f = codecs.open(sys.argv[1], "r", encoding="utf-8")
    
    prem = f.readline().strip()
    if prem.startswith("#"):
        type = prem[1:]
    else:
        raise Exception("Type de vers non indiqué")

    for r in scande_texte(type, f, mode="txt"):
        print codecs.encode(r, "utf-8")

    
    #for r in scande_texte("hd", f, mode="txt"):
    #    print codecs.encode(r, "utf-8")

    #for r in scande_texte("hd", [u"ille, datis vadibus qui rur' extractus in urb' est"]):
    #    print codecs.encode(r, "utf-8")

if __name__ == "__main__":
    main()



# À faire :
# - distinction voyelles/consolles (i/j, u/v)