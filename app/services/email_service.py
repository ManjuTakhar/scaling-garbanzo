import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.username = settings.SMTP_USERNAME
        self.password = settings.SMTP_PASSWORD
        self.from_email = settings.FROM_EMAIL

    def send_workspace_invitation_email(
        self, 
        to_email: str, 
        workspace_name: str, 
        inviter_name: str, 
        magic_link: str,
        role: str = "Member"
    ) -> bool:
        """Send workspace invitation email with magic link"""
        try:
            # Check if email configuration is set up
            if not self.username or not self.password:
                logger.error("Email configuration not set up. Please configure SMTP_USERNAME and SMTP_PASSWORD in .env file")
                return False
            
            logger.info(f"Attempting to send invitation email to {to_email}")
            logger.info(f"SMTP Server: {self.smtp_server}:{self.smtp_port}")
            logger.info(f"From Email: {self.from_email}")
            
            # Create message
            message = MIMEMultipart()
            message["From"] = self.from_email
            message["To"] = to_email
            message["Subject"] = f"You're invited to join {workspace_name} on Synchrone AI"

            # Create email body
            body = self._get_invitation_email_body(workspace_name, inviter_name, magic_link, role)
            message.attach(MIMEText(body, "html"))

            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                text = message.as_string()
                server.sendmail(self.from_email, to_email, text)
            
            logger.info(f"✅ Workspace invitation email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send workspace invitation email to {to_email}: {str(e)}")
            logger.error(f"Error type: {type(e).__name__}")
            return False

    def send_magic_link_login_email(self, to_email: str, magic_link: str) -> bool:
        """Send magic link login email"""
        try:
            # Check if email configuration is set up
            if not self.username or not self.password:
                logger.error("Email configuration not set up. Please configure SMTP_USERNAME and SMTP_PASSWORD in .env file")
                return False
            
            logger.info(f"Attempting to send magic link login email to {to_email}")
            
            # Create message
            message = MIMEMultipart()
            message["From"] = self.from_email
            message["To"] = to_email
            message["Subject"] = "Your Synchrone AI Login Link"

            # Create email body
            body = self._get_magic_link_login_email_body(magic_link)
            message.attach(MIMEText(body, "html"))

            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                text = message.as_string()
                server.sendmail(self.from_email, to_email, text)
            
            logger.info(f"✅ Magic link login email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send magic link login email to {to_email}: {str(e)}")
            return False

    def send_magic_link_signup_email(self, to_email: str, magic_link: str) -> bool:
        """Send magic link signup email"""
        try:
            # Check if email configuration is set up
            if not self.username or not self.password:
                logger.error("Email configuration not set up. Please configure SMTP_USERNAME and SMTP_PASSWORD in .env file")
                return False
            
            logger.info(f"Attempting to send magic link signup email to {to_email}")
            
            # Create message
            message = MIMEMultipart()
            message["From"] = self.from_email
            message["To"] = to_email
            message["Subject"] = "Complete Your Synchrone AI Registration"

            # Create email body
            body = self._get_magic_link_signup_email_body(magic_link)
            message.attach(MIMEText(body, "html"))

            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                text = message.as_string()
                server.sendmail(self.from_email, to_email, text)
            
            logger.info(f"✅ Magic link signup email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send magic link signup email to {to_email}: {str(e)}")
            return False

    def send_magic_link_generic_email(self, to_email: str, magic_link: str, purpose: str) -> bool:
        """Send generic magic link email"""
        try:
            # Check if email configuration is set up
            if not self.username or not self.password:
                logger.error("Email configuration not set up. Please configure SMTP_USERNAME and SMTP_PASSWORD in .env file")
                return False
            
            logger.info(f"Attempting to send magic link {purpose} email to {to_email}")
            
            # Create message
            message = MIMEMultipart()
            message["From"] = self.from_email
            message["To"] = to_email
            message["Subject"] = f"Your Synchrone AI {purpose.title()} Link"

            # Create email body
            body = self._get_magic_link_generic_email_body(magic_link, purpose)
            message.attach(MIMEText(body, "html"))

            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                text = message.as_string()
                server.sendmail(self.from_email, to_email, text)
            
            logger.info(f"✅ Magic link {purpose} email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send magic link {purpose} email to {to_email}: {str(e)}")
            return False

    def send_otp_email(self, to_email: str, otp_code: str, purpose: str) -> bool:
        """Send OTP email to the user"""
        try:
            # Create message
            message = MIMEMultipart()
            message["From"] = self.from_email
            message["To"] = to_email
            message["Subject"] = self._get_subject(purpose)

            # Create email body
            body = self._get_email_body(otp_code, purpose)
            message.attach(MIMEText(body, "html"))

            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                text = message.as_string()
                server.sendmail(self.from_email, to_email, text)
            
            logger.info(f"OTP email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send OTP email to {to_email}: {str(e)}")
            return False

    def _get_magic_link_login_email_body(self, magic_link: str) -> str:
        """Generate magic link login email body HTML"""
        return f"""
        <html>
            <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f4;">
                <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                    <div style="text-align: center; margin-bottom: 30px;">
                        <h1 style="color: #333; margin-bottom: 10px;">Welcome Back!</h1>
                        <p style="color: #666; font-size: 16px;">Click the link below to securely log into your Synchrone AI account</p>
                    </div>
                    
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px; text-align: center; margin: 30px 0;">
                        <h2 style="color: white; margin: 0 0 15px 0; font-size: 24px;">Secure Login</h2>
                        <p style="color: white; margin: 0 0 20px 0; opacity: 0.9; font-size: 16px;">
                            No password required - just click the button below
                        </p>
                        <a href="{magic_link}" 
                           style="display: inline-block; background-color: white; color: #667eea; padding: 15px 30px; text-decoration: none; border-radius: 25px; font-weight: bold; font-size: 16px; margin-top: 10px;">
                            Login to Synchrone AI
                        </a>
                    </div>
                    
                    <div style="text-align: center; margin-top: 30px;">
                        <p style="color: #666; font-size: 14px; margin: 0;">This link will expire in 30 minutes for security.</p>
                        <p style="color: #666; font-size: 14px; margin: 10px 0 0 0;">If you didn't request this login link, please ignore this email.</p>
                    </div>
                    
                    <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee;">
                        <p style="color: #999; font-size: 12px; text-align: center; margin: 0;">
                            If the button doesn't work, copy and paste this link into your browser:<br>
                            <a href="{magic_link}" style="color: #667eea; word-break: break-all;">{magic_link}</a>
                        </p>
                    </div>
                </div>
            </body>
        </html>
        """

    def _get_magic_link_signup_email_body(self, magic_link: str) -> str:
        """Generate magic link signup email body HTML"""
        return f"""
        <html>
            <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f4;">
                <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                    <div style="text-align: center; margin-bottom: 30px;">
                        <h1 style="color: #333; margin-bottom: 10px;">Welcome to Synchrone AI!</h1>
                        <p style="color: #666; font-size: 16px;">Complete your registration by clicking the link below</p>
                    </div>
                    
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px; text-align: center; margin: 30px 0;">
                        <h2 style="color: white; margin: 0 0 15px 0; font-size: 24px;">Complete Registration</h2>
                        <p style="color: white; margin: 0 0 20px 0; opacity: 0.9; font-size: 16px;">
                            You're almost ready to start using Synchrone AI
                        </p>
                        <a href="{magic_link}" 
                           style="display: inline-block; background-color: white; color: #667eea; padding: 15px 30px; text-decoration: none; border-radius: 25px; font-weight: bold; font-size: 16px; margin-top: 10px;">
                            Complete Registration
                        </a>
                    </div>
                    
                    <div style="text-align: center; margin-top: 30px;">
                        <p style="color: #666; font-size: 14px; margin: 0;">This link will expire in 30 minutes for security.</p>
                        <p style="color: #666; font-size: 14px; margin: 10px 0 0 0;">If you didn't sign up for Synchrone AI, please ignore this email.</p>
                    </div>
                    
                    <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee;">
                        <p style="color: #999; font-size: 12px; text-align: center; margin: 0;">
                            If the button doesn't work, copy and paste this link into your browser:<br>
                            <a href="{magic_link}" style="color: #667eea; word-break: break-all;">{magic_link}</a>
                        </p>
                    </div>
                </div>
            </body>
        </html>
        """

    def _get_magic_link_generic_email_body(self, magic_link: str, purpose: str) -> str:
        """Generate generic magic link email body HTML"""
        return f"""
        <html>
            <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f4;">
                <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                    <div style="text-align: center; margin-bottom: 30px;">
                        <h1 style="color: #333; margin-bottom: 10px;">Synchrone AI</h1>
                        <p style="color: #666; font-size: 16px;">Click the link below to {purpose}</p>
                    </div>
                    
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px; text-align: center; margin: 30px 0;">
                        <h2 style="color: white; margin: 0 0 15px 0; font-size: 24px;">Secure Access</h2>
                        <p style="color: white; margin: 0 0 20px 0; opacity: 0.9; font-size: 16px;">
                            Click the button below to {purpose}
                        </p>
                        <a href="{magic_link}" 
                           style="display: inline-block; background-color: white; color: #667eea; padding: 15px 30px; text-decoration: none; border-radius: 25px; font-weight: bold; font-size: 16px; margin-top: 10px;">
                            {purpose.title()}
                        </a>
                    </div>
                    
                    <div style="text-align: center; margin-top: 30px;">
                        <p style="color: #666; font-size: 14px; margin: 0;">This link will expire in 30 minutes for security.</p>
                        <p style="color: #666; font-size: 14px; margin: 10px 0 0 0;">If you didn't request this, please ignore this email.</p>
                    </div>
                    
                    <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee;">
                        <p style="color: #999; font-size: 12px; text-align: center; margin: 0;">
                            If the button doesn't work, copy and paste this link into your browser:<br>
                            <a href="{magic_link}" style="color: #667eea; word-break: break-all;">{magic_link}</a>
                        </p>
                    </div>
                </div>
            </body>
        </html>
        """

    def _get_subject(self, purpose: str) -> str:
        """Get email subject based on purpose"""
        subjects = {
            "signup": "Welcome to Synchrone AI - Verify your email",
            "login": "Your Synchrone AI login code",
            "password_reset": "Reset your Synchrone AI password"
        }
        return subjects.get(purpose, "Your verification code")

    def _get_invitation_email_body(self, workspace_name: str, inviter_name: str, magic_link: str, role: str) -> str:
        """Generate workspace invitation email body HTML"""
        return f"""
        <html>
            <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f4;">
                <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                    <div style="text-align: center; margin-bottom: 30px;">
                        <h1 style="color: #333; margin-bottom: 10px;">You're Invited!</h1>
                        <p style="color: #666; font-size: 16px;">Join <strong>{workspace_name}</strong> on Synchrone AI</p>
                    </div>
                    
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px; text-align: center; margin: 30px 0;">
                        <h2 style="color: white; margin: 0 0 15px 0; font-size: 24px;">Welcome to the team!</h2>
                        <p style="color: white; margin: 0 0 20px 0; opacity: 0.9; font-size: 16px;">
                            {inviter_name} has invited you to join <strong>{workspace_name}</strong> as a <strong>{role}</strong>
                        </p>
                        <a href="{magic_link}" 
                           style="display: inline-block; background-color: white; color: #667eea; padding: 15px 30px; text-decoration: none; border-radius: 25px; font-weight: bold; font-size: 16px; margin-top: 10px;">
                            Accept Invitation
                        </a>
                    </div>
                    
                    <div style="text-align: center; margin-top: 30px;">
                        <p style="color: #666; font-size: 14px; margin: 0;">This invitation will expire in 7 days.</p>
                        <p style="color: #666; font-size: 14px; margin: 10px 0 0 0;">If you didn't expect this invitation, you can safely ignore this email.</p>
                    </div>
                    
                    <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee;">
                        <p style="color: #999; font-size: 12px; text-align: center; margin: 0;">
                            If the button doesn't work, copy and paste this link into your browser:<br>
                            <a href="{magic_link}" style="color: #667eea; word-break: break-all;">{magic_link}</a>
                        </p>
                    </div>
                </div>
            </body>
        </html>
        """

    def _get_email_body(self, otp_code: str, purpose: str) -> str:
        """Generate email body HTML"""
        if purpose == "signup":
            return f"""
            <html>
                <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f4;">
                    <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                        <div style="text-align: center; margin-bottom: 30px;">
                            <h1 style="color: #333; margin-bottom: 10px;">Welcome to Synchrone AI</h1>
                            <p style="color: #666; font-size: 16px;">Please verify your email to complete your registration</p>
                        </div>
                        
                        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px; text-align: center; margin: 30px 0;">
                            <h2 style="color: white; margin: 0 0 10px 0; font-size: 32px; letter-spacing: 5px;">{otp_code}</h2>
                            <p style="color: white; margin: 0; opacity: 0.9;">Your verification code</p>
                        </div>
                        
                        <div style="text-align: center; margin-top: 30px;">
                            <p style="color: #666; font-size: 14px; margin: 0;">This code will expire in 10 minutes.</p>
                            <p style="color: #666; font-size: 14px; margin: 10px 0 0 0;">If you didn't request this, please ignore this email.</p>
                        </div>
                    </div>
                </body>
            </html>
            """
        elif purpose == "login":
            return f"""
            <html>
                <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f4;">
                    <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                        <div style="text-align: center; margin-bottom: 30px;">
                            <h1 style="color: #333; margin-bottom: 10px;">Synchrone AI Login</h1>
                            <p style="color: #666; font-size: 16px;">Here's your login verification code</p>
                        </div>
                        
                        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px; text-align: center; margin: 30px 0;">
                            <h2 style="color: white; margin: 0 0 10px 0; font-size: 32px; letter-spacing: 5px;">{otp_code}</h2>
                            <p style="color: white; margin: 0; opacity: 0.9;">Your login code</p>
                        </div>
                        
                        <div style="text-align: center; margin-top: 30px;">
                            <p style="color: #666; font-size: 14px; margin: 0;">This code will expire in 10 minutes.</p>
                            <p style="color: #666; font-size: 14px; margin: 10px 0 0 0;">If you didn't request this, please secure your account immediately.</p>
                        </div>
                    </div>
                </body>
            </html>
            """
        else:
            return f"""
            <html>
                <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f4;">
                    <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                        <div style="text-align: center; margin-bottom: 30px;">
                            <h1 style="color: #333; margin-bottom: 10px;">Verification Code</h1>
                            <p style="color: #666; font-size: 16px;">Your verification code for Synchrone AI</p>
                        </div>
                        
                        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px; text-align: center; margin: 30px 0;">
                            <h2 style="color: white; margin: 0 0 10px 0; font-size: 32px; letter-spacing: 5px;">{otp_code}</h2>
                            <p style="color: white; margin: 0; opacity: 0.9;">Your verification code</p>
                        </div>
                        
                        <div style="text-align: center; margin-top: 30px;">
                            <p style="color: #666; font-size: 14px; margin: 0;">This code will expire in 10 minutes.</p>
                        </div>
                    </div>
                </body>
            </html>
            """

# Create a singleton instance
email_service = EmailService()
