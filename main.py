# Libraries
import os
import pandas as pd
import re
import streamlit as st
import openai
from PIL import Image



# Set the page configuration
st.set_page_config(page_title='shro', layout='wide', page_icon='logo.png')

# Load the image
icon_path = "logo.png"  # Update with your actual path
icon_image = Image.open(icon_path)

example_path = "example_csv.png"  # Update with your actual path
example_image = Image.open(example_path)

# Create columns for layout
col1, col2, col3, col4 = st.columns([2, 1, 4, 1])

# Add the icon and title
with col2:
    st.image(icon_image, width=120)  # Adjust width to fit well

with col3:
    st.title("shro")
    st.header("Your spreadsheet hero.")
    # st.write("""
    # Upload your spreadsheet, describe what you want to do, and download the updated file!
    # """)

# Create layout with columns
col1, col2, col3 = st.columns([2, 4, 2])

# File Upload in the first column
with col2:
    st.markdown("<h3 style='text-align: center;'>Shro is an AI powered spreadsheet editor. Simply upload a spreadsheet (.csv or .xlsx), enter your OpenAI key, enter your desired edits/manipulations, and let AI do the rest!</h3>", unsafe_allow_html=True)
    st.markdown("<p>Here's an example: Say you have a spreadsheet where the first column contains names of animals, and the next columns contain headers dictating characteristics of the animals (species, weight, diet, location, habitat, etc.), such as this: <p>", unsafe_allow_html=True)
    st.image(example_image, width=500)
    st.markdown("<p>Simply upload that incomplete file, describe your request (such as: 'Here is a file with animal information. Please complete my spreadsheet.'), enter a new file name, and click review and apply changes. Then, download your updated file! Note: please be sure to press enter after each step!<p>", unsafe_allow_html=True)
    st.subheader('Step 1: Upload Your File')
    selected_file = st.file_uploader("Upload a spreadsheet (.csv or .xlsx)", type=["csv", "xlsx"])

# Process if a file is uploaded
if selected_file is not None:

    # Check file extension and read file into a DataFrame
    if selected_file.name.endswith(".csv"):
        df = pd.read_csv(selected_file)
        df_copy = df.copy()
        file_extension = '.csv'
    elif selected_file.name.endswith(".xlsx"):
        df = pd.read_excel(selected_file)
        df_copy = df.copy()
        file_extension = '.xlsx'

    # Display the original dataset
    with col2:
        st.subheader('Step 2: Preview Your Data')
        st.dataframe(df, use_container_width=True)

    # Fetch column headers
    headers = df.columns.tolist()

    # Convert dataframe to a json string
    json_data = df.to_json(orient="records", indent=2)

    # Create layout with columns
    col1, col2, col3 = st.columns([2, 4, 2])

    with col2:
        # Enter OpenAI Key
        st.subheader('Step 3: Enter your OpenAI Key')
        st.markdown("<p>An OpenAI key is required to run this application, You can get your own here: <a href=https://platform.openai.com/docs/quickstart#create-and-export-an-api-key><u>Acquire an OpenAI key</u></a>. It does cost money to use tokens to access OpenAI's LLMs, but they are relatively inespensive. You can find more about tokem pricing <a href=https://openai.com/api/pricing/><u>here</u></a>. This app is currently running with gpt-3.5-turbo.<p>",unsafe_allow_html=True)
        open_ai_key = st.text_input("Press enter after entering OpenAI key", key="openAI_key")
        #openai.api_key = open_ai_key
        st.write(f"OpenAI Key: {open_ai_key}")

        st.subheader('Step 4: Enter the Max Number of Tokens')
        st.markdown("<p>The max number of tokens is the maximum number of tokens used by OpenAIs LLM. Bigger spreadsheets will require greater numbers of tokens for completeness. Please adjust this accordingly!<p>",unsafe_allow_html=True)
        max_tokens = st.text_input("Press enter after entering your max number of tokens", key="Max Tokens")
        st.write(f"Max Number of Tokens: {max_tokens}")

        # User Prompt Section
        st.subheader('Step 5: Describe Your Request')
        user_prompt = st.text_input("What would you like to do to your spreadsheet? Press enter after it is input", key="user_prompt_input")
        st.write(f"You entered: {user_prompt}")

        # User Input for New Filename
        st.subheader('Step 6: Name Your New File')
        updated_filename = st.text_input("Enter a name for the new file (no extension). Press enter after new file is added", key="updated_filename_input")


    # Create layout with columns
    col1, col2, col3 = st.columns([2, 4, 2])

    with col2:
        # Add side-by-side previews
        if user_prompt and updated_filename:
            st.subheader("Step 7: Review and Apply Changes")

            # Generate and apply code on button click
            if st.button("Generate and Apply Code"):
                with st.spinner("Applying changes..."):
                    try:
                        # Generate code using OpenAI API
                        input_prompt = f"""
                        I have the following information in my spreadsheet: {json_data}. 
                        This is the user task: {user_prompt} 
                        Write me code to perform the user task on my dataframe (titled 'df').
                        Ensure that the code completes the entire spreadsheet. 
                        """
                        client = openai.OpenAI(api_key=open_ai_key)

                        response = client.chat.completions.create(
                            model="gpt-3.5-turbo",
                            messages=[{"role": "system", "content": "You are a helpful assistant that generates Python code."},
                                      {"role": "user", "content": input_prompt}],
                            max_tokens=int(max_tokens)
                        )
                        # generated_code = response["choices"][0]["message"]["content"] # Old response access
                        # New reponse access
                        generated_code = response.choices[0].message.content

                        # Display the generated code
                        st.subheader('Generated Python Code:')
                        st.code(generated_code, language='python')

                        # Extract and execute the code
                        code_block = re.search(r"```python\n(.*?)\n```", generated_code, re.DOTALL)
                        code_to_execute = code_block.group(1) if code_block else generated_code
                        local_vars = {"df": df}
                        exec(code_to_execute, {}, local_vars)
                        updated_df = local_vars.get("df")

                        # Save the updated DataFrame
                        # updated_file_path = f"/Users/rossbrancati/PycharmProjects/shro_v0/data/{updated_filename}.csv"
                        #updated_df.to_csv(updated_file_path, index=False)

                        # Show side-by-side comparison
                        st.subheader("Updated Data")
                        #with col_updated:
                        st.caption("Updated Data")
                        st.dataframe(updated_df)

                        # Save and provide download button
                        updated_file_path = f"{updated_filename}.csv"
                        # st.success(f"File processed successfully: {updated_file_path}")
                        st.download_button(
                            label="Download Updated File",
                            data=updated_df.to_csv(index=False).encode('utf-8'),
                            file_name=updated_file_path,
                            mime="text/csv"
                        )

                    except Exception as e:
                        st.error(f"An error occurred: {e}")


