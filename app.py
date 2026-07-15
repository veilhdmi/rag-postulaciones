import streamlit as st
from dotenv import load_dotenv

from rag import answer, build_index, retrieve

load_dotenv()

st.set_page_config(page_title="RAG Postulaciones", page_icon="📋")
st.title("Asistente de Postulaciones")
st.caption("Pregúntale a tu historial de postulaciones en Google Sheets.")

question = st.text_input("Tu pregunta", placeholder="¿A qué empresas postulé en junio?")

if st.button("Preguntar") and question:
    with st.spinner("Sincronizando Sheet y buscando..."):
        collection, records = build_index()

    if not records:
        st.warning("No encontré postulaciones en el Sheet.")
    else:
        context_docs = retrieve(collection, question)
        with st.spinner("Generando respuesta..."):
            reply = answer(question, context_docs)

        st.markdown("### Respuesta")
        st.write(reply)

        with st.expander(f"Evidencia usada ({len(context_docs)} filas)"):
            for doc in context_docs:
                st.markdown(f"- {doc}")
