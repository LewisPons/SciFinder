import streamlit as st
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
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

    # Add the consolidated date fields back to the dictionary
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
st.title("PubMed Recommendation App")

# Example inputs
examples = {
    "Cancer Research": "Recent advancements in immunotherapy for treating various types of cancer.",
    "Neurodegenerative Diseases": "The role of protein misfolding in Alzheimer's and Parkinson's diseases.",
    "Antibiotic Resistance": "Emerging strategies to combat antibiotic-resistant bacteria in hospital settings.",
    "Genetic Engineering": "CRISPR-Cas9 applications in treating genetic disorders and ethical considerations.",
    "COVID-19": "Long-term effects of COVID-19 infection and potential treatments for long COVID."
}

# Sidebar for examples
st.sidebar.header("Example Inputs")
selected_example = st.sidebar.selectbox(
    "Choose an example input:",
    [""] + list(examples.keys())
)

# User input
if selected_example:
    user_input = st.text_area("Enter your text here:", value=examples[selected_example], height=100)
else:
    user_input = st.text_area("Enter your text here:", height=100)

if st.button("Get Recommendations"):
    if user_input:
        # Encode user input
        inference = model.encode(user_input).tolist()

        # Query Pinecone
        recommendations = index.query(
            vector=inference,
            top_k=5,
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
        st.subheader("Top 5 Recommendations:")
        for i, rec in enumerate(parsed_recommendations, 1):
            st.write(f"**Recommendation {i}**")
            st.write(f"**Title:** {rec.get('abstract_title', 'N/A')}")
            st.write(f"**Authors:** {', '.join(rec.get('authors', 'N/A'))}")
            st.write(f"**Abstract:** {rec.get('abstract_text', 'N/A')}") 
            # st.write(f"**Score:** {rec['score']:.4f}")
            # st.write(f"**ID:** {rec['id']}")
            st.write(f"**Link to pubmed:** [Paper](https://pubmed.ncbi.nlm.nih.gov/{rec['id']}/)")
            st.write("---")

    else:
        st.warning("Please enter some text to get recommendations.")

# Add some information about the app
st.sidebar.header("About")
st.sidebar.info(
    "This app uses a PubMed-based model to find similar articles "
    "based on your input. It queries a Pinecone vector database "
    "to retrieve the top 5 most relevant results."
)