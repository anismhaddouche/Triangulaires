import pandas as pd 
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(layout="wide")
# Charger les données
data= pd.read_csv("TestData_v1.csv", sep=";", encoding="utf8", index_col=[0])
data.rename(columns={"Agence": 'agence_1', "Nom Tiers Agence": 'agence_2'}, inplace=True)

st.write("## Sélection de la date des soldes")
mois_an_solde = st.selectbox("## Choisissez une date :", sorted(data['Date Solde'].unique(), reverse=True))
# st.title(f"Date des soldes : {mois_an_solde}")


# df_all = data[(data["Date Solde"] == mois_an_solde ) & (data['Solde'] != 0)]
df_all = data[(data["Date Solde"] == mois_an_solde )]
st.write(df_all)

# Affichage des agences côte à côte
col1, col2, col3 = st.columns(3)

# 1- Afficher le df_all des commandes confirmées et demander à l'utilisateur de Choisir la première agence (A)
df = df_all[df_all["Solde confirmé ?"] == 'Oui']
with col1:
    st.write("## Sélection de l'agence A")
    selected_agence_a = st.selectbox("Choisissez l'agence A :", sorted(df['agence_1'].unique()))

# 2.1- L'utilisateur doit choisir dans la colonne 2 de df_a une deuxième agence (B)
with col2:
    st.write("## Sélection de l'agence B")
    df_a = df[df['agence_1'] == selected_agence_a]
    selected_agence_b = st.selectbox("Choisissez l'agence B :", sorted(df_a['agence_2'].unique()))

# 2.2- Filtrer sur agence_b dans le df --> en sortie df_b
df_b = df[(df['agence_1'] == selected_agence_b) & (df['agence_2'] != selected_agence_a)]

# 3.1- L'utilisateur doit choisir dans la colonne 2 de df_b une troisième agence (c)
with col3:
    st.write("## Sélection de l'agence C")
    selected_agence_c = st.selectbox("Choisissez l'agence C :", sorted(df_b['agence_2'].unique()))

# Calcul des soldes entre les agences sélectionnées
Solde_ab = df[(df["agence_1"] == selected_agence_a) & (df["agence_2"] == selected_agence_b)]
Solde_bc = df[(df["agence_1"] == selected_agence_b) & (df['agence_2'] == selected_agence_c)]
# Solde_ac = df[(df['agence_2'] == selected_agence_a) & (df['agence_1'] == selected_agence_c)]
Solde_ac = df[(df['agence_1'] == selected_agence_c) & (df['agence_2'] == selected_agence_a)]

st.write("## Soldes entre A, B et C")
soldes = pd.concat([Solde_ab, Solde_bc, Solde_ac], ignore_index=True)
st.write(soldes)

if Solde_ac.empty :
        st.write(f"## Pas de triangulaire possible")
            
else : 
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
