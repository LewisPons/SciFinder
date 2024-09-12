import streamlit as st
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
import random
# from utils import consolidate_flat_dict

# Utils
def extract_authors(flat_dict):
    # Initialize an empty list to store the authors
    authors = []
    index = 0
    
    while True:
        # Build the keys for ForeName, LastName, and Initials
        fore_name_key = f'abstract_authors_list_Author_ForeName_{index}'
        last_name_key = f'abstract_authors_list_Author_LastName_{index}'
        initials_key = f'abstract_authors_list_Author_Initials_{index}'
        collective_name_key = f'abstract_authors_list_Author_CollectiveName_{index}'
        
        # Check if at least one name key exists, otherwise break the loop
        if fore_name_key not in flat_dict and last_name_key not in flat_dict and collective_name_key not in flat_dict:
            break
        
        # Handle CollectiveName if available
        if collective_name_key in flat_dict and flat_dict[collective_name_key]:
            authors.append(flat_dict[collective_name_key])
        else:
            # Extract ForeName, LastName, and Initials
            fore_name = flat_dict.get(fore_name_key, "")
            last_name = flat_dict.get(last_name_key, "")
            initials = flat_dict.get(initials_key, "")
            
            # Construct the full author name
            if fore_name or last_name:
                author_name = f"{fore_name} {initials} {last_name}".strip()
                authors.append(author_name)
        
        # Increment index to process the next author
        index += 1

    return authors

def consolidate_author_keys(flat_dict):
    # Extract authors using the previous function
    authors_list = extract_authors(flat_dict)
    
    # Remove all keys related to abstract_authors_list_Author_*
    keys_to_remove = [key for key in flat_dict if key.startswith('abstract_authors_list_Author_')]
    
    for key in keys_to_remove:
        del flat_dict[key]
    
    # Add the consolidated author list to the dictionary
    flat_dict['authors'] = authors_list
    
    return flat_dict

def consolidate_dates(flat_dict):
    # Extract date and date_revised fields
    consolidated_date = {
        'Day': flat_dict.pop('date_Day', None),
        'Month': flat_dict.pop('date_Month', None),
        'Year': flat_dict.pop('date_Year', None)
    }

    consolidated_revised_date = {
        'Day': flat_dict.pop('date_revised_Day', None),
        'Month': flat_dict.pop('date_revised_Month', None),
        'Year': flat_dict.pop('date_revised_Year', None)
    }

    # Add the consolidated date fields back to the dictionarBy
    flat_dict['date'] = consolidated_date
    flat_dict['date_revised'] = consolidated_revised_date
    
    return flat_dict

def consolidate_flat_dict(flat_dict):
    flat_dict = consolidate_author_keys(flat_dict)
    flat_dict = consolidate_dates(flat_dict)
    return flat_dict



# Load environment variable


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


# Example inputs
examples = {
    "Cancer Research": [
        "Recent advancements in immunotherapy for treating various types of cancer.",
        "Targeted therapy approaches using small molecule inhibitors for specific cancer mutations.",
        "Development of liquid biopsy techniques for early cancer detection and monitoring.",
        "Combination therapies involving chemotherapy and immunotherapy for improved outcomes.",
        "Personalized cancer vaccines based on individual tumor genomics."
    ],
    "Neurodegenerative Diseases": [
        "The role of protein misfolding in Alzheimer's and Parkinson's diseases.",
        "Investigating the gut-brain axis in neurodegenerative disorders.",
        "Potential neuroprotective effects of exercise and diet in slowing disease progression.",
        "Gene therapy approaches for treating Huntington's disease and ALS.",
        "The impact of sleep disorders on the development and progression of neurodegenerative diseases."
    ],
    "Antibiotic Resistance": [
        "Emerging strategies to combat antibiotic-resistant bacteria in hospital settings.",
        "Development of novel antimicrobial peptides as alternatives to traditional antibiotics.",
        "Phage therapy as a potential solution for treating multidrug-resistant infections.",
        "The role of the microbiome in promoting or preventing antibiotic resistance.",
        "Machine learning approaches for predicting antibiotic resistance patterns."
    ],
    "Genetic Engineering": [
        "CRISPR-Cas9 applications in treating genetic disorders and ethical considerations.",
        "Gene drive technology for controlling disease-carrying insect populations.",
        "Synthetic biology approaches for creating artificial organs and tissues.",
        "Epigenetic editing techniques for modifying gene expression without altering DNA sequences.",
        "Development of genetically modified crops for improved yield and resistance to climate change."
    ],
    "COVID-19": [
        "Long-term effects of COVID-19 infection and potential treatments for long COVID.",
        "Development and efficacy of mRNA vaccines against new viral variants.",
        "The impact of social distancing measures on mental health and strategies for mitigation.",
        "Artificial intelligence applications in COVID-19 diagnosis and treatment planning.",
        "Investigating the origins of SARS-CoV-2 and strategies for preventing future pandemics."
    ]
}

# Sidebar for examples
st.sidebar.header("Example Inputs")
selected_category = st.sidebar.selectbox(
    "Choose a research category:",
    [""] + list(examples.keys())
)

# User input
if selected_category:
    random_example = random.choice(examples[selected_category])
    user_input = st.text_area("Enter your text here:", value=random_example, height=100)
else:
    user_input = st.text_area("Enter your text here:", height=100)

number_of_recommendations = st.number_input("How many papers do you need",min_value=3, max_value=15,  placeholder="Type a number...")

if st.button("Get Recommendations"):
    if user_input:
        # Encode user input
        inference = model.encode(user_input).tolist()

        # Query Pinecone
        recommendations = index.query(
            vector=inference,
            top_k=number_of_recommendations,
            include_values=True,
            include_metadata=True
        )
        recommendations_dict = recommendations.to_dict()

        # Parse recommendations
        parsed_recommendations = [
            {**consolidate_flat_dict(match["metadata"]), **{"score": match["score"]}, **{"id": match["id"]}} 
            for match in recommendations_dict["matches"]
        ]

        # Display recommendations
        st.subheader(f"Top {number_of_recommendations} Recommendations:")
        for i, rec in enumerate(parsed_recommendations, 1):
            # st.write(f"**Recommendation {i}**")
            st.write(f"**Title:** {rec.get('abstract_title', 'N/A')}")
            st.write(f"**Authors:** {', '.join(rec.get('authors', 'N/A'))}")
            st.write(f"**Abstract:** {rec.get('abstract_text', 'N/A')}") 
            # st.write(f"**Score:** {rec['score']:.4f}")
            # st.write(f"**ID:** {rec['id']}")
            st.write(f"**Link to pubmed:** [Paper](https://pubmed.ncbi.nlm.nih.gov/{rec['id']}/)")
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
