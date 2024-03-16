import smtplib, os, json
from email.message import EmailMessage
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


def notification(message):
    message = json.loads(message)
    mp3_fid = message["mp3_id"]
    sender_address = os.environ.get("GMAIL_ADDRESS")
    sender_password = os.environ.get("GMAIL_PASSWORD")

    if not sender_address or not sender_password:
        raise Exception("set GMAIL_ADDRESS and GMAIL_PASSWORD in .env")

    receiver_address = message.get("user")

    if not receiver_address:
        return

    msg = EmailMessage()
    msg.set_content(
        "mp3 file is now ready. download url: "
        + os.environ.get("GATEWAY_URL", "")
        + os.environ.get("DOWNLOAD_ENDPOINT", "").format(mp3_fid)
    )
    msg["Subject"] = "MP3 Download"
    msg["To"] = receiver_address

    session = smtplib.SMTP("smtp.gmail.com", 587)
    session.starttls()
    session.login(sender_address, sender_password)
    session.send_message(msg, sender_address, receiver_address)
    session.quit()
    print("Mail Sent")
