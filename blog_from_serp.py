import os
import streamlit as st
import google.generativeai as genai

# Initialize the AI model configuration
def configure_gemini():
    genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
    return genai.GenerativeModel(model_name="gemini-1.5-flash-latest", generation_config={"max_output_tokens": 2048})

# Function to initialize the conversation and session state
def initialize_state(num_sections, include_table, include_conclusion):
    if 'convo' not in st.session_state:
        model = configure_gemini()
        st.session_state['convo'] = model.start_chat(history=[])
        st.session_state['blog_parts'] = {'intro': None}
        st.session_state['current_part'] = 'intro'
        
        # Configure the parts to generate based on user inputs
        for i in range(1, num_sections + 1):
            st.session_state['blog_parts'][f'main_content_{i}'] = None
        if include_table:
            st.session_state['blog_parts']['table'] = None
        st.session_state['blog_parts']['faqs'] = None
        if include_conclusion:
            st.session_state['blog_parts']['conclusion'] = None

# Function to generate each blog section with enhanced prompts
def generate_blog_section(blog_topic, blog_tone, blog_language):
    convo = st.session_state['convo']
    current_part = st.session_state['current_part']
    
    # Refined prompts based on the section
    if current_part == 'intro':
        prompt = f"Write a captivating introduction for a {blog_language} blog post on the topic '{blog_topic}'. This intro should hook readers and be inviting in tone."
    elif current_part.startswith('main_content'):
        section_num = current_part.split('_')[-1]
        prompt = f"Write section {section_num} for '{blog_topic}' in {blog_language}. Make it informative and engaging in a {blog_tone} tone."
    elif current_part == 'table':
        prompt = f"Create a simple table summarizing key points about '{blog_topic}' in {blog_language}. This table should be easy to read, possibly featuring comparisons or stats."
    elif current_part == 'faqs':
        prompt = f"Write a FAQ section for '{blog_topic}' with brief, {blog_tone}-style answers to common questions."
    elif current_part == 'conclusion':
        prompt = f"Write a friendly conclusion for the blog on '{blog_topic}', summarizing the main takeaways with a call-to-action."

    # Generate response with spinner
    with st.spinner(f"Generating {current_part.replace('_', ' ').title()}..."):
        convo.send_message(prompt)
        response = convo.last.text
    
    # Store response and update the current part
    st.session_state['blog_parts'][current_part] = response
    next_part = list(st.session_state['blog_parts'].keys())[list(st.session_state['blog_parts'].keys()).index(current_part) + 1]
    st.session_state['current_part'] = next_part if next_part else 'complete'

    return response

# Main app function
def main():
    st.set_page_config(page_title="Customizable AI Blog Generator", layout="wide")
    st.title("Customizable AI Blog Generator")
    st.markdown("Generate an engaging blog in configurable sections. Powered by generative AI.")

    # Input for blog topic and customization options
    blog_topic = st.text_input("Enter the main topic of your blog:")
    blog_tone = st.selectbox('Blog Tone', ['Professional', 'Casual', 'Formal'])
    blog_language = st.selectbox('Language', ['English', 'Spanish', 'Chinese', 'Hindi', 'Vietnamese'])

    # Customization options
    num_sections = st.slider("Number of Main Sections", min_value=1, max_value=5, value=3)
    include_table = st.checkbox("Include Table")
    include_conclusion = st.checkbox("Include Conclusion")
    
    if st.button('Generate Blog'):
        if blog_topic:
            initialize_state(num_sections, include_table, include_conclusion)
            st.success('Blog generation started! Please wait as each section is generated.')

            # Generate each blog section sequentially
            while 'convo' in st.session_state and st.session_state['current_part'] != 'complete':
                part_content = generate_blog_section(blog_topic, blog_tone, blog_language)
                st.subheader(st.session_state['current_part'].replace("_", " ").title())
                st.write(part_content)
            
            st.success("All parts of the blog have been generated!")
            st.subheader("Complete Blog Post")
            complete_blog = "\n\n".join(st.session_state['blog_parts'].values())
            st.write(complete_blog)

if __name__ == "__main__":
    main()
