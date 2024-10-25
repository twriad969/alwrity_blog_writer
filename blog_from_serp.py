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

# Function to generate each blog section with enhanced prompts
def generate_blog_section(blog_topic, blog_type, blog_tone, blog_language):
    convo = st.session_state['convo']
    current_part = st.session_state['current_part']
    
    # Refined natural language prompts for each part
    if current_part == 'intro':
        prompt = f"""
        Write a captivating introduction for a {blog_language} blog post on the topic "{blog_topic}".
        This intro should hook readers, briefly outline what they’ll learn, and be inviting in tone. Imagine you're talking directly to a curious reader who wants practical insights about this topic.
        """
    elif current_part == 'main_content_1':
        prompt = f"""
        Create the **first main section** for a blog on "{blog_topic}" in {blog_language}.
        Start with a clear subheading, then explain a foundational aspect of the topic in a {blog_tone} way, sharing relevant details that build interest.
        """
    elif current_part == 'main_content_2':
        prompt = f"""
        Continue with the **second main section** for the topic "{blog_topic}".
        Introduce a new angle or important point, keeping the language conversational and easy to follow. Remember to make it engaging and informative.
        """
    elif current_part == 'main_content_3':
        prompt = f"""
        Develop the **third section** of the main content for "{blog_topic}".
        Offer additional insights or practical examples, ensuring this content flows naturally and aligns with the {blog_tone} style.
        """
    elif current_part == 'table':
        prompt = f"""
        Construct a simple, informative **table** summarizing key points about "{blog_topic}".
        This table should be easy to read and enhance the blog’s structure, possibly featuring comparisons or essential statistics.
        """
    elif current_part == 'faqs':
        prompt = f"""
        Write a set of **Frequently Asked Questions (FAQs)** for "{blog_topic}".
        Provide concise answers to common questions a reader might have, in a {blog_tone} tone, with no more than 2-3 sentences per answer.
        """
    elif current_part == 'conclusion':
        prompt = f"""
        Craft a friendly and thoughtful **conclusion** for the blog on "{blog_topic}".
        Summarize the main takeaways and offer a gentle call-to-action or final thought, leaving readers with something memorable.
        """
    
    # Send the prompt to the AI model
    convo.send_message(prompt)
    response = convo.last.text

    # Store the generated part in session state
    st.session_state['blog_parts'][current_part] = response

    # Move to the next part
    next_parts = {
        'intro': 'main_content_1',
        'main_content_1': 'main_content_2',
        'main_content_2': 'main_content_3',
        'main_content_3': 'table',
        'table': 'faqs',
        'faqs': 'conclusion',
        'conclusion': 'complete'
    }
    st.session_state['current_part'] = next_parts.get(current_part, 'complete')

    return response

# Main app function
def main():
    # Page configuration
    st.set_page_config(page_title="Gemwriter - AI Blog Generator", layout="wide")

    # Title and description
    st.title("Gemwriter - 7-Part AI Blog Post Generator")
    st.markdown("Generate an engaging, SEO-friendly blog in 7 sections, designed to capture and hold reader interest. Proudly open-sourced by ronok.")

    # Blog topic input
    blog_topic = st.text_input("Enter the main topic of your blog:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        blog_type = st.selectbox('Blog Post Type', ['General', 'How-to Guides', 'Listicles', 'Cheat Sheets', 'Customize'])
        if blog_type == 'Customize':
            blog_language = st.text_input("Enter your custom type:")
    
    with col2:
        blog_tone = st.selectbox('Blog Tone', ['Professional', 'Casual', 'Customize'])
        if blog_tone == 'Customize':
            blog_language = st.text_input("Enter your custom tone:")
    
    with col3:
        blog_language = st.selectbox('Language', ['English', 'Spanish', 'Chinese', 'Hindi', 'Vietnamese', 'Customize'])
        if blog_language == 'Customize':
            blog_language = st.text_input("Enter your custom language:")

    # Start the blog generation
    if st.button('Start Blog Generation'):
        if blog_topic:
            initialize_state()
            st.success('Blog generation started! Beginning with the introduction.')

    # Generate the blog sections step by step
    if 'convo' in st.session_state and st.session_state['current_part'] != 'complete':
        current_part = st.session_state['current_part']
        
        # Dynamic button labels for each section
        part_labels = {
            'intro': 'Generate Blog Introduction',
            'main_content_1': 'Generate Main Content (Part 1)',
            'main_content_2': 'Generate Main Content (Part 2)',
            'main_content_3': 'Generate Main Content (Part 3)',
            'table': 'Generate Table',
            'faqs': 'Generate FAQs',
            'conclusion': 'Generate Conclusion'
        }

        if st.button(part_labels.get(current_part, "Next Section")):
            part_content = generate_blog_section(blog_topic, blog_type, blog_tone, blog_language)
            st.subheader(current_part.replace("_", " ").title())
            st.write(part_content)

    # Show the complete blog post when all parts are done
    if st.session_state.get('current_part') == 'complete':
        st.success("All parts of the blog have been generated!")
        if st.button('View Complete Blog'):
            st.subheader("Complete Blog Post")
            complete_blog = "\n\n".join(st.session_state['blog_parts'].values())
            st.write(complete_blog)


if __name__ == "__main__":
    main()
