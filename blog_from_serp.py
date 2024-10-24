import time
import os
import streamlit as st
from tenacity import retry, stop_after_attempt, wait_random_exponential
import google.generativeai as genai
from queue import Queue, Empty
from threading import Thread, Lock

# Constants
MAX_REQUESTS_PER_MINUTE = 10
REQUEST_INTERVAL = 60 / MAX_REQUESTS_PER_MINUTE  # Time to wait between requests

# Global variables to track requests
request_queue = Queue()
processed_requests = 0
request_lock = Lock()

# Function to process the queue
def process_queue():
    global processed_requests
    while True:
        try:
            # Get the next request from the queue
            task = request_queue.get(timeout=1)
            if task:
                with request_lock:
                    # Check if the request limit is reached
                    if processed_requests >= MAX_REQUESTS_PER_MINUTE:
                        # Wait for the next minute window
                        st.warning("Rate limit reached. Waiting for 60 seconds to resume pending tasks.")
                        time.sleep(60)
                        processed_requests = 0  # Reset counter after the wait

                    # Process the request
                    task['result'].append(generate_text_with_exception_handling(task['prompt']))

                    # Increment the processed requests count
                    processed_requests += 1

                    # Wait for the defined interval before the next request
                    time.sleep(REQUEST_INTERVAL)

            request_queue.task_done()

        except Empty:
            continue

# Start the background queue processing thread
Thread(target=process_queue, daemon=True).start()

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
    title_result = []
    request_queue.put({'prompt': generate_title_prompt(input_blog_keywords, input_type, input_language), 'result': title_result})
    request_queue.join()  # Wait until task is completed
    title = title_result[0]
    
    st.subheader('**Blog Title**')
    st.write(title)

    # Step 2: Generate introduction
    intro_result = []
    request_queue.put({'prompt': generate_introduction_prompt(title, input_language), 'result': intro_result})
    request_queue.join()
    introduction = intro_result[0]
    
    st.subheader('**Introduction**')
    st.write(introduction)

    # Step 3: Generate the headings
    headings_result = []
    request_queue.put({'prompt': generate_headings_prompt(title, input_language), 'result': headings_result})
    request_queue.join()
    headings = headings_result[0].split("\n")
    headings = [heading.strip() for heading in headings if heading.strip()]

    # Step 4: Generate content for each heading in multiple parts and refine
    st.subheader('**Content**')
    content_pieces = []
    for heading in headings:
        content_result = []
        request_queue.put({'prompt': generate_heading_content_prompt(heading, input_language, input_tone), 'result': content_result})
        request_queue.join()
        refined_content = refine_in_parts(content_result[0], input_language, input_tone, pieces=5)
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
    faqs_result = []
    request_queue.put({'prompt': generate_faqs_prompt(input_blog_keywords, input_language), 'result': faqs_result})
    request_queue.join()
    faqs = faqs_result[0].split("\n")
    st.subheader('**FAQs**')
    for faq in faqs:
        if ":" in faq:
            question, answer = faq.split(":", 1)
            st.write(f"**Q:** {question.strip()}\n**A:** {answer.strip()}")

# Generate prompts
def generate_title_prompt(keywords, blog_type, language):
    return f"Generate a creative and captivating {language} blog title using these keywords: {keywords}. The blog type is {blog_type}."

def generate_introduction_prompt(title, language):
    return f"Write a catchy and engaging introduction for a blog titled '{title}' in {language}. Ensure the introduction naturally hooks the reader and provides an exciting preview of the blog content."

def generate_headings_prompt(title, language):
    return f"Generate 5 clear, SEO-optimized headings for a blog titled '{title}' in {language}. The headings should be informative and engaging."

def generate_heading_content_prompt(heading, language, tone):
    return f"Write high-quality, informative content for the heading '{heading}' in {language}. Use a {tone} tone and ensure the content is valuable, with practical insights and tips."

def generate_faqs_prompt(keywords, language):
    return f"Generate 5 frequently asked questions (FAQs) along with detailed answers for the topic based on the keywords '{keywords}' in {language}. Ensure the questions are informative and the answers are helpful."

# Refine content in smaller parts
def refine_in_parts(content, language, tone, pieces=5):
    content_chunks = split_content_into_chunks(content, pieces)
    refined_chunks = []
    
    for chunk in content_chunks:
        prompt = f"Refine the following text to make it sound natural, engaging, and free of repetitive or robotic phrases. Ensure the tone is {tone}:\n\n{chunk}"
        chunk_result = []
        request_queue.put({'prompt': prompt, 'result': chunk_result})
        request_queue.join()
        refined_chunks.append(chunk_result[0])
    
    return "\n\n".join(refined_chunks)

# Split content into chunks
def split_content_into_chunks(content, pieces):
    words = content.split()
    chunk_size = max(1, len(words) // pieces)
    return [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]

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
