from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.properties import StringProperty
import random
import string
import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email_validator import validate_email, EmailNotValidError
from dotenv import load_dotenv

load_dotenv()
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USERNAME = os.getenv('SMTP_USERNAME')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD') 
FROM_EMAIL = os.getenv('SMTP_USERNAME')   

def send_email(to_email, subject, message):
    try:
        validate_email(to_email)

        msg = MIMEMultipart()
        msg['From'] = FROM_EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'plain'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(FROM_EMAIL, to_email, msg.as_string())
        server.quit()

        print(f"Email sent successfully to {to_email}")
    except EmailNotValidError as e:
        print(f"Invalid email address: {e}")
    except Exception as e:
        print(f"Error sending email: {e}")

class SignInScreen(Screen):
    def sign_in(self, *args):
        email = self.ids.email_input.text
        username = self.ids.username_input.text
        password = self.ids.password_input.text
        confirm_password = self.ids.confirm_password_input.text

        if not email or not username or not password or not confirm_password:
            self.show_popup('Error', 'All fields are required')
            return

        if password != confirm_password:
            self.show_popup('Error', 'Passwords do not match')
            return

        verification_code = self.send_verification_code(email)
        self.manager.current = 'verify'
        verify_screen = self.manager.get_screen('verify')
        verify_screen.verification_code = verification_code
        verify_screen.email = email
        verify_screen.username = username
        verify_screen.password = password

    def send_verification_code(self, email):
        verification_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        subject = "Your Verification Code"
        message = f"Your verification code is: {verification_code}"
        send_email(email, subject, message)
        return verification_code

    def show_popup(self, title, message):
        popup = Popup(title=title, content=Label(text=message), size_hint=(0.8, 0.5))
        popup.open()

class LoginScreen(Screen):
    def log_in(self, *args):
        username_email = self.ids.username_email_input.text
        password = self.ids.password_input.text
        
        if not username_email or not password:
            self.show_popup('Error', 'All fields are required')
            return
        
        if self.validate_user(username_email, password):
            self.load_user_settings(username_email)
            self.manager.current = 'home'
        else:
            self.show_popup('Error', 'Invalid username/email or password')
    
    def validate_user(self, username_email, password):
        if os.path.exists('users.json'):
            with open('users.json', 'r') as f:
                data = json.load(f)
        else:
            return False
        
        for user in data.values():
            if (user['username'] == username_email or user['email'] == username_email) and user['password'] == password:
                return True
        return False

    def load_user_settings(self, username_email):
        """Load user settings including food photos"""
        if os.path.exists('users.json'):
            with open('users.json', 'r') as f:
                data = json.load(f)
            
            for username, user_data in data.items():
                if user_data['username'] == username_email or user_data['email'] == username_email:
                    # Load settings
                    home_screen = self.manager.get_screen('home')
                    home_screen.calories_consumed = sum(food['calories'] for food in user_data['settings'].get('foods', []))
                    home_screen.daily_calorie_limit = user_data['settings'].get('daily_calorie_limit', 2000)
                    home_screen.goal_weight = user_data['settings'].get('goal_weight', 70)
                    home_screen.current_weight = user_data['settings'].get('current_weight', 70)
                    home_screen.is_dark_mode = user_data['settings'].get('is_dark_mode', False)
                    home_screen.foods = user_data['settings'].get('foods', [])
                    
                    # Load food photos into camera screen
                    camera_screen = self.manager.get_screen('camera')
                    camera_screen.food_photos = []  # Reset photos list
                    
                    # Load valid photos for this user
                    if 'settings' in user_data and 'food_photos' in user_data['settings']:
                        valid_photos = []
                        for photo in user_data['settings']['food_photos']:
                            if os.path.exists(photo['path']):
                                valid_photos.append(photo)
                        
                        camera_screen.food_photos = valid_photos
                        
                        # Update JSON with valid photos only
                        data[username]['settings']['food_photos'] = valid_photos
                        with open('users.json', 'w') as f:
                            json.dump(data, f)
                    break

    def show_popup(self, title, message):
        popup = Popup(title=title, content=Label(text=message), size_hint=(0.8, 0.5))
        popup.open()

class DeleteAccountScreen(Screen):
    def confirm_delete_account(self):
        username_email = self.ids.username_email_input.text
        password = self.ids.password_input.text

        if not username_email or not password:
            self.show_popup('Error', 'Username/Email and Password are required')
            return

        if os.path.exists('users.json'):
            with open('users.json', 'r') as f:
                data = json.load(f)

            user_found = False
            for user in list(data.keys()):
                if (data[user]['username'] == username_email or data[user]['email'] == username_email) and data[user]['password'] == password:
                    user_found = True
                    break

            if user_found:
                confirm_popup = ConfirmDeletePopup(delete_account_callback=self.delete_account)
                confirm_popup.open()
            else:
                self.show_popup('Error', 'Invalid Username/Email or Password')
        else:
            self.show_popup('Error', 'No accounts found')

    def delete_account(self):
        username_email = self.ids.username_email_input.text
        password = self.ids.password_input.text

        with open('users.json', 'r') as f:
            data = json.load(f)

        for user in list(data.keys()):
            if (data[user]['username'] == username_email or data[user]['email'] == username_email) and data[user]['password'] == password:
                del data[user]
                break

        with open('users.json', 'w') as f:
            json.dump(data, f)
        self.show_popup('Success', 'Account deleted successfully')

    def show_popup(self, title, message):
        popup = Popup(title=title, content=Label(text=message), size_hint=(0.8, 0.5))
        popup.open()

class ConfirmDeletePopup(Popup):
    def __init__(self, delete_account_callback, **kwargs):
        super().__init__(**kwargs)
        self.delete_account_callback = delete_account_callback

    def delete_account(self):
        self.delete_account_callback()
        self.dismiss()

class VerifyScreen(Screen):
    verification_code = StringProperty('')
    email = StringProperty('')
    username = StringProperty('')
    password = StringProperty('')

    def verify(self, *args):
        input_code = self.ids.verification_code_input.text
        if input_code == self.verification_code:
            self.save_user(self.email, self.username, self.password)
            self.manager.current = 'login'
        else:
            self.show_popup('Error', 'Invalid verification code')

    def save_user(self, email, username, password):
        user_data = {
            'email': email,
            'username': username,
            'password': password,
            'settings': {
                'goal_weight': 80,
                'current_weight': 100,
                'daily_calorie_limit': 2000,
                'is_dark_mode': False,
                'foods': []
            }
        }
        if os.path.exists('users.json'):
            with open('users.json', 'r') as f:
                data = json.load(f)
        else:
            data = {}

        data[username] = user_data

        with open('users.json', 'w') as f:
            json.dump(data, f)

    def show_popup(self, title, message):
        popup = Popup(title=title, content=Label(text=message), size_hint=(0.8, 0.5))
        popup.open()