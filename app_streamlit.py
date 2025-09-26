import streamlit as st
import requests
import json

# Configuration de l'API (conserve votre URL)
API_RAG_URL = "https://chat-services.sandbox.gouv.tg/rag-chat"

st.title("Interface de Test pour le Chatbot RAG")

# Initialisation de l'historique de la conversation
if "messages" not in st.session_state:
    st.session_state.messages = []

# Affichage des messages de l'historique
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Champ de saisie de l'utilisateur
if prompt := st.chat_input("Posez votre question ici..."):
    # Ajoute et affiche le message de l'utilisateur
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Prépare et affiche la réponse de l'assistant (mode non-streamé)
    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown("...")

        payload = {
            "question": prompt,
            "history": st.session_state.messages[:-1],
            "platform": "service_public",
            "stream": False  # On désactive le streaming
        }

        try:
            # Appel API simple, non-streamé
            response = requests.post(API_RAG_URL, json=payload)
            response.raise_for_status()
            response_data = response.json()
            
            full_answer = response_data.get("answer", "Désolé, une erreur est survenue.")
            sources = response_data.get("sources", [])

            # Affiche la réponse complète
            placeholder.markdown(full_answer)

            # Affiche les sources si elles existent
            if sources:
                with st.expander("Sources utilisées"):
                    for i, source in enumerate(sources):
                        st.write(f"{i+1}. {source.get('source', 'Source inconnue')}")
            
            # Ajoute la réponse complète à l'historique
            st.session_state.messages.append({"role": "assistant", "content": full_answer})

        except requests.exceptions.RequestException as e:
            st.error(f"Erreur de connexion à l'API : {e}")
