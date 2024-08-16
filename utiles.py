import json
import hashlib
import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
from typing import Dict, Any


def create_unique_hash(elements: list) -> str:
    """Crée un hash unique pour une liste d'éléments."""
    sorted_elements = sorted(elements)
    elements_string = ",".join(sorted_elements)
    unique_hash = hashlib.sha256(elements_string.encode()).hexdigest()
    return unique_hash


def search_triangle_in_json(
    agence_1: str, tiers_2: str, tiers_3: str, support='PAL EUROPE' 
) -> Dict[str, Any]:
    """Recherche des données pour une triangulaire donnée dans un fichier JSON en fonction de son hash."""
    # Créer le hash pour le triangle recherché
    json_file= f"data/1_triangles_{support}.json"
    search_triangle = [agence_1, tiers_2, tiers_3]
    search_hash = create_unique_hash(search_triangle)

    # Lire le fichier JSON
    try:
        with open(json_file, "r") as file:
            triangles_dict = json.load(file)
    except FileNotFoundError:
        raise FileNotFoundError(f"Le fichier {json_file} est introuvable.")
    except json.JSONDecodeError:
        raise ValueError("Le fichier JSON est mal formé.")

    # Rechercher les données dans le dictionnaire
    for triangle_data in triangles_dict[agence_1][1:]:  # Skip the first item (count)
        if triangle_data.get("hash") == search_hash:
            return {
                "triangle": triangle_data.get("triangle"),
                "data": triangle_data.get("data"),
                "len_data": triangle_data.get("len_data"),
            }

    return "Triangle non trouvé dans le fichier JSON."


def plot_triangulaires(df: pd.DataFrame, num_cols: int = 3):
    """Trace les graphiques des triangulaires en fonction des données dans le dataframe."""
    COL_NAME_1 = "T_1"
    COL_NAME_2 = "T_2"

    # Déterminer le nombre total d'agences et le nombre de lignes nécessaires
    num_agences = len(df[COL_NAME_1].unique())
    num_rows = (num_agences + num_cols - 1) // num_cols

    # Créer une grille de graphiques côte à côte
    fig, axs = plt.subplots(num_rows, num_cols, figsize=(15, 5 * num_rows))

    # Parcourir chaque agence et créer un graphique
    for i, agence in enumerate(df[COL_NAME_1].unique()):
        df_agence = df[df[COL_NAME_1] == agence]
        colors = ["green" if solde < 0 else "red" for solde in df_agence["Solde"]]
        row = i // num_cols
        col = i % num_cols

        if num_rows > 1:
            ax = axs[row, col] if i < num_agences else None
        else:
            ax = axs[col] if i < num_agences else None

        if ax is not None:
            bars = ax.bar(list(df_agence[COL_NAME_2].values), df_agence["Solde"], color=colors)
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

        if num_rows > 1:
            ax = axs[row, col]
        else:
            ax = axs[col]
        ax.axis("off")

    plt.tight_layout()
    st.pyplot(fig)


def balance_two_accounts(df: pd.DataFrame, T_1: str, T_2: str) -> pd.DataFrame:
    """Calcule le nouveau solde après suppression du solde entre T_1 et T_2."""
    # Étape 1 : Équilibrer T_1 vers T_2
    val_col = df.at[T_2, T_1]
    if val_col != 0:
        df.at[T_2, T_1] = 0  # Mettre à zéro la colonne T_1 de T_2
        print(f"Step 1: Transfer {val_col} from {T_1} to {T_2}")
        condition = (df[T_1] != val_col) & (df[T_1] != 0)
        df.loc[condition, T_1] += val_col
        df.loc[T_1, condition] -= val_col

    # Étape 2 : Équilibrer T_2 vers T_1
    val_col = df.at[T_1, T_2]
    if val_col != 0:
        df.at[T_1, T_2] = 0  # Mettre à zéro la colonne T_2 de T_1
        print(f"Step 2: Transfer {val_col} from {T_2} to {T_1}")
        condition = (df[T_2] != val_col) & (df[T_2] != 0)
        df.loc[condition, T_2] += val_col
        df.loc[T_2, condition] -= val_col

    return df


def reverse_asymetric_matrix(asymmetric_matrix: pd.DataFrame) -> pd.DataFrame:
    """Transforme un dataframe asymétrique en dataframe "normal"."""

    data_reversed = []
    for agence_1 in asymmetric_matrix.index:
        for agence_2 in asymmetric_matrix.columns:
            value = asymmetric_matrix.loc[agence_1, agence_2]
            if value != 0:
                data_reversed.append([agence_1, agence_2, value])

    reversed_asymmetric_matrix = pd.DataFrame(
        data_reversed, columns=["T_1", "T_2", "Solde"]
    )
    reversed_asymmetric_matrix.reset_index(drop=True, inplace=True)

    return reversed_asymmetric_matrix


def create_unique_hash(elements):
    """ Crée un hash unique pour une liste d'éléments """
    sorted_elements = sorted(elements)
    elements_string = ','.join(sorted_elements)
    unique_hash = hashlib.sha256(elements_string.encode()).hexdigest()
    return unique_hash

