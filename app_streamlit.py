import streamlit as st
import requests
import json

# Configuration de l'API
API_RAG_URL = "https://chat-services.sandbox.gouv.tg/rag-chat"

st.title("Interface de Test pour le Chatbot RAG")

# Initialisation de l'historique de la conversation dans la session Streamlit
if "messages" not in st.session_state:
    st.session_state.messages = []

# Affichage des messages de l'historique
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Fonction pour gérer la réponse en streaming
def stream_rag_response(question: str, history: list):
    """Appelle l'API RAG et yield les morceaux de la réponse."""
    payload = {
        "question": question,
        "history": history,
        "platform": "service_public",
        "stream": True
    }
    
    try:
        with requests.post(API_RAG_URL, json=payload, stream=True) as response:
            response.raise_for_status()
            for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
                # On ignore les chunks spéciaux (sources)
                if chunk and not chunk.startswith("__SOURCES__"):
                    yield chunk
    except requests.exceptions.RequestException as e:
        yield f"\n[Erreur de connexion à l'API] : {e}"

# Champ de saisie de l'utilisateur
if prompt := st.chat_input("Posez votre question ici..."):
    # Ajoute et affiche le message de l'utilisateur
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Prépare et affiche la réponse de l'assistant en streaming
    with st.chat_message("assistant"):
        # Utilise st.write_stream pour afficher le flux de réponse
        response = st.write_stream(stream_rag_response(prompt, st.session_state.messages[:-1]))
    
    # Ajoute la réponse complète de l'assistant à l'historique
    st.session_state.messages.append({"role": "assistant", "content": response})
