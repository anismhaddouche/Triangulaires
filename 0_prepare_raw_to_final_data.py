import pandas as pd 
import warnings
warnings.filterwarnings('ignore')

def prep_data(df:pd.DataFrame):
    """
    Nettoyage et préparation des données brute dans 00_raw.xlsx (donnée de la requête Myreport).
    Donne en sortie le fichier 0_final.xlsx
    """
    df.drop('Région',axis=1,inplace=True)
    df.dropna(inplace=True)
    df[df.duplicated(keep=False)]
    filtered_df = df[df["Solde"] != 0]
    filtered_df.rename(columns={"Agence":'T_1', "Typologie Tiers":'TT_2', "Tiers Complet": 'T_2'},inplace=True)
    filtered_df.insert(2,"TT_1",'Agence')
    columns_arragend = ['T_1', 'TT_1','T_2','TT_2','Support','Solde' ]
    filtered_df = filtered_df[columns_arragend]

    # Créer un nouveau dataframe avec des données inversés
    filtered_df_inv = filtered_df[['T_2', 'TT_2','T_1', 'TT_1','Support']]
    filtered_df_inv.rename(columns={"T_2":'T_1', "TT_2":'TT_1', "T_1": 'T_2',"TT_1":'TT_2'},inplace=True)
    filtered_df_inv['Solde'] = -filtered_df['Solde']
    filtered_df[filtered_df.duplicated(keep=False)]
    filtered_df_inv[filtered_df_inv.duplicated(keep=False)]
    new_df = pd.concat([filtered_df, filtered_df_inv], ignore_index=True)
    new_df[new_df.duplicated(keep=False)]
    new_df.drop_duplicates(inplace=True)
    new_df.to_excel('data/0_final.xlsx',index=False)


if __name__=="__main__":
    df = pd.read_excel("data/00_raw.xlsx",sheet_name="Feuil1",skiprows=[0,1,2,3,4])
    prep_data(df)
