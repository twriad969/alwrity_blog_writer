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
        
        # Configure parts dynamically based on user input
        for i in range(1, num_sections + 1):
            st.session_state['blog_parts'][f'main_content_{i}'] = None
        if include_table:
            st.session_state['blog_parts']['table'] = None
        st.session_state['blog_parts']['faqs'] = None
        if include_conclusion:
            st.session_state['blog_parts']['conclusion'] = None

# Enhanced prompt generation for SEO and human-like language
def generate_prompt(current_part, blog_topic, blog_tone, blog_language):
    prompts = {
        'intro': f"Craft a captivating introduction for a {blog_language} blog post on '{blog_topic}' that’s SEO-optimized. Hook readers, provide a quick preview of what’s to come, and make it relatable to a reader looking for useful insights.",
        'main_content': f"Write a main section for the blog post on '{blog_topic}' in {blog_language}. Start with a clear, SEO-friendly subheading and write in a {blog_tone} tone, including engaging details and examples to draw the reader in.",
        'table': f"Create a well-organized table summarizing key points about '{blog_topic}'. Use a simple structure, add comparisons, or present essential statistics for easy reference.",
        'faqs': f"Write an FAQ section on '{blog_topic}' with SEO keywords in the questions. Provide concise answers in a {blog_tone} tone, and keep answers to 2-3 sentences for readability.",
        'conclusion': f"Write a thoughtful conclusion for the blog on '{blog_topic}'. Summarize the main points and offer a call-to-action, leaving readers with something to remember or act upon."
    }

    if current_part.startswith('main_content'):
        section_number = current_part.split('_')[-1]
        return f"{prompts['main_content']} This is section {section_number}."
    return prompts[current_part]

# Function to generate each blog section
def generate_blog_section(blog_topic, blog_tone, blog_language):
    convo = st.session_state['convo']
    current_part = st.session_state['current_part']
    
    # Generate prompt and get response
    prompt = generate_prompt(current_part, blog_topic, blog_tone, blog_language)
    
    # Use spinner to indicate generation in progress
    with st.spinner(f"Generating {current_part.replace('_', ' ').title()}..."):
        convo.send_message(prompt)
        response = convo.last.text
    
    # Store generated content and update the current part
    st.session_state['blog_parts'][current_part] = response
    parts_list = list(st.session_state['blog_parts'].keys())
    next_index = parts_list.index(current_part) + 1
    
    # Ensure next part exists, otherwise mark as complete
    st.session_state['current_part'] = parts_list[next_index] if next_index < len(parts_list) else 'complete'
    return response

# Main app function
def main():
    st.set_page_config(page_title="SEO-Friendly AI Blog Generator", layout="wide")
    st.title("SEO-Friendly AI Blog Generator")
    st.markdown("Generate an engaging, customizable blog in SEO-optimized sections.")

    # Input for blog topic and customization options
    blog_topic = st.text_input("Enter the main topic of your blog:")
    blog_tone = st.selectbox('Blog Tone', ['Professional', 'Casual', 'Formal'])
    blog_language = st.selectbox('Language', ['English', 'Spanish', 'Chinese', 'Hindi', 'Vietnamese'])

    # Customization options for sections
    num_sections = st.slider("Number of Main Sections", min_value=1, max_value=5, value=3)
    include_table = st.checkbox("Include Table")
    include_conclusion = st.checkbox("Include Conclusion")
    
    if st.button('Generate Blog'):
        if blog_topic:
            initialize_state(num_sections, include_table, include_conclusion)
            st.success('Blog generation started! Please wait as each section is generated.')

            # Sequential generation of blog sections
            while 'convo' in st.session_state and st.session_state['current_part'] != 'complete':
                part_content = generate_blog_section(blog_topic, blog_tone, blog_language)
                st.subheader(st.session_state['current_part'].replace("_", " ").title())
                st.write(part_content)
            
            st.success("All parts of the blog have been generated!")
            st.subheader("Complete Blog Post")
            complete_blog = "\n\n".join(part for part in st.session_state['blog_parts'].values() if part)
            st.write(complete_blog)

if __name__ == "__main__":
    main()
