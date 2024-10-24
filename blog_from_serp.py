import os
import streamlit as st
import google.generativeai as genai

# Initialize the AI model configuration
def configure_gemini():
    genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
    return genai.GenerativeModel(model_name="gemini-1.5-flash-latest", generation_config={"max_output_tokens": 2048})

# Function to initialize the conversation and session state
def initialize_state():
    if 'convo' not in st.session_state:
        model = configure_gemini()
        st.session_state['convo'] = model.start_chat(history=[])
        st.session_state['blog_parts'] = {
            'intro': None,
            'body': None,
            'faqs': None,
            'conclusion': None
        }
        st.session_state['current_part'] = 'intro'  # Start with the introduction

# Function to generate each blog section
def generate_blog_section(blog_topic, blog_type, blog_tone, blog_language):
    convo = st.session_state['convo']
    current_part = st.session_state['current_part']
    
    # Define natural language prompts for each part
    if current_part == 'intro':
        prompt = f"""
        You are a creative {blog_language} SEO expert and {blog_type} blog writer.
        Please write a compelling and engaging **Introduction** for a blog post on the topic: {blog_topic}.
        Use a {blog_tone} tone, and ensure the introduction hooks the reader's attention.
        """
    elif current_part == 'body':
        prompt = f"""
        Now let's move on to the **main content** of the blog post on "{blog_topic}".
        Make sure the content is valuable, informative, and well-structured.
        Include a **Table of Contents** and explain each section in depth. The tone should remain {blog_tone}.
        """
    elif current_part == 'faqs':
        prompt = f"""
        Now, provide a set of **Frequently Asked Questions (FAQs)** related to the topic: {blog_topic}.
        Include at least five FAQs with thoughtful and useful answers, keeping the tone {blog_tone}.
        """
    elif current_part == 'conclusion':
        prompt = f"""
        Finally, please write a **Conclusion** for the blog post on "{blog_topic}".
        Summarize the key points of the blog, and provide a closing remark or a call to action for the reader.
        The tone should stay {blog_tone}.
        """

    # Send the prompt to the AI model
    convo.send_message(prompt)
    response = convo.last.text

    # Store the generated part in session state
    st.session_state['blog_parts'][current_part] = response

    # Move to the next part
    if current_part == 'intro':
        st.session_state['current_part'] = 'body'
    elif current_part == 'body':
        st.session_state['current_part'] = 'faqs'
    elif current_part == 'faqs':
        st.session_state['current_part'] = 'conclusion'
    elif current_part == 'conclusion':
        st.session_state['current_part'] = 'complete'

    return response

# Main app function
def main():
    # Page configuration
    st.set_page_config(page_title="Alwrity - AI Blog Generator", layout="wide")

    # Title and description
    st.title("✍️ Alwrity - 4-Part AI Blog Post Generator")
    st.markdown("Create a full blog post in 4 parts (Intro, Main Content, FAQs, Conclusion) with natural transitions.")

    # Input fields for the blog topic and settings
    blog_topic = st.text_input("Enter the main topic of your blog:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        blog_type = st.selectbox('Blog Post Type', ['General', 'How-to Guides', 'Listicles', 'Cheat Sheets', 'Job Posts'])
    
    with col2:
        blog_tone = st.selectbox('Blog Tone', ['Professional', 'Casual', 'Informative'])
    
    with col3:
        blog_language = st.selectbox('Language', ['English', 'Spanish', 'Chinese', 'Hindi', 'Vietnamese'])

    # Start the blog generation
    if st.button('Start Blog Generation'):
        if blog_topic:
            initialize_state()
            st.success('Blog generation started! Let\'s begin with the introduction.')

    # Generate the blog sections step by step
    if 'convo' in st.session_state and st.session_state['current_part'] != 'complete':
        current_part = st.session_state['current_part']
        if current_part == 'intro':
            if st.button('Generate Blog Introduction'):
                intro = generate_blog_section(blog_topic, blog_type, blog_tone, blog_language)
                st.subheader("Introduction")
                st.write(intro)
        elif current_part == 'body':
            if st.button('Generate Blog Main Content'):
                body = generate_blog_section(blog_topic, blog_type, blog_tone, blog_language)
                st.subheader("Main Content")
                st.write(body)
        elif current_part == 'faqs':
            if st.button('Generate FAQs'):
                faqs = generate_blog_section(blog_topic, blog_type, blog_tone, blog_language)
                st.subheader("Frequently Asked Questions (FAQs)")
                st.write(faqs)
        elif current_part == 'conclusion':
            if st.button('Generate Conclusion'):
                conclusion = generate_blog_section(blog_topic, blog_type, blog_tone, blog_language)
                st.subheader("Conclusion")
                st.write(conclusion)

    # Show the complete blog post when all parts are done
    if st.session_state.get('current_part') == 'complete':
        st.success("All parts of the blog have been generated!")
        if st.button('View Complete Blog'):
            st.subheader("Complete Blog Post")
            complete_blog = "\n\n".join(st.session_state['blog_parts'].values())
            st.write(complete_blog)


if __name__ == "__main__":
    main()
