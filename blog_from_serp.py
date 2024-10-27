import os
import streamlit as st
import google.generativeai as genai

# Configure the AI model
def configure_gemini():
    genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
    return genai.GenerativeModel(model_name="gemini-1.5-flash-latest", generation_config={"max_output_tokens": 2048})

# Initialize conversation and session states
def initialize_state(num_sections, include_table, include_conclusion):
    if 'convo' not in st.session_state:
        model = configure_gemini()
        st.session_state['convo'] = model.start_chat(history=[])
        
        # Define blog structure based on customization
        st.session_state['blog_parts'] = {
            'intro': None,
            **{f'main_content_{i}': None for i in range(1, num_sections + 1)},
            'table': None if not include_table else None,
            'faqs': None,
            'conclusion': None if not include_conclusion else None
        }
        st.session_state['current_part'] = 'intro'

# Generate human-friendly, SEO-focused prompts
def generate_prompt(current_part, blog_topic, blog_tone, blog_language):
    prompts = {
        'intro': f"Write a friendly and engaging intro for a {blog_language} blog on '{blog_topic}'. Get the reader interested and give a quick overview of what they’ll learn.",
        'main_content': f"Write a main section for a blog post on '{blog_topic}' in {blog_language}. Use clear subheadings, keep a {blog_tone} tone, and add helpful details and examples.",
        'table': f"Create a simple table for '{blog_topic}' that highlights key points, comparisons, or interesting stats. Make it easy to read and useful.",
        'faqs': f"Create an FAQ for '{blog_topic}' with common questions. Keep answers short and use a {blog_tone} tone.",
        'conclusion': f"Write a friendly conclusion for the blog on '{blog_topic}'. Summarize main points and encourage readers to take action or remember key insights."
    }

    if current_part.startswith('main_content'):
        section_num = current_part.split('_')[-1]
        return f"{prompts['main_content']} This is section {section_num}."

    return prompts[current_part]

# Generate each blog section with proper sequence
def generate_blog_section(blog_topic, blog_tone, blog_language):
    convo = st.session_state['convo']
    current_part = st.session_state['current_part']
    
    # Prompt and generate content
    prompt = generate_prompt(current_part, blog_topic, blog_tone, blog_language)
    with st.spinner(f"Generating {current_part.replace('_', ' ').title()}..."):
        convo.send_message(prompt)
        response = convo.last.text

    # Store generated part and update sequence
    st.session_state['blog_parts'][current_part] = response
    parts_list = list(st.session_state['blog_parts'].keys())
    next_index = parts_list.index(current_part) + 1
    st.session_state['current_part'] = parts_list[next_index] if next_index < len(parts_list) else 'complete'
    
    return response

# Main app function
def main():
    st.set_page_config(page_title="Human-Friendly AI Blog Generator", layout="wide")
    st.title("Human-Friendly AI Blog Generator")
    st.markdown("Create an SEO-friendly, reader-focused blog in easy-to-read sections.")

    # User input for blog topic and customization
    blog_topic = st.text_input("Enter your blog topic:")
    blog_tone = st.selectbox("Choose the blog tone", ["Friendly", "Informative", "Conversational"])
    blog_language = st.selectbox("Choose the blog language", ["English", "Spanish", "Chinese", "Hindi", "Vietnamese"])
    
    # Options for customizing the blog structure
    num_sections = st.slider("Number of Main Sections", min_value=1, max_value=5, value=3)
    include_table = st.checkbox("Include a Table Section")
    include_conclusion = st.checkbox("Include a Conclusion Section")

    if st.button('Generate Blog'):
        if blog_topic:
            initialize_state(num_sections, include_table, include_conclusion)
            st.success('Blog generation started! Generating sections one by one.')

            # Sequentially generate each section
            while 'convo' in st.session_state and st.session_state['current_part'] != 'complete':
                part_content = generate_blog_section(blog_topic, blog_tone, blog_language)
                st.subheader(st.session_state['current_part'].replace("_", " ").title())
                st.write(part_content)
            
            # Display the final blog
            st.success("Your blog is ready!")
            st.subheader("Complete Blog Post")
            complete_blog = "\n\n".join(part for part in st.session_state['blog_parts'].values() if part)
            st.write(complete_blog)

if __name__ == "__main__":
    main()
