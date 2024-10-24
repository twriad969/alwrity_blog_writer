import os
import streamlit as st
from tenacity import retry, stop_after_attempt, wait_random_exponential
import google.generativeai as genai


# Configure the Gemini AI model
def configure_gemini():
    genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
    return genai.GenerativeModel(model_name="gemini-1.5-flash-latest", generation_config={"max_output_tokens": 8192})


# Function to handle the conversation and remember history
def initiate_conversation():
    if 'convo' not in st.session_state:
        model = configure_gemini()
        st.session_state['convo'] = model.start_chat(history=[])
        st.session_state['blog_content'] = ""
        st.session_state['current_part'] = 1  # Start with part 1


# Function to generate part of the blog based on the conversation state
def generate_blog_part(input_keywords, blog_type, blog_tone, blog_language):
    if 'convo' in st.session_state:
        prompt = f"""
        You are Alwrity, an SEO expert & {blog_language} Creative Content writer.
        You specialize in writing {blog_type} blog posts.
        This blog will be generated in three parts. 
        Now generate **Part {st.session_state['current_part']}** of the blog post.

        Ensure the content is SEO-optimized and follows the {blog_tone} tone. 
        Blog topic: {input_keywords}
        """

        conversation = st.session_state['convo']
        conversation.send_message(prompt)

        response = conversation.last.text
        st.session_state['blog_content'] += response

        st.session_state['current_part'] += 1  # Move to the next part
        return response

    return None


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
    st.markdown("Create high-quality blog content effortlessly in parts with our AI-powered tool. Ideal for bloggers and content creators. 🚀")

    # Input section
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

    # Initialize conversation on button click
    if st.button('Start Blog Generation'):
        initiate_conversation()
        st.success('Blog generation started. You can now request the first part!')

    # Button to generate each part
    if st.button('Generate Next Part of Blog'):
        if input_blog_keywords:
            generated_part = generate_blog_part(input_blog_keywords, blog_type, input_blog_tone, input_blog_language)
            if generated_part:
                st.subheader(f'**Part {st.session_state["current_part"] - 1} of Your Blog Post**')
                st.write(generated_part)
            else:
                st.error("❌ Blog part generation failed. Try again.")
        else:
            st.error('❌ Please provide blog keywords before generating.')

    # Display the full blog post so far
    if st.session_state['blog_content']:
        st.subheader('**Your Full Blog Post (So Far)**')
        st.write(st.session_state['blog_content'])


if __name__ == "__main__":
    main()
