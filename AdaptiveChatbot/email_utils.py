import smtplib
from email.message import EmailMessage


def send_email(subject:str, recipient:str, content:str):
    # init
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = "AdaptiveBizapp"
    msg['To'] = recipient
    msg.set_content(content)

    # Prepare Simple Mail Transfer Protocol (SMTP) server to send e-mail
    MyServer = smtplib.SMTP('smtp.gmail.com', 587)
    MyServer.starttls()
    MyServer.login("adaptivebizappchatbot@gmail.com", "enzeupktbmopckvt")
    MyServer.send_message(msg)
    MyServer.quit()