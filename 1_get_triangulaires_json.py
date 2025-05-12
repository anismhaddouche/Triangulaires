import pandas as pd
from tqdm import tqdm
import time
import json
from utiles import create_unique_hash
from typing import Dict, List, Union



def get_triangulaires(df: pd.DataFrame, type_pal:str)->Dict[str, List[Union[int, Dict[str, Union[List[str], str, List[Dict[str, Union[str, int]]]]]]]]:
    """ Calcule toutes les triangulaires possibles pour un type de palette"""
    
    start_time = time.time()
    output_file=f"data/1_triangles_{type_pal}.json"
    output_file=output_file.replace(" ","_")
    
    df_pal=df[df["Support"]==type_pal]
    
    # Dictionnaire pour stocker les triangles trouvés avec agence_a comme clé
    triangles_dict = {}

    # Créer un set pour stocker les relations existantes
    relations = set(zip(df_pal['T_1'], df_pal['T_2']))

    # Extraire les agences principales uniquement une fois
    agences_principales = df_pal[df_pal['TT_1'] == "Agence"]['T_1'].unique()
    agences_secondaires = df_pal['T_2'].unique()
    agences_tertiaires = df_pal['T_1'].unique()

    # Itérer sur chaque agence principale avec une barre de progression
    for agence_a in tqdm(agences_principales, desc="Recherche des triangulaires..."):
        print(agence_a)
        # Liste pour stocker les triangles avec leurs données pour l'agence actuelle
        triangles_agence_data = []

        # Itérer sur chaque agence secondaire
        for agence_b in agences_secondaires:
            # Vérifier l'existence de la relation entre agence_a et agence_b
            if (agence_a, agence_b) not in relations:
                continue

            # Itérer sur chaque agence tertiaire
            for agence_c in agences_tertiaires:
                # Vérifier les deux relations supplémentaires pour former un triangle
                if ((agence_b, agence_c) in relations and
                    (agence_c, agence_a) in relations):
                    
                    # Créer un tuple trié pour le triangle (pour éliminer les doublons)
                    triangle = tuple(sorted([agence_a, agence_b, agence_c]))

                    # Calculer le hash unique pour ce triangle
                    triangle_hash = create_unique_hash(triangle)

                    # Filtrer le DataFrame pour ce triplet spécifique
                    df_triplet = df_pal[df_pal['T_1'].isin(triangle) & df_pal['T_2'].isin(triangle)]
                    df_triplet = df_triplet.drop_duplicates()

                    # Ajouter le triplet et les données correspondantes avec le hash
                    triangles_agence_data.append({
                        "triangle": list(triangle),
                        "hash": triangle_hash,
                        "data": df_triplet.to_dict(orient='records'),
                        "len_data": len(df_triplet)
                    })

        # Ajouter les résultats au dictionnaire final
        triangles_agence_data.insert(0, len(triangles_agence_data))
        if len(triangles_agence_data) != 1:
            triangles_dict[agence_a] = triangles_agence_data

    # Calculer et afficher le temps d'exécution total
    elapsed_time = time.time() - start_time
    print(f"Temps de recherche total : {elapsed_time:.2f} secondes")
    print("Enregistrement du fichier Json....")
    # Exporter les résultats en JSON
    with open(output_file, 'w') as json_file:
        json.dump(triangles_dict, json_file, indent=4, ensure_ascii=True)
    print("Enregistrement terminé")
    return triangles_dict



if __name__=="__main__":
    df = pd.read_excel('data/0_final.xlsx')
    # print('### Traitement des Palettes EUROPE...')
    # get_triangulaires(df, 'PAL EUROPE')
    print('### Traitement des Palettes EUROPE...')
    get_triangulaires(df, 'PAL EUROPE')




