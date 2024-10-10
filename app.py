import streamlit as st
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
import random

from src.utils.helpers import parse_date
from src.utils.parsing_utils import consolidate_flat_dict
from src.utils.constants import EXAMPLES


# Initialize SentenceTransformer model
@st.cache_resource
def load_model():
    return SentenceTransformer("neuml/pubmedbert-base-embeddings")


model = load_model()

# Initialize Pinecone
pc = Pinecone(api_key=st.secrets["PINECONE_API_KEY"])
index = pc.Index("pubmed-test")

# Streamlit app
st.title("NutriSearch: Your Personal Research Assistant 🦦")

# App information
st.markdown("---")
st.header("About NutriSearch")
st.info(
    "This app uses a PubMed-based model to find relevant articles "
    "based on your input. It queries a vast database of medical and "
    "scientific literature to retrieve the most pertinent results. "
    "Perfect for staying up-to-date with the latest research in "
    "nutrition science and related fields!"
)

# Instructions
st.header("How to Use")
st.markdown(
    """
    1. Select a research category or enter your own topic.
    2. If you choose a category, a random example will appear. Feel free to use or modify it.
    3. Click "Get Recommendations" to discover relevant articles.
    4. Expand each result to view detailed information.
    5. Explore different topics to broaden your knowledge!
    """
)


# Sidebar for examples
st.sidebar.header("Example Inputs")
selected_category = st.sidebar.selectbox(
    "Choose a research category:", [""] + list(EXAMPLES.keys())
)

# User input
if selected_category:
    random_example = random.choice(EXAMPLES[selected_category])
    user_input = st.text_area("Enter your text here:", value=random_example, height=100)
else:
    user_input = st.text_area("Enter your text here:", height=100)

number_of_recommendations = st.number_input(
    "How many papers do you need",
    min_value=3,
    max_value=15,
    placeholder="Type a number...",
)

if st.button("Get Recommendations"):
    if user_input:
        # Encode user input
        inference = model.encode(user_input).tolist()

        # Query Pinecone
        recommendations = index.query(
            vector=inference,
            top_k=number_of_recommendations,
            include_values=True,
            include_metadata=True,
        )
        recommendations_dict = recommendations.to_dict()

        # Parse recommendations
        parsed_recommendations = [
            {
                **consolidate_flat_dict(match["metadata"]),
                **{"score": match["score"]},
                **{"id": match["id"]},
            }
            for match in recommendations_dict["matches"]
        ]

        # Display recommendations
        st.subheader(f"Top {number_of_recommendations} Recommendations:")
        for i, rec in enumerate(parsed_recommendations, 1):

            parsed_date = parse_date(rec.get("date"))

            # st.write(f"**Recommendation {i}**")
            st.write(f"**Title:** {rec.get('abstract_title', 'N/A')}")
            st.write(f"**Authors:** {', '.join(rec.get('authors', 'N/A'))}")
            st.write(f"**Date:** {parsed_date}")
            st.write(f"**Abstract:** {rec.get('abstract_text', 'N/A')}")
            # st.write(f"**Score:** {rec['score']:.4f}")
            # st.write(f"**ID:** {rec['id']}")
            st.write(
                f"**Link to pubmed:** [Paper](https://pubmed.ncbi.nlm.nih.gov/{rec['id']}/)"
            )
            st.write("---")

    else:
        st.warning("Please enter some text to get recommendations.")


# Personal message in the sidebar
st.sidebar.markdown("---")
st.sidebar.header("💌 Un mensaje especial para tí")
st.sidebar.markdown(
    """
    🌟 Para mi maravillosa, inteligente y talentosa, novia, Fernanda.

    Hice esta app solo para ti, sabiendo cuánto te gusta estudiar e investigar en el campo de la nutrición.
    Tu pasión por aprender y tu dedicación a tu trabajo me inspiran cada día.

    Espero que esta AI te ayude a descubrir nuevas e interesantes investigaciones en ciencia de la nutrición y más allá.
    Que alimente tu curiosidad y apoye tu crecimiento como la brillante nutricionista que eres.

    Tu curiosidad y sed de conocimiento es una de las muchas cosas que adoro de ti.
    ¡Sigue brillando y cambiando vidas con tu conocimiento!

    Con todo mi amor y apoyo,
    Tu novio, Lewispons 💖

    PD. Hice entrené esta AI usando papers en Inglés, así que vas a tener que escribirle en Inglés
    Te debo la version en español!
    """
)
