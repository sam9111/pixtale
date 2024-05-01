# Pixtale

With Pixtale, users can get videos of their trips narrated by Gemini AI. The process involves uploading a zip file containing photos and videos from the trip or selecting a Google Photos album. Pixtale then extracts metadata, generates descriptions using Gemini AI, creates a narrative script, converts the narration to audio, and combines everything into a final video. Additionally, Pixtale generates captions, hashtags, and a mini blog post to share on social media.

https://devpost.com/software/pixtale
![Pixtale (1)](https://github.com/sam9111/pixtale/assets/60708693/3b1bd829-a6f3-4810-ac94-f0cddfe505d5)

## Google APIs Used

OAuth 2.0 Client IDs

- Vertex AI API
- Cloud Text-to-Speech API
- Places API
- Photos Library API

## How to Run This Flask App

Note for Devpost team: testing@devpost.com has been given Editor role permissions to the GCP project (pixtale-420019)

Please run the below commands and authenticate with testing@devpost.com since the Vertex AI API, Cloud Text-to-Speech API and Photos Library API use OAuth 2.0 Client IDs.
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
4. Once the app starts running, the Google Oauth consent screen will pop up to select a particular google account ( this can be any Google account i.e. even other than testing@devpost.com ) with albums you might want to use in Pixtale.
<img width="1512" alt="Screenshot 2024-05-01 at 11 01 19 PM" src="https://github.com/sam9111/pixtale/assets/60708693/daedf0bb-4455-4506-84c5-f76288301a08">

 If denied access, no Google Photos album will be available in the dropdown at localhost:5000
 
 If an account is given access, a token.json file should appear in the _secrets_ folder.

## Notes

sample.zip contains a few photos and videos to test Pixtale with.

Since this can only be tested in a local environment, processing can be slow for audio and video generation. Hence, please consider trying out features and waiting completely for it to finish before trying out something else.


