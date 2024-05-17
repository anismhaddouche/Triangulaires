import pandas as pd 
import matplotlib.pyplot as plt
import streamlit as st
st.set_page_config(layout="wide")


# Charger les données TODO : Rajouter un filtre sur le type de palettes 
df = pd.read_csv("data/Mouvements_Emballages_ST_Details_cleaned.csv", sep=";", encoding="utf8", index_col=[0])



with st.sidebar:
    st.header("Filtres")
    # Choisir une région 
    region = st.selectbox("## Choisissez une région :", sorted(df['Région'].unique()))
    df_region = df[(df['Région']==region)]
    # Choisir une date
    mois_an_solde = st.selectbox("## Choisissez une date :", sorted(df['Date Solde'].unique(), reverse=True))
    df_region_date = df_region[(df_region['Région']==region) & (df_region["Date Solde"] == mois_an_solde )]
    # Choisir un support 
    support = st.selectbox("## Choissiez un support : ", df_region_date['Support'].unique())
    df_region_date_support = df_region_date[df_region_date["Support"] == support]
    # Choisir une agence A
    selected_agence_a = st.selectbox("Choisissez l'agence A :", df_region_date_support['agence_1'].unique())
    df_a = df_region_date_support[df_region_date_support['agence_1'] == selected_agence_a]
    # Choisir une agence B 
    selected_agence_b = st.selectbox("Choisissez l'agence B :", df_a['agence_2'].unique())
    #---------------------------------
list_triangulaire = []
for agence_a in df_region_date_support['agence_1'].unique(): 
    for agence_b in df_region_date_support['agence_2'].unique():
        if not df_region_date_support[(df_region_date_support['agence_1']== agence_a) & (df_region_date_support['agence_2'] == agence_b)].empty: 
            for agence_c in df_region_date_support['agence_1'].unique():
                if not df_region_date_support[(df_region_date_support['agence_1']== agence_b) & (df_region_date_support['agence_2'] == agence_c)].empty: 
                    if not df_region_date_support[(df_region_date_support['agence_1']== agence_c) & (df_region_date_support['agence_2'] == agence_a)].empty: 
                        list_triangulaire.append([agence_a, agence_b, agence_c])
liste_combinaisons  =  list_triangulaire       
combinaisons_uniques = set()
# Liste pour stocker les combinaisons uniques
combinaisons_sans_doublons = []
# Parcourir la liste de listes
for combinaison in liste_combinaisons:
    # Convertir la combinaison en tuple pour la rendre hashable
    combinaison_tuple = tuple(combinaison)
    # Vérifier si la combinaison n'existe pas déjà dans l'ensemble des combinaisons uniques
    if combinaison_tuple not in combinaisons_uniques:
        # Ajouter la combinaison à la liste des combinaisons uniques et à l'ensemble
        combinaisons_sans_doublons.append(combinaison)
        combinaisons_uniques.add(combinaison_tuple)

#Afficher les combinaisons uniques sans doublons

st.write(combinaisons_uniques)


# 2.2- Filtrer sur agence_b dans le df --> en sortie df_b
df_b = df_region_date_support[(df_region_date_support['agence_1'] == selected_agence_b) & (df_region_date_support['agence_2'] != selected_agence_a)]

# Filter uniquement sur les agences avec un solde existant avec A 

# 3.1- L'utilisateur doit choisir dans la colonne 2 de df_b une troisième agence (c)  uniquement les agences qui ont un solde avec A 
list_agences_c = []
for agence in df_b['agence_2'].unique(): 
    if not df_region_date_support[(df_region_date_support['agence_1']== agence) & (df_region_date_support['agence_2'] == selected_agence_a)].empty: 
        list_agences_c.append(agence)
if len(list_agences_c) == 0:
    st.write(f"## Pas de triangulaire possible")
            
else : 
    
    st.write(f"## {len(list_agences_c)} triangulaire(s) possible(s)")
    selected_agence_c = st.selectbox("Choisissez l'agence C :", sorted(list_agences_c))

    # Calcul des soldes entre les agences sélectionnées
    Solde_ab = df_region_date_support[(df_region_date_support["agence_1"] == selected_agence_a) & (df_region_date_support["agence_2"] == selected_agence_b)]
    Solde_bc = df_region_date_support[(df_region_date_support["agence_1"] == selected_agence_b) & (df_region_date_support['agence_2'] == selected_agence_c)]
    Solde_ac = df_region_date_support[(df_region_date_support['agence_1'] == selected_agence_c) & (df_region_date_support['agence_2'] == selected_agence_a)]

    st.write("## Soldes entre A, B et C")
    soldes = pd.concat([Solde_ab, Solde_bc, Solde_ac], ignore_index=True)
    st.write(soldes)


    # Concaténation des soldes
    # Duplication du dataframe et inversion des colonnes et des signes
    df2 = soldes.copy()
    df2['agence_1'], df2['agence_2'] = df2['agence_2'], df2['agence_1']
    df2['Solde'] *= -1
    df_final = pd.concat([soldes, df2], ignore_index=True)
    # Affichage des barres pour chaque agence avec Streamlit
    st.write("## Visualisation des soldes entre les agences sélectionnées")

    # Déterminer le nombre de colonnes pour la grille
    num_cols = 3

    # Déterminer le nombre total d'agences et le nombre de lignes nécessaires
    num_agences = len(df_final['agence_1'].unique())
    num_rows = (num_agences + num_cols - 1) // num_cols

    # Créer une grille de graphiques côte à côte
    fig, axs = plt.subplots(num_rows, num_cols, figsize=(15, 5*num_rows))

    # Parcourir chaque agence et créer un graphique
    for i, agence in enumerate(df_final['agence_1'].unique()):
        df_agence = df_final[df_final['agence_1'] == agence]
        colors = ['green' if solde < 0 else 'red' for solde in df_agence['Solde']]
        row = i // num_cols
        col = i % num_cols
        # Vérifier si l'index est valide avant d'accéder à la grille d'axes
        if num_rows > 1:
            ax = axs[row, col] if i < num_agences else None
        else:
            ax = axs[col] if i < num_agences else None
        if ax is not None:
            bars = ax.bar(list(df_agence['agence_2'].values), df_agence['Solde'], color=colors)
            for bar, solde in zip(bars, df_agence['Solde']):
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), str(solde), ha='center', va='bottom')
            ax.set_title(agence)

    # Supprimer les axes non utilisés
    for i in range(num_agences, num_rows*num_cols):
        row = i // num_cols
        col = i % num_cols
        # Vérifier si l'index est valide avant d'accéder à la grille d'axes
        if num_rows > 1:
            ax = axs[row, col]
        else:
            ax = axs[col]
        ax.axis('off')
    plt.tight_layout()
    st.pyplot(fig)
    
