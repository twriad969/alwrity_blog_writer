import time
import os
import streamlit as st
from tenacity import retry, stop_after_attempt, wait_random_exponential
import google.generativeai as genai

def main():
    # Set page configuration
    st.set_page_config(page_title="Alwrity - AI Blog Writer", layout="wide")

    # Apply custom CSS for styling
    st.markdown("""<style>
        .block-container { padding: 0rem 1rem; }
        ::-webkit-scrollbar-track { background: #e1ebf9; }
        ::-webkit-scrollbar-thumb { background-color: #90CAF9; border-radius: 10px; border: 3px solid #e1ebf9; }
        ::-webkit-scrollbar-thumb:hover { background: #64B5F6; }
        ::-webkit-scrollbar { width: 16px; }
        div.stButton > button:first-child {
            background: #1565C0; color: white; border: none; padding: 12px 24px; 
            border-radius: 8px; font-size: 16px; margin: 10px 2px; cursor: pointer; 
            transition: background-color 0.3s ease; box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.2); font-weight: bold;
        }
    </style>""", unsafe_allow_html=True)

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

        # Generate Blog button
        if st.button('**Write Blog Post ✍️**'):
            with st.spinner('Generating your blog post...'):
                if not input_blog_keywords:
                    st.error('**🫣 Provide Inputs to generate Blog Post. Keywords are required!**')
                else:
                    generate_full_blog(input_blog_keywords, blog_type, input_blog_tone, input_blog_language)


# Function to orchestrate the multi-stage blog generation
def generate_full_blog(input_blog_keywords, input_type, input_tone, input_language):
    # Step 1: Generate the blog title
    title = generate_blog_title(input_blog_keywords, input_type, input_language)
    st.subheader('**Blog Title**')
    st.write(title)

    # Step 2: Generate introduction
    introduction = generate_introduction(title, input_language)
    st.subheader('**Introduction**')
    st.write(introduction)

    # Step 3: Generate the headings
    headings = generate_blog_headings(title, input_language)

    # Step 4: Generate content for each heading in multiple parts and refine
    st.subheader('**Content**')
    content_pieces = []
    for heading in headings:
        content = generate_content_for_heading(heading, input_language, input_tone)
        refined_content = refine_in_parts(content, input_language, input_tone, pieces=5)  # Split and refine in 5 parts
        content_pieces.append(f"### {heading}\n{refined_content}")
    
    # Step 5: Combine and display the final content
    final_content = "\n\n".join(content_pieces)
    st.write(final_content)

    # Step 6: Add table after content if requested
    if st.checkbox('Add a Table Section?'):
        table_content = st.text_area("Enter table content in markdown format (headers separated by '|'):")
        if table_content:
            st.subheader('**Table Section**')
            st.markdown(table_content)

    # Step 7: Generate FAQs in correct format
    faqs = generate_faqs(input_blog_keywords, input_language)
    st.subheader('**FAQs**')
    for faq in faqs:
        st.write(f"**Q:** {faq['question']}\n**A:** {faq['answer']}")

# Generate introduction
def generate_introduction(title, language):
    prompt = f"Write a catchy and engaging introduction for a blog titled '{title}' in {language}. Ensure the introduction naturally hooks the reader and provides an exciting preview of the blog content."
    return generate_text_with_exception_handling(prompt)

# Generate the blog title
def generate_blog_title(keywords, blog_type, language):
    prompt = f"Generate a creative and captivating {language} blog title that uses the following keywords: {keywords}. The blog type is {blog_type}. Ensure the title feels natural and attention-grabbing."
    return generate_text_with_exception_handling(prompt)

# Generate blog headings
def generate_blog_headings(title, language):
    prompt = f"Generate 5 clear, SEO-optimized headings for a blog titled '{title}' in {language}. The headings should be informative and engaging, giving readers a solid structure to follow."
    headings = generate_text_with_exception_handling(prompt).split("\n")
    return [heading.strip() for heading in headings if heading.strip()]

# Generate content for each heading
def generate_content_for_heading(heading, language, tone):
    prompt = f"Write high-quality, informative content for the heading '{heading}' in {language}. Use a {tone} tone and ensure the content is valuable, with practical insights and tips."
    return generate_text_with_exception_handling(prompt)

# Refine the content in smaller parts to avoid robotic or repetitive phrasing
def refine_in_parts(content, language, tone, pieces=5):
    # Split content into smaller chunks for refinement
    content_chunks = split_content_into_chunks(content, pieces)
    refined_chunks = []
    
    for chunk in content_chunks:
        prompt = f"Refine the following text to make it sound natural, engaging, and free of repetitive or robotic phrases. Ensure the tone is {tone}:\n\n{chunk}"
        refined_chunks.append(generate_text_with_exception_handling(prompt))
    
    return "\n\n".join(refined_chunks)

# Split the content into smaller chunks
def split_content_into_chunks(content, pieces):
    words = content.split()
    chunk_size = max(1, len(words) // pieces)
    return [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]

# Generate FAQs in the correct format (without external formatting issues)
def generate_faqs(keywords, language):
    prompt = f"Generate 5 frequently asked questions (FAQs) along with detailed answers for the topic based on the keywords '{keywords}' in {language}. Ensure the questions are informative and the answers are helpful."
    faq_text = generate_text_with_exception_handling(prompt)
    faq_lines = faq_text.split("\n")
    faqs = []
    for line in faq_lines:
        if ":" in line:
            question, answer = line.split(":", 1)
            faqs.append({"question": question.strip(), "answer": answer.strip()})
    return faqs

# Exception handling for text generation
@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def generate_text_with_exception_handling(prompt):
    try:
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        model = genai.GenerativeModel(model_name="gemini-1.5-flash-latest", generation_config={"max_output_tokens": 8192})
        convo = model.start_chat(history=[])
        convo.send_message(prompt)
        return convo.last.text
    except Exception as e:
        st.exception(f"An unexpected error occurred: {e}")
        return None


if __name__ == "__main__":
    main()
