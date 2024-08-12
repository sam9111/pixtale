# Pixtale

With Pixtale, users can get videos of their trips narrated by Gemini AI. The process involves uploading a zip file containing photos and videos from the trip or selecting a Google Photos album. Pixtale then extracts metadata, generates descriptions using Gemini AI, creates a narrative script, converts the narration to audio, and combines everything into a final video. Additionally, Pixtale generates captions, hashtags, and a mini blog post to share on social media.
![Pixtale whiteboard](https://github.com/user-attachments/assets/a11f578b-9f82-4ebe-b851-6d977d1cb481)

## Google APIs Used

Uses OAuth 2.0 Client IDs using _secrets_/client_secret.json:

- Vertex AI API
- Cloud Text-to-Speech API
- Photos Library API

Uses API key in .env:

- Places API

## How to Run This Flask App

Please run the below commands and authenticate with a Google account with access to this project (pixtale-420019) since the Vertex AI API, Cloud Text-to-Speech API and Photos Library API use OAuth 2.0 Client IDs.
```
gcloud auth application-default login
gcloud auth application-default set-quota-project pixtale-420019
```
1. Ensure you have Python and FFMPEG ( needed for video and audio processing ) is installed on your system.
2. Install the required packages using pip:
   ```
   pip install -r requirements.txt
   ```
3. This project uses Tailwind CSS and Flowbite so please run the below command to install into node_modules
   ```
   npm i
   ```
3. Run the app:
   ```
   python app.py
   ```
4. Once the app starts running, the Google Oauth consent screen will pop up to select a particular google account ( this can be any Google account ) with albums you might want to use in Pixtale.
<img width="1512" alt="Screenshot 2024-05-01 at 11 01 19 PM" src="https://github.com/sam9111/pixtale/assets/60708693/daedf0bb-4455-4506-84c5-f76288301a08">

 If denied access, no Google Photos album will be available in the dropdown at localhost:5000
 
 If an account is given access, a token.json file should appear in the _secrets_ folder.

## Notes

sample.zip contains a few photos and videos to test Pixtale with.

Since this can only be tested in a local environment, processing can be slow for audio and video generation. Hence, please consider trying out features and waiting completely for it to finish before trying out something else.


