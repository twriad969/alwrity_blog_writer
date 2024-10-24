import time
import os
import streamlit as st
from tenacity import retry, stop_after_attempt, wait_random_exponential
import google.generativeai as genai
from exa_py import Exa

# To store conversation history
conversation_history = []

def main():
    # Set page configuration
    st.set_page_config(page_title="Alwrity - AI Blog Writer", layout="wide")
    
    # Apply custom CSS for styling and scrollbar
    st.markdown("""
        <style>
            .block-container { padding-top: 0rem; padding-bottom: 0rem; padding-left: 1rem; padding-right: 1rem; }
            ::-webkit-scrollbar-track { background: #e1ebf9; }
            ::-webkit-scrollbar-thumb { background-color: #90CAF9; border-radius: 10px; border: 3px solid #e1ebf9; }
            ::-webkit-scrollbar-thumb:hover { background: #64B5F6; }
            ::-webkit-scrollbar { width: 16px; }
            div.stButton > button:first-child {
                background: #1565C0; color: white; border: none; padding: 12px 24px; 
                border-radius: 8px; text-align: center; display: inline-block; 
                font-size: 16px; margin: 10px 2px; cursor: pointer; 
                transition: background-color 0.3s ease; box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.2); font-weight: bold;
            }
        </style>
    """, unsafe_allow_html=True)

    # Title and description
    st.title("✍️ Alwrity - AI Blog Post Generator")
    st.markdown("Create high-quality blog content effortlessly with our AI-powered tool. Ideal for bloggers and content creators. 🚀")

    # Input section
    with st.expander("**PRO-TIP** - Read the instructions below. 📝", expanded=True):
        input_blog_keywords = st.text_input('**Enter main keywords of your blog!** (Blog Title Or Content Topic)', 
                                            help="The main topic or title for your blog.")
        
        col1, col2, col3 = st.columns([5, 5, 5])
        
        with col1:
            blog_type = st.selectbox('**Choose Blog Post Type** 📄', 
                                     options=['General', 'How-to Guides', 'Listicles', 'Job Posts', 'Cheat Sheets', 'Customize'], 
                                     index=0)
            if blog_type == 'Customize':
                blog_type = st.text_input("**Enter your custom blog type**", help="Provide a custom blog type if you chose 'Customize'.")
        
        with col2:
            input_blog_tone = st.selectbox('**Choose Blog Tone** 🎨', 
                                           options=['General', 'Professional', 'Casual', 'Customize'], 
                                           index=0)
            if input_blog_tone == 'Customize':
                input_blog_tone = st.text_input("**Enter your custom blog tone**", help="Provide a custom blog tone if you chose 'Customize'.")
        
        with col3:
            input_blog_language = st.selectbox('**Choose Language** 🌐', 
                                               options=['English', 'Vietnamese', 'Chinese', 'Hindi', 'Spanish', 'Customize'], 
                                               index=0)
            if input_blog_language == 'Customize':
                input_blog_language = st.text_input("**Enter your custom language**", help="Provide a custom language if you chose 'Customize'.")

        # Generate Blog FAQ button
        if st.button('**Write Blog Post (Part 1: Introduction) ✍️**'):
            with st.spinner('Generating the first part of your blog post...'):
                if not input_blog_keywords:
                    st.error('**🫣 Provide Inputs to generate Blog Post. Keywords are required!**')
                else:
                    generate_blog_in_parts(input_blog_keywords, blog_type, input_blog_tone, input_blog_language, part='introduction')

        # Button for part 2 (body)
        if st.button('**Write Blog Post (Part 2: Body) ✍️**'):
            with st.spinner('Generating the second part of your blog post...'):
                generate_blog_in_parts(input_blog_keywords, blog_type, input_blog_tone, input_blog_language, part='body')

        # Button for part 3 (conclusion)
        if st.button('**Write Blog Post (Part 3: Conclusion) ✍️**'):
            with st.spinner('Generating the third part of your blog post...'):
                generate_blog_in_parts(input_blog_keywords, blog_type, input_blog_tone, input_blog_language, part='conclusion')


# Function to generate the blog post in parts using the LLM
def generate_blog_in_parts(input_blog_keywords, input_type, input_tone, input_language, part):
    global conversation_history  # To keep track of history

    # Customize the prompt based on the part
    prompt = f"""
    You are Alwrity, an SEO expert & {input_language} Creative Content writer.
    You specialize in writing {input_type} blog posts.
    Please write the {part} of the blog post based on the following keywords and ensure SEO-optimization.
    
    Blog keywords: {input_blog_keywords}
    
    Please continue from the last part written:
    {''.join(conversation_history)}  # Add previous conversation for context
    """
    
    # Generate the next part of the blog
    new_text = generate_text_with_exception_handling(prompt)
    if new_text:
        conversation_history.append(new_text)  # Update the history
        st.write(new_text)
    else:
        st.error("💥 **Failed to generate blog post. Please try again!**")


# Exception handling for text generation
@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def generate_text_with_exception_handling(prompt):
    try:
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        model = genai.GenerativeModel(model_name="gemini-1.5-flash-latest", generation_config={"max_output_tokens": 8192})
        convo = model.start_chat(history=[])
        response = convo.send_message(prompt)
        return response.last.text
    except Exception as e:
        st.exception(f"An unexpected error occurred: {e}")
        return None


if __name__ == "__main__":
    main()
