import streamlit as st
import pandas as pd
import os
import requests
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
import joblib

# Fonction pour afficher le pied de page
def footer():
    st.markdown(
        """
        <style>
        .footer {
            position: fixed;
            bottom: 0;
            width: 100%;
            background-color: #f1f1f1;
            text-align: center;
            padding: 10px 0;
            font-size: 12px;
            color: #555555;
        }
        </style>
        <div class="footer">
            <p>© 2025 Nom de votre entreprise - Tous droits réservés</p>
            <p><a href="https://github.com/votre-utilisateur" target="_blank">GitHub Repository</a></p>
        </div>
        """,
        unsafe_allow_html=True
    )

# Fonction pour uploader le fichier CSV
def upload_file():
    st.title("Application de Scoring de Crédit")
    
    # Demander le nom d'utilisateur et le nom du dépôt GitHub
    github_username = st.text_input("Entrez votre nom d'utilisateur GitHub")
    github_repo = st.text_input("Entrez le nom de votre dépôt GitHub")
    
    # Demander à l'utilisateur de télécharger un fichier CSV
    uploaded_file = st.file_uploader("Téléchargez un fichier CSV", type=["csv"])
    
    if uploaded_file is not None:
        # Sauvegarder le fichier localement
        with open("uploaded_file.csv", "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Empaqueter le fichier sur GitHub
        if github_username and github_repo:
            upload_to_github("uploaded_file.csv", github_username, github_repo)
        
        # Lire le fichier CSV
        df = pd.read_csv("uploaded_file.csv")
        
        # Affichage des 10 premières lignes
        st.subheader("Aperçu des 10 premières lignes du fichier")
        st.write(df.head(10))
        
        # Structure des données
        st.subheader("Aperçu de la structure des données")
        st.write(df.info())
        
        # Résumé des données
        st.subheader("Résumé des données")
        st.write(df.describe())
        
        return df
    else:
        st.warning("Veuillez télécharger un fichier CSV.")
        return None

# Fonction pour uploader le fichier sur GitHub
def upload_to_github(file_path, username, repo):
    url = f"https://api.github.com/repos/{username}/{repo}/contents/{file_path}"
    with open(file_path, "rb") as file:
        content = file.read()
    encoded_content = content.encode("base64")
    
    headers = {
        "Authorization": f"token {os.environ.get('GITHUB_TOKEN')}",
        "Content-Type": "application/json",
    }
    
    data = {
        "message": "Upload new file",
        "content": encoded_content,
        "branch": "main"
    }
    
    response = requests.put(url, json=data, headers=headers)
    
    if response.status_code == 201:
        st.success(f"Le fichier a été téléchargé avec succès sur GitHub : {username}/{repo}")
    else:
        st.error(f"Échec de l'upload sur GitHub : {response.text}")

# Fonction de traitement des données
def process_data(df):
    # Recodage des variables et traitement des valeurs manquantes
    # Exemple : Remplir les valeurs manquantes par la moyenne pour les numériques
    df.fillna(df.mean(), inplace=True)
    
    return df

# Sélection des variables explicatives
def select_features(df):
    st.subheader("Sélection des variables explicatives")
    
    # Par exemple, prendre toutes les variables sauf la cible
    X = df.drop("target", axis=1)
    y = df["target"]
    
    return X, y

# Construction du modèle de régression logistique
def build_model(X, y):
    st.subheader("Construction du modèle de régression logistique")
    
    # Division des données en train et test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Normalisation des données
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Modèle de régression logistique
    model = LogisticRegression()
    model.fit(X_train_scaled, y_train)
    
    # Prédictions et évaluation
    score = model.score(X_test_scaled, y_test)
    
    st.write(f"Score du modèle (précision) : {score}")
    
    # Sauvegarder le modèle et le scaler
    joblib.dump(model, "credit_scoring_model.pkl")
    joblib.dump(scaler, "scaler.pkl")
    
    return model, scaler

# Scoring des nouveaux clients
def scoring_new_clients(model, scaler):
    st.subheader("Scoring des nouveaux clients")
    
    # Demander les caractéristiques du client ou importer un fichier CSV
    new_client_file = st.file_uploader("Importer un fichier CSV avec les nouveaux clients", type=["csv"])
    
    if new_client_file is not None:
        new_df = pd.read_csv(new_client_file)
        
        # Appliquer le même prétraitement sur les nouveaux clients
        new_data_scaled = scaler.transform(new_df)
        
        # Prédictions
        scores = model.predict_proba(new_data_scaled)[:, 1]
        
        # Attribution des notes
        grades = assign_grades(scores)
        
        new_df["Score"] = scores
        new_df["Grade"] = grades
        
        st.write(new_df)
        
        # Sauvegarder les résultats dans un fichier CSV
        new_df.to_csv("clients_with_scores.csv", index=False)
        st.download_button("Télécharger le fichier avec les scores et notes", "clients_with_scores.csv")
    
# Fonction pour attribuer des notes
def assign_grades(scores):
    grades = []
    for score in scores:
        if score >= 0.9:
            grades.append("AAA")
        elif score >= 0.8:
            grades.append("AA")
        elif score >= 0.7:
            grades.append("A")
        elif score >= 0.6:
            grades.append("BBB")
        else:
            grades.append("BB")
    return grades

# Fonction principale
def main():
    # Étape 1 : Importation du fichier
    df = upload_file()
    
    if df is not None:
        # Étape 2 : Traitement des données
        df = process_data(df)
        
        # Étape 3 : Sélection des variables explicatives
        X, y = select_features(df)
        
        # Étape 4 : Construction du modèle de régression logistique
        model, scaler = build_model(X, y)
        
        # Étape 5 : Scoring des nouveaux clients
        scoring_new_clients(model, scaler)
    
    # Ajouter le pied de page
    footer()

if __name__ == "__main__":
    main()
