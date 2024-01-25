from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from translate import get_translated_video
from sms import send_media_msg
from upload import upload_link_file_to_aws

app = Flask(__name__)

@app.route("/whatsapp", methods=['POST'])
def whatsapp():
    num_media = int(request.values.get('NumMedia', 0))  # Number of media items in the message
    resp = MessagingResponse()
    msg = resp.message()

    if num_media > 0:
        media_url = request.values.get('MediaUrl0', '')  # URL of the media item
        media_content_type = request.values.get('MediaContentType0', '')  # Content type of media

        if 'video' in media_content_type:
            msg.body("Received a video file. Translating now, please wait a minute.")
            get_translated_video(media_url, language='hindi')
        else:
            msg.body("Received a file, but it's not a video. Please upload a video and try again")
    else:
        msg.body("No media file received.")
    return str(resp)


@app.route("/callback", methods=['GET', 'POST'])
def callback():
    data = request.json 
    if not data["error"]:
        synced_vid_link = data["result"]["url"]
        reuploaded_synced_vid = upload_link_file_to_aws(synced_vid_link, 'synced_vid.mp4')
        send_media_msg(reuploaded_synced_vid)

    return 'OK', 200

if __name__ == "__main__":
    app.run(debug=True, port=9000)