# Calorie-Tracker-App
**AI-Powered Nutrition and Calorie Management**

Welcome to Calorie Tracker App, a Kivy-based mobile application designed to make tracking your daily nutrition and calorie intake effortless and intelligent. This comprehensive app combines cutting-edge AI food recognition technology with traditional manual entry methods to provide accurate calorie tracking for your health and fitness goals.

## Features
- **AI Food Recognition**: Take photos of your meals and get automatic food identification and calorie estimation using advanced machine learning.
- **Manual Food Entry**: Add custom foods with personalized calorie and portion information.
- **USDA Food Database Search**: Access thousands of foods from the official USDA nutrition database with real-time search.
- **Weight Goal Tracking**: Set target weight goals and monitor your progress with current weight tracking.
- **Secure User Accounts**: Create personal accounts with email verification and secure login system.
- **Photo History**: View and manage all your captured food photos with the ability to delete unwanted entries.
- **Dark/Light Theme**: Customize your app experience with toggleable dark and light mode themes.
- **Daily Calorie Limits**: Set personalized daily calorie goals and track your progress in real-time.
- **Food Management**: View, edit, and delete your logged foods with an intuitive interface.

## How to Use

### Setting Up Your Account:
1. Launch the app and click "Sign Up" to create a new account.
2. Enter your email address, username, password, and confirm password.
3. Check your email for a 6-digit verification code.
4. Enter the verification code to activate your account.
5. Log in using your username/email and password.

### Tracking Food with AI Recognition:
1. From the home screen, tap the "Camera" button to access the food recognition feature.
2. Point your camera at the food item you want to track.
3. Tap the capture button to take a photo.
4. Wait for the AI analysis to complete (usually 2-3 seconds).
5. Review the detected food name and estimated calories.
6. The food will be automatically added to your daily calorie count.

### Manual Food Entry:
1. On the home screen, tap "Settings" then select "Add Food Manually".
2. Enter the food name, weight in grams, and calorie count.
3. Tap "Submit" to add the food to your daily tracking.
4. The calories will be instantly added to your daily total.

### Searching the Food Database:
1. Access "Settings" from the home screen and select "Food Search".
2. Type the name of the food you're looking for in the search box.
3. Browse through the results showing food names and calories per 100g.
4. Select the food item that matches what you consumed.

### Managing Your Weight Goals:
1. Tap "Settings" on the home screen and select "Set Weight Goal".
2. Enter your current weight and target weight in kilograms.
3. Save your settings to track your progress over time.

### Setting Daily Calorie Limits:
1. From "Settings", choose "Set Daily Calorie Limit".
2. Enter your desired daily calorie target.
3. Monitor your progress throughout the day on the home screen.

### Viewing Your Food History:
1. Go to the camera screen and tap "View Photos" to see all your captured food images.
2. Review past meals with their detected names and calorie counts.
3. Delete any unwanted photos by tapping the "Delete" button on individual items.

## Setup Requirements

### Environment Configuration
Create a `.env` file in the project root directory with the following variables:

```env
# Email Configuration (for account verification)
SMTP_USERNAME=your_gmail_address@gmail.com
SMTP_PASSWORD=your_gmail_app_password

# Food Recognition API Key
LOGMEAL_API_KEY=your_logmeal_api_key_here

# USDA Nutrition Database API Key
CHOMP_API_KEY=your_usda_fdc_api_key_here
```

### Required API Keys:

**Gmail SMTP Setup (for email verification):**
- Enable 2-factor authentication on your Google account
- Generate an App Password: Google Account → Security → App Passwords
- Use your full Gmail address for `SMTP_USERNAME`
- Use the 16-character app password for `SMTP_PASSWORD`

**LogMeal API (for AI food recognition):**
- Sign up at https://logmeal.es/
- Navigate to your dashboard and copy your API key
- Paste the key as `LOGMEAL_API_KEY`

**USDA Food Data Central API (for nutrition database):**
- Register at https://fdc.nal.usda.gov/api-guide.html
- Request a free API key from the FDC portal
- Enter the key as `CHOMP_API_KEY`

### Installation:
1. Install Python 3.7 or higher
2. Install required packages: `pip install kivy requests python-dotenv email-validator`
3. Configure your `.env` file with the API keys above
4. Run the application: `python main.py`

## Technical Requirements
- Python 3.7+
- Kivy framework
- Active internet connection for API services
- Camera access for food photo recognition
- Email account for verification setup
