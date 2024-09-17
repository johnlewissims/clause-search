import pandas as pd
import openai
import streamlit as st

## Get key from env variable
openai.api_key = st.secrets["OPENAI_API_KEY"]

def analyze_prohibited_use(text):
    """Analyzes the 'Prohibited Use' clause for coffee/espresso prohibition."""
    try:
        chat_completion = openai.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert in writing and reviewing commercial real estate lease contracts with a specialty in permitted use."
                },
                {
                    "role": "user",
                    "content": f"{prohibited_use_prompt}\n\n{text}"
                }
            ],
            model="gpt-4o",
            max_tokens=10,
            temperature=0
        )
        return chat_completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error analyzing prohibited use: {e}")
        return "Error"

def analyze_use_clause(text):
    """Analyzes the 'Use' clause for coffee/espresso allowance."""
    try:
        chat_completion = openai.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert in writing and reviewing commercial real estate lease contracts with a specialty in permitted use."
                },
                {
                    "role": "user",
                    "content": f"{use_clause_prompt}\n\n{text}"
                }
            ],
            model="gpt-4o",
            max_tokens=10,
            temperature=0
        )
        return chat_completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error analyzing use clause: {e}")
        return "Error"

def process_excel(file, location_column, clause_type_column, clause_language_column):
    df = pd.read_excel(file)
    results = []
    
    ## log out the location column
    print(df[location_column])

    # Grouping by location
    grouped = df.groupby(location_column)
    
    print(grouped)

    for location, group in grouped:
        prohibited_use_result = "Not Found"
        use_clause_result = "Not Found"
        
        # Check for 'Prohibited Use' clause
        prohibited_rows = group[group[clause_type_column] == "Prohibited Use"]
        if not prohibited_rows.empty:
            for index, row in prohibited_rows.iterrows():
                clause_text = str(row[clause_language_column])
                prohibited_use_result = analyze_prohibited_use(clause_text)
                break  # Consider only the first "Prohibited Use" clause
        
        # Check for 'Use' clause
        use_rows = group[group[clause_type_column] == "Use"]
        if not use_rows.empty:
            for index, row in use_rows.iterrows():
                clause_text = str(row[clause_language_column])
                use_clause_result = analyze_use_clause(clause_text)
                break  # Consider only the first "Use" clause
        
        # Append results for each location
        results.append({
            'Location Name': location,
            'Prohibited Use': prohibited_use_result,
            'Use Clause': use_clause_result
        })
    
    # Convert results to a DataFrame
    results_df = pd.DataFrame(results)
    return results_df

# Streamlit app UI
st.title("Clause Analysis")

uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])
location_column = st.text_input("Enter the column name for location (e.g., 'Location Name')", value="LOCATION")
clause_type_column = st.text_input("Enter the column name for clause type (e.g., 'Critical Clause Type')", value="Critical Clause Type")
clause_language_column = st.text_input("Enter the column name for clause language (e.g., 'Clause')", value="Critical Clause Language")
prohibited_use_prompt = st.text_input("Prohibited Use Prompt:", value="Determine if the lease prohibits the sale of coffee and/or espresso products at the location based solely on the exact contractual language. Return the result of the analysis on the ability to sell coffee and/or espresso (Prohibited, Not Prohibited).")
use_clause_prompt = st.text_input("Use Clause Prompt:", value="Determine what the language here is stating about coffee as it relates to the tenant selling coffee, based solely on the exact contractual language. Return the result of the analysis on the ability to sell coffee and/or espresso. Return either Allowed, Prohibited, Inconclusive.")

if uploaded_file and location_column and clause_type_column and clause_language_column:
    if st.button("Process File"):
        with st.spinner("Processing... Please wait."):
            # Process the uploaded file with corrected column references
            result_df = process_excel(uploaded_file, location_column, clause_type_column, clause_language_column)
            
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