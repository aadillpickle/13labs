from twilio.rest import Client
import os
from dotenv import load_dotenv

load_dotenv()
client = Client(os.environ.get("TWILIO_ACCOUNT_SID"), os.environ.get("TWILIO_AUTH_TOKEN"))
def send_media_msg(mediaUrl):
    message = client.messages.create(
        media_url=mediaUrl,
        from_=f'whatsapp:+{os.environ.get("TWILIO_PHONE_NUMBER")}', 
        to=f'whatsapp:+{os.environ.get("MY_PHONE_NUMBER")}'
    )
    return message.sid