import streamlit as st 
import pandas as pd 
import json 
import matplotlib.pyplot as plt 
from utiles import *
st.set_page_config(layout="wide")


# Charger les données

# Création de sidebar pour choisir type de support
SUPPORT=['PAL EUROPE', 'PAL DUSS']

with st.sidebar:
    st.write(f"## Date de solde :    date ")
    support = st.selectbox(
        "## Choisissez un support : ", SUPPORT
    )
file_name = support.replace(" ","_")    
with open(f"data/1_triangles_{file_name}.json","r") as f_in:
    data=json.load(f_in)

 
st.write("# Avant triangulaires ")
###############################  Avant Triangulaire  ###############################

#-1 Choisir l'agence a 
list_agence_a = list(data.keys())
list_agence_a.sort()
selected_agence_a = st.selectbox("Choisissez une agence:", list_agence_a)
#-- Lister toutes les triangulaire possibles pour cette agence : 
all_triangulaire_for_agence_a = [triangulaire['triangle'] for triangulaire in data[selected_agence_a][1:]]

#-2 Choisir le tier 2. Le choix ce fait sur les triangulaires ou l'agence "a" est présente
#-- Liste de tous les tiers avec tiangulaires possibles avec l'agence "a"
list_tier_b = list({item for sublist in all_triangulaire_for_agence_a for item in sublist 
                       if item != selected_agence_a})
list_tier_b.sort()
selected_tier_b = st.selectbox("Choisissez le premier tier (agence, client ou transporteur):", list_tier_b)

#-3 Choisir le tier c 
#-- Toutes les triangulaires contenant l'agence a et le tiers b 
all_triangulaire_for_agence_a_b = [sublist for sublist in all_triangulaire_for_agence_a 
                 if selected_agence_a in sublist and selected_tier_b in sublist]

#--Liste de tous les tiers avec tiangulaires possibles avec l'agence "a" et le tier 2
list_tier_c = list({item for sublist in all_triangulaire_for_agence_a_b 
                for item in sublist 
                if item not in [selected_agence_a, selected_tier_b]})
list_tier_c.sort()

selected_tier_c = st.selectbox("Choisissez le second tier (agence, client ou transporteur):", list_tier_c)

#-4 Afficher les données
data = search_triangle_in_json(selected_agence_a, selected_tier_b, selected_tier_c,support=file_name)
df = pd.DataFrame(data['data'])
st.write(df)
plot_triangulaires(df)

st.write("# Aprés triangulaires ")
###############################  Après Triangulaire  ###############################

#5- Choisir deux tiers dont on souhaite réduire le solde à 0
unique_agencies_list = list(df['T_1'].unique())
agency1 = st.selectbox("Choisissez l'agence A :", unique_agencies_list)
unique_agencies_list.remove(agency1)
agency2 = st.selectbox("Choisissez l'agence B :",unique_agencies_list )
asymmetric_matrix = df.pivot(index='T_1', columns='T_2', values='Solde')
asymmetric_matrix = asymmetric_matrix.fillna(0)


#6- Appeler la fonction pour équilibrer les Soldes
balanced_asymmetric_matrix = balance_two_accounts(asymmetric_matrix, agency1, agency2)
reversed_reverse_asymetric_matrix = reverse_asymetric_matrix(balanced_asymmetric_matrix)
st.write(reversed_reverse_asymetric_matrix)
# st.write(balanced_asymmetric_matrix)
st.write("Visualisation des soldes après triangulaires (*) :")
plot_triangulaires(reversed_reverse_asymetric_matrix, 3)


st.write("""
        (*) Comment lire ces graphiques :
        * Rouge (solde positif)   : Lorsque la colonne est en rouge, cela signifie que l’agence en titre doit des palettes à l’agence en bas de la colonne.
        * Vert (solde négatif) : Lorsque la colonne est en vert, c’est l’inverse. Cela signifie que l’agence en titre doit récupérer des palettes de l’agence en bas.
        """)