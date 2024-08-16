

## Remarques :
### data 

- Attention, la requête de l'onglet ST-détails du fichier source Mouvements_Emballages est légèrement modifiée par rapport au PUSH qui porte le même nom. La différence se trouve dans la colonne Nom Tiers Agence et dans la requête où nous filtrons uniquement sur les agences.

- Dans la V3, nous utilisons les données issue de la requête de l'onglet "SV - Détails" car nous avons besoins que des soldes validés (à confirmer avec C.F)
- Dans la préparation des données : 
    - On ne prends pas les soldes = 0
    - On ne prends à la fin que les agences qui on au moins deux relations. C'est une condition nécéssaire pour avoir une triangulaire
    - Dans le fichier source 'raw', j'ai des tiers dont le 'tiers complet' est vide, je les drops car ce ne sont pas des agences d'exploitation.

- Le fichier raw est traité par prepare_raw_data et donne en sortie le fichier final.xlsx
- Exemple de lecture. Ci-dessous PATL ALLONNES doit récupérer 9 palette à PRA FEILLENS
    T_1	            TT_1	T_2	            TT_2	Support	    Solde
    PATL ALLONNES	Agence	PRA FEILLENS	Agence	PAL EUROPE	-9

### Documentation du Format JSON

Le fichier JSON contient un dictionnaire où chaque clé représente une agence. Pour chaque agence, nous avons une liste de triangulaires possibles. Chaque triangulaire est représenté par un dictionnaire contenant deux clés principales : `triangle` et `data`.

#### Structure du Fichier JSON

Le fichier JSON est structuré comme suit :

```json
    {
        "Nom_Agence_1": [nb_triangulaire,
            {
                "triangle": ["Nom_Agence_1", "tier_2", "tier_3"],
                "data": [
                    {
                        "T_1": "Agence_1",
                        "TT_1": "Agence",
                        "T_2": "Agence_2",
                        "TT_2": "Agence",
                        "Support": "Support_Description",
                        "Solde": Valeur_Solde
                    },
                    ...
                ]
            },
            ...
        ],
        ...
    }
```