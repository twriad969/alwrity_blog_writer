import time
import os
import streamlit as st
from tenacity import retry, stop_after_attempt, wait_random_exponential
import google.generativeai as genai
from exa_py import Exa


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

    # Step 2: Generate the headings
    headings = generate_blog_headings(title, input_language)
    st.subheader('**Headings**')
    for i, heading in enumerate(headings, 1):
        st.write(f"{i}. {heading}")
    
    # Step 3: Generate content for each heading
    st.subheader('**Content**')
    content_pieces = []
    for heading in headings:
        content = generate_content_for_heading(heading, input_language, input_tone)
        refined_content = refine_content(content, input_language, input_tone)
        content_pieces.append(f"### {heading}\n{refined_content}")
    
    # Step 4: Combine and display the refined content
    final_content = "\n\n".join(content_pieces)
    st.write(final_content)

    # Step 5: Generate FAQs
    faqs = generate_faqs(input_blog_keywords, input_language)
    st.subheader('**FAQs**')
    for faq in faqs:
        st.write(f"**Q:** {faq['question']}\n**A:** {faq['answer']}")


# Step 1: Generate the blog title
def generate_blog_title(keywords, blog_type, language):
    prompt = f"Generate a single engaging and natural-sounding {language} blog title based on the following keywords: {keywords}. The blog type is {blog_type}. The title should be catchy and human-readable, without sounding robotic."
    return generate_text_with_exception_handling(prompt)


# Step 2: Generate blog headings
def generate_blog_headings(title, language):
    prompt = f"Generate exactly 5 detailed, SEO-optimized headings for a blog titled '{title}' in {language}. These headings should be clear, concise, and valuable, without any generic or repetitive text."
    headings = generate_text_with_exception_handling(prompt).split("\n")
    return [heading.strip() for heading in headings if heading.strip()]


# Step 3: Generate content for each heading
def generate_content_for_heading(heading, language, tone):
    prompt = f"Write high-quality content for the heading '{heading}' in {language}. The tone should be {tone}. Avoid robotic or repetitive phrases, and ensure the content is valuable, well-researched, and engaging for the reader."
    return generate_text_with_exception_handling(prompt)


# Step 4: Refine content to remove robotic text
def refine_content(content, language, tone):
    prompt = f"Refine the following content to remove any robotic-sounding text, making it more human-like, valuable, and engaging. Ensure the tone is {tone} and maintain a natural flow:\n\n{content}"
    return generate_text_with_exception_handling(prompt)


# Step 5: Generate FAQs
def generate_faqs(keywords, language):
    prompt = f"Generate 5 frequently asked questions (FAQs) with detailed answers based on the keywords '{keywords}' in {language}. Make sure the questions and answers are natural-sounding and provide useful information, without sounding robotic."
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
