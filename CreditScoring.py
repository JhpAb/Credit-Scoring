import streamlit as st
import pandas as pd
import requests
from io import StringIO
import re

# Menu de navigation
page = st.sidebar.selectbox("Sélectionnez une étape", ["1. Importation des données", "2. Traitement des données",
                                                     "3. Choix des variables explicatives", "4. Modèle de régression logistique",
                                                     "5. Scoring des clients", "6. Enregistrement des résultats"])

# Pages du projet (comme dans les étapes précédentes)
if page == "1. Importation des données":
    st.title("Importation des données")

    # Demander le lien de partage Google Drive
    drive_link = st.text_input("Entrez le lien de partage Google Drive pour le fichier CSV")

    if drive_link:
        try:
            # Utiliser une expression régulière pour extraire l'ID du fichier
            file_id_match = re.search(r'/d/([a-zA-Z0-9_-]+)', drive_link)
            if file_id_match:
                file_id = file_id_match.group(1)
                download_url = f"https://drive.google.com/uc?export=download&id={file_id}"

                # Télécharger le fichier CSV
                response = requests.get(download_url)
                response.raise_for_status()

                # Lire le fichier CSV à partir de la réponse
                df = pd.read_csv(StringIO(response.text), on_bad_lines='warn')
                st.success("Fichier CSV chargé avec succès !")
                st.write("Aperçu des 10 premières lignes :", df.head())
                st.write("Résumé des données :", df.describe())
                st.write("Structure des données :", df.info())
            else:
                st.error("Lien Google Drive invalide. Veuillez fournir un lien de partage valide.")

        except Exception as e:
            st.error(f"Erreur lors du chargement du fichier : {e}")

elif page == "2. Traitement des données":
    st.title("Traitement des données")
    if 'df' in locals():
        st.write("Données manquantes :", df.isnull().sum())
        st.write("Apurement des données numériques...")
        st.write("Boxplot des données...")
    else:
        st.warning("Veuillez importer un fichier CSV d'abord.")

elif page == "3. Choix des variables explicatives":
    st.title("Choix des variables explicatives")
    if 'df' in locals():
        st.write("V de Cramer pour analyser la corrélation entre les variables.")
    else:
        st.warning("Veuillez importer un fichier CSV d'abord.")

elif page == "4. Modèle de régression logistique":
    st.title("Construction du modèle de régression logistique")
    if 'df' in locals():
        st.write("Création et entraînement du modèle...")
    else:
        st.warning("Veuillez importer un fichier CSV d'abord.")

elif page == "5. Scoring des clients":
    st.title("Scoring des nouveaux clients")
    if 'df' in locals():
        st.write("Calcul des scores et des notes pour les clients.")
    else:
        st.warning("Veuillez importer un fichier CSV d'abord.")

elif page == "6. Enregistrement des résultats":
    st.title("Enregistrement des résultats")
    if 'df' in locals():
        st.write("Télécharger le fichier avec les résultats.")
        df['score'] = "calculé"
        df['note'] = "A+"
        st.download_button("Télécharger le fichier", df.to_csv(), file_name="resultats_clients.csv", mime="text/csv")
    else:
        st.warning("Veuillez importer un fichier CSV d'abord.")

# Pied de page
st.markdown("""
    <hr>
    <footer style="text-align:center;">
        <p>© 2025 Scoring Credit Apk- Tous droits réservés.</p>
        <p>Développé par Jean Pierre ABBE</p>
        <p><a href="mailto: abbejeanpierre0808@gmail.com">Contactez-nous</a></p>
    </footer>
    """, unsafe_allow_html=True)
