import google.generativeai as genai
from django.conf import settings
from decouple import config
import os
import json

class GeminiService:
    def log(self, msg):
        log_file = os.path.join(settings.BASE_DIR, 'gemini_debug.log')
        with open(log_file, 'a') as f:
            f.write(f"{msg}\n")

    def __init__(self):
        self.log("\n--- AIService Init ---")
        
        # Load Google API Key
        self.google_api_key = getattr(settings, 'GOOGLE_API_KEY', None)
        if not self.google_api_key:
            self.google_api_key = config('GOOGLE_API_KEY', default=None)
        
        # Load Hugging Face API Key
        self.huggingface_key = getattr(settings, 'HUGGINGFACE_API_KEY', None)
        if not self.huggingface_key:
            self.huggingface_key = config('HUGGINGFACE_API_KEY', default=None)
        
        self.log(f"Google API Key: {'Present' if self.google_api_key else 'Missing'}")
        self.log(f"Hugging Face Key: {'Present' if self.huggingface_key else 'Missing'}")

        if self.google_api_key:
            try:
                genai.configure(api_key=self.google_api_key)
                # Use gemini-flash-latest as it has available quota and is robust.
                self.model = genai.GenerativeModel('models/gemini-flash-latest')
                self.active = True
                self.log("GeminiService: SUCCESS - Model initialized (gemini-flash-latest).")
            except Exception as e:
                self.log(f"GeminiService: ERROR - {e}")
                self.active = False
        else:
            self.log("GeminiService: FAILURE - No Google API Key found.")
            self.active = False

    def chat_response(self, message, history=[]):
        """
        Handles multi-turn chat using Gemini's chat session.
        History should be a list of dicts: [{'role': 'user'|'model', 'text': '...'}]
        """
        if not self.active:
            return None

        try:
            # Convert history to Gemini format
            gemini_history = []
            for msg in history:
                gemini_history.append({
                    "role": "user" if msg['role'] == 'user' else "model",
                    "parts": [msg['text']]
                })

            chat = self.model.start_chat(history=gemini_history)
            response = chat.send_message(message)
            
            if response and hasattr(response, 'text'):
                return response.text
            return None
        except Exception as e:
            self.log(f"Gemini Chat Error: {e}")
            if "429" in str(e):
                return "QUOTA_EXCEEDED"
            return None

    def generate_response(self, prompt, system_instruction=None):
        if not self.active:
            self.log("GeminiService: generate_response called but NOT active.")
            return None
        
        try:
            self.log(f"GeminiService: Sending prompt: {prompt[:100]}...")
            if system_instruction:
                full_prompt = f"System: {system_instruction}\n\nUser: {prompt}"
            else:
                full_prompt = prompt
                
            response = self.model.generate_content(full_prompt)
            if response and hasattr(response, 'text'):
                self.log(f"GeminiService: RECEIVED response: {response.text[:100]}...")
                return response.text
            self.log("GeminiService: RECEIVED empty response or no text attribute.")
            return None
        except Exception as e:
            self.log(f"Gemini API Error (generate_response): {e}")
            if "429" in str(e):
                return "QUOTA_EXCEEDED"
            return None

    def analyze_resume(self, resume_text, job_description):
        if not self.active:
            self.log("GeminiService: analyze_resume called but NOT active.")
            return None

        prompt = f"""
        Analyze the following resume against the job description.
        Provide a JSON response ONLY with the following keys:
        {{
            "resume_score": (integer 0-100),
            "overall_summary": "concise summary",
            "strengths": ["list of strengths"],
            "weaknesses": ["list of gaps/missing keywords"],
            "missing_keywords": ["top 3 missing specific keywords"],
            "improvement_suggestions": ["actionable tips to improve the resume"]
        }}

        Resume: {resume_text}
        Job Description: {job_description}
        """
        
        try:
            response = self.model.generate_content(prompt)
            # Find JSON in response text
            text = response.text
            start = text.find('{')
            end = text.rfind('}') + 1
            if start != -1 and end != -1:
                return json.loads(text[start:end])
            return None
        except Exception as e:
            self.log(f"Gemini Analysis Error: {e}")
            if "429" in str(e):
                return "QUOTA_EXCEEDED"
            return None

    def detect_ai_image(self, image_file):
        if not self.active:
            self.log("GeminiService: detect_ai_image called but NOT active.")
            return None

        prompt = """
        Analyze this image and determine if it is AI-generated or a real photo taken by a human/camera.
        Look for common AI artifacts like:
        - Inconsistent shadows or lighting
        - Strange textures in hair or skin
        - Nonsensical background details
        - Distorted limbs or fingers
        - "Too perfect" or "painted" look
        
        Provide a JSON response ONLY with the following keys:
        {
            "is_ai_generated": (boolean),
            "confidence_score": (float 0-100),
            "explanation": "Brief technical explanation of why you reached this conclusion"
        }
        """
        
        try:
            # Read image data
            image_data = image_file.read()
            # Reset file pointer if needed by other views, but since we are in API it's fine
            
            response = self.model.generate_content([prompt, {'mime_type': image_file.content_type, 'data': image_data}])
            
            text = response.text
            start = text.find('{')
            end = text.rfind('}') + 1
            if start != -1 and end != -1:
                return json.loads(text[start:end])
            
            self.log(f"Gemini Detect Error: Could not parse JSON from {text}")
            return None
        except Exception as e:
            self.log(f"Gemini Detect AI Image Error: {e}")
            if "429" in str(e):
                return "QUOTA_EXCEEDED"
            return None
    def transcribe_audio_whisper(self, audio_data, mime_type="audio/webm"):
        """Transcribes audio using Hugging Face Whisper Large v3 Turbo."""
        if not self.huggingface_key:
            return None

        # Use openai/whisper-large-v3-turbo for balance of speed and state-of-the-art accuracy
        model_id = "openai/whisper-large-v3-turbo"
        api_url = f"https://api-inference.huggingface.co/models/{model_id}"
        headers = {"Authorization": f"Bearer {self.huggingface_key}"}

        import requests
        try:
            self.log(f"Whisper STT: Attempting via {model_id}...")
            # Whisper Inference API takes raw binary data
            response = requests.post(api_url, headers=headers, data=audio_data, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                transcription = result.get("text", "").strip()
                if transcription:
                    self.log(f"Whisper STT: SUCCESS - {transcription[:50]}...")
                    return transcription
            
            self.log(f"Whisper STT: API Error {response.status_code} - {response.text}")
            return None
        except Exception as e:
            self.log(f"Whisper STT: Exception - {e}")
            return None

    def transcribe_audio(self, audio_file, language=None):
        """Transcribes audio using Gemini 1.5 Flash."""
        if not self.active:
            self.log("GeminiService: transcribe_audio called but NOT active.")
            return None

        lang_instruction = f"The expected language is: {language}." if language and language != "Multi-Language" else "The language might vary, please auto-detect."

        prompt = f"""TRANSCRIPTION TASK:
1. Transcribe the following audio accurately and verbatim.
2. {lang_instruction}
3. Preserve all punctuation, capitalization, and formatting.
4. Do not summarize or explain.
5. If the language is not English, transcribe it in its native script.
6. If there is background noise, ignore it and focus on the primary speaker.
"""
        
        try:
           # Read audio data
            audio_data = audio_file.read()
            # If it's a file-like object, it might need reset
            if hasattr(audio_file, 'seek'):
                audio_file.seek(0)
            
            # MIME type detection for audio
            mime_type = getattr(audio_file, 'content_type', None)
            if not mime_type or mime_type == 'application/octet-stream':
                 # Fallback based on extension if possible, else default to webm
                 if hasattr(audio_file, 'name') and audio_file.name.endswith('.mp3'):
                     mime_type = 'audio/mpeg'
                 elif hasattr(audio_file, 'name') and audio_file.name.endswith('.wav'):
                     mime_type = 'audio/wav'
                 elif hasattr(audio_file, 'name') and audio_file.name.endswith('.webm'):
                     mime_type = 'audio/webm'
                 else:
                     mime_type = 'audio/webm'

            # Refinement for browser-specific webm formats
            if 'webm' in mime_type and 'codecs=' not in mime_type:
                 mime_type = 'audio/webm;codecs=opus'

            self.log(f"Transcribing audio: Size={len(audio_data)} bytes, MIME={mime_type}")
            
            if len(audio_data) < 100:
                self.log("Gemini STT: Audio data too small, ignoring.")
                return None

            # 1. PRIMARY: Try Whisper via Hugging Face (Higher accuracy, better for verbatim)
            transcription = self.transcribe_audio_whisper(audio_data, mime_type=mime_type)
            if transcription:
                return transcription

            # 2. FALLBACK: Try Gemini 1.5 Flash
            self.log("Gemini STT: Falling back to Gemini 1.5 Flash...")
            response = self.model.generate_content(
                [
                    prompt,
                    {
                        "mime_type": mime_type,
                        "data": audio_data
                    }
                ],
                generation_config={
                    "temperature": 0.1,
                    "top_p": 1,
                    "top_k": 1,
                    "max_output_tokens": 2048,
                }
            )
            if response and hasattr(response, 'text'):
                return response.text.strip()
            return None
        except Exception as e:
            self.log(f"Gemini Transcribe Audio Error: {e}")
            if "429" in str(e):
                return "QUOTA_EXCEEDED"
            return None


    def generate_image_huggingface(self, prompt):
        """Generates an image using Hugging Face Inference API."""
        if not self.huggingface_key or self.huggingface_key == "your_huggingface_api_key_here":
            self.log("Hugging Face API Key is missing or default. Skipping.")
            return None

        # Modern Models: SDXL is high fidelity, FLUX is state-of-the-art
        models = [
            "black-forest-labs/FLUX.1-schnell",
            "stabilityai/stable-diffusion-xl-base-1.0",
            "ByteDance/SDXL-Lightning"
        ]
        
        # We try different API endpoints
        endpoints = [
            "https://api-inference.huggingface.co/models/{model_id}",
            "https://router.huggingface.co/hf-inference/models/{model_id}"
        ]
        
        # CLEAN HEADERS: Do not add extra metadata that triggers WAF blocks
        headers = {"Authorization": f"Bearer {self.huggingface_key}"}

        import requests
        for model_id in models:
            for api_url_template in endpoints:
                api_url = api_url_template.format(model_id=model_id)
                try:
                    self.log(f"HF Gen: Trying {model_id} via {api_url.split('/')[2]}...")
                    # SDXL and FLUX usually benefit from longer timeouts (up to 90s for warm up)
                    response = requests.post(api_url, headers=headers, json={"inputs": prompt}, timeout=90)
                    
                    if response.status_code == 200:
                        self.log(f"Hugging Face API: SUCCESS using {model_id}")
                        return response.content
                    elif response.status_code == 503:
                        self.log(f"Hugging Face: {model_id} is LOADING (503). Skipping to next model...")
                        break # Try next model if this one is loading
                    elif response.status_code in [401, 403]:
                        self.log(f"Hugging Face AUTH ERROR: {response.status_code}")
                        return None # Auth error is fatal for HF
                    else:
                        self.log(f"Hugging Face API Error ({model_id}): {response.status_code}")
                except Exception as e:
                    self.log(f"Hugging Face API Exception ({model_id}): {e}")
        
        # 3. Last Resort: AI Horde (Distributed GPU Network)
        try:
            self.log("All primary providers failed. Attempting AI Horde (Distributed Network)...")
            # Stable Horde allows anonymous requests with '0000000000'
            horde_url = "https://stablehorde.net/api/v2/generate/sync"
            horde_payload = {
                "prompt": prompt,
                "params": {"sampler_name": "k_euler", "cfg_scale": 7.5, "width": 512, "height": 512, "steps": 20},
                "models": ["stable_diffusion"],
            }
            horde_headers = {"apikey": "0000000000", "Client-Agent": "DocZen:1.0:AIStudio"}
            horde_resp = requests.post(horde_url, json=horde_payload, headers=horde_headers, timeout=60)
            if horde_resp.status_code == 200:
                horde_data = horde_resp.json()
                if "generations" in horde_data and len(horde_data["generations"]) > 0:
                    import base64
                    img_data = base64.b64decode(horde_data["generations"][0]["img"])
                    self.log("AI Horde: SUCCESS")
                    return img_data
        except Exception as e:
            self.log(f"AI Horde Exception: {e}")

        return None

    def generate_image(self, prompt, style=None):
        # Enhance prompt based on style for better results (especially realism)
        style_enhancements = {
            "realistic": "professional photography, 8k resolution, highly detailed, sharp focus, cinematic lighting, realistic textures, realistic skin, canon eos r5, masterpiece, photorealistic",
            "anime": "anime art style, vibrant colors, expressive eyes, clean lines, high quality illustration, Makoto Shinkai style, featured on pixiv",
            "digital-art": "digital painting, smooth gradients, crisp details, professional illustration, artstation trend, 8k, detailed concept art",
            "oil-painting": "oil painting on canvas, thick brushstrokes, rich textures, classic fine art aesthetic, Rembrandt lighting, gallery quality",
            "3d-render": "octane render, unreal engine 5, 3d model, raytracing, cinematic lighting, 4k, photorealistic 3d, v-ray",
            "cyberpunk": "cyberpunk aesthetic, neon lights, rainy city, futuristic technology, pink and cyan color palette, high detail, blade runner style, volumetric lighting"
        }
        
        enhanced_prompt = prompt
        if style:
            # Map style ID to enhancement or use as fallback
            enhancement = style_enhancements.get(style.lower(), f"{style} style")
            if style.lower() in style_enhancements:
                enhanced_prompt = f"{prompt}, {enhancement}"
            else:
                enhanced_prompt = f"{prompt}, {style} style"

        # 1. Try Hugging Face first if key is available
        if self.huggingface_key and self.huggingface_key != "your_huggingface_api_key_here":
            self.log(f"ImageGen: Using Hugging Face with enhanced prompt: {enhanced_prompt[:100]}...")
            image_bytes = self.generate_image_huggingface(enhanced_prompt)
            if image_bytes:
                return {
                    "image_bytes": image_bytes,
                    "provider": "huggingface",
                    "message": f"Generated image via Hugging Face for: {enhanced_prompt[:50]}..."
                }

        # 2. Fallback to Pollinations.ai or Gemini (if indirect)
        import urllib.parse
        import random
        
        self.log(f"ImageGen: Using Pollinations (Flux) with enhanced prompt: {enhanced_prompt[:100]}...")
        encoded_prompt = urllib.parse.quote(enhanced_prompt)
        seed = random.randint(1, 1000000)
        # Flux model at pollinations is the current state-of-the-art for free generation.
        # We also include width/height and enhance it for the flux engine.
        image_url = f"https://pollinations.ai/p/{encoded_prompt}?width=1024&height=1024&seed={seed}&model=flux&nologo=true&enhance=true"
        
        return {
            "image_url": image_url,
            "provider": "pollinations",
            "message": f"Generated image via Pollinations for: {enhanced_prompt[:50]}..."
        }

ai_service = GeminiService()
