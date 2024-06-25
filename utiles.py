
import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd 


def balance_two_accounts(df, agency1, agency2):
    steps = []  # Liste pour stocker les étapes de transfert

    # Etape 1 : Équilibrer agency1 vers agency2
    val_col = df.at[agency2, agency1]
    if val_col != 0:
        df.at[agency2, agency1] = 0  # Mettre à zéro la colonne agency1 de agency2
        print(f"Step 1: Transfer {val_col} from {agency1} to {agency2}")
        condition = (df[agency1] != val_col) & (df[agency1] != 0)
        df.loc[condition, agency1] += val_col
        df.loc[agency1, condition] -= val_col
        # steps.append(f"Transfer {val_col} from {agency1} to {agency2}")

    # Etape 2 : Équilibrer agency2 vers agency1
    val_col = df.at[agency1, agency2]
    if val_col != 0:
        df.at[agency1, agency2] = 0  # Mettre à zéro la colonne agency2 de agency1
        print(f"Step 2: Transfer {val_col} from {agency2} to {agency1}")
        condition = (df[agency2] != val_col) & (df[agency2] != 0)
        df.loc[condition, agency2] += val_col
        df.loc[agency2, condition] -= val_col
        # steps.append(f"Transfer {val_col} from {agency2} to {agency1}")
    return df

def get_triangulaires(df_support):
    list_triangulaire = []
    for agence_a in df_support["agence_1"].unique():
        for agence_b in df_support["agence_2"].unique():
            if not df_support[
                (df_support["agence_1"] == agence_a)
                & (df_support["agence_2"] == agence_b)
            ].empty:
                for agence_c in df_support["agence_1"].unique():
                    if not df_support[
                        (df_support["agence_1"] == agence_b)
                        & (df_support["agence_2"] == agence_c)
                    ].empty:
                        if not df_support[
                            (df_support["agence_1"] == agence_c)
                            & (df_support["agence_2"] == agence_a)
                        ].empty:
                            list_triangulaire.append([agence_a, agence_b, agence_c])
    return list_triangulaire

def get_agences_triangulaires(list_triangulaire):
    unique_agencies = set()
    for combination in list_triangulaire:
        for agency in combination:
            unique_agencies.add(agency)
    unique_agencies_list = list(unique_agencies)
    unique_agencies_list.sort()
    return unique_agencies_list


def reverse_asymetric_matrix(asymmetric_matrix):
    data_reversed = []
    for agence_1 in asymmetric_matrix.index:
        for agence_2 in asymmetric_matrix.columns:
            if asymmetric_matrix.loc[agence_1, agence_2] != 0:
                data_reversed.append([agence_1, agence_2, asymmetric_matrix.loc[agence_1, agence_2], 'Oui'])

    reversed_asymmetric_matrix = pd.DataFrame(data_reversed, columns=['agence_1', 'agence_2', 'Solde', 'Solde confirmé ?'])
    reversed_asymmetric_matrix.reset_index()
    # Ajout de l'index
    return reversed_asymmetric_matrix

def plot_triangulaires(df_final,num_cols = 3):
        
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