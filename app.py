import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

st.set_page_config(page_title="YouTube Video Translator", page_icon="🌐")

# Custom CSS for better aesthetics
st.markdown("""
<style>
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 1.5rem;
        overflow-y: auto;
    }
    .main {
        background-color: #f0f2f6;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 50px;
        font-weight: bold;
        background-color: #4CAF50;
        color: white;
    }
    .stTextInput>div>div>input {
        border-radius: 10px;
        height: 50px;
    }
    .stSelectbox>div>div {
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.header("About")
st.sidebar.info(
    "This app translates YouTube video transcripts to your desired language using Gemini AI."
)
st.sidebar.markdown("---")

# Main App
st.markdown(
    """<h1 style="display: flex; align-items: center;">
    <img src="https://upload.wikimedia.org/wikipedia/commons/0/09/YouTube_full-color_icon_%282017%29.svg" width="100" style="margin-right: 10px;">
    YouTube Video Translator
    </h1>""", 
    unsafe_allow_html=True
)
# st.markdown("### Translate video transcripts to any language")

# Input
youtube_url = st.text_input("Enter YouTube Video URL", placeholder="e.g., https://www.youtube.com/watch?v=dQw4w9WgXcQ")

if youtube_url:
    st.video(youtube_url)

# Language selection
language_options = {
    "English": "en",
    "Hindi": "hi",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Chinese (Simplified)": "zh-CN",
    "Japanese": "ja",
    "Korean": "ko",
    "Russian": "ru",
    "Arabic": "ar"
}

selected_language_name = st.selectbox("Select Target Language", list(language_options.keys()))
selected_language_code = language_options[selected_language_name]

# API Key Input (Optional - uses .env by default)
# api_key = st.text_input("Enter Gemini API Key (optional)", type="password", value=os.getenv("GOOGLE_API_KEY", ""))

if st.button("Translate"):
    if not youtube_url:
        st.error("Please enter a YouTube URL")
    else:
        try:
            # Extract video ID
            video_id = youtube_url.split("v=")[-1].split("&")[0]
            
            with st.spinner("Fetching transcript..."):
                # Get transcript list and fetch the first available transcript
                transcript_list = YouTubeTranscriptApi().list(video_id)
                try:
                    first_transcript = next(iter(transcript_list))
                    transcript_data = first_transcript.fetch()
                    transcript = " ".join([item.text for item in transcript_data])
                except StopIteration:
                    transcript = ""
            
            if not transcript:
                st.error("Could not fetch transcript. The video may not have captions or is not available in your region.")
            else:
                # Configure Gemini
                client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
                
                # Translation prompt
                prompt = f"""
                Translate the following YouTube video transcript to {selected_language_name}.
                Keep the tone conversational and natural, as if explaining the video to someone.
                Maintain the structure with paragraphs where appropriate.
                
                Transcript:
                {transcript}
                
                Translated Transcript:
                """
                
                with st.spinner(f"Translating to {selected_language_name}..."):
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=prompt
                    )
                    translated_text = response.text
                
                # Display results
                st.success("Translation Complete!")
                
                st.markdown("---")
                st.subheader(f"Original Transcript (English)")
                st.text_area("Original", transcript, height=300)
                
                st.markdown("---")
                st.subheader(f"Translated Transcript ({selected_language_name})")
                st.text_area("Translated", translated_text, height=300)
                
                # Download button
                st.download_button(
                    label=f"Download {selected_language_name} Transcript",
                    data=translated_text,
                    file_name=f"translated_transcript_{selected_language_code}.txt",
                    mime="text/plain"
                )
                
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.error("Troubleshooting:")
            st.error("- Make sure the video has English captions.")
            st.error("- Check if the video is available in your region.")
            st.error("- Verify your API key is correct.")