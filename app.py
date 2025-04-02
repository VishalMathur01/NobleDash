import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# Load Nobel Prize Data Without University Affiliations
data_wo_uni = pd.read_html("https://en.wikipedia.org/wiki/List_of_Nobel_laureates")[0]

# Load Nobel Prize Data With University Affiliations
data_w_uni = pd.read_html("https://en.wikipedia.org/wiki/List_of_Nobel_laureates_by_university_affiliation", match="Nobel laureates by affiliation")[0]

# Data Cleaning
def clean_data():
    global data_wo_uni, data_w_uni
    data_wo_uni.columns = [col.replace("(The Sveriges Riksbank Prize)", "Economics").strip() for col in data_wo_uni.columns]
    data_w_uni = data_w_uni.dropna()
    data_w_uni = data_w_uni.drop_duplicates()
clean_data()

# Save Data
def save_data():
    data_wo_uni.to_csv("nobel_laureates_without_affiliation.csv", index=False)
    data_w_uni.to_csv("nobel_laureates_with_affiliation.csv", index=False)
    data_w_uni.to_json("nobel_laureates_with_affiliation.json", orient="records")
save_data()

# Streamlit App
def run_streamlit_app():
    st.set_page_config(layout="wide")  # Set landscape layout
    st.title("Nobel Laureates Dashboard")
    st.sidebar.header("Filters")
    
    year_range = st.sidebar.slider("Select Year Range", int(data_wo_uni.Year.min()), int(data_wo_uni.Year.max()), (int(data_wo_uni.Year.min()), int(data_wo_uni.Year.max())))
    category = st.sidebar.selectbox("Select Category", options=["All"] + list(data_wo_uni.columns[1:]))
    selected_university = st.sidebar.selectbox("Select a University", options=["All"] + list(data_w_uni['Affiliation'].unique()))
    
    col1, col2 = st.columns(2)  # Arrange charts in landscape mode
    
    with col1:
        st.subheader("Top 10 Universities with Most Nobel Laureates")
        filtered_university_data = data_w_uni if selected_university == "All" else data_w_uni[data_w_uni['Affiliation'] == selected_university]
        top_universities = filtered_university_data['Affiliation'].value_counts().head(10)
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.barplot(x=top_universities.values, y=top_universities.index, palette='coolwarm', ax=ax)
        ax.set_xlabel("Number of Nobel Laureates")
        ax.set_ylabel("University")
        st.pyplot(fig)
    
    with col2:
        st.subheader("Trends in Nobel Prizes by Category (Area Chart)")
        filtered_nobel_data = data_wo_uni[(data_wo_uni['Year'] >= year_range[0]) & (data_wo_uni['Year'] <= year_range[1])]
        if category != "All":
            filtered_nobel_data = filtered_nobel_data[['Year', category]]
        yearly_counts = filtered_nobel_data.melt(id_vars=['Year'], var_name='Category', value_name='Laureate')
        yearly_counts = yearly_counts.groupby(['Year', 'Category']).count().reset_index()
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.lineplot(data=yearly_counts, x='Year', y='Laureate', hue='Category', palette='tab10', ax=ax)
        ax.fill_between(yearly_counts['Year'], yearly_counts['Laureate'], alpha=0.3)
        ax.set_xlabel("Year")
        ax.set_ylabel("Number of Awards")
        ax.legend(title="Category", bbox_to_anchor=(1.05, 1), loc='upper left')
        st.pyplot(fig)
    
    st.subheader("Nobel Prize Winners")
    filtered_data = data_wo_uni[(data_wo_uni['Year'] >= year_range[0]) & (data_wo_uni['Year'] <= year_range[1])]
    if category != "All":
        filtered_data = filtered_data[['Year', category]]
    st.write(filtered_data)
    
    st.subheader("Affiliation Analysis")
    if selected_university != "All":
        uni_data = data_w_uni[data_w_uni['Affiliation'] == selected_university]
    else:
        uni_data = data_w_uni
    st.write(uni_data)
    
    # Data Download Section
    st.subheader("Download Data")
    st.download_button(label="Download Nobel Laureates Data (CSV)", data=open("nobel_laureates_without_affiliation.csv", "rb"), file_name="nobel_laureates_without_affiliation.csv", mime="text/csv")
    st.download_button(label="Download Nobel Laureates with Affiliations (CSV)", data=open("nobel_laureates_with_affiliation.csv", "rb"), file_name="nobel_laureates_with_affiliation.csv", mime="text/csv")

if __name__ == "__main__":
    run_streamlit_app()