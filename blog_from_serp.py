import os
import streamlit as st
import google.generativeai as genai


# Function to configure the generative AI model (Gemini)
def configure_gemini():
    genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
    return genai.GenerativeModel(model_name="gemini-1.5-flash-latest", generation_config={"max_output_tokens": 2048})


# Initialize the conversation and blog storage
def initiate_conversation():
    if 'convo' not in st.session_state:
        model = configure_gemini()
        st.session_state['convo'] = model.start_chat(history=[])
        # Initialize the blog content storage
        st.session_state['blog_content'] = {
            'intro': None,
            'body': None,
            'faqs': None,
            'conclusion': None
        }
        # Set the current part to 'intro' to start generating the introduction
        st.session_state['current_part'] = 'intro'


# Function to generate each section of the blog naturally
def generate_blog_section(input_keywords, blog_type, blog_tone, blog_language):
    if 'convo' in st.session_state:
        current_part = st.session_state['current_part']
        
        # Use specific prompts for each section
        if current_part == 'intro':
            prompt = f"""
            You are a {blog_language} SEO expert and skilled {blog_type} blog writer. 
            Write an **engaging introduction** for a blog post based on the topic: {input_keywords}.
            Ensure the tone is {blog_tone} and make it captivating for readers, setting up a strong base for the rest of the post.
            """
        elif current_part == 'body':
            prompt = f"""
            Now, let's proceed with the **main content** of the blog post. 
            Provide valuable insights on the topic "{input_keywords}", while ensuring the content is SEO-optimized and informative.
            Make sure to include a **Table of Contents** and structure the content clearly and in-depth for the reader.
            """
        elif current_part == 'faqs':
            prompt = f"""
            For the next section, let's generate **Frequently Asked Questions (FAQs)** related to the topic: {input_keywords}.
            Include at least five FAQs that are commonly searched, and provide well-detailed answers for each question.
            """
        elif current_part == 'conclusion':
            prompt = f"""
            Finally, write a **conclusion** for the blog post on "{input_keywords}".
            Summarize the key points, provide closing thoughts, and offer a call to action or a final remark for the reader.
            """
        
        # Generate the blog section
        conversation = st.session_state['convo']
        conversation.send_message(prompt)
        response = conversation.last.text

        # Store the generated part in the session state
        st.session_state['blog_content'][current_part] = response

        # Move to the next section
        if current_part == 'intro':
            st.session_state['current_part'] = 'body'
        elif current_part == 'body':
            st.session_state['current_part'] = 'faqs'
        elif current_part == 'faqs':
            st.session_state['current_part'] = 'conclusion'
        elif current_part == 'conclusion':
            st.session_state['current_part'] = 'complete'

        return response

    return None


# Main app function
def main():
    # Set up the page configuration
    st.set_page_config(page_title="Alwrity - Natural 4-Part AI Blog Writer", layout="wide")

    # Title and description
    st.title("✍️ Alwrity - 4-Part AI Blog Post Generator")
    st.markdown("Generate a complete blog post naturally in 4 parts (Intro, Content, FAQs, Conclusion). The AI will guide you smoothly through each part. 🚀")

    # Blog topic input
    if 'blog_topic' not in st.session_state:
        st.session_state['blog_topic'] = ""

    if not st.session_state['blog_topic']:
        st.session_state['blog_topic'] = st.text_input('**Enter the main topic of your blog** (Blog Title or Content Topic)')

    if st.session_state['blog_topic']:
        input_blog_keywords = st.session_state['blog_topic']

        # Collect blog settings
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            blog_type = st.selectbox('**Choose Blog Post Type** 📄', 
                                     options=['General', 'How-to Guides', 'Listicles', 'Job Posts', 'Cheat Sheets'], index=0)
        
        with col2:
            input_blog_tone = st.selectbox('**Choose Blog Tone** 🎨', 
                                           options=['General', 'Professional', 'Casual'], index=0)
        
        with col3:
            input_blog_language = st.selectbox('**Choose Language** 🌐', 
                                               options=['English', 'Vietnamese', 'Chinese', 'Hindi', 'Spanish'], index=0)

        # Initialize the conversation on first click
        if st.button('Start Blog Generation'):
            initiate_conversation()
            st.success('Blog generation started! Let\'s begin with the introduction.')

        # Generate each part of the blog based on the state and show it directly
        if 'convo' in st.session_state and st.session_state['current_part'] != 'complete':
            current_part = st.session_state['current_part']
            if current_part == 'intro':
                if st.button('Generate Blog Introduction'):
                    intro_part = generate_blog_section(input_blog_keywords, blog_type, input_blog_tone, input_blog_language)
                    if intro_part:
                        st.subheader('**Introduction**')
                        st.write(intro_part)
            elif current_part == 'body':
                if st.button('Generate Blog Main Content'):
                    body_part = generate_blog_section(input_blog_keywords, blog_type, input_blog_tone, input_blog_language)
                    if body_part:
                        st.subheader('**Main Content**')
                        st.write(body_part)
            elif current_part == 'faqs':
                if st.button('Generate FAQs'):
                    faq_part = generate_blog_section(input_blog_keywords, blog_type, input_blog_tone, input_blog_language)
                    if faq_part:
                        st.subheader('**Frequently Asked Questions (FAQs)**')
                        st.write(faq_part)
            elif current_part == 'conclusion':
                if st.button('Generate Conclusion'):
                    conclusion_part = generate_blog_section(input_blog_keywords, blog_type, input_blog_tone, input_blog_language)
                    if conclusion_part:
                        st.subheader('**Conclusion**')
                        st.write(conclusion_part)
                        st.success("All parts of the blog have been generated!")

        # Once all parts are complete, show the full blog
        if st.session_state['current_part'] == 'complete':
            st.success("✅ All parts of the blog are complete!")
            if st.button('View Complete Blog'):
                st.subheader('**Your Complete Blog Post**')
                complete_blog = "\n\n".join(st.session_state['blog_content'].values())
                st.write(complete_blog)


if __name__ == "__main__":
    main()
