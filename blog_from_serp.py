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
        st.session_state['blog_content'] = []  # To store the four parts
        st.session_state['current_part'] = 1  # Start with part 1

# Function to generate a part of the blog post
def generate_blog_part(input_keywords, blog_type, blog_tone, blog_language):
    if 'convo' in st.session_state:
        part_num = st.session_state['current_part']
        prompt = f"""
        You are a {blog_language} SEO expert and {blog_type} blog writer.
        Generate **Part {part_num}** of a 4-part blog post on the following topic:
        
        **Topic**: {input_keywords}
        **Tone**: {blog_tone}
        
        Make sure to create a valuable and easy-to-read blog post part, with clear insights and proper formatting.
        """
        
        conversation = st.session_state['convo']
        conversation.send_message(prompt)
        
        response = conversation.last.text
        
        # Store the generated part in memory
        st.session_state['blog_content'].append(response)
        st.session_state['current_part'] += 1  # Move to the next part
        
        return response
    return None

# Main application function
def main():
    # Set up the page
    st.set_page_config(page_title="4-Part Blog Generator", layout="wide")

    # Title and description
    st.title("✍️ Alwrity - 4-Part AI Blog Post Generator")
    st.markdown("Effortlessly generate a high-quality blog post in 4 parts. Each part will be valuable and easy to read. 🚀")

    # Input for blog topic
    if 'blog_topic' not in st.session_state:
        st.session_state['blog_topic'] = ""

    if not st.session_state['blog_topic']:
        st.session_state['blog_topic'] = st.text_input('**Enter the main topic of your blog** (Blog Title or Content Topic)')
    
    if st.session_state['blog_topic']:
        input_blog_keywords = st.session_state['blog_topic']

        # Collect blog type, tone, and language settings
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

        # Initialize conversation on button click
        if st.button('Start Blog Generation'):
            initiate_conversation()
            st.success('Blog generation started. You can now generate the first part!')

        # If the conversation is ongoing, display a prompt for each part
        if 'convo' in st.session_state and st.session_state['current_part'] <= 4:
            if st.button(f'Generate Part {st.session_state["current_part"]} of the Blog'):
                generated_part = generate_blog_part(input_blog_keywords, blog_type, input_blog_tone, input_blog_language)
                if generated_part:
                    st.subheader(f'**Part {st.session_state["current_part"] - 1} of Your Blog Post**')
                    st.write(generated_part)
                    if st.session_state['current_part'] > 4:
                        st.success("All parts of the blog are now complete!")
                else:
                    st.error("❌ Failed to generate blog part. Try again.")
        else:
            if st.session_state['current_part'] > 4:
                st.success("✅ All 4 parts of the blog have been generated!")
                if st.button('View Complete Blog'):
                    st.subheader('**Your Complete 4-Part Blog Post**')
                    complete_blog = "\n\n".join(st.session_state['blog_content'])
                    st.write(complete_blog)

if __name__ == "__main__":
    main()
