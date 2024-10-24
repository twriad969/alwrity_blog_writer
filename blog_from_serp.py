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
            'main_content_3': None,
            'table': None,
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
        Please write a detailed and engaging **Introduction** for a blog post on the topic: {blog_topic}.
        Ensure the introduction hooks the reader with valuable insights and introduces the topic in a conversational and human-like tone.
        """
    elif current_part == 'main_content_1':
        prompt = f"""
        Let's start with the **first part of the main content** of the blog post on "{blog_topic}".
        Provide detailed insights that cover important aspects of the topic in a way that's engaging, well-structured, and informative. Include relevant subheadings.
        Keep the tone {blog_tone} and focus on making the content valuable and easy to understand.
        """
    elif current_part == 'main_content_2':
        prompt = f"""
        Now, move on to the **second part of the main content** for the blog post on "{blog_topic}".
        Expand further on the topic, introducing new points or diving deeper into subtopics.
        Maintain the same valuable and engaging tone to keep the reader's interest, and ensure it's informative and well-organized.
        """
    elif current_part == 'main_content_3':
        prompt = f"""
        Now, let's continue with the **third part of the main content** of the blog post on "{blog_topic}".
        Continue exploring additional important aspects of the topic. Make sure the content is thorough and provides value to the reader.
        Ensure this section contributes to the overall structure of the post, keeping the writing in a {blog_tone} tone.
        """
    elif current_part == 'table':
        prompt = f"""
        Now, create a **Table** summarizing key information related to the topic "{blog_topic}".
        The table should highlight important details, comparisons, or statistics that add value to the blog. Keep it simple and easy to read for the audience.
        """
    elif current_part == 'faqs':
        prompt = f"""
        Let's now create a concise set of **Frequently Asked Questions (FAQs)** for the blog post on "{blog_topic}".
        Provide 3 to 4 FAQs that are relevant and concise. Ensure the answers are short, clear, and to the point.
        """
    elif current_part == 'conclusion':
        prompt = f"""
        Finally, write a **Conclusion** for the blog post on "{blog_topic}".
        Summarize the key points discussed in the post, and provide a final takeaway or a call to action for the reader. Keep the tone friendly and engaging.
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
        st.session_state['current_part'] = 'main_content_3'
    elif current_part == 'main_content_3':
        st.session_state['current_part'] = 'table'
    elif current_part == 'table':
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
    st.title("gemwriter - 7-Part AI Blog Post Generator")
    st.markdown("Create a human-friendly, SEO-optimized blog post in 7 parts (Intro, Main Content in 3 Parts, Table, FAQs, Conclusion) with natural, easy-to-read transitions. proudly open source via ronok")

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
        elif current_part == 'main_content_3':
            if st.button('Generate Main Content (Part 3)'):
                main_content_3 = generate_blog_section(blog_topic, blog_type, blog_tone, blog_language)
                st.subheader("Main Content (Part 3)")
                st.write(main_content_3)
        elif current_part == 'table':
            if st.button('Generate Table'):
                table = generate_blog_section(blog_topic, blog_type, blog_tone, blog_language)
                st.subheader("Table")
                st.write(table)
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
