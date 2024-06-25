import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from utiles import balance_two_accounts, get_triangulaires, get_agences_triangulaires, plot_triangulaires, reverse_asymetric_matrix
st.set_page_config(layout="wide")



  

#  Charger les données
st.write("# Triangulaires avant")
df = pd.read_csv(
    "data/Mouvements_Emballages_ST_Details_cleaned.csv",
    sep=",",
    encoding="utf8",
    index_col=[0],
)

# Création de sidebar pour choisir type de support
with st.sidebar:
    st.write(f"## Date de solde :    {df['Date Solde'].loc[0]}")
    support = st.selectbox(
        "## Choisissez un support : ", df["Support"].unique()
    )
    df_support = df[df["Support"] == support]
    df_support = df_support[
        df_support["Solde"] != 0
    ]
    df_support.drop_duplicates(inplace=True)
    
df_support.drop(["Date Solde", "Support"], axis=1, inplace=True)
# Chercher toutes les triangulaires possibles
list_triangulaire = get_triangulaires(df_support)
# Lister les agences qui apparaissent dans au moins une triangulaire
unique_agencies_list = get_agences_triangulaires(list_triangulaire)

if len(unique_agencies_list) == 0:
    st.write("# Pas de triangulaire possible")
else:
    # Afficher les combinaisons uniques sans doublons
    st.write(f"Afficher les agences concernées par des triangulaires :") 
    if st.button('Afficher'):
        st.write(unique_agencies_list)
    selected_agence_a = st.selectbox("Choisissez l'agence A :", unique_agencies_list)
    df_a = df_support[
        df_support["agence_1"] == selected_agence_a
    ]
    # Choisir une agence B
    selected_agence_b = st.selectbox(
        "Choisissez l'agence B :", df_a["agence_2"].dropna().unique()
    )
    df_b = df_support[
        (df_support["agence_1"] == selected_agence_b)
        & (df_support["agence_2"] != selected_agence_a)
    ]
    # L'utilisateur doit choisir dans la colonne 2 de df_b une troisième agence C uniquement les agences qui ont un solde avec A
    list_agences_c = []
    for agence in df_b["agence_2"].unique():
        if not df_support[
            (df_support["agence_1"] == agence)
            & (df_support["agence_2"] == selected_agence_a)
        ].empty:
            list_agences_c.append(agence)
    if len(list_agences_c) == 0:
        st.write(f"### Pas de triangulaire possible entre ces deux agences. Choisissez une autre agence B")

    else:
        # st.write(f"### {len(list_agences_c)} triangulaire(s) possible(s)")
       
        selected_agence_c = st.selectbox(
            f"Choisissez l'agence C ({len(list_agences_c)} triangulaire(s) possible(s)) :", sorted(list_agences_c)
        )
        # unique_agencies_list.remove(selected_agence_b)
        # selected_agence_c = st.selectbox("Choisissez l'agence C :", unique_agencies_list)
        # Calcul des soldes entre les agences sélectionnées
        Solde_ab = df_support[
            (df_support["agence_1"] == selected_agence_a)
            & (df_support["agence_2"] == selected_agence_b)
        ]
        Solde_bc = df_support[
            (df_support["agence_1"] == selected_agence_b)
            & (df_support["agence_2"] == selected_agence_c)
        ]
        Solde_ac = df_support[
            (df_support["agence_1"] == selected_agence_c)
            & (df_support["agence_2"] == selected_agence_a)
        ]
        # st.write("### Soldes entre A, B et Cs")
        soldes = pd.concat([Solde_ab, Solde_bc, Solde_ac], ignore_index=True)
        # st.write(soldes)
        df2 = soldes.copy()
        df2["agence_1"], df2["agence_2"] = df2["agence_2"], df2["agence_1"]
        df2["Solde"] *= -1
        df_final = pd.concat([soldes, df2], ignore_index=True)
        # st.write(df_final)

        # Affichage des barres pour chaque agence avec Streamlit
        st.write("Visualisation des soldes avant triangulaire (*) :")
        plot_triangulaires(df_final)
       
    
        # if st.button("Action"):
            # agency1 = "PLM PLAN D'ORGON"
            # agency2 = "GUIDEZ MONCHY LE PREUX"
        st.write("# Triangulaires après")
        unique_agencies_list = list(df_final['agence_1'].unique())
        agency1 = st.selectbox("Choisissez l'agence A :", unique_agencies_list)
        unique_agencies_list.remove(agency1)
        agency2 = st.selectbox("Choisissez l'agence B :",unique_agencies_list )

        # st.write(df_final.sort_values(by=["agence_1"]))
        
        asymmetric_matrix = df_final.pivot(index='agence_1', columns='agence_2', values='Solde')
        asymmetric_matrix = asymmetric_matrix.fillna(0)
        # st.write((asymmetric_matrix))
        
    
        # # Appeler la fonction pour équilibrer les comptes
        balanced_asymmetric_matrix = balance_two_accounts(asymmetric_matrix, agency1, agency2)
        reversed_reverse_asymetric_matrix = reverse_asymetric_matrix(balanced_asymmetric_matrix)
        # st.write(reversed_reverse_asymetric_matrix)
        # st.write(balanced_asymmetric_matrix)
        st.write("Visualisation des soldes après triangulaire (*) :")
        plot_triangulaires(reversed_reverse_asymetric_matrix, 3)
            
        st.write("""
                (*) Comment lire ces graphiques :
                * Rouge (solde positif)   : Lorsque la colonne est en rouge, cela signifie que l’agence en titre doit des palettes à l’agence en bas de la colonne.
                * Vert (solde négatif) : Lorsque la colonne est en vert, c’est l’inverse. Cela signifie que l’agence en titre doit récupérer des palettes de l’agence en bas.
                """)