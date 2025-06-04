from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.properties import (
    StringProperty,
    NumericProperty,
    BooleanProperty,
    ListProperty,
    ObjectProperty,
)
from kivy.uix.camera import Camera
import json
import os
from dotenv import load_dotenv
import requests
from kivy.clock import Clock
import time
from kivy.uix.scrollview import ScrollView 
from kivy.core.window import Window
from login import SignInScreen, VerifyScreen, LoginScreen, DeleteAccountScreen
from kivy.uix.image import Image
import requests

load_dotenv()

API_KEY = os.getenv('CHOMP_API_KEY')

class WelcomeScreen(Screen):
    pass

class HomeScreen(Screen):
    calories_consumed = NumericProperty(0)
    daily_calorie_limit = NumericProperty(2000)
    goal_weight = NumericProperty(70)
    current_weight = NumericProperty(70)
    is_dark_mode = BooleanProperty(False)
    foods = ListProperty([])

    bg_color = ListProperty([1, 1, 1, 1])
    text_color = ListProperty([0, 0, 0, 1])
    button_bg_color = ListProperty([0.9, 0.9, 0.9, 1])
    button_text_color = ListProperty([0, 0, 0, 1])

    def __init__(self, **kwargs):
        super(HomeScreen, self).__init__(**kwargs)
        self.bind(is_dark_mode=self.on_is_dark_mode)

    def on_is_dark_mode(self, instance, value):
        if value:
            self.bg_color = [0.1, 0.1, 0.1, 1]
            self.text_color = [1, 1, 1, 1]
            self.button_bg_color = [0.2, 0.2, 0.2, 1]
            self.button_text_color = [1, 1, 1, 1]
        else:
            self.bg_color = [1, 1, 1, 1]
            self.text_color = [0, 0, 0, 1]
            self.button_bg_color = [0.9, 0.9, 0.9, 1]
            self.button_text_color = [0, 0, 0, 1]
        self.save_user_settings() 

    def load_settings(self):
        username = self.manager.get_screen('login').ids.username_email_input.text
        if os.path.exists('users.json'):
            with open('users.json', 'r') as f:
                data = json.load(f)
                if username in data and 'settings' in data[username]:
                    settings = data[username]['settings']
                    self.goal_weight = settings.get('goal_weight', 70)
                    self.current_weight = settings.get('current_weight', 70)
                    self.daily_calorie_limit = settings.get('daily_calorie_limit', 2000)
                    self.is_dark_mode = settings.get('is_dark_mode', False)
                    self.foods = settings.get('foods', [])
                    self.calories_consumed = sum(item['calories'] for item in self.foods)
        else:
            self.goal_weight = 70
            self.current_weight = 70
            self.daily_calorie_limit = 2000
            self.is_dark_mode = False
            self.foods = []
            self.calories_consumed = 0

    def on_enter(self):
        if self.manager.previous == 'login':
            self.load_settings()

    def open_daily_limit_popup(self):
        content = DailyLimitPopup()
        popup = Popup(title='Set Daily Calorie Limit', content=content)
        content.popup = popup
        popup.open()

    def open_weight_goal_popup(self):
        content = WeightGoalPopup()
        popup = Popup(title='Set Weight Goal', content=content)
        content.popup = popup 
        popup.open()

    def update_daily_calorie_limit(self, daily_calorie_limit):
        self.daily_calorie_limit = daily_calorie_limit
        self.save_user_settings() 

    def add_food(self, food, grams, calories):
        for existing_food in self.foods:
            if (existing_food['food'] == food and 
                existing_food['grams'] == grams and 
                existing_food['calories'] == calories):
                return
    
        self.foods.insert(0, {'food': food, 'grams': grams, 'calories': calories})
        self.calories_consumed += calories
        self.save_user_settings()

    def update_calories_text(self):
        self.calories_text = f"{self.calories_consumed} calories / {self.daily_calorie_limit}"

    def update_goal_weight(self, goal_weight):
        self.goal_weight = goal_weight
        self.save_user_settings()

    def update_current_weight(self, current_weight):
        self.current_weight = current_weight
        self.save_user_settings()

    def update_weight_texts(self):
        self.current_weight_text = f"Current Weight: {self.current_weight} kg"
        self.goal_weight_text = f"Goal Weight: {self.goal_weight} kg"

    def show_daily_limit_popup(self, instance):
        content = DailyLimitPopup()
        popup = Popup(title="Set Daily Calorie Limit", content=content, size_hint=(0.8, 0.5))
        content.popup = popup 
        popup.open()

    def toggle_dark_mode(self):
        self.is_dark_mode = not self.is_dark_mode
        self.save_user_settings()

    def show_my_food_list(self, instance):
        self.food_list_popup = Popup(
            title="List of My Foods",
            size_hint=(0.9, 0.8),
            content=self.create_food_list_layout()
        )
        self.food_list_popup.open()

    def create_food_list_layout(self):
        main_layout = BoxLayout(orientation="vertical", spacing=5, padding=5)
    
        scroll_layout = BoxLayout(orientation="vertical", spacing=5, size_hint_y=None)
        scroll_layout.bind(minimum_height=scroll_layout.setter('height'))
    
        for index, food in enumerate(self.foods):
            food_item_layout = BoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                height='40dp'
            )
        
            food_label = Label(
                text=f"{food['food']}: {food['grams']}g, {food['calories']} calories",
                size_hint_x=0.8
            )
        
            delete_button = Button(
                text="Delete",
                size_hint_x=0.2,
                size_hint_y=None,
                height='30dp',
                background_color=(1, 0.3, 0.3, 1)
            )

            delete_button.bind(on_release=lambda btn, idx=index: self.delete_food_item(idx))
        
            food_item_layout.add_widget(food_label)
            food_item_layout.add_widget(delete_button)
        
            scroll_layout.add_widget(food_item_layout)
    
        scroll_view = ScrollView(size_hint=(1, 1))
        scroll_view.add_widget(scroll_layout)
    
        main_layout.add_widget(scroll_view)
    
        back_button = Button(
            text="Back",
            size_hint_y=None,
            height='40dp',
            background_color=(0.3, 0.3, 0.3, 1) 
        )
        back_button.bind(on_release=lambda btn: self.food_list_popup.dismiss())
    
        main_layout.add_widget(back_button)
    
        return main_layout

    def delete_food_item(self, index):
        username = self.manager.get_screen('login').ids.username_email_input.text
    
        if os.path.exists('users.json'):
            with open('users.json', 'r') as f:
                data = json.load(f)
        
            if username in data:
                if 0 <= index < len(self.foods):
                    self.calories_consumed -= self.foods[index]['calories']
                    self.foods.pop(index)
                    data[username]['settings']['foods'] = self.foods
                
                    with open('users.json', 'w') as f:
                        json.dump(data, f)
                    
                    self.food_list_popup.content = self.create_food_list_layout()

    def save_user_settings(self):
        username = self.manager.get_screen('login').ids.username_email_input.text
    
        with open('users.json', 'r') as f:
            data = json.load(f)
    
        if username in data:
            data[username]['settings'] = {
                'goal_weight': self.goal_weight,
                'current_weight': self.current_weight,
                'daily_calorie_limit': self.daily_calorie_limit,
                'is_dark_mode': self.is_dark_mode,
                'foods': self.foods 
            }
        
            with open('users.json', 'w') as f:
                json.dump(data, f)


    def fetch_food_list(self):
        url = f'https://api.nal.usda.gov/fdc/v1/foods/list?api_key={API_KEY}'
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            food_list = []
            for item in data:
                calories = 'N/A'
                if item['foodNutrients']:
                    for nutrient in item['foodNutrients']:
                        if 'value' in nutrient:
                            calories = nutrient['value']
                            break
                food_list.append({
                    'food_name': item['description'],
                    'calories': calories,
                    'grams': item['servingSize'] if 'servingSize' in item else 'N/A'
                })
            return food_list
        except requests.exceptions.RequestException as e:
            print(f"Error fetching food list: {e}")
            return None
        
    def show_food_list(self, instance):
        main_layout = BoxLayout(orientation="vertical", spacing=10, padding=10)
    
        search_box = TextInput(
            hint_text='Search foods...',
            size_hint_y=None,
            height='40dp',
            multiline=False
        )
    
        results_layout = BoxLayout(orientation="vertical", spacing=5, size_hint_y=None)
        results_layout.bind(minimum_height=results_layout.setter('height'))
    
        scroll_view = ScrollView(size_hint=(1, 1))
        scroll_view.add_widget(results_layout)
    
        def search_foods(instance, value):
            results_layout.clear_widgets()

            if len(value) < 2:
                return
        
            url = f'https://api.nal.usda.gov/fdc/v1/foods/search?api_key={API_KEY}&query={value}'
            try:
                response = requests.get(url)
                response.raise_for_status()
                data = response.json()
            
                # Create a set to track unique food descriptions
                seen_foods = set()
        
                if 'foods' in data:
                    for food in data['foods']:
                        # Only process this food if we haven't seen its description before
                        if food['description'] not in seen_foods:
                            calories = 'N/A'
                            for nutrient in food.get('foodNutrients', []):
                                if nutrient.get('nutrientName') == 'Energy' and nutrient.get('unitName') == 'KCAL':
                                    calories = f"{nutrient.get('value', 'N/A'):.1f}"
                                    break
                    
                            food_label = Label(
                                text=f"{food['description']}: {calories} kcal/100g",
                                size_hint_y=None,
                                height='40dp',
                                text_size=(scroll_view.width - 20, None),
                                halign='left',
                                valign='middle'
                            )
                            results_layout.add_widget(food_label)
                        
                            # Add this food's description to our set of seen foods
                            seen_foods.add(food['description'])
            
                if not results_layout.children:
                    results_layout.add_widget(
                        Label(
                            text="No results found",
                            size_hint_y=None,
                            height='40dp'
                        )
                    )
                
            except requests.exceptions.RequestException as e:
                results_layout.add_widget(
                    Label(
                        text=f"Error fetching data: {str(e)}",
                        size_hint_y=None,
                        height='40dp'
                    )
                )
    
        search_box.bind(text=search_foods)
    
        main_layout.add_widget(search_box)
        main_layout.add_widget(scroll_view)
    
        popup = Popup(
            title="Search Foods",
            content=main_layout,
            size_hint=(0.9, 0.9)
        )
        popup.open()

    def fetch_food_data(self, food_name):
        url = f'https://api.nal.usda.gov/fdc/v1/foods/list?api_key={API_KEY}'
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            if data['items']:
                food_item = data['items'][0]
                return {
                    'food_name': food_item['name'],
                    'calories': food_item['calories'],
                    'grams': food_item['serving_size']
                }
        except requests.exceptions.RequestException as e:
            print(f"Error fetching food data: {e}")
        return None

    def show_food_input(self, *args):
        content = FoodInputPopup()
        popup = Popup(title="Add Food", content=content, size_hint=(0.8, 0.5))
        content.popup = popup

        def on_submit(instance):
            food = content.ids.food_input.text
            grams = int(content.ids.grams_input.text)
            calories = int(content.ids.calories_input.text)
            self.add_food(food, grams, calories)
            self.save_user_settings()
            popup.dismiss()

        content.ids.submit_button.bind(on_release=on_submit)
        popup.open()

    def go_to_camera(self, *args):
        self.manager.current = 'camera'

    def show_weight_goal(self, *args):
        content = WeightGoalPopup()
        popup = Popup(title="Set Weight Goal", content=content, size_hint=(0.8, 0.5))
        content.popup = popup

        def on_submit(instance):
            current_weight = int(content.ids.current_weight_input.text)
            goal_weight = int(content.ids.goal_weight_input.text)
            self.update_current_weight(current_weight)
            self.update_goal_weight(goal_weight)
            self.save_user_settings()
            popup.dismiss()

        content.submit = on_submit
        popup.open()

    def show_settings(self, *args):
        settings_layout = GridLayout(cols=1, spacing=10, padding=10, size_hint=(1, 1))
    
        daily_limit_button = Button(
            text="Set Daily Calorie Limit",
            size_hint=(1, None),
            height='48dp'
        )
        daily_limit_button.bind(on_release=self.show_daily_limit_popup)
    
        toggle_theme_button = Button(
            text="Toggle Dark Mode",
            size_hint=(1, None),
            height='48dp'
        )
        toggle_theme_button.bind(on_release=lambda x: setattr(self, 'is_dark_mode', not self.is_dark_mode))
    
        food_list_button = Button(
            text="Food Search",
            size_hint=(1, None),
            height='48dp'
        )
        food_list_button.bind(on_release=self.show_food_list)
    
        my_foods_button = Button(
            text="My Foods",
            size_hint=(1, None),
            height='48dp'
        )
        my_foods_button.bind(on_release=self.show_my_food_list)
    
        settings_layout.add_widget(daily_limit_button)
        settings_layout.add_widget(toggle_theme_button)
        settings_layout.add_widget(food_list_button)
        settings_layout.add_widget(my_foods_button)
    
        popup = Popup(
            title='Settings',
            content=settings_layout,
            size_hint=(0.9, None),  
            height='300dp',
            auto_dismiss=True,
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        popup.open()

# Update FoodHistoryPopup class:

class FoodHistoryPopup(BoxLayout):
    def __init__(self, photos, on_delete=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = 10
        self.padding = 10
        self.popup = None
        self.on_delete = on_delete
        
        scroll_layout = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        scroll_layout.bind(minimum_height=scroll_layout.setter('height'))
        
        for i, photo in enumerate(photos):
            item = BoxLayout(orientation='vertical', size_hint_y=None, height=450)
            
            image = Image(source=photo['path'], size_hint_y=None, height=300)
            desc = Label(text=f"Food: {photo['food']}\nCalories: {photo['calories']}", 
                        size_hint_y=None, height=100)
            
            # Add delete button
            delete_btn = Button(
                text='Delete Photo',
                size_hint_y=None,
                height=50,
                background_color=(1, 0.3, 0.3, 1)
            )
            delete_btn.bind(on_release=lambda btn, idx=i: self.delete_photo(idx))
            
            item.add_widget(image)
            item.add_widget(desc)
            item.add_widget(delete_btn)
            scroll_layout.add_widget(item)
            
        scroll_view = ScrollView(size_hint=(1, 1))
        scroll_view.add_widget(scroll_layout)
        self.add_widget(scroll_view)
        
        close_button = Button(text='Close', size_hint_y=None, height=50)
        close_button.bind(on_release=self.dismiss_popup)
        self.add_widget(close_button)
    
    def delete_photo(self, index):
        if self.on_delete:
            self.on_delete(index)
            if self.popup:
                self.popup.dismiss()

    def dismiss_popup(self, *args):
        if self.popup:
            self.popup.dismiss()

# Update the CameraScreen class:

class CameraScreen(Screen):
    is_flash_on = BooleanProperty(False)
    camera_ready = BooleanProperty(False)
    flash_button_color = ListProperty([0.3, 0.3, 0.3, 1])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.logmeal_api_key = os.getenv('LOGMEAL_API_KEY')
        self.food_photos = []
        # Create base photos directory
        self.photos_base_dir = 'food_photos'
        if not os.path.exists(self.photos_base_dir):
            os.makedirs(self.photos_base_dir)
        Clock.schedule_once(self.init_camera, 0)

    def get_user_photos_dir(self):
        """Get user-specific photos directory"""
        username = self.manager.get_screen('login').ids.username_email_input.text
        user_dir = os.path.join(self.photos_base_dir, username)
        if not os.path.exists(user_dir):
            os.makedirs(user_dir)
        return user_dir

    def init_camera(self, dt):
        """Initialize camera when screen loads"""
        self.camera_ready = True
        if hasattr(self.ids, 'camera'):
            self.ids.camera.play = True

    def toggle_flash(self, *args):
        """Toggle camera flash"""
        self.is_flash_on = not self.is_flash_on
        self.flash_button_color = [1, 0.8, 0, 1] if self.is_flash_on else [0.3, 0.3, 0.3, 1]
        if hasattr(self.ids, 'camera'):
            try:
                self.ids.camera.flash = 'on' if self.is_flash_on else 'off'
            except:
                pass

    def go_back(self, *args):
        """Return to previous screen"""
        self.manager.current = 'home'

    def analyze_food_image(self, image_path):
        """Analyze food image using LogMeal API and USDA API"""
        url = 'https://api.logmeal.es/v2/recognition/complete'
        headers = {'Authorization': f'Bearer {self.logmeal_api_key}'}
        
        try:
            if not os.path.exists(image_path):
                print(f"Image file not found: {image_path}")
                return None
                
            # Get food name from LogMeal
            with open(image_path, 'rb') as img:
                files = {'image': ('image.jpg', img, 'image/jpeg')}
                response = requests.post(url, headers=headers, files=files)
                print(f"API Response: {response.text}")  # Debug print
                
                if response.status_code == 200:
                    data = response.json()
                    if 'recognition_results' in data and data['recognition_results']:
                        # Get the top result
                        top_result = data['recognition_results'][0]
                        food_name = top_result['name']
                        
                        # Get food type for better estimation
                        food_type = None
                        if 'foodType' in data and data['foodType']:
                            food_type = data['foodType'][0]['name']
                        
                        # Set serving size based on food type
                        serving_sizes = {
                            'drinks': 330,     # ml for drinks
                            'snacks': 50,      # g for snacks
                            'meals': 300,      # g for meals
                            'default': 100     # g default
                        }
                        
                        serving_size = serving_sizes.get(food_type, serving_sizes['default'])
                        
                        # Estimate calories based on food type and name
                        if 'drinks' in food_type or 'energydrink' in food_name.lower():
                            calories_per_100 = 45  # Average energy drink calories per 100ml
                            total_calories = int((calories_per_100 * serving_size) / 100)
                        else:
                            # Query USDA for calories
                            usda_url = f'https://api.nal.usda.gov/fdc/v1/foods/search?api_key={API_KEY}&query={food_name}'
                            usda_response = requests.get(usda_url)
                            
                            if usda_response.status_code == 200:
                                usda_data = usda_response.json()
                                if 'foods' in usda_data and usda_data['foods']:
                                    food = usda_data['foods'][0]
                                    for nutrient in food.get('foodNutrients', []):
                                        if nutrient.get('nutrientName') == 'Energy':
                                            calories_per_100 = nutrient.get('value', 100)
                                            total_calories = int((calories_per_100 * serving_size) / 100)
                                            break
                                else:
                                    total_calories = 200  # Default calories if no USDA data
                            else:
                                total_calories = 200  # Default calories if USDA API fails
                        
                        return {
                            'food': food_name,
                            'grams': serving_size,
                            'calories': total_calories,
                            'path': image_path
                        }
                
                print(f"API Error: {response.status_code}")
                return None
                    
        except Exception as e:
            print(f"Error analyzing image: {str(e)}")
            return None

    def on_enter(self):
        """Load user's food photos when screen is entered"""
        username = self.manager.get_screen('login').ids.username_email_input.text
        
        # Reset food_photos list
        self.food_photos = []
        
        # Create user directory if it doesn't exist
        user_photos_dir = self.get_user_photos_dir()
        
        if os.path.exists('users.json'):
            with open('users.json', 'r') as f:
                data = json.load(f)
            
            # Find the correct user
            for user_id, user_data in data.items():
                if user_data['username'] == username:
                    if 'settings' in user_data and 'food_photos' in user_data['settings']:
                        stored_photos = user_data['settings']['food_photos']
                        
                        # Verify photos exist and use absolute paths
                        valid_photos = []
                        for photo in stored_photos:
                            photo_path = os.path.abspath(photo['path'])
                            if os.path.exists(photo_path):
                                photo['path'] = photo_path
                                valid_photos.append(photo)
                        
                        # Update instance photos list
                        self.food_photos = valid_photos
                        
                        # Update storage with valid photos
                        user_data['settings']['food_photos'] = valid_photos
                        with open('users.json', 'w') as f:
                            json.dump(data, f)
                    break

    def capture(self):
        """Capture and analyze photo"""
        if not self.camera_ready:
            return
                
        try:
            camera = self.ids.camera
            timestr = time.strftime("%Y%m%d_%H%M%S")
            username = self.manager.get_screen('login').ids.username_email_input.text
            
            # Get user-specific directory
            user_photos_dir = self.get_user_photos_dir()
            photo_filename = f"food_photo_{timestr}.jpg"
            photo_path = os.path.join(user_photos_dir, photo_filename)
            abs_photo_path = os.path.abspath(photo_path)
            
            # Take photo
            camera.export_to_png(photo_path)
            
            if not os.path.exists(abs_photo_path):
                raise Exception("Failed to save photo")
                
            loading_popup = Popup(
                title='Analyzing Food',
                content=Label(text='Please wait while we analyze your food...'),
                size_hint=(None, None), 
                size=(450, 250)
            )
            loading_popup.open()
            
            result = self.analyze_food_image(abs_photo_path)
            loading_popup.dismiss()
            
            if result:
                # Update result with absolute path
                result['path'] = abs_photo_path
                
                # Load and update user data
                if os.path.exists('users.json'):
                    with open('users.json', 'r') as f:
                        data = json.load(f)
                    
                    # Initialize user settings if needed
                    if username not in data:
                        data[username] = {'settings': {}}
                    if 'settings' not in data[username]:
                        data[username]['settings'] = {}
                    if 'food_photos' not in data[username]['settings']:
                        data[username]['settings']['food_photos'] = []
                    
                    # Add new photo to user's photos
                    data[username]['settings']['food_photos'].insert(0, result)
                    
                    # Save updated data
                    with open('users.json', 'w') as f:
                        json.dump(data, f)
                    
                    # Update current session
                    self.food_photos.insert(0, result)
                    
                    # Update home screen
                    home_screen = App.get_running_app().root.get_screen('home')
                    home_screen.add_food(result['food'], result['grams'], result['calories'])
                
                popup = Popup(
                    title='Food Analyzed',
                    content=Label(text=f"Detected: {result['food']}\nEstimated calories: {result['calories']}"),
                    size_hint=(None, None),
                    size=(400, 200)
                )
            else:
                popup = Popup(
                    title='Analysis Failed',
                    content=Label(text='Could not analyze the food in this image. Please try again.'),
                    size_hint=(None, None),
                    size=(450, 250)
                )
            popup.open()
            Clock.schedule_once(lambda dt: popup.dismiss(), 3)
        
        except Exception as e:
            print(f"Error in capture: {str(e)}")
            error_popup = Popup(
                title='Error',
                content=Label(text=f'Failed to process photo: {str(e)}'),
                size_hint=(None, None),
                size=(400, 200)
            )
            error_popup.open()
            Clock.schedule_once(lambda dt: error_popup.dismiss(), 2)

    def view_photos(self):
        """View saved photos for the user"""
        if not self.food_photos:
            popup = Popup(
                title='No Photos',
                content=Label(text='No photos found for this user.'),
                size_hint=(None, None),
                size=(400, 200)
            )
            popup.open()
            return

        content = FoodHistoryPopup(self.food_photos, on_delete=self.delete_photo)
        popup = Popup(title='Saved Photos', content=content, size_hint=(0.9, 0.9))
        content.popup = popup
        popup.open()

    def delete_photo(self, index):
        """Delete a photo from the user's saved photos"""
        username = self.manager.get_screen('login').ids.username_email_input.text

        if os.path.exists('users.json'):
            with open('users.json', 'r') as f:
                data = json.load(f)

            if username in data:
                if 0 <= index < len(self.food_photos):
                    photo_path = self.food_photos[index]['path']
                    if os.path.exists(photo_path):
                        os.remove(photo_path)
                    self.food_photos.pop(index)
                    data[username]['settings']['food_photos'] = self.food_photos

                    with open('users.json', 'w') as f:
                        json.dump(data, f)

                    # Refresh the photo view
                    self.view_photos()

class FoodInputPopup(BoxLayout):
    popup = ObjectProperty(None)

    def submit(self):
        food_name = self.ids.food_input.text
        grams = self.ids.grams_input.text
        calories = self.ids.calories_input.text
        
        if not food_name or not grams or not calories:
            self.show_error_popup("All fields are required")
            return
            
        try:
            grams = int(grams)
            calories = int(calories)
            if grams <= 0 or calories <= 0:
                self.show_error_popup("Grams and calories must be positive numbers")
                return
            App.get_running_app().root.get_screen('home').add_food(food_name, grams, calories)
            self.popup.dismiss()
        except ValueError:
            self.show_error_popup("Grams and calories must be valid numbers")
    
    def show_error_popup(self, message):
        error_popup = Popup(
            title='Error',
            content=Label(text=message),
            size_hint=(None, None),
            size=(400, 200)
        )
        error_popup.open()

class WeightGoalPopup(BoxLayout):
    popup = ObjectProperty(None)

    def submit(self, instance=None):
        current_weight = self.ids.current_weight_input.text
        goal_weight = self.ids.goal_weight_input.text
    
        if not current_weight or not goal_weight:
            self.show_error_popup("All fields are required")
            return
            
        try:
            current_weight = int(current_weight)
            goal_weight = int(goal_weight)
            if current_weight <= 0 or goal_weight <= 0:
                self.show_error_popup("Weights must be positive numbers")
                return
            home_screen = App.get_running_app().root.get_screen('home')
            home_screen.update_current_weight(current_weight)
            home_screen.update_goal_weight(goal_weight)
            home_screen.save_user_settings()
            self.popup.dismiss()
        except ValueError:
            self.show_error_popup("Weights must be valid numbers")
    
    def show_error_popup(self, message):
        error_popup = Popup(
            title='Error',
            content=Label(text=message),
            size_hint=(None, None),
            size=(400, 200)
        )
        error_popup.open()

class DailyLimitPopup(BoxLayout):
    popup = ObjectProperty(None)

    def submit(self):
        new_limit = self.ids.daily_limit_input.text
        if new_limit.isdigit():
            App.get_running_app().root.get_screen('home').update_daily_calorie_limit(int(new_limit))
        self.popup.dismiss()

class CalorieTrackerApp(App):
    def build(self):
        Builder.load_file('design.kv')
        
        sm = ScreenManager()
        sm.add_widget(WelcomeScreen(name='welcome'))
        sm.add_widget(SignInScreen(name='sign_in'))
        sm.add_widget(VerifyScreen(name='verify'))
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(CameraScreen(name='camera'))
        sm.add_widget(DeleteAccountScreen(name='delete_account'))
        return sm

if __name__ == "__main__":
    CalorieTrackerApp().run()