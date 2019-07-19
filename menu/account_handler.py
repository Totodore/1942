import requests
import json

def get_online_score():
    try:
        r = requests.get("http://xrtp.scriptis.fr/scores.json", timeout=5)
        score_json = r.json()
        print(score_json)
    except requests.ConnectionError:
        print("ERROR ! Connection error while requesting online scores, check your connection or contact us")
        return False
    except requests.Timeout:
        print("ERROR ! Connection timed out while requesting online scores, check your connection or contact us")
        return False
    if len(score_json) == 0:
        print("ERROR ! Connection error while requesting online scores, check your connection or contact us")
        return False

    #On trie le score
    sorted_score = []
    #Pour chaque score à trier
    for score in score_json["score"]:
        print(score)
        i = 0
        #Pour chaque score déjà trié
        for sorted_score_el in sorted_score:
            #si le score à trier est plus petit qu'un score trié on le met juste après
            if score["score"] < sorted_score_el["score"]:
                sorted_score.insert(i, score)
                break
            i += 1
        #si le score à trier n'est pas encore dans les score triés ca veut dire
        # qu'il est plus grand que tous alors on le met en premier
        if not score in sorted_score:
            sorted_score.insert(0, score)
    print(sorted_score)
    return sorted_score


def set_online_score(json_data):
    json_tosave = {
        "score": json_data
    }
    data = {"json": json.dumps(json_tosave, indent=4)}
    print(json_data)
    try:
        print("Request Launched")
        r = requests.post("http://xrtp.scriptis.fr/add_score.php", data)
        if r.status_code == 202: return True
        else: return False
    except requests.ConnectionError:
        print("ERROR ! Connection error while requesting online scores, check your connection or contact us")
        return False
    except requests.Timeout:
        print("ERROR ! Connection timed out while requesting online scores, check your connection or contact us")
        return False
