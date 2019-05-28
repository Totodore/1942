import os
import json
import operator
"""
Fonction de récupèration de la sauvegarde du mode campagne
"""
def get_save_campain():
    save_file = None
    #si ya pas de fichier lance la création d'un fichier de sauvegarde et on retourne -1
    try:
        save_file = open("./save/save.txt", "r")        
    except FileNotFoundError:
        set_save_campain(0)
        return -1
    line = save_file.readline()
    if len(line) != 1: #si le contenus du fichier save est différent de un caractère on créer save et on retourne -1
        set_save_campain(0)
        return -1
    #sinon on retourne l'index de la save
    return line

"""
Fonction de création ou de changement de la save du mode campagne
"""
def set_save_campain(level):
    #on supprime l'ancienne save
    try:
        os.remove("./save/save.txt")        
    except FileNotFoundError:
        pass
    #on créé une nouvelle   
    save_file = open("./save/save.txt", "x")
    #on écrit le dernier niveau disponible dedans
    save_file.write(str(level))
    save_file.close()


"""
Fonction de récupération de la sauvegarde du mode arcade
"""
def get_save_arcade():
    save_file = None
    #si ya pas de fichier lance la création d'un fichier de sauvegarde puis on relit le fichier
    try:
        save_file = open("./save/arcade.json", "r")        
    except FileNotFoundError:
        set_save_arcade()
        return get_save_arcade()

    try:
        json_save = json.load(save_file)
    except (ValueError, RecursionError):
        print("Error while parsing json arcade data !")
        set_save_arcade()
        return get_save_arcade()

    returned_data = []

    #Pour chaque score à trier
    for score in json_save["score"]:
        i = 0
        #Pour chaque score déjà trié
        for sorted_score in returned_data:
            #si le score à trier est plus petit qu'un score trié on le met juste après
            if score["score"] < sorted_score["score"]:
                returned_data.insert(i, score)
                break
            i += 1
        #si le score à trier n'est pas encore dans les score triés ca veut dire 
        # qu'il est plus grand que tous alors on le met en premier
        if not score in returned_data:
            returned_data.insert(0, score)
    #on retourne le tout
    return returned_data
    
"""
Fonction de création ou de changement de la save du mode arcade
"""

def set_save_arcade(json_data = None):
    #on supprime l'ancienne save
    try:
        os.remove("./save/arcade.json")        
    except FileNotFoundError:
        pass
    #on créé une nouvelle   
    save_file = open("./save/arcade.json", "x")
    #on écrit tous les gagnants dedans
    
    if json_data:
        json_tosave = {
            "score": json_data
        }
        save_file.write(json.dumps(json_tosave, indent=4))
    else: 
        save_file.write('{"score": []}')
    save_file.close()