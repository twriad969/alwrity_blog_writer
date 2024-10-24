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
            'main_content_1': None,
            'main_content_2': None,
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
        You are a professional {blog_language} SEO expert and {blog_type} blog writer.
        Please write a compelling, detailed, and engaging **Introduction** for a blog post on the topic: {blog_topic}.
        Ensure the introduction hooks the reader with valuable insights and introduces the topic in a conversational and human-like tone.
        """
    elif current_part == 'main_content_1':
        prompt = f"""
        Now, let's dive into the **first part of the main content** of the blog post on "{blog_topic}".
        Provide detailed and valuable insights, structured for readability and SEO optimization.
        Include subheadings where necessary, and make sure the tone is {blog_tone}.
        This part should cover some of the most important aspects of the topic in a way that educates and engages the reader.
        """
    elif current_part == 'main_content_2':
        prompt = f"""
        Now, let's move on to the **second part of the main content** of the blog post on "{blog_topic}".
        Continue expanding on the topic, going deeper into more advanced points or covering additional critical aspects of the subject.
        The writing should be detailed, well-structured, and easy to read. The tone remains {blog_tone}, and this section should feel as valuable as the first.
        """
    elif current_part == 'faqs':
        prompt = f"""
        Now, let's generate a set of **Frequently Asked Questions (FAQs)** related to the topic: {blog_topic}.
        Include at least five detailed FAQs with clear, concise, and informative answers. Ensure the questions are relevant to the topic and are likely to be asked by readers.
        """
    elif current_part == 'conclusion':
        prompt = f"""
        Finally, write a **Conclusion** for the blog post on "{blog_topic}".
        Summarize the key points of the blog, provide a final takeaway for the reader, and offer a call to action if applicable.
        The tone should be friendly and engaging.
        """
    
    # Send the prompt to the AI model
    convo.send_message(prompt)
    response = convo.last.text

    # Store the generated part in session state
    st.session_state['blog_parts'][current_part] = response

    # Move to the next part
    if current_part == 'intro':
        st.session_state['current_part'] = 'main_content_1'
    elif current_part == 'main_content_1':
        st.session_state['current_part'] = 'main_content_2'
    elif current_part == 'main_content_2':
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
    st.title("✍️ Alwrity - 5-Part AI Blog Post Generator")
    st.markdown("Create a human-friendly, SEO-optimized blog post in 5 parts (Intro, Main Content in 2 Parts, FAQs, Conclusion) with natural, easy-to-read transitions.")

    # Blog topic input
    blog_topic = st.text_input("Enter the main topic of your blog:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        blog_type = st.selectbox('Blog Post Type', ['General', 'How-to Guides', 'Listicles', 'Cheat Sheets', 'Job Posts'])
    
    with col2:
        blog_tone = st.selectbox('Blog Tone', ['Professional', 'Casual', 'Informative'])
    
    with col3:
        blog_language = st.selectbox('Language', ['English', 'Spanish', 'Chinese', 'Hindi', 'Vietnamese', 'Customize'])
        if blog_language == 'Customize':
            blog_language = st.text_input("Enter your custom language:")

    # Start the blog generation
    if st.button('Start Blog Generation'):
        if blog_topic:
            initialize_state()
            st.success('Blog generation started! Let\'s begin with the introduction.')

    # Generate the blog sections step by step
    if 'convo' in st.session_state and st.session_state['current_part'] != 'complete':
        current_part = st.session_state['current_part']
        
        # Dynamically change the button label based on the section being generated
        if current_part == 'intro':
            if st.button('Generate Blog Introduction'):
                intro = generate_blog_section(blog_topic, blog_type, blog_tone, blog_language)
                st.subheader("Introduction")
                st.write(intro)
        elif current_part == 'main_content_1':
            if st.button('Generate Main Content (Part 1)'):
                main_content_1 = generate_blog_section(blog_topic, blog_type, blog_tone, blog_language)
                st.subheader("Main Content (Part 1)")
                st.write(main_content_1)
        elif current_part == 'main_content_2':
            if st.button('Generate Main Content (Part 2)'):
                main_content_2 = generate_blog_section(blog_topic, blog_type, blog_tone, blog_language)
                st.subheader("Main Content (Part 2)")
                st.write(main_content_2)
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
