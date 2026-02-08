######################################## 
# 2024.04. IT Betyár - itbetyar.hu
# Huggingface - image-2-story 
# Frissítve: 2026.02

import os
from transformers import BlipProcessor, BlipForConditionalGeneration
from openai import OpenAI
from huggingface_hub import InferenceClient
import streamlit as st
from PIL import Image

# Retrieve API keys from environment variables
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
HUGGING_API_KEY = os.environ.get('HUGGING_API_KEY')

# Client init
openai_client = OpenAI(api_key=OPENAI_API_KEY)
hf_client = InferenceClient(
    provider="replicate",
    api_key=HUGGING_API_KEY
)

# 1. lépés: képből szöveg
def img2story(image_path):
    try:
        processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
        
        raw_image = Image.open(image_path).convert('RGB')
        inputs = processor(raw_image, return_tensors="pt")
        out = model.generate(**inputs)
        text = processor.decode(out[0], skip_special_tokens=True)
        
        print("Image to text:", text)
        return text
    except Exception as e:
        print(f"Error in img2story: {e}")
        return "A beautiful scene"

# 2. lépés, llm, szöveg kiegészítés
def generate_story(scenario):
    prompt = f"You are a story teller. Generate a short story based on the following scenario in no more than 20 words:\n\nScenario: {scenario}\n\nStory:"
    
    completion = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a story teller."},
            {"role": "user", "content": prompt}
        ],
    )
    
    story = completion.choices[0].message.content
    print(f"Story: {story}")
    return story

# 3. lépés: text to speech
def text2speech(message):
    try:
        audio_bytes = hf_client.text_to_speech(
            text=message,
            model="hexgrad/Kokoro-82M",
        )
        
        with open('audio.flac', 'wb') as file:
            file.write(audio_bytes)
        return True
    except:
        return False

def main():
    st.set_page_config(page_title="Képből audio történet", page_icon="🤖")

        # Display the additional image with a specific width - KÖZÉPRE IGAZÍTVA
    if os.path.exists("mulimodal_cover.webp"):
        col1, col2, col3 = st.columns([0.1, 4, 0.1])
        with col2:
            st.image("mulimodal_cover.webp", use_container_width=True)
    
    st.markdown("<h1 style='text-align: center;'>Image to Audio Story</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center;'>Változtassunk egy képet egy audio történetté</h4>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: pink;'>IT Betyár multimodal minta | Diákoknak</h4>", unsafe_allow_html=True)
    st.markdown("""
            <p style='text-align: center; color: white;'>
                Multimodal: szinte fel se tűnik ma már, de a modern AI hálózatok 
                nem csak text-to-text alapúak. Általában több almodell dolgozik 
                együtt - képfelismerés, szövegértés, hangszintézis - hogy komplex 
                feladatokat oldjanak meg.
            </p>
            """, unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center;'>Alábbi app minta, összesen 3 modellt működtet</h4>", unsafe_allow_html=True)

            
    
    
    uploaded_file = st.file_uploader("Válassz egy képet...", type="jpg")
    
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        with open(uploaded_file.name, "wb") as file:
            file.write(bytes_data)
        
        st.image(uploaded_file, caption='Uploaded Image.', width='stretch')
        
        scenario = img2story(uploaded_file.name)
        story = generate_story(scenario)
        audio_success = text2speech(story)
        
        with st.expander("scenario"):
            st.write(scenario)
        with st.expander("story"):
            st.write(story)
        
        if audio_success and os.path.exists("audio.flac"):
            st.audio("audio.flac")
        else:
            st.info("🔊 Audio is processing, please try again in a moment.")

if __name__ == '__main__':
    main()