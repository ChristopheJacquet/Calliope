#!/usr/bin/env python
# coding=utf8

import codecs

def strlist(l):
    return u"[{0}]".format(u", ".join(unicode(x) for x in l))



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


class TypeVers:
    def __init__(self, motif_pieds):
        self.motif_pieds = motif_pieds
        
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
P_INDIF_TROCHEE_SPONDEE = TypePied([2, 0], u't/s')

V_HEXAMETRE = TypeVers([
    ChoixPied([P_DACTYLE, P_SPONDEE]),
    ChoixPied([P_DACTYLE, P_SPONDEE]),
    ChoixPied([P_DACTYLE, P_SPONDEE]),
    ChoixPied([P_DACTYLE, P_SPONDEE]),
    ChoixPied([P_DACTYLE, P_SPONDEE]),
    P_INDIF_TROCHEE_SPONDEE
])

V_SENAIRE_IAMBIQUE = TypeVers([
    P_IAMBE,
    P_IAMBE,
    P_IAMBE,
    P_IAMBE,
    P_IAMBE,
    ChoixPied([P_IAMBE, P_DACTYLE])
])

def voyelle(c):
    return c in u"aeiouæœαε"

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
        elif c in u"ǣ": c = u"æ"
        elif c in u"/,?;.:«»()": continue
        
        resultat += c
    
    return resultat

# si un mot se termine par une voyelle, et si le mot suivant commence par
# une voyelle, alors on supprime la voyelle finale du premier mot
def applique_elisions(vers):
    resultat = u""
    
    for i in range(0, len(vers)-2):
        if voyelle(vers[i]) and vers[i+1] == u" " and voyelle(vers[i+2]):
            continue
        resultat += vers[i]
        
    resultat += vers[-2:]
    
    return resultat


# remplace les diphtongues par des voyelles uniques
# qv devient qu
def remplace_diphtongues(vers):
    return vers.replace(u"qu", u"q").replace(u" iu", u" ju").replace(u"ae", u"æ").replace(u"eu", u"ε").replace(u"au", u"α").replace(u"oe", u"œ")
    
def diphtongue(c):
    return c in u"æœαε"


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
    

def quantites_evidentes(pieds):
    resultat = []
    for p in pieds:
        q = 0
        if len(p.consonnes) >= 2:
            q = 2
        if diphtongue(p.voyelle):
            q = 2
        resultat += [q]
    return resultat


def formate_scansion(vers, pieds, quantites):
    for i in range(len(pieds)-1, -1, -1):
        if quantites[i] > 0:   # si une quantité a été affectée
            if quantites[i] == 1:
                c = u"\u0306"
            elif quantites[i] == 2:
                c = u"\u0304"
            vers = vers[:pieds[i].position+1] + c + vers[pieds[i].position+1:]
    return vers
        

def scande(vers, type_vers):
    #print( u"Entrée :    {0}".format(vers) )
    
    versNormalise = normalise(vers)
    #print( u"Normalisé : {0}".format(versNormalise) )
    
    versElide = applique_elisions(versNormalise)
    #print( u"Élidé :     {0}".format(versElide) )
    
    versSimplifie = remplace_diphtongues(versElide)
    #print( u"Simplifié : {0}".format(versSimplifie) )
    
    pieds = decoupe_pieds(versSimplifie)
    #print( u"Pieds :     {0}".format(strlist(pieds)) )
    
    quantites = quantites_evidentes(pieds)
    res_quantites_apriori = formate_scansion(versSimplifie, pieds, quantites)
    #print( u"Longueurs : {0}".format(res) )
    
    possibilites = type_vers.scande( quantites )
    
    if possibilites == None or possibilites == []:
        return (False, u"-- Quantités a priori : {0}\n".format(res_quantites_apriori) )
    else:
        txt = u""
        for (p, forme_vers) in possibilites:
            res = formate_scansion(versSimplifie, pieds, p)
            #print( u"Possibilité :  {0}\t\t{1}".format(res, forme_vers) )
            #txt += u"hello\n"
            txt += u"{1:10}\t\t{0}\n".format(res, forme_vers)
        return (True, txt)
    

def forme_vers_horace(l):
    if l % 2 == 0:
        return V_HEXAMETRE
    else:
        return V_SENAIRE_IAMBIQUE

types = {
    "hdsi": forme_vers_horace
}

def scande_texte(type, lignes):
    if not type in types:
        yield u"Type inconnu: " + type
        return
        
    schema_fun = types[type]
    i=0
    succes = 0
    for l in lignes:
        l = l.strip()
        yield u"* {0}".format(l)
        (ok, msg) = scande(l, forme_vers_horace(i))
        yield msg
        if ok:
            succes += 1
        i += 1
        yield ""

    yield u"Solutions trouvées dans {0} cas sur {1}".format(succes, i)


def main():
    # vers d'Horace...
    #scande(u"Āltĕră /jām tĕrĭ/tūr bēl/līs cī/vīlĭbŭs /ǣtas", V_HEXAMETRE)
    
    #scande(u"sŭīs ĕt īpsă Rōmă vīrĭbūs rŭīt", V_SENAIRE_IAMBIQUE)
    
    f = codecs.open("horace_brut.txt", "r", encoding="utf-8")
    
    for r in scande_texte("hdsi", f):
        yield r


if __name__ == "__main__":
    main()



# À faire :
# - distinction voyelles/consolles (i/j, u/v)