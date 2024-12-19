"""All mails."""
from initializers.aws import LAMBDA_CLIENT
import json
from pydantic import EmailStr
from datetime import datetime


def lambda_mail_sender(body, subject, recipients_list: list):
    """Invoke email sender lambda to send mail."""
    event = {}
    event['body'] = body
    event['subject'] = subject
    event['recipients_list'] = recipients_list
    LAMBDA_CLIENT.invoke(
        FunctionName='3d_mapping_mail_sender',
        InvocationType='Event',
        Payload=json.dumps(event)
    )

def send_signup_mail(verification_url, recipient: str, recepient_name: str):
    """Send signup mail to user."""
    try:
        body = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Signup</title>
</head>
<body style="font-family: Arial, sans-serif; color: #333; margin: 0; padding: 0;">
    <table width="100%" cellspacing="0" cellpadding="0" border="0" style="max-width: 700px;margin:"0 auto";  background-color: #F5F6FF; border-radius: 8px; overflow: hidden;">
        <tr>
            <td style="background-color: #1e3d5d; padding: 20px; text-align: center;">
                <img width="400" src="https://botlabdynamics.com/sites/default/files/2022-11/BL%20Botlab%20Dynamics%20%281%29.png" alt="Botlab Dynamics Logo">
 
            </td>
        </tr>
        <tr>
            <td style="padding: 32px;">
                <p style="font-size: 16px; line-height: 1.5; margin: 0;">Dear <span style="color: #2969FF;">{},</span></p>
                <p style="font-size: 16px; line-height: 1.5; margin: 20px 0;">Thank you for signing up. To verify your email address, please click on the link below:</p>
                <p style="text-align: center;">
                    <a href="{}" style="display: inline-block; padding: 10px 20px; font-size: 16px; color: #ffffff; background-color: #28a745; text-decoration: none; border-radius: 4px;">Click here to verify</a>
                </p>
                <p style="font-size: 16px; line-height: 1.5; margin: 20px 0;">If the above link does not work, you can copy and paste the following URL into your browser:</p>
                <p style="font-size: 16px; line-height: 1.5; margin: 20px 0; word-break: break-all;">
                    <a href="{}" style="color: #007bff; text-decoration: none;">https://example.com/verification-link</a>
                </p>
                <p style="font-size: 16px; line-height: 1.5; margin: 20px 0;">Once your email is verified, you'll be able to access all the features of Botlab Dynamics Drone Mapping.</p>
                <div style="margin-top: 32px;">
                <p>Best regards,</p>
                <p>The Drone Mapping Team</p>
                <p><span style="font-weight: bold;">Contact:</span> 9873088096</p>
            </div>
            </td>
        </tr>
        
    </table>
</body>
</html>'''
        # body = """
        # <head>
        #     <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
        # </head>
        # <body>
        #     <h2>Welcome to Botlab dynamics drone mapping!</h2>
        #     <p>Dear {},</p>
        #     <p>Thank you for signing up. To verify your email address, please click on the following link:</p>
        #     <p><a href="{}">Click here to verify</a></p>
        #     <p>If the above link does not work, you can copy and paste the following URL into your browser:</p>
        #     <p<a>{}</a></p>
        #     <p>Once your email is verified, you'll be able to access all the features of Botlab dynamics drone mapping.
        #     </p>
        #     <p>Best regards,<br> The Drone Mapping Team</p>
        # </body>
        # """
        body = body.format(recepient_name, verification_url, verification_url)
        lambda_mail_sender(body=body, subject="Verify SignUp", recipients_list=[recepient_name])
        return True

    except Exception as ex:
        print(f"{ex=}")
        return False


def send_password_otp_mail(otp, recipient: EmailStr,):
    """Send password otp mail."""
    try:
        body = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reset Password OTP</title>
</head>
<body style="font-family: Arial, sans-serif; color: #333; margin: 0; padding: 0;">
    <table width="100%" cellspacing="0" cellpadding="0" border="0" style="max-width: 700px;margin:"0 auto"; background-color: #F5F6FF; border-radius: 8px; overflow: hidden;">
        <tr>
            <td style="background-color: #1e3d5d; padding: 20px; text-align: center;">
                <img src="https://botlabdynamics.com/sites/default/files/2022-11/BL%20Botlab%20Dynamics%20%281%29.png" alt="Botlab Dynamics Logo" style="width: 200px; max-width: 100%;">
            </td>
        </tr>
        <tr>
            <td style="padding: 32px;">
                <p style="font-size: 16px; line-height: 1.5; margin: 0;">Hello,</p>
                <p style="font-size: 16px; line-height: 1.5; margin: 20px 0;">To assist you with resetting your password, please use the One-Time Password (OTP) provided below:</p>
               <div style="text-align: center; margin-top: 32px;">
                    <p style="font-size: 16px; margin: 0;">Your Reset Password OTP Code</p>
                    <p style="font-weight: bold; font-size: 30px; margin: 18px 0; user-select: none;">{}</p>
                    <p style="font-size: 16px; line-height: 1.5; margin: 0;">(This code will expire <span style="font-weight: bold;">10 minutes</span> after it was sent.)</p>
                </div>
                <p style="font-size: 16px; line-height: 1.5; margin: 20px 0;">For your security, do not share this OTP with anyone. If you did not request a password reset, please ignore this email.</p>
                <div style="margin-top: 32px;">
                    <p style="font-size: 16px; line-height: 1.5; margin: 0;">Best regards,</p>
                    <p style="font-size: 16px; line-height: 1.5; margin: 0;">The Drone Mapping Team</p>
                    <p style="font-size: 16px; color: #666; margin: 0;"><span style="font-weight: bold;">Contact:</span> 9873088096</p>
                </div>
            </td>
        </tr>
    </table>
</body>
</html>'''
#         body = '''
# <body style="-webkit-touch-callout: none; -webkit-user-select: none; -khtml-user-select: none;
# -moz-user-select: none; -ms-user-select: none; user-select: none;">
#     <h2>Botlab dynamics drone mapping!</h2>
#     <p>Dear User,</p>
#     <p>To regenrate new password, Please use below otp code.</p>
#     <p style = " background-color: black; color: white; width: min-content; padding: 20px 30px; font-weight: bold;
#     letter-spacing: 4px;">{}</p>
#     <p>Please do not share this otp with anyone.
#     </p>
#     <p>Best regards,<br> The Drone Mapping Team</p>
# </body>
#         '''
        body = body.format(otp)
        lambda_mail_sender(body=body, subject="Password OTP", recipients_list=[recipient])
        return True
    except Exception as ex:
        print(f"{ex=}")
        return False


def send_login_otp_mail(otp, recipient: EmailStr):
    """Send login otp mail to user."""
    try:
        body = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login OTP</title>
</head>
<body style="font-family: Arial, sans-serif; color: #333;margin: 0; padding: 0;">
    <table width="100%" cellspacing="0" cellpadding="0" border="0" style="max-width: 700px; margin:"0 auto"; background-color: #F5F6FF; border-radius: 8px; overflow: hidden;">
        <tr>
            <td style="background-color: #1e3d5d; padding: 20px; text-align: center;">
                <img width="400" src="https://botlabdynamics.com/sites/default/files/2022-11/BL%20Botlab%20Dynamics%20%281%29.png" alt="Botlab Dynamics Logo" >
            </td>
        </tr>
        <tr>
            <td style="padding: 32px;">
                <p style="font-size: 16px; line-height: 1.5; margin: 0;">Dear <span style="color: #2969FF;">{},</span></p>
                <p style="font-size: 16px; line-height: 1.5; margin: 20px 0;">Thank you for choosing our service. To ensure the security of your account, please use the One-Time Password (OTP) provided below to complete your verification.</p>
                <p style="font-size: 16px; line-height: 1.5; margin: 20px 0;">Please enter this code on the verification page within the next 10 minutes. Do not share this code with anyone to keep your account secure.</p>
                <div style="text-align: center; margin-top: 32px;">
                    <p style="font-size: 16px; margin: 0;">Your Login OTP Code</p>
                    <p style="font-weight: bold; font-size: 30px; margin: 18px 0; user-select: none;">{}</p>
                    <p style="font-size: 16px; line-height: 1.5; margin: 0;">(This code will expire <span style="font-weight: bold;">10 minutes</span> after it was sent.)</p>
                </div>
                <div style="margin-top: 32px;">
                    <p style="font-size: 16px; line-height: 1.5; margin: 0;">Best regards,</p>
                    <p style="font-size: 16px; line-height: 1.5; margin: 0;">The Drone Mapping Team</p>
                    <p style="font-size: 14px; color: #666; margin: 0;"><span style="font-weight: bold;">Contact:</span> 9873088096</p>
                </div>
            </td>
        </tr>
    </table>
</body>
</html>'''
#         body = '''
# <body style="-webkit-touch-callout: none; -webkit-user-select: none; -khtml-user-select: none;
# -moz-user-select: none; -ms-user-select: none; user-select: none;">
#     <h2>Botlab dynamics drone mapping!</h2>
#     <p>Dear User,</p>
#     <p>To Login to your account, Please use below otp code.</p>
#     <p style = " background-color: black; color: white; width: min-content; padding: 20px 30px; font-weight: bold;
#     letter-spacing: 4px;">{}</p>
#     <p>Please do not share this otp with anyone.
#     </p>
#     <p>Best regards,<br> The Drone Mapping Team</p>
# </body>
#         '''
        body = body.format(recipient, otp)
        lambda_mail_sender(body=body, subject="Login OTP", recipients_list=[recipient])
        return True
    except Exception as ex:
        print(f"{ex=}")
        return False


def send_successfully_login_mail(recipient: EmailStr):
    """Send successfull login mail to user."""
    try:
        now = datetime.now()
        current_date = now.strftime("%d/%m/%Y")
        current_time = now.strftime("%H:%M:%S")
        body = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login Success</title>
    <style>
    body{
          font-family: "Open Sans", sans-serif;
          box-sizing: border-box;
    }
    h1,h2,h3,h4,h5,h6,p,span{
        margin: 0;
        padding: 0;
        color: #000000;
        line-height: 28px;
        letter-spacing: 0.3px;
    }
</style>
</head>
<body style="font-family: Arial, sans-serif; color: #333;margin: 0; padding: 0;">
    <table width="100%" cellspacing="0" cellpadding="0" border="0" style="max-width: 700px;margin:"0 auto"; background-color: #F5F6FF; border-radius: 8px; overflow: hidden;">
        <tr>
              <td style="background-color: #1e3d5d; padding: 20px; text-align: center;">
                   <img width="400" src="https://botlabdynamics.com/sites/default/files/2022-11/BL%20Botlab%20Dynamics%20%281%29.png" alt="">
            </td>
        </tr>
        <tr>
            <td style="padding:32px;">
                <p style="font-size: 16px; line-height: 1.5; margin: 0;">Dear <span style="color: #2969FF;">{},</span></p>
                <p style="font-size: 16px; line-height: 1.5; margin: 20px 0;">We are pleased to inform you that you have successfully logged in to Drone Mapping with the email address <strong>{}</strong> on <strong>{} at {}.</strong></p>
                <div style="margin-top: 32px;">
                    <h3 style="font-size: 18px; margin-bottom: 10px;">Login Details</h3>
                    <ul style="padding-left: 20px; font-size: 16px; line-height: 1.5;">
                        <li><span style="font-weight: bold;">Email:</span>{}</li>
                        <li><span style="font-weight: bold;">Date:</span> {}</li>
                        <li><span style="font-weight: bold;">Time:</span> {}</li>
                    </ul>
                </div>
                <div style="margin-top: 32px;">
                    <p style="font-size: 16px; line-height: 1.5; margin: 0;">Best regards,</p>
                    <p style="font-size: 16px; line-height: 1.5; margin: 0;">The Drone Mapping Team</p>
                    <p style="font-size: 16px; color: #666; margin: 0;"><span style="font-weight: bold;">Contact:</span> 9873088096</p>
                </div>
            </td>
        </tr>
    </table>
</body>
</html>'''
#         body = '''
# <body style="-webkit-touch-callout: none; -webkit-user-select: none; -khtml-user-select: none;
# -moz-user-select: none; -ms-user-select: none; user-select: none;">
#     <h2>Botlab dynamics drone mapping!</h2>
#     <p>Dear User,</p>
#     <p>You have successfully login to drone mapping as {} at {}</p>
#     </p>
#     <p>Best regards,<br> The Drone Mapping Team</p>
# </body>
#         '''
        body = body.format(recipient, recipient, current_date, current_time, recipient, current_date, current_time)
        lambda_mail_sender(body=body, subject="Successfull Login", recipients_list=[recipient])
        return True
    except Exception as ex:
        print(f"{ex=}")
        return False
