import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from decouple import config
import logging

logger = logging.getLogger(__name__)

def send_otp_email(email, otp_code, username="User"):
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = config('BREVO_API_KEY')

    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
    
    sender_email = config('BREVO_SENDER_EMAIL')
    sender_name = config('BREVO_SENDER_NAME', default='DocZen')

    subject = f"{otp_code} is your DocZen verification code"
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>DocZen Verification</title>
    </head>
    <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f4f7; color: #333;">
        <div style="max-width: 600px; margin: 40px auto; background-color: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.1); border: 1px solid #e1e1e8;">
            <!-- Modern Header with Gradient -->
            <div style="background: linear-gradient(135deg, #030014 0%, #1e1b4b 100%); padding: 40px 20px; text-align: center;">
                <h1 style="margin: 0; color: #ffffff; font-size: 32px; font-weight: 800; letter-spacing: -1px;">
                    Doc<span style="color: #8b5cf6;">Zen</span>
                </h1>
                <p style="margin: 10px 0 0; color: #94a3b8; font-size: 14px; text-transform: uppercase; letter-spacing: 2px;">Identity Verification</p>
            </div>
            
            <div style="padding: 40px 30px;">
                <h2 style="margin: 0 0 20px; color: #1e1b4b; font-size: 24px; font-weight: 700; text-align: center;">Verify Your Account</h2>
                
                <p style="margin: 0 0 30px; color: #475569; font-size: 16px; line-height: 1.6; text-align: center;">
                    Hello <strong>{username}</strong>,<br><br>
                    You are receiving this email because a login request was made for your DocZen account. To ensure your security, please use the 6-digit code below to complete the verification process.
                </p>
                
                <!-- Stylized OTP Box -->
                <div style="background-color: #f8fafc; border: 2px dashed #e2e8f0; border-radius: 12px; padding: 30px; text-align: center; margin-bottom: 30px;">
                    <div style="font-size: 48px; font-weight: 800; color: #8b5cf6; letter-spacing: 15px; text-indent: 15px;">
                        {otp_code}
                    </div>
                    <p style="margin: 15px 0 0; color: #64748b; font-size: 13px; font-weight: 600;">Valid for the next 5 minutes</p>
                </div>
                
                <div style="background-color: #fff7ed; border-left: 4px solid #f59e0b; padding: 15px; border-radius: 4px; margin-bottom: 30px;">
                    <p style="margin: 0; color: #b45309; font-size: 14px; line-height: 1.5;">
                        <strong>Security Reminder:</strong> Never share this code with anyone. If you didn't request this, please secure your account immediately.
                    </p>
                </div>
                
                <p style="margin: 0; color: #64748b; font-size: 15px; line-height: 1.6; text-align: center;">
                    Need help? <a href="#" style="color: #8b5cf6; text-decoration: none; font-weight: 600;">Contact our support team</a>
                </p>
            </div>
            
            <!-- Footer -->
            <div style="background-color: #f8fafc; padding: 30px; text-align: center; border-top: 1px solid #f1f5f9;">
                <p style="margin: 0; color: #94a3b8; font-size: 12px; line-height: 1.5;">
                    &copy; DocZen AI. Empowering your document workflow with artificial intelligence.<br>
                    This is an automated security message, please do not reply.
                </p>
                <div style="margin-top: 15px;">
                    <a href="#" style="color: #8b5cf6; text-decoration: none; font-size: 12px; margin: 0 10px;">Privacy Policy</a>
                    <span style="color: #cbd5e1;">&bull;</span>
                    <a href="#" style="color: #8b5cf6; text-decoration: none; font-size: 12px; margin: 0 10px;">Security Guide</a>
                </div>
            </div>
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
