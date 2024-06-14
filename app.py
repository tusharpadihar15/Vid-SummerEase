import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import openai
from gtts import gTTS # For audio conversion
from googletrans import Translator, LANGUAGES
import base64
# Set your OpenAI API key here
openai.api_key = 'your OpenAI API key'


def set_bg_hack(main_bg):
    '''
    A function to unpack an image from root folder and set as bg.
 
    Returns
    -------
    The background.
    '''
    # Set background
    main_bg_ext = "png"
        
    st.markdown(#"stHeader"
         f"""
         <style>
         .stApp {{
             background: url(data:image/{main_bg_ext};base64,{base64.b64encode(open(main_bg, "rb").read()).decode()});
             background-size: cover
         }}
         </style>
         """,
         unsafe_allow_html=True
     )
setpat = r'C:\Users\hp\Downloads\DALL.png'
set_bg_hack(setpat)



def get_transcript(video_id):
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = ' '.join([item['text'] for item in transcript_list])
        return transcript
    except TranscriptsDisabled:
        st.error("Transcripts are disabled for this video.")
        return None
    except NoTranscriptFound:
        st.error("No transcript found for this video.")
        return None

def preprocess_text(text, max_length=5000):
    """Preprocess the text to fit within OpenAI's token limits."""
    return text[:max_length]

def summarize_text(text):
    truncated_text = preprocess_text(text)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Summarize the following text and give respone in points when needed, give respone in atleast 150 words:\n\n{truncated_text}"}
        ]
    )
    return response['choices'][0]['message']['content']

def answer_question(text, question):
    truncated_text = preprocess_text(text)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant. that gives the answers of the question in very precise way."},
            {"role": "user", "content": f"{question}\n\n{truncated_text}"}
        ]
    )
    return response['choices'][0]['message']['content']

def translate_text(text, dest_language):
    translator = Translator()
    translated = translator.translate(text, dest=dest_language)
    return translated.text

def generate_audio_summary(summary, lang='en'):
    tts = gTTS(text=summary, lang=lang)
    audio_file = 'summary.mp3'
    tts.save(audio_file)
    return audio_file

# Streamlit UI setup
st.title("Vid SummarEase & QA Tool")

action = st.radio("Choose an action:", ("Summarize", "Ask a Question"))

with st.form("summarizer_form"):
    video_url = st.text_input("Enter YouTube Video URL:", "")
    if action == "Summarize":
        language = st.selectbox("Choose Language for Summary:", options=list(LANGUAGES.values()))
        summary_format = st.radio("Choose Form of Summary:", ("Text", "Audio"))
    else:
        question = st.text_input("Enter your question:")
    submitted = st.form_submit_button("Submit")

if submitted and video_url:
    video_id = video_url.split("watch?v=")[-1] #to find id from the url
    transcript = get_transcript(video_id) # to generate transcript    
    if transcript:
        if action == "Summarize":
            with st.spinner('Generating an summary...'):

                summary = summarize_text(transcript)
                if language != "English":
                    lang_code = [code for code, lang in LANGUAGES.items() if lang == language][0]
                    summary = translate_text(summary, dest_language=lang_code)

                if summary_format == "Text":
                    st.subheader("Summary:")
                    st.write(summary)
                elif summary_format == "Audio":
                    if language != "English":
                        lang_code = [code for code, lang in LANGUAGES.items() if lang == language][0]
                    else:
                        lang_code = 'en'
                    audio_file = generate_audio_summary(summary, lang=lang_code)
                    st.audio(audio_file, format='audio/mp3', start_time=0)
        elif action == "Ask a Question" and question:
            with st.spinner('Generating an answer...'):
                answer = answer_question(transcript, question)
                st.subheader("Answer:")
                st.write(answer)