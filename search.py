import pandas as pd
import openai
import streamlit as st

## Get key from env variable
openai.api_key = st.secrets["OPENAI_API_KEY"]

def summarize_text(text):
    """Function to use GPT-4 to summarize a given text."""
    try:
        chat_completion = openai.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": f"Summarize the following text in a few words:\n\n{text}",
                },
                {   
                    "role": "system", 
                    "content": "You are a helpful assistant that summarizes text."
                }
            ],
            model="gpt-4o",
            max_tokens=100
        )
        
        return chat_completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error summarizing text: {e}")
        return ""
    
    
def is_allowed(text, keyword="coffee"):
    """Function to determine if keyword is allowed in the given text."""
    try:
        chat_completion = openai.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that answers questions with 'Yes' or 'No'."
                },
                {
                    "role": "user",
                    "content": f"Based on the following text, is {keyword} allowed?  Please answer 'Yes' if coffee preparation is allowed under any circumstances, even with conditions. Answer 'No' if it is strictly prohibited without any conditions.\n\n{text}"
                }
            ],
            max_tokens=3,
            model="gpt-4o",
            temperature=0  # Ensures deterministic responses
        )
        answer = chat_completion.choices[0].message.content.strip()
        # Normalize the answer to "Yes" or "No"
        if "yes" in answer.lower():
            return "Yes"
        elif "no" in answer.lower():
            return "No"
        else:
            return "Uncertain"
    except Exception as e:
        print(f"Error determining if coffee is allowed: {e}")
        return "Error"


def process_excel(file, column_name, column_title, search_term=None):
    df = pd.read_excel(file)
    results = []

    for index, row in df.iterrows():
        row_title = str(row[column_title])
        cell_text = str(row[column_name])

        if search_term and search_term.lower() not in cell_text.lower():
            continue

        summary = summarize_text(cell_text)
        
        results.append({
            'Location Name': row_title,
            'Coffee Allowed': is_allowed(cell_text, "coffee"),
            'Summary': summary,
        })
    
    results_df = pd.DataFrame(results)
    return results_df

# Streamlit app UI
st.title("Excel Processor: Coffee Clause Analysis")

uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])
column_to_search = st.text_input("Enter the column name to search (e.g., 'Clause')", value="Clause")
column_title = st.text_input("Enter the column name for titles (e.g., 'Location Name')", value="Location Name")
search_keyword = st.text_input("Enter a search keyword (e.g., 'coffee')", value="coffee")

if uploaded_file and column_to_search and column_title:
    if st.button("Process File"):
        with st.spinner("Processing... Please wait."):
            # Process the uploaded file
            result_df = process_excel(uploaded_file, column_to_search, column_title, search_term=search_keyword)
            
            # Display the result DataFrame
            st.write("Processing complete! Here are the results:")
            st.dataframe(result_df)

            # Provide a download link for the processed file
            output_file = "output_summary.xlsx"
            result_df.to_excel(output_file, index=False)
            with open(output_file, "rb") as file:
                st.download_button(
                    label="Download Processed File",
                    data=file,
                    file_name="output_summary.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )