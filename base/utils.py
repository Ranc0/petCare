from mailersend import emails

mailer = emails.NewEmail('Ymlsn.8cad8597cbcc83e6806aecb2d686d21c08d068d205b2741fe3e0cd760f086cad')  # 👈 Paste your API token here

def send_otp_email(to_email, otp_code):
    mail_body = f'Your OTP code is: {otp_code}'
    mail_subject = 'OTP Verification'
    
    mailer.set_mail_from('pet_care_otp@outlook.com', 'Pet Care')
    mailer.set_mail_to([{'email': to_email}])
    mailer.set_subject(mail_subject)
    mailer.set_text(mail_body)

    response = mailer.send()
    return response
