import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from decouple import config
import logging

logger = logging.getLogger(__name__)

def send_otp_email(email, otp_code):
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = config('BREVO_API_KEY')

    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
    
    sender_email = config('BREVO_SENDER_EMAIL')
    sender_name = config('BREVO_SENDER_NAME', default='DocZen')

    subject = f"{otp_code} is your DocZen verification code"
    html_content = f"""
    <html>
        <body>
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e1e1e1; border-radius: 10px;">
                <h2 style="color: #2D3FE3; text-align: center;">DocZen Verification</h2>
                <p>Hello,</p>
                <p>Use the following code to verify your identity. This code will expire in 5 minutes.</p>
                <div style="text-align: center; margin: 30px 0;">
                    <span style="font-size: 32px; font-weight: bold; letter-spacing: 5px; color: #2D3FE3; background: #f0f2ff; padding: 10px 20px; border-radius: 5px;">{otp_code}</span>
                </div>
                <p>If you didn't request this code, please ignore this email.</p>
                <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">
                <p style="font-size: 12px; color: #888; text-align: center;">&copy; 2024 DocZen. All rights reserved.</p>
            </div>
        </body>
    </html>
    """

    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": email}],
        html_content=html_content,
        sender={"email": sender_email, "name": sender_name},
        subject=subject
    )

    try:
        api_response = api_instance.send_transac_email(send_smtp_email)
        logger.info(f"OTP email sent successfully to {email}. Message ID: {api_response.message_id}")
        return True
    except ApiException as e:
        logger.error(f"Exception when calling TransactionalEmailsApi->send_transac_email: {e}")
        return False
