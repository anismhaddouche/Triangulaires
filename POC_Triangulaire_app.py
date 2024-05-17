import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(layout="wide")


#  Charger les donnée
df = pd.read_csv(
    "data/Mouvements_Emballages_ST_Details_cleaned.csv",
    sep=";",
    encoding="utf8",
    index_col=[0],
)
df.drop(["Région"], axis=1, inplace=True)
#  Filtre sur la région la date et le support
with st.sidebar:
    st.header("Filtres")
    # Choisir une date
    mois_an_solde = st.selectbox(
        "## Choisissez une date :", sorted(df["Date Solde"].unique(), reverse=True)
    )
    df_date = df[
                 (df["Date Solde"] == mois_an_solde)
    ]
    # Choisir un support
    support = st.selectbox(
        "## Choissiez un support : ", df_date["Support"].unique()
    )
    df_date_support = df_date[df_date["Support"] == support]
    df_date_support = df_date_support[
        df_date_support["Solde"] != 0
    ]
    df_date_support.drop_duplicates(inplace=True)
df_date_support.drop(["Date Solde", "Support"], axis=1, inplace=True)

# Calcul de toutes les triangulaires possibles en fonction des filtres précédents
list_triangulaire = []
for agence_a in df_date_support["agence_1"].unique():
    for agence_b in df_date_support["agence_2"].unique():
        if not df_date_support[
            (df_date_support["agence_1"] == agence_a)
            & (df_date_support["agence_2"] == agence_b)
        ].empty:
            for agence_c in df_date_support["agence_1"].unique():
                if not df_date_support[
                    (df_date_support["agence_1"] == agence_b)
                    & (df_date_support["agence_2"] == agence_c)
                ].empty:
                    if not df_date_support[
                        (df_date_support["agence_1"] == agence_c)
                        & (df_date_support["agence_2"] == agence_a)
                    ].empty:
                        list_triangulaire.append([agence_a, agence_b, agence_c])

# Lister les agences qui apparaissent dans au moins une triangulaire
unique_agencies = set()
for combination in list_triangulaire:
    for agency in combination:
        unique_agencies.add(agency)
unique_agencies_list = list(unique_agencies)

if len(unique_agencies_list) == 0:
    st.write("# Pas de triangulaire possible")
else:
    # Afficher les combinaisons uniques sans doublons
    if st.button('Afficher les agences concernées pas des triangulaires'):
        st.write(unique_agencies_list)
    selected_agence_a = st.selectbox("Choisissez l'agence A :", unique_agencies_list)
    df_a = df_date_support[
        df_date_support["agence_1"] == selected_agence_a
    ]
    # Choisir une agence B
    selected_agence_b = st.selectbox(
        "Choisissez l'agence B :", df_a["agence_2"].dropna().unique()
    )
    df_b = df_date_support[
        (df_date_support["agence_1"] == selected_agence_b)
        & (df_date_support["agence_2"] != selected_agence_a)
    ]
    # L'utilisateur doit choisir dans la colonne 2 de df_b une troisième agence C uniquement les agences qui ont un solde avec A
    list_agences_c = []
    for agence in df_b["agence_2"].unique():
        if not df_date_support[
            (df_date_support["agence_1"] == agence)
            & (df_date_support["agence_2"] == selected_agence_a)
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
        Solde_ab = df_date_support[
            (df_date_support["agence_1"] == selected_agence_a)
            & (df_date_support["agence_2"] == selected_agence_b)
        ]
        Solde_bc = df_date_support[
            (df_date_support["agence_1"] == selected_agence_b)
            & (df_date_support["agence_2"] == selected_agence_c)
        ]
        Solde_ac = df_date_support[
            (df_date_support["agence_1"] == selected_agence_c)
            & (df_date_support["agence_2"] == selected_agence_a)
        ]
        # st.write("### Soldes entre A, B et Cs")
        soldes = pd.concat([Solde_ab, Solde_bc, Solde_ac], ignore_index=True)
        # st.write(soldes)
        df2 = soldes.copy()
        df2["agence_1"], df2["agence_2"] = df2["agence_2"], df2["agence_1"]
        df2["Solde"] *= -1
        df_final = pd.concat([soldes, df2], ignore_index=True)
        # Affichage des barres pour chaque agence avec Streamlit
        st.write("Visualisation des soldes (*)")
        # Déterminer le nombre de colonnes pour la grille
        num_cols = 3
        # Déterminer le nombre total d'agences et le nombre de lignes nécessaires
        num_agences = len(df_final["agence_1"].unique())
        num_rows = (num_agences + num_cols - 1) // num_cols
        # Créer une grille de graphiques côte à côte
        fig, axs = plt.subplots(num_rows, num_cols, figsize=(15, 5 * num_rows))
        # Parcourir chaque agence et créer un graphique
        for i, agence in enumerate(df_final["agence_1"].unique()):
            df_agence = df_final[df_final["agence_1"] == agence]
            colors = ["green" if solde < 0 else "red" for solde in df_agence["Solde"]]
            row = i // num_cols
            col = i % num_cols
            # Vérifier si l'index est valide avant d'accéder à la grille d'axes
            if num_rows > 1:
                ax = axs[row, col] if i < num_agences else None
            else:
                ax = axs[col] if i < num_agences else None
            if ax is not None:
                bars = ax.bar(
                    list(df_agence["agence_2"].values), df_agence["Solde"], color=colors
                )
                for bar, solde in zip(bars, df_agence["Solde"]):
                    ax.text(
                        bar.get_x() + bar.get_width() / 2,
                        bar.get_height(),
                        str(solde),
                        ha="center",
                        va="bottom",
                    )
                ax.set_title(agence)
        # Supprimer les axes non utilisés
        for i in range(num_agences, num_rows * num_cols):
            row = i // num_cols
            col = i % num_cols
            # Vérifier si l'index est valide avant d'accéder à la grille d'axes
            if num_rows > 1:
                ax = axs[row, col]
            else:
                ax = axs[col]
            ax.axis("off")
        plt.tight_layout()
        st.pyplot(fig)
        st.write("""
                (*) Comment les ces graphiques :
                * Vert (solde négatif) : Lorsque la colonne est en vert, cela signifie que l’agence en titre doit des palettes à l’agence en bas de la colonne.
                * Rouge (solde positif) : Lorsque la colonne est en rouge, c’est l’inverse. Cela signifie que l’agence en titre doit récupérer des palettes de l’agence en bas.
                """)