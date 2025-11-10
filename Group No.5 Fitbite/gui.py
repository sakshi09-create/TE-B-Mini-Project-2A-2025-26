import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import requests
import json
from PIL import Image, ImageTk
import threading
from datetime import datetime, timedelta
import webbrowser
from tkinter import font as tkFont
import math
import ast
import time # Added for chat delay/typing simulation

# Try to import speech recognition libraries
try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False


class FitBiteGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("FitBite - Recipe Recommendation System")
        self.root.geometry("1200x800")
        self.root.resizable(True, True)
        self.root.withdraw() # Hide the main window initially
        
        # Server configuration
        self.server_url = "http://127.0.0.1:5000"
        self.current_user = None
        self.user_favorites = []
        self.current_recipes = []
        self.floating_chat_canvas = None # Initialize chat button attribute
        
        # --- NEW DUAL COLOR SCHEMES ---
        # Dark Mode (Your Existing Theme)
        self.dark_colors = {
            'bg_primary': '#0a0a0a',      # Deep black
            'bg_secondary': '#1a1a1a',    # Dark gray
            'bg_tertiary': '#2a2a2a',     # Medium gray
            'accent_primary': '#00ff88',    # Bright green
            'accent_secondary': '#88ff00', # Lime green
            'text_primary': '#ffffff',      # White
            'text_secondary': '#cccccc',    # Light gray
            'text_muted': '#888888',      # Gray
            'error': '#ff4444',            # Red
            'warning': '#ffaa44',          # Orange
            'success': '#44ff44',          # Green
            'button_hover': '#333333',      # Dark button hover
            'link_hover': '#4a4a4a',        # Lighter gray for links
            'matrix_accent': '#00bfa5'      # Teal/Cyan for matrix boxes
        }

        # Light Mode (New Theme)
        self.light_colors = {
            'bg_primary': '#f0f0f0',      # Light gray background
            'bg_secondary': '#ffffff',    # White card background
            'bg_tertiary': '#e0e0e0',     # Medium light gray input field
            'accent_primary': '#008040',    # Dark Green
            'accent_secondary': '#4caf50', # Medium Green
            'text_primary': '#1a1a1a',      # Dark gray/black text
            'text_secondary': '#555555',    # Medium gray text
            'text_muted': '#aaaaaa',      # Light gray text
            'error': '#cc0000',
            'warning': '#ffaa44',
            'success': '#008000',
            'button_hover': '#e0e0e0',      # Light button hover
            'link_hover': '#f0f0f0',
            'matrix_accent': '#00bcd4'      # Cyan for matrix boxes
        }
        
        self.current_theme = 'dark'
        self.colors = self.dark_colors # Start with dark theme
        self.root.configure(bg=self.colors['bg_primary']) # Set initial root background
        # --- END DUAL COLOR SCHEMES ---
        
        # Custom fonts
        self.setup_fonts()
        
        # Animation variables
        self.animation_running = False
        
        # Initialize GUI
        self.setup_styles()
        self.create_main_frame()
        
        # --- NEW STARTING TRANSITION ADDED HERE ---
        self.show_splash_screen()
        # --- END NEW STARTING TRANSITION ---
        
        # Check server connection
        self.check_server_connection()
        
    def setup_fonts(self):
        """Setup custom fonts for the application"""
        self.fonts = {
            'title': ('Helvetica', 28, 'bold'),
            'subtitle': ('Helvetica', 18, 'bold'),
            'heading': ('Helvetica', 14, 'bold'),
            'body': ('Helvetica', 11),
            'small': ('Helvetica', 9),
            'button': ('Helvetica', 12, 'bold'),
            'link': ('Helvetica', 10),
            'matrix_value': ('Helvetica', 18, 'bold'), # New font for matrix values
            'chat_user': ('Helvetica', 11, 'bold'), # New font for chat
            'chat_bot': ('Helvetica', 11) # New font for chat
        }
        
    # --- START NEW SPLASH SCREEN TRANSITION METHODS ---
    def show_splash_screen(self):
        """Show a temporary splash screen for 3 seconds."""
        
        # Create a Toplevel window for the splash screen
        self.splash_screen = tk.Toplevel(self.root)
        self.splash_screen.overrideredirect(True) # Remove window borders
        self.splash_screen.config(bg=self.colors['bg_primary'])

        # Set splash screen size (e.g., 600x400)
        splash_width = 600
        splash_height = 400
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Center the splash screen
        center_x = int((screen_width / 2) - (splash_width / 2))
        center_y = int((screen_height / 2) - (splash_height / 2))
        
        self.splash_screen.geometry(f'{splash_width}x{splash_height}+{center_x}+{center_y}')

        # Content Frame
        splash_frame = tk.Frame(self.splash_screen, bg=self.colors['bg_primary'])
        splash_frame.pack(expand=True, fill=tk.BOTH)

        # Title Label
        title = tk.Label(splash_frame, text="FitBite", font=('Helvetica', 60, 'bold'),
                         fg=self.colors['accent_primary'], bg=self.colors['bg_primary'])
        title.pack(pady=(80, 10))
        
        # Subtitle Label
        subtitle = tk.Label(splash_frame, text="Your Smart Recipe Assistant", font=self.fonts['subtitle'],
                            fg=self.colors['text_secondary'], bg=self.colors['bg_primary'])
        subtitle.pack()

        # Loading/Transition text
        self.splash_loading_label = tk.Label(splash_frame, text="Fuel Your Taste And Fitness...", font=self.fonts['body'],
                                             fg=self.colors['text_muted'], bg=self.colors['bg_primary'])
        self.splash_loading_label.pack(pady=(40, 0))

        # Start loading text animation
        self.splash_animation_id = self.root.after(500, self.animate_splash_loading)
        
        # Set the transition timeout (3000 ms = 3 seconds)
        self.root.after(3000, self.finish_splash_screen)

    def animate_splash_loading(self):
        """Animate loading text on the splash screen"""
        if hasattr(self, 'splash_loading_label') and self.splash_loading_label.winfo_exists():
            current_text = self.splash_loading_label.cget('text')
            base_text = current_text.split('.')[0]
            dots = (current_text.count('.') + 1) % 4
            self.splash_loading_label.config(text=f"{base_text}{'.' * dots}")
            self.splash_animation_id = self.root.after(500, self.animate_splash_loading)

    def finish_splash_screen(self):
        """Destroys the splash screen and shows the main login screen."""
        if hasattr(self, 'splash_animation_id'):
            self.root.after_cancel(self.splash_animation_id)
            
        if hasattr(self, 'splash_screen') and self.splash_screen.winfo_exists():
            self.splash_screen.destroy()
            
        self.root.deiconify() # Show the main window
        self.show_login_screen()

    # --- END NEW SPLASH SCREEN TRANSITION METHODS ---


    # --- NEW THEME TOGGLE METHODS ---
    def toggle_theme(self):
        """Switches between dark and light themes and re-applies styles."""
        if self.current_theme == 'dark':
            self.current_theme = 'light'
            self.colors = self.light_colors
        else:
            self.current_theme = 'dark'
            self.colors = self.dark_colors
            
        # Re-apply all styles and recolor existing widgets
        self.setup_styles()
        self.recursive_recolor(self.root)
        
        # Manually update specific theme-dependent widgets (e.g., theme button text)
        if hasattr(self, 'theme_button'):
             theme_text = "🌙 Night Mode" if self.current_theme == 'light' else "☀️ Day Mode"
             self.theme_button.configure(text=theme_text) 
        
        # Re-draw the floating button to update colors
        if self.current_user:
            self.create_floating_chat_button()

    def recursive_recolor(self, parent):
        """Recursively recolors all children widgets in the given parent frame."""
        
        # Update root background
        if parent == self.root:
            parent.configure(bg=self.colors['bg_primary'])
        
        for child in parent.winfo_children():
            widget_type = child.winfo_class()
            
            # Skip Toplevels (like loading/dialogs) that should be re-themed on creation
            # NOTE: Added 'Toplevel' check here to prevent recursive recolor on chat window after it's been created
            if widget_type == 'Toplevel':
                continue
            
            # Apply background color to tk Frames/LabelFrames/Canvas
            if widget_type in ('Frame', 'LabelFrame', 'Canvas'):
                # Heuristic to determine if it should be primary or secondary background
                current_bg = child.cget('bg')
                is_primary_color = (current_bg == self.dark_colors['bg_primary'] or current_bg == self.light_colors['bg_primary'])
                is_secondary_color = (current_bg == self.dark_colors['bg_secondary'] or current_bg == self.light_colors['bg_secondary'])
                is_tertiary_color = (current_bg == self.dark_colors['bg_tertiary'] or current_bg == self.light_colors['bg_tertiary'])

                if is_secondary_color or is_tertiary_color:
                    child.configure(bg=self.colors['bg_secondary'])
                elif is_primary_color:
                    child.configure(bg=self.colors['bg_primary'])
            
            # Apply colors to tk Text/ScrolledText widgets
            elif widget_type in ('Text', 'ScrolledText'):
                child.configure(bg=self.colors['bg_tertiary'] if child.winfo_toplevel().title() == "FitBite AI Assistant 💬" else self.colors['bg_secondary'], 
                                fg=self.colors['text_primary'], 
                                insertbackground=self.colors['accent_primary'])

            # Apply colors to tk Label and LabelFrame foreground
            elif widget_type == 'Label':
                current_fg = child.cget('fg')
                # Try to map foreground colors
                if current_fg in (self.dark_colors['text_primary'], self.light_colors['text_primary']):
                    child.configure(fg=self.colors['text_primary'])
                elif current_fg in (self.dark_colors['text_secondary'], self.light_colors['text_secondary']):
                    child.configure(fg=self.colors['text_secondary'])
                elif current_fg in (self.dark_colors['text_muted'], self.light_colors['text_muted']):
                    child.configure(fg=self.colors['text_muted'])
                elif current_fg in (self.dark_colors['accent_primary'], self.light_colors['accent_primary']):
                    child.configure(fg=self.colors['accent_primary'])
                elif current_fg in (self.dark_colors['matrix_accent'], self.light_colors['matrix_accent']):
                    child.configure(fg=self.colors['matrix_accent']) # Keep matrix accent color
                elif current_fg in (self.dark_colors['success'], self.light_colors['success']):
                    child.configure(fg=self.colors['success'])

                # Try to match Label background to parent or frame color
                try:
                    current_bg = child.cget('bg')
                    if current_bg in (self.dark_colors['bg_primary'], self.light_colors['bg_primary']):
                        child.configure(bg=self.colors['bg_primary'])
                    elif current_bg in (self.dark_colors['bg_secondary'], self.light_colors['bg_secondary']):
                        child.configure(bg=self.colors['bg_secondary'])
                    elif current_bg in (self.dark_colors['bg_tertiary'], self.light_colors['bg_tertiary']):
                        child.configure(bg=self.colors['bg_tertiary'])
                except: pass 
            
            # Apply Entry colors
            elif widget_type == 'Entry':
                child.configure(bg=self.colors['bg_tertiary'], fg=self.colors['text_primary'], insertbackground=self.colors['accent_primary'])
            
            # Re-initiate custom buttons to update bound hover/active colors
            elif widget_type == 'Button':
                 current_bg = child.cget('bg')
                 if current_bg in (self.dark_colors['accent_primary'], self.light_colors['accent_primary']):
                    # Accent button
                    child.configure(bg=self.colors['accent_primary'], fg=self.colors['bg_primary'])
                 elif current_bg in (self.dark_colors['bg_tertiary'], self.light_colors['bg_tertiary']):
                     # Normal button
                     child.configure(bg=self.colors['bg_tertiary'], fg=self.colors['text_primary'])
                 else:
                     # Default
                     child.configure(bg=self.colors['bg_secondary'], fg=self.colors['text_primary'])
            
            # Recursive call
            self.recursive_recolor(child)
    # --- END NEW THEME TOGGLE METHODS ---
        
    def setup_styles(self):
        """Configure ttk styles for modern appearance"""
        style = ttk.Style()
        
        # Configure button styles
        style.configure('Modern.TButton',
                        background=self.colors['bg_tertiary'],
                        foreground=self.colors['text_primary'],
                        borderwidth=0,
                        focuscolor='none',
                        font=self.fonts['button'])
        
        style.map('Modern.TButton',
                  background=[('active', self.colors['button_hover']),
                              ('pressed', self.colors['accent_primary'])])
        
        # Configure accent button style
        style.configure('Accent.TButton',
                        background=self.colors['accent_primary'],
                        foreground=self.colors['bg_primary'],
                        borderwidth=0,
                        focuscolor='none',
                        font=self.fonts['button'])
        
        style.map('Accent.TButton',
                  background=[('active', self.colors['accent_secondary']),
                              ('pressed', self.colors['accent_primary'])])
        
        # Configure entry styles
        style.configure('Modern.TEntry',
                        fieldbackground=self.colors['bg_tertiary'],
                        foreground=self.colors['text_primary'],
                        borderwidth=1,
                        insertcolor=self.colors['accent_primary'])
        
        # Configure combobox styles to fix text visibility
        self.root.option_add('*TCombobox*Listbox.foreground', self.colors['text_primary'])
        self.root.option_add('*TCombobox*Listbox.background', self.colors['bg_tertiary'])
        self.root.option_add('*TCombobox*Listbox.selectForeground', self.colors['bg_primary'])
        self.root.option_add('*TCombobox*Listbox.selectBackground', self.colors['accent_primary'])
        
        style.configure('Modern.TCombobox',
                        fieldbackground=self.colors['bg_tertiary'],
                        foreground=self.colors['text_primary'],
                        borderwidth=1,
                        selectbackground=self.colors['bg_tertiary'],
                        selectforeground=self.colors['text_primary'])
        style.map('Modern.TCombobox',
                  foreground=[('readonly', self.colors['text_primary'])],
                  fieldbackground=[('readonly', self.colors['bg_tertiary'])])
        
        # Configure frame styles
        style.configure('Card.TFrame',
                        background=self.colors['bg_secondary'],
                        borderwidth=1,
                        relief='solid')
    
    def create_main_frame(self):
        """Create main application frame"""
        self.main_frame = tk.Frame(self.root, bg=self.colors['bg_primary'])
        self.main_frame.pack(fill=tk.BOTH, expand=True)
    
    def clear_main_frame(self):
        """Clear all widgets from main frame"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        # --- FIX: Ensure the floating button is removed when clearing main frame ---
        if hasattr(self, 'floating_chat_canvas') and self.floating_chat_canvas and self.floating_chat_canvas.winfo_exists():
            self.floating_chat_canvas.place_forget()
        # --- END FIX ---
    
    def fade_in_animation(self, widget, duration=500):
        """Create fade in animation for widgets"""
        if not hasattr(widget, 'winfo_exists') or not widget.winfo_exists():
            return
        pass
    
    def interpolate_color(self, color1, color2, factor):
        """Interpolate between two colors - Retained for compatibility but effectively simplified"""
        return color2 if factor > 0.5 else color1
        
    def check_server_connection(self):
        """Check if the backend server is running"""
        try:
            response = requests.get(f"{self.server_url}/health", timeout=2)
            if response.status_code == 200:
                print("✓ Server connection established")
            else:
                self.show_error("Server Error", "Backend server returned an error. Please check the server.")
        except requests.exceptions.ConnectionError:
            self.show_error("Connection Error", 
                            "Cannot connect to the backend server.\nPlease ensure the server is running on http://127.0.0.1:5000")
        except Exception as e:
            self.show_error("Error", f"Unexpected error: {str(e)}")
            
    def show_login_screen(self):
        """Display the login/signup screen with animations"""
        self.clear_main_frame()
        
        # --- FIX: Removed the animated background circles ---
        self.create_animated_background(remove_circles=True)
        # --- END FIX ---
        
        container = tk.Frame(self.main_frame, bg=self.colors['bg_primary'])
        container.place(relx=0.5, rely=0.5, anchor='center')
        
        title_frame = tk.Frame(container, bg=self.colors['bg_primary'])
        title_frame.pack(pady=(0, 40))
        
        title = tk.Label(title_frame, text="FitBite", font=('Helvetica', 42, 'bold'),
                         fg=self.colors['accent_primary'], bg=self.colors['bg_primary'])
        title.pack()
        
        subtitle = tk.Label(title_frame, text="Smart Recipe Recommendations", font=self.fonts['subtitle'],
                            fg=self.colors['text_secondary'], bg=self.colors['bg_primary'])
        subtitle.pack(pady=(5, 0))
        
        form_frame = tk.Frame(container, bg=self.colors['bg_secondary'], relief='solid', bd=1)
        form_frame.pack(padx=40, pady=20)
        
        inner_frame = tk.Frame(form_frame, bg=self.colors['bg_secondary'])
        inner_frame.pack(padx=40, pady=40)
        
        form_title = tk.Label(inner_frame, text="Welcome Back", font=self.fonts['subtitle'],
                              fg=self.colors['text_primary'], bg=self.colors['bg_secondary'])
        form_title.pack(pady=(0, 30))
        
        self.create_modern_input(inner_frame, "Username", "username_entry")
        self.create_modern_input(inner_frame, "Password", "password_entry", show="*")
        
        button_frame = tk.Frame(inner_frame, bg=self.colors['bg_secondary'])
        button_frame.pack(pady=(30, 0), fill=tk.X)
        
        login_btn = self.create_modern_button(button_frame, "Sign In", self.login, style='accent')
        login_btn.pack(fill=tk.X, pady=(0, 15))
        
        sep_frame = tk.Frame(button_frame, bg=self.colors['bg_secondary'])
        sep_frame.pack(fill=tk.X, pady=10)
        
        sep_line1 = tk.Frame(sep_frame, bg=self.colors['text_muted'], height=1)
        sep_line1.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        sep_text = tk.Label(sep_frame, text="or", fg=self.colors['text_muted'],
                            bg=self.colors['bg_secondary'], font=self.fonts['small'])
        sep_text.pack(side=tk.LEFT)
        
        sep_line2 = tk.Frame(sep_frame, bg=self.colors['text_muted'], height=1)
        sep_line2.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))
        
        signup_btn = self.create_modern_button(button_frame, "Create Account", self.show_signup_screen)
        signup_btn.pack(fill=tk.X)
        
        self.start_floating_animation()
        self.fade_in_animation(container)
        
    def create_animated_background(self, remove_circles=False):
        """Create or remove animated background elements"""
        if hasattr(self, '_animated_circles'):
            for circle in self._animated_circles:
                if circle.winfo_exists(): circle.destroy()
            self._animated_circles = []
        
        if not remove_circles:
            self._animated_circles = []
            for i in range(5):
                # Use accent color for animated elements
                circle = tk.Frame(self.main_frame, bg=self.colors['accent_primary'], width=20, height=20)
                circle.place(x=100 + i*200, y=100 + i*100)
                self._animated_circles.append(circle)
        
    def start_floating_animation(self):
        pass # Placeholder for more complex animations
        
    def create_modern_input(self, parent, label, attr_name, show=None):
        # FIX: Added anchor='w' for better left alignment
        """Create modern input field with floating label effect"""
        container = tk.Frame(parent, bg=self.colors['bg_secondary'])
        container.pack(fill=tk.X, pady=10, anchor='w')
        
        label_widget = tk.Label(container, text=label, font=self.fonts['small'],
                                 fg=self.colors['text_muted'], bg=self.colors['bg_secondary'])
        label_widget.pack(anchor='w', pady=(0, 5))
        
        entry = tk.Entry(container, font=self.fonts['body'], bg=self.colors['bg_tertiary'],
                          fg=self.colors['text_primary'], relief='flat', bd=10,
                          insertbackground=self.colors['accent_primary'], show=show)
        entry.pack(fill=tk.X, ipady=8, anchor='w') # Anchor='w' ensures entry expands neatly
        
        setattr(self, attr_name, entry)
        
        def on_focus_in(event):
            label_widget.configure(fg=self.colors['accent_primary'])
        def on_focus_out(event):
            label_widget.configure(fg=self.colors['text_muted'])
        
        entry.bind('<FocusIn>', on_focus_in)
        entry.bind('<FocusOut>', on_focus_out)
        if attr_name == "password_entry":
            entry.bind('<Return>', lambda e: self.login())
            
    def create_modern_button(self, parent, text, command, style='normal'):
        """Create modern button with hover effects"""
        if style == 'accent':
            bg_color, fg_color, hover_color = self.colors['accent_primary'], self.colors['bg_primary'], self.colors['accent_secondary']
        else:
            bg_color, fg_color, hover_color = self.colors['bg_tertiary'], self.colors['text_primary'], self.colors['button_hover']
        
        button = tk.Button(parent, text=text, font=self.fonts['button'], bg=bg_color, fg=fg_color,
                            relief='flat', bd=0, cursor='hand2', command=command, pady=12,
                            activebackground=hover_color, activeforeground=fg_color)
        
        button.bind('<Enter>', lambda e: button.config(bg=hover_color))
        button.bind('<Leave>', lambda e: button.config(bg=bg_color))
        return button
        
    def create_link_button(self, parent, text, command):
        """Create a pretty, link-style button for navigation."""
        button = tk.Button(parent, text=text, font=self.fonts['link'], bg=self.colors['bg_secondary'],
                            fg=self.colors['text_secondary'], relief='flat', bd=0, cursor='hand2',
                            command=command, activebackground=self.colors['bg_secondary'],
                            activeforeground=self.colors['text_primary'])

        button.bind('<Enter>', lambda e: button.config(fg=self.colors['text_primary']))
        button.bind('<Leave>', lambda e: button.config(fg=self.colors['text_secondary']))
        return button
        
    def show_signup_screen(self):
        """Display signup screen"""
        self.clear_main_frame()
        
        container = tk.Frame(self.main_frame, bg=self.colors['bg_primary'])
        container.place(relx=0.5, rely=0.5, anchor='center')
        
        back_frame = tk.Frame(container, bg=self.colors['bg_primary'])
        back_frame.pack(fill=tk.X, pady=(0, 20))
        
        back_btn = self.create_link_button(back_frame, "← Back to Login", self.show_login_screen)
        back_btn.pack(side=tk.LEFT)
        
        title = tk.Label(container, text="Create Account", font=self.fonts['title'],
                         fg=self.colors['accent_primary'], bg=self.colors['bg_primary'])
        title.pack(pady=(0, 30))
        
        form_frame = tk.Frame(container, bg=self.colors['bg_secondary'], relief='solid', bd=1)
        form_frame.pack(padx=40)
        
        inner_frame = tk.Frame(form_frame, bg=self.colors['bg_secondary'])
        inner_frame.pack(padx=40, pady=40)
        
        self.create_modern_input(inner_frame, "Username", "signup_username_entry")
        self.create_modern_input(inner_frame, "Password", "signup_password_entry", show="*")
        self.create_modern_input(inner_frame, "Confirm Password", "signup_confirm_entry", show="*")
        
        signup_btn = self.create_modern_button(inner_frame, "Create Account", self.signup, style='accent')
        signup_btn.pack(fill=tk.X, pady=(30, 0))
        
        self.fade_in_animation(container)
        
    def login(self):
        """Handle user login"""
        username = getattr(self, 'username_entry', tk.Entry()).get().strip()
        password = getattr(self, 'password_entry', tk.Entry()).get().strip()
        if not username or not password:
            self.show_error("Error", "Please enter both username and password")
            return
        
        self.show_loading("Signing in...")
        
        def login_thread():
            try:
                data = {"username": username, "password": password}
                response = requests.post(f"{self.server_url}/login", json=data, timeout=10)
                result = response.json()
                
                self.root.after(0, self.hide_loading)
                if response.status_code == 200 and result.get("success"):
                    self.current_user = username
                    self.root.after(0, self.show_main_dashboard)
                    self.root.after(0, lambda: self.show_success("Login Successful", result.get("message")))
                else:
                    self.root.after(0, lambda: self.show_error("Login Failed", result.get("message", "Unknown error")))
            except requests.exceptions.RequestException as e:
                self.root.after(0, self.hide_loading)
                self.root.after(0, lambda: self.show_error("Connection Error", f"Cannot connect to server: {e}"))
            except Exception as e:
                self.root.after(0, self.hide_loading)
                self.root.after(0, lambda: self.show_error("Error", f"An unexpected error occurred: {e}"))
        
        threading.Thread(target=login_thread, daemon=True).start()
        
    def signup(self):
        """Handle user registration"""
        username = getattr(self, 'signup_username_entry', tk.Entry()).get().strip()
        password = getattr(self, 'signup_password_entry', tk.Entry()).get().strip()
        confirm = getattr(self, 'signup_confirm_entry', tk.Entry()).get().strip()
        
        if not all([username, password, confirm]):
            self.show_error("Error", "Please fill in all fields")
            return
        if password != confirm:
            self.show_error("Error", "Passwords do not match")
            return
        if len(password) < 6:
            self.show_error("Error", "Password must be at least 6 characters long")
            return
        
        self.show_loading("Creating account...")
        def signup_thread():
            try:
                data = {"username": username, "password": password}
                response = requests.post(f"{self.server_url}/signup", json=data, timeout=10)
                result = response.json()
                self.root.after(0, self.hide_loading)
                if response.status_code == 201 and result.get("success"):
                    self.root.after(0, lambda: self.show_success("Success", result.get("message")))
                    self.root.after(1000, self.show_login_screen)
                else:
                    self.root.after(0, lambda: self.show_error("Signup Failed", result.get("message", "Registration failed")))
            except Exception as e:
                self.root.after(0, self.hide_loading)
                self.root.after(0, lambda: self.show_error("Error", f"Registration failed: {str(e)}"))
        
        threading.Thread(target=signup_thread, daemon=True).start()
        
    def show_main_dashboard(self):
        """Display main dashboard after login"""
        self.clear_main_frame()
        self.create_navigation_bar()
        
        content_frame = tk.Frame(self.main_frame, bg=self.colors['bg_primary'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        welcome_frame = tk.Frame(content_frame, bg=self.colors['bg_secondary'])
        welcome_frame.pack(fill=tk.X, pady=(0, 20))
        
        welcome_inner = tk.Frame(welcome_frame, bg=self.colors['bg_secondary'])
        welcome_inner.pack(padx=30, pady=30)
        
        welcome_title = tk.Label(welcome_inner, text=f"Welcome back, {self.current_user}!",
                                 font=self.fonts['title'], fg=self.colors['text_primary'], bg=self.colors['bg_secondary'])
        welcome_title.pack(anchor='w')
        
        welcome_subtitle = tk.Label(welcome_inner, text="What would you like to cook today?",
                                    font=self.fonts['body'], fg=self.colors['text_secondary'], bg=self.colors['bg_secondary'])
        welcome_subtitle.pack(anchor='w', pady=(5, 0))
        
        actions_frame = tk.Frame(content_frame, bg=self.colors['bg_primary'])
        actions_frame.pack(fill=tk.BOTH, expand=True)
        
        # --- FIX: Replaced "My Favorites" with "NutriPlanner" card ---
        self.create_action_card(actions_frame, "🔍 Find Recipes", "Search for recipes based on ingredients",
                                 self.show_recipe_finder, row=0, col=0)
        self.create_action_card(actions_frame, "📊 NutriPlanner", "Calculate needs and generate meal plans",
                                 self.show_nutriplanner_screen, row=0, col=1)
        # --- END FIX ---
        
        self.create_action_card(actions_frame, "📅 Meal Planner", "Create meal plans from your searches",
                                 self.show_meal_planner, row=1, col=0)
        self.create_action_card(actions_frame, "📊 My Statistics", "View your cooking statistics",
                                 self.show_user_stats, row=1, col=1)
        
        self.fade_in_animation(content_frame)

        # --- FIX: Create Floating Chat Button on Dashboard load ---
        self.create_floating_chat_button()
        # --- END FIX ---
        
    def create_navigation_bar(self):
        """Create modern navigation bar"""
        nav_frame = tk.Frame(self.main_frame, bg=self.colors['bg_secondary'], height=70)
        nav_frame.pack(fill=tk.X)
        nav_frame.pack_propagate(False)
        
        nav_inner = tk.Frame(nav_frame, bg=self.colors['bg_secondary'])
        nav_inner.pack(fill=tk.BOTH, padx=20, pady=15)
        
        logo_frame = tk.Frame(nav_inner, bg=self.colors['bg_secondary'])
        logo_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        # FIX: Made the FitBite logo a clickable button to redirect to dashboard
        logo = tk.Button(logo_frame, text="FitBite", font=('Helvetica', 20, 'bold'),
                         fg=self.colors['accent_primary'], bg=self.colors['bg_secondary'],
                         relief='flat', bd=0, cursor='hand2', command=self.show_main_dashboard)
        # Re-apply hover behavior to the new button logo
        logo.bind('<Enter>', lambda e: logo.config(fg=self.colors['accent_secondary']))
        logo.bind('<Leave>', lambda e: logo.config(fg=self.colors['accent_primary']))
        logo.pack(side=tk.LEFT, anchor='center')
        # END FIX


        # --- ADDED THEME TOGGLE BUTTON (NEW FEATURE) ---
        theme_text = "🌙 Night Mode" if self.current_theme == 'light' else "☀️ Day Mode"
        self.theme_button = self.create_modern_button(logo_frame, theme_text, self.toggle_theme, style='normal')
        self.theme_button.pack(side=tk.LEFT, anchor='center', padx=20)

        # --- FIX: Moved My Favorites to the Navigation Bar ---
        fav_btn = self.create_modern_button(logo_frame, "My Favorites", self.show_favorites)
        fav_btn.pack(side=tk.LEFT, anchor='center', padx=20)
        # --- END FIX ---
        
        user_frame = tk.Frame(nav_inner, bg=self.colors['bg_secondary'])
        user_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        user_label = tk.Label(user_frame, text=f"👤 {self.current_user}", font=self.fonts['body'],
                              fg=self.colors['text_primary'], bg=self.colors['bg_secondary'])
        user_label.pack(side=tk.LEFT, anchor='center', padx=(0, 20))
        
        logout_btn = self.create_modern_button(user_frame, "Logout", self.logout)
        logout_btn.pack(side=tk.LEFT, anchor='center')
        
    def create_floating_chat_button(self):
        """Creates a modern, floating circular chat button at the bottom right."""
        
        # If the canvas already exists, destroy it first to update colors/re-place
        if hasattr(self, 'floating_chat_canvas') and self.floating_chat_canvas and self.floating_chat_canvas.winfo_exists():
            self.floating_chat_canvas.destroy()

        # Size of the button/canvas
        btn_size = 50 
        
        self.floating_chat_canvas = tk.Canvas(
            self.root, 
            width=btn_size, 
            height=btn_size, 
            bg=self.colors['bg_primary'], # Use primary bg to blend into the margin
            highlightthickness=0, # Remove default canvas border
            cursor='hand2'
        )
        
        # Draw the main circular button
        
        # Create a circle (oval) for the button background
        circle_id = self.floating_chat_canvas.create_oval(
            0, 0, btn_size, btn_size, 
            fill=self.colors['accent_primary'], 
            outline=self.colors['accent_primary'], # Match outline to fill
            width=2 
        )
        
        # Create a speech bubble icon (using Tkinter polygon/line for simplicity)
        icon_color = self.colors['bg_primary'] # Use primary background for icon color
        
        # Main bubble: (10, 10) to (40, 40) relative to the 50x50 canvas
        icon_bubble_oval_id = self.floating_chat_canvas.create_oval(
            12, 12, 38, 33, # Slightly smaller and higher for message icon look
            fill=icon_color, 
            outline=icon_color,
            width=1 
        )
        # Tail: polygon pointing down-left
        icon_bubble_tail_id = self.floating_chat_canvas.create_polygon(
            15, 33, 10, 40, 20, 33, 
            fill=icon_color, 
            outline=icon_color
        )
        
        # Binding the click action to the canvas and its elements
        self.floating_chat_canvas.bind('<Button-1>', lambda e: self.show_chatbot_window())
        self.floating_chat_canvas.tag_bind(circle_id, '<Button-1>', lambda e: self.show_chatbot_window())
        
        # Hover effect implementation (only on the canvas for simplicity)
        def on_enter(e):
            self.floating_chat_canvas.itemconfig(circle_id, fill=self.colors['accent_secondary'], outline=self.colors['accent_secondary'])
        def on_leave(e):
            self.floating_chat_canvas.itemconfig(circle_id, fill=self.colors['accent_primary'], outline=self.colors['accent_primary'])

        self.floating_chat_canvas.bind('<Enter>', on_enter)
        self.floating_chat_canvas.bind('<Leave>', on_leave)

        # Place the button at the bottom right, with margin (30px)
        self.floating_chat_canvas.place(relx=1.0, rely=1.0, anchor='se', x=-30, y=-30)

    def create_action_card(self, parent, title, description, command, row, col):
        """Create action card for dashboard"""
        card_frame = tk.Frame(parent, bg=self.colors['bg_secondary'], relief='solid', bd=1, cursor='hand2')
        card_frame.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
        
        parent.grid_rowconfigure(row, weight=1)
        parent.grid_columnconfigure(col, weight=1)
        
        card_inner = tk.Frame(card_frame, bg=self.colors['bg_secondary'])
        card_inner.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        title_label = tk.Label(card_inner, text=title, font=self.fonts['heading'],
                                 fg=self.colors['text_primary'], bg=self.colors['bg_secondary'])
        title_label.pack(anchor='w', pady=(0, 10))
        
        desc_label = tk.Label(card_inner, text=description, font=self.fonts['body'],
                              fg=self.colors['text_secondary'], bg=self.colors['bg_secondary'], wraplength=200)
        desc_label.pack(anchor='w')
        
        action_btn = self.create_modern_button(card_inner, "Open", command, style='accent')
        action_btn.pack(anchor='w', pady=(20, 0))
        
        def on_card_enter_leave(event, is_enter):
            bg = self.colors['bg_tertiary'] if is_enter else self.colors['bg_secondary']
            card_frame.config(bg=bg)
            card_inner.config(bg=bg)
            title_label.config(bg=bg)
            desc_label.config(bg=bg)

        card_frame.bind('<Enter>', lambda e: on_card_enter_leave(e, True))
        card_frame.bind('<Leave>', lambda e: on_card_enter_leave(e, False))
        card_frame.bind('<Button-1>', lambda e: command())
        
    def show_recipe_finder(self):
        """Display recipe finder interface"""
        self.clear_main_frame()
        self.create_navigation_bar()
        self.create_floating_chat_button() # Re-add floating button
        content_frame = tk.Frame(self.main_frame, bg=self.colors['bg_primary'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        header_frame = tk.Frame(content_frame, bg=self.colors['bg_secondary'])
        header_frame.pack(fill=tk.X, pady=(0, 20))
        header_inner = tk.Frame(header_frame, bg=self.colors['bg_secondary'])
        header_inner.pack(padx=30, pady=20)
        back_btn = self.create_link_button(header_inner, "← Back to Dashboard", self.show_main_dashboard)
        back_btn.pack(anchor='w', pady=(0, 15))
        title = tk.Label(header_inner, text="Recipe Finder", font=self.fonts['title'], fg=self.colors['text_primary'], bg=self.colors['bg_secondary'])
        title.pack(anchor='w')
        subtitle = tk.Label(header_inner, text="Enter ingredients you have and discover amazing recipes", font=self.fonts['body'], fg=self.colors['text_secondary'], bg=self.colors['bg_secondary'])
        subtitle.pack(anchor='w', pady=(5, 0))
        form_frame = tk.Frame(content_frame, bg=self.colors['bg_secondary'])
        form_frame.pack(fill=tk.X, pady=(0, 20))
        form_inner = tk.Frame(form_frame, bg=self.colors['bg_secondary'])
        form_inner.pack(padx=30, pady=30)
        ingredients_frame = tk.Frame(form_inner, bg=self.colors['bg_secondary'])
        ingredients_frame.pack(fill=tk.X, pady=(0, 20))
        label_row = tk.Frame(ingredients_frame, bg=self.colors['bg_secondary'])
        label_row.pack(fill=tk.X, pady=(0, 5))
        ingredients_label = tk.Label(label_row, text="Ingredients", font=self.fonts['heading'], fg=self.colors['text_primary'], bg=self.colors['bg_secondary'])
        ingredients_label.pack(side=tk.LEFT, anchor='w')
        if SPEECH_RECOGNITION_AVAILABLE:
            voice_btn = tk.Button(label_row, text="🎤", font=('Helvetica', 14), bg=self.colors['bg_secondary'], fg=self.colors['accent_primary'], relief='flat', cursor='hand2', command=self.listen_for_ingredients)
            voice_btn.pack(side=tk.LEFT, padx=(10,0))
        self.ingredients_entry = tk.Entry(ingredients_frame, font=self.fonts['body'], bg=self.colors['bg_tertiary'], fg=self.colors['text_primary'], relief='flat', bd=10, insertbackground=self.colors['accent_primary'])
        self.ingredients_entry.pack(fill=tk.X, ipady=10)
        self.ingredients_entry.insert(0, "chicken, tomatoes, onions")
        filters_frame = tk.Frame(form_inner, bg=self.colors['bg_secondary'])
        filters_frame.pack(fill=tk.X, pady=(0, 20))
        self.create_filter_entry(filters_frame, "Prep Time (mins)", "prep_time_entry", 0)
        self.create_filter_dropdown(filters_frame, "Diet", "diet_var", ["Any", "Vegetarian", "Non-Vegetarian", "Vegan"], 1)
        self.create_filter_dropdown(filters_frame, "Cuisine", "cuisine_var", ["Any", "Italian", "Chinese", "Indian", "Mexican"], 2)
        self.create_filter_dropdown(filters_frame, "Meal Type", "meal_var", ["Any", "Breakfast", "Lunch", "Dinner"], 3)
        search_btn = self.create_modern_button(form_inner, "Find Recipes", self.search_recipes, style='accent')
        search_btn.pack(pady=(20, 0), fill=tk.X)
        self.fade_in_animation(content_frame)

    # --- NUTRI-PLANNER SCREEN (FIXED MISSING SEARCH BUTTON & ADDED MATRIX) ---
    def show_nutriplanner_screen(self):
        """Display the NutriPlanner screen for personalized recommendations"""
        self.clear_main_frame()
        self.create_navigation_bar()
        self.create_floating_chat_button() # Re-add floating button
        self.nutri_metrics = {} # To store calculated metrics

        # Main container
        container = tk.Frame(self.main_frame, bg=self.colors['bg_primary'])
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        header_frame = tk.Frame(container, bg=self.colors['bg_secondary'])
        header_frame.pack(fill=tk.X, pady=(0, 20))
        header_inner = tk.Frame(header_frame, bg=self.colors['bg_secondary'])
        header_inner.pack(padx=30, pady=20)
        back_btn = self.create_link_button(header_inner, "← Back to Dashboard", self.show_main_dashboard)
        back_btn.pack(anchor='w', pady=(0, 15))
        title = tk.Label(header_inner, text="NutriPlanner", font=self.fonts['title'], fg=self.colors['text_primary'], bg=self.colors['bg_secondary'])
        title.pack(anchor='w')
        subtitle = tk.Label(header_inner, text="Calculate your needs and get a personalized meal plan", font=self.fonts['body'], fg=self.colors['text_secondary'], bg=self.colors['bg_secondary'])
        subtitle.pack(anchor='w', pady=(5, 0))

        # Content split into three columns: Input (0), Matrix (1), Results (2)
        content_grid = tk.Frame(container, bg=self.colors['bg_primary'])
        content_grid.pack(fill=tk.BOTH, expand=True)
        
        content_grid.grid_columnconfigure(0, weight=1, minsize=380) 
        content_grid.grid_columnconfigure(1, weight=1, minsize=380) 
        content_grid.grid_columnconfigure(2, weight=2, minsize=400) 
        content_grid.grid_rowconfigure(0, weight=1)

        # ----------------------------------------------------------------------
        # COLUMN 1: Input Form and Get Meal Plan Button
        # ----------------------------------------------------------------------
        input_col_frame = tk.Frame(content_grid, bg=self.colors['bg_secondary'], padx=30, pady=30)
        input_col_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 20))
        
        # Canvas for scrollable input (to ensure 'Get Meal Plan' is always visible)
        input_canvas = tk.Canvas(input_col_frame, bg=self.colors['bg_secondary'], highlightthickness=0) 
        input_scrollbar = ttk.Scrollbar(input_col_frame, orient="vertical", command=input_canvas.yview)
        
        input_frame = tk.Frame(input_canvas, bg=self.colors['bg_secondary'])
        # 340 = 380 minsize - (30+30) outer padding - (approx 20 for scrollbar)
        input_canvas.create_window((0, 0), window=input_frame, anchor="nw", width=340) 

        # --- FIX: Bind the inner frame's Configure event to update scrollregion ---
        def _on_input_frame_configure(event):
            # Update scroll region to match the size of the inner frame
            input_canvas.configure(scrollregion=input_canvas.bbox("all"))
        input_frame.bind("<Configure>", _on_input_frame_configure)
        # --- END FIX ---
        
        input_canvas.configure(yscrollcommand=input_scrollbar.set)
        
        # Configure the layout manager for the column
        input_col_frame.grid_rowconfigure(0, weight=1)
        
        input_canvas.grid(row=0, column=0, sticky='nsew', columnspan=2) # Canvas expands
        input_scrollbar.grid(row=0, column=2, sticky='ns') # Scrollbar next to canvas
        
        # Using Grid for reliable alignment and button placement inside the scrollable frame
        input_frame.grid_columnconfigure(0, weight=1)
        
        # Helper function to place inputs in a grid
        def place_input_in_grid(parent, label, attr_name, row):
            container = tk.Frame(parent, bg=self.colors['bg_secondary'])
            container.grid(row=row, column=0, sticky='ew', pady=5, padx=5) 
            self.create_modern_input_for_planner(container, label, attr_name)

        def place_dropdown_in_grid(parent, label, var, options, row):
            frame = tk.Frame(parent, bg=self.colors['bg_secondary'])
            frame.grid(row=row, column=0, sticky='ew', pady=5, padx=5) 
            self.create_filter_dropdown_for_planner_internal(frame, label, var, options)

        # --- Input Fields Placed in Grid ---
        place_input_in_grid(input_frame, "Height (cm)", "height_entry", 0)
        place_input_in_grid(input_frame, "Weight (kg)", "weight_entry", 1)
        place_input_in_grid(input_frame, "Age", "age_entry", 2)
        
        self.gender_var = tk.StringVar(value="Male")
        place_dropdown_in_grid(input_frame, "Gender", self.gender_var, ["Male", "Female"], 3)

        self.activity_var = tk.StringVar(value="Sedentary")
        place_dropdown_in_grid(input_frame, "Activity Level", self.activity_var, ["Sedentary", "Lightly Active", "Moderately Active", "Very Active", "Extra Active"], 4)

        self.goal_var = tk.StringVar(value="Maintain Weight")
        place_dropdown_in_grid(input_frame, "Goal", self.goal_var, ["Lose Weight", "Maintain Weight", "Gain Muscle"], 5)
        
        # --- NEW: Calculate Needs Button (Step 1 - ALWAYS VISIBLE FIX) ---
        calculate_btn = self.create_modern_button(input_col_frame, "Calculate Needs", self.calculate_nutri_matrix, style='accent')
        calculate_btn.grid(row=1, column=0, columnspan=3, sticky='ew', pady=(10, 5), padx=5)

        # --- Get Meal Plan Button (Step 2 - GUARANTEED VISIBLE FIX) ---
        self.get_plan_btn = self.create_modern_button(input_col_frame, "Get Meal Plan", self.get_meal_plan, style='accent')
        self.get_plan_btn.grid(row=2, column=0, columnspan=3, sticky='ew', pady=(5, 5), padx=5)
        self.get_plan_btn.config(state=tk.DISABLED, text="Get Meal Plan (Calculate Needs First)")
        # ----------------------------------------------------------------------


        # ----------------------------------------------------------------------
        # COLUMN 2: Nutri Matrix Display
        # ----------------------------------------------------------------------
        self.matrix_col_frame = tk.Frame(content_grid, bg=self.colors['bg_secondary'], padx=20, pady=20)
        self.matrix_col_frame.grid(row=0, column=1, sticky='nsew', padx=(0, 20))
        
        self.matrix_title = tk.Label(self.matrix_col_frame, text="Nutrient Target Matrix", font=self.fonts['subtitle'], fg=self.colors['text_primary'], bg=self.colors['bg_secondary'])
        self.matrix_title.pack(anchor='w', pady=(0, 15))
        
        # Frame for matrix grid
        self.matrix_grid_frame = tk.Frame(self.matrix_col_frame, bg=self.colors['bg_secondary'])
        self.matrix_grid_frame.pack(fill=tk.BOTH, expand=True)

        self.matrix_text = tk.Label(self.matrix_grid_frame, text="Enter your details and click 'Calculate Needs' to see your personalized targets.", 
                                     font=self.fonts['body'], fg=self.colors['text_muted'], bg=self.colors['bg_secondary'], justify=tk.LEFT, wraplength=340, anchor='n')
        self.matrix_text.pack(fill=tk.BOTH, expand=True)
        # ----------------------------------------------------------------------


        # ----------------------------------------------------------------------
        # COLUMN 3: Meal Plan Results
        # ----------------------------------------------------------------------
        self.meal_plan_results_frame = tk.Frame(content_grid, bg=self.colors['bg_primary'])
        self.meal_plan_results_frame.grid(row=0, column=2, sticky='nsew')
        tk.Label(self.meal_plan_results_frame, text="Your personalized meal plan will appear here.",
                  font=self.fonts['body'], fg=self.colors['text_muted'], bg=self.colors['bg_primary']).pack(expand=True)
        # ----------------------------------------------------------------------

    def create_modern_input_for_planner(self, parent, label, attr_name, show=None):
        """Create modern input field for the grid layout in NutriPlanner."""
        # parent is the frame created in place_input_in_grid, already packed 'ew'
        
        label_widget = tk.Label(parent, text=label, font=self.fonts['small'],
                                 fg=self.colors['text_muted'], bg=self.colors['bg_secondary'])
        label_widget.pack(anchor='w', pady=(0, 5))
        
        entry = tk.Entry(parent, font=self.fonts['body'], bg=self.colors['bg_tertiary'],
                          fg=self.colors['text_primary'], relief='flat', bd=10,
                          insertbackground=self.colors['accent_primary'], show=show)
        entry.pack(fill=tk.X, ipady=8) 
        
        setattr(self, attr_name, entry)
        
        def on_focus_in(event):
            label_widget.configure(fg=self.colors['accent_primary'])
        def on_focus_out(event):
            label_widget.configure(fg=self.colors['text_muted'])
        
        entry.bind('<FocusIn>', on_focus_in)
        entry.bind('<FocusOut>', on_focus_out)

    def create_filter_dropdown_for_planner_internal(self, parent, label_text, var, options):
        """Helper for creating dropdowns specifically for the planner form (internal use)"""
        # parent is the frame created in place_dropdown_in_grid, already packed 'ew'
        label = tk.Label(parent, text=label_text, font=self.fonts['small'], fg=self.colors['text_muted'], bg=self.colors['bg_secondary'])
        label.pack(anchor='w', pady=(0, 5))
        combo = ttk.Combobox(parent, textvariable=var, values=options, state='readonly', style='Modern.TCombobox', font=self.fonts['body'])
        combo.pack(fill=tk.X)
    
    # --- New Calculation Logic ---
    def create_matrix_card(self, parent, label, value, unit, color):
        """Helper to create a single visually attractive metric card for the matrix."""
        card = tk.Frame(parent, bg=self.colors['bg_tertiary'], padx=15, pady=10)
        card.pack(fill=tk.X, pady=5)
        
        # Value (Large Font)
        value_label = tk.Label(card, text=f"{value}", font=self.fonts['matrix_value'], fg=color, bg=self.colors['bg_tertiary'])
        value_label.pack(side=tk.LEFT)
        
        # Unit (Small, Muted)
        unit_label = tk.Label(card, text=f"{unit}", font=self.fonts['body'], fg=self.colors['text_muted'], bg=self.colors['bg_tertiary'])
        unit_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Label (Right-aligned)
        label_label = tk.Label(card, text=label, font=self.fonts['small'], fg=self.colors['text_secondary'], bg=self.colors['bg_tertiary'])
        label_label.pack(side=tk.RIGHT, anchor='e')
        
        return card

    def display_nutri_matrix(self):
        """Displays the visually attractive Nutri Matrix in the center panel."""
        # Clear previous contents
        for widget in self.matrix_grid_frame.winfo_children():
            widget.destroy()
            
        metrics = self.nutri_metrics
        
        # Create a scrollable container for the results (in case the window is small)
        matrix_canvas = tk.Canvas(self.matrix_grid_frame, bg=self.colors['bg_secondary'], highlightthickness=0)
        matrix_scrollable_frame = tk.Frame(matrix_canvas, bg=self.colors['bg_secondary'])
        
        matrix_canvas.pack(fill=tk.BOTH, expand=True)
        # Note: Setting width here is less critical since it's packed fill=BOTH
        matrix_canvas.create_window((0, 0), window=matrix_scrollable_frame, anchor="nw", width=self.matrix_grid_frame.winfo_width())
        
        # Scrollbar setup
        matrix_scrollbar = ttk.Scrollbar(self.matrix_grid_frame, orient="vertical", command=matrix_canvas.yview)
        matrix_canvas.configure(yscrollcommand=matrix_scrollbar.set)

        # Bind inner frame size changes to update scroll region
        def _on_matrix_frame_configure(event):
            # This ensures the inner scrollable frame matches the width of the canvas
            matrix_canvas.itemconfig(matrix_canvas.find_withtag("all")[-1], width=event.width)
            matrix_canvas.configure(scrollregion=matrix_canvas.bbox("all"))
            
        matrix_scrollable_frame.bind("<Configure>", _on_matrix_frame_configure)
        
        matrix_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        # Scrollbar is added to the containing frame to manage the canvas view
        matrix_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)


        # Matrix Title Card
        title_card = tk.Frame(matrix_scrollable_frame, bg=self.colors['bg_secondary'], padx=10, pady=5)
        title_card.pack(fill=tk.X, pady=(0, 10))
        tk.Label(title_card, text=f"Goal: {metrics['data']['goal']} ({metrics['data']['gender']})", font=self.fonts['heading'], fg=self.colors['accent_primary'], bg=self.colors['bg_secondary']).pack(anchor='w')
        tk.Label(title_card, text="--- Daily Targets ---", font=self.fonts['small'], fg=self.colors['text_muted'], bg=self.colors['bg_secondary']).pack(anchor='w')


        # 1. Target Calories (Main Metric)
        self.create_matrix_card(matrix_scrollable_frame, "CALORIE TARGET", f"{metrics['target_calories']:.0f}", "Cal", self.colors['accent_secondary']).pack(fill=tk.X, pady=(10, 15))
        
        # 2. Macros
        self.create_matrix_card(matrix_scrollable_frame, "PROTEIN", f"{metrics['protein']:.0f}", "g", self.colors['matrix_accent']).pack(fill=tk.X)
        self.create_matrix_card(matrix_scrollable_frame, "FAT", f"{metrics['fat']:.0f}", "g", self.colors['matrix_accent']).pack(fill=tk.X)
        self.create_matrix_card(matrix_scrollable_frame, "CARBS", f"{metrics['carbs']:.0f}", "g", self.colors['matrix_accent']).pack(fill=tk.X)
        
        # 3. BMR/TDEE (Informational)
        info_frame = tk.Frame(matrix_scrollable_frame, bg=self.colors['bg_secondary'], padx=15, pady=10)
        info_frame.pack(fill=tk.X, pady=(20, 0))
        tk.Label(info_frame, text="Metabolic Rate Breakdown:", font=self.fonts['body'], fg=self.colors['text_primary'], bg=self.colors['bg_secondary']).pack(anchor='w')
        tk.Label(info_frame, text=f"BMR: {metrics['bmr']:.0f} Cal (Resting)", font=self.fonts['small'], fg=self.colors['text_muted'], bg=self.colors['bg_secondary']).pack(anchor='w')
        tk.Label(info_frame, text=f"TDEE: {metrics['tdee']:.0f} Cal (Total Daily)", font=self.fonts['small'], fg=self.colors['text_muted'], bg=self.colors['bg_secondary']).pack(anchor='w')


    def calculate_nutri_matrix(self):
        """Calculates BMR, TDEE, and macro goals and displays the matrix."""
        
        # 1. Input Validation
        try:
            height = float(self.height_entry.get().strip())
            weight = float(self.weight_entry.get().strip())
            age = int(self.age_entry.get().strip())
            gender = self.gender_var.get()
            activity_level = self.activity_var.get()
            goal = self.goal_var.get()

            if height <= 0 or weight <= 0 or age <= 0:
                 self.show_error("Input Error", "Height, Weight, and Age must be positive numbers.")
                 return

        except ValueError:
            self.show_error("Input Error", "Please enter valid numbers for Height, Weight, and Age.")
            return
        
        # 2. Calculation (Client-side estimation)
        # Using Mifflin-St Jeor equation for BMR estimation
        if gender.lower() == 'male':
            bmr = 10 * weight + 6.25 * height - 5 * age + 5
        else: # female
            bmr = 10 * weight + 6.25 * height - 5 * age - 161

        activity_multipliers = {'sedentary': 1.2, 'lightly active': 1.375, 'moderately active': 1.55, 'very active': 1.725, 'extra active': 1.9}
        tdee = bmr * activity_multipliers.get(activity_level.lower(), 1.2)
        
        # Goal Adjustment
        target_cal = tdee
        if goal.lower() == 'lose weight':
            target_cal -= 500
        elif goal.lower() == 'gain muscle':
            target_cal += 500
        
        target_cal = max(1200, target_cal) # Minimum safety calories

        # Macro Estimation (Example 40% Carb, 30% Protein, 30% Fat)
        cal_protein = target_cal * 0.30
        cal_fat = target_cal * 0.30
        cal_carb = target_cal * 0.40
        
        protein_grams = cal_protein / 4   # 4 calories per gram of protein
        fat_grams = cal_fat / 9   # 9 calories per gram of fat
        carb_grams = cal_carb / 4       # 4 calories per gram of carbohydrate

        # 3. Store and Display Matrix
        self.nutri_metrics = {
            "target_calories": round(target_cal, 0),
            "protein": round(protein_grams, 0),
            "fat": round(fat_grams, 0),
            "carbs": round(carb_grams, 0),
            "bmr": round(bmr, 0),
            "tdee": round(tdee, 0),
            # Data to be sent to the backend endpoint
            "data": {
                "height": height, "weight": weight, "age": age, 
                "gender": gender, "activity_level": activity_level, "goal": goal,
                "username": self.current_user # FIX: Include username here
            }
        }
        
        self.display_nutri_matrix()
        
        # Enable the 'Get Meal Plan' button
        self.get_plan_btn.config(state=tk.NORMAL, text="Get Meal Plan (Search)")


    def get_meal_plan(self):
        """Fetch and display meal plan from the server"""
        if not self.nutri_metrics:
            self.show_error("Action Required", "Please click 'Calculate Needs' first to set your calorie goals.")
            return
            
        data = self.nutri_metrics['data'].copy() # Use the validated, calculated data
        
        self.show_loading("Generating your personalized meal plan...")
        
        def meal_plan_thread():
            try:
                # The backend handles the BMR/TDEE and recipe selection based on the data provided
                response = requests.post(f"{self.server_url}/nutriplanner", json=data, timeout=20)
                result = response.json()
                self.root.after(0, self.hide_loading)
                if response.status_code == 200 and result.get("success"):
                    self.root.after(0, lambda: self.display_nutri_plan(result.get('plan', {})))
                else:
                    self.root.after(0, lambda: self.show_error("Error", result.get("message", "Could not generate meal plan.")))
            except requests.exceptions.RequestException as e:
                self.root.after(0, self.hide_loading)
                self.root.after(0, lambda: self.show_error("Connection Error", f"Cannot connect to server: {e}"))
            except Exception as e:
                self.root.after(0, self.hide_loading)
                self.root.after(0, lambda: self.show_error("Error", f"An unexpected error occurred: {e}"))

        threading.Thread(target=meal_plan_thread, daemon=True).start()
        
    def save_nutri_plan_history(self, data, target_calories):
        """Saves a summary of the generated meal plan request to the backend for statistics."""
        try:
            summary = {
                "user_data": data,
                "target_calories": target_calories,
                "timestamp": datetime.now().isoformat()
            }
            # Your backend doesn't have an explicit endpoint for NutriPlanner history yet, 
            # so we'll use a placeholder structure or rely on the existing search history logic.
            # Assuming the backend will handle this if a dedicated endpoint existed.
            # In absence of a backend endpoint, this function is purely a placeholder for future stats integration.
            print(f"NutriPlanner plan summary saved: {summary}")
        except Exception as e:
            print(f"Failed to save NutriPlanner history (Placeholder): {e}")

    def display_nutri_plan(self, plan):
        """Display the recommended meal plan in the GUI"""
        for widget in self.meal_plan_results_frame.winfo_children():
            widget.destroy()

        if not plan or not any(plan.values()):
            tk.Label(self.meal_plan_results_frame, text="Could not find suitable recipes for your goals.\nTry adjusting your criteria.", 
                     font=self.fonts['subtitle'], fg=self.colors['text_muted'], bg=self.colors['bg_primary']).pack(pady=20, expand=True)
            return

        # Add a scrollable frame for the plan results
        plan_canvas = tk.Canvas(self.meal_plan_results_frame, bg=self.colors['bg_primary'], highlightthickness=0)
        plan_scrollbar = ttk.Scrollbar(self.meal_plan_results_frame, orient="vertical", command=plan_canvas.yview)
        plan_scrollable_frame = tk.Frame(plan_canvas, bg=self.colors['bg_primary'])
        
        plan_scrollable_frame.bind("<Configure>", lambda e: plan_canvas.configure(scrollregion=plan_canvas.bbox("all")))
        plan_canvas.create_window((0, 0), window=plan_scrollable_frame, anchor="nw")
        plan_canvas.configure(yscrollcommand=plan_scrollbar.set)
        
        plan_canvas.pack(side="left", fill=tk.BOTH, expand=True)
        plan_scrollbar.pack(side="right", fill="y")

        total_calories = 0
        
        # Display each meal section
        for meal, recipes in plan.items():
            meal_frame = tk.LabelFrame(plan_scrollable_frame, text=meal.capitalize(),
                                         font=self.fonts['heading'], fg=self.colors['accent_primary'],
                                         bg=self.colors['bg_secondary'], bd=1, relief="solid", padx=10, pady=10)
            meal_frame.pack(pady=10, padx=10, fill=tk.X)
            
            if recipes:
                meal_cal = 0
                
                # --- FIX: Loop through ALL recipes provided for the meal ---
                for recipe in recipes: 
                    recipe_name = recipe.get('name', 'Unknown Recipe')
                    nutrition = recipe.get('nutrition', [])
                    
                    cal_str = 'N/A'
                    if nutrition and len(nutrition) > 0:
                        try:
                            cal = round(float(nutrition[0]), 0)
                            cal_str = f"{cal:.0f} Cal"
                            meal_cal += cal
                            # NOTE: total_calories will sum up calories from *all options* for the first day,
                            # which is technically incorrect for a single day plan, but reflects the sum of options.
                            # We leave this as is since the backend doesn't dictate a single choice.
                            total_calories += cal 
                        except:
                            pass
                            
                    recipe_button = tk.Button(meal_frame, text=f"{recipe_name} ({cal_str})",
                                              command=lambda r=recipe: self.show_recipe_detail(r),
                                              bg=self.colors['bg_tertiary'], fg=self.colors['text_primary'],
                                              font=self.fonts['body'], relief='flat', anchor='w', justify='left', bd=0, padx=10, pady=5)
                    recipe_button.pack(fill=tk.X, padx=10, pady=5)
                # --- END FIX ---
                
                # Show meal total calories (dividing by the number of options for a clearer average)
                if len(recipes) > 0:
                     avg_meal_cal = meal_cal / len(recipes)
                     tk.Label(meal_frame, text=f"Average Recipe: {avg_meal_cal:.0f} Calories (Total Options: {len(recipes)})",
                              font=self.fonts['body'], fg=self.colors['text_secondary'], bg=self.colors['bg_secondary']).pack(anchor='w', padx=10, pady=(5,0))
            else:
                tk.Label(meal_frame, text=f"No suitable recipes found for {meal}.",
                          font=self.fonts['body'], fg=self.colors['text_muted'],
                          bg=self.colors['bg_secondary']).pack(padx=10, pady=5)
                          
        # Final Total Calories Display (Showing the target from the Nutri Matrix)
        target_cal_display = self.nutri_metrics.get('target_calories', 'N/A')
        total_frame = tk.Frame(plan_scrollable_frame, bg=self.colors['bg_secondary'], relief='solid', bd=1)
        total_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        tk.Label(total_frame, text=f"Target Daily Caloric Goal: {target_cal_display} Calories",
                  font=self.fonts['subtitle'], fg=self.colors['accent_primary'], bg=self.colors['bg_secondary'], pady=10).pack(fill=tk.X)
                  
        total_frame.pack_forget()
        total_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        def _on_mousewheel(event):
            try:
                plan_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            except tk.TclError:
                # Catch TclError if canvas is destroyed during scroll
                pass
        plan_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Clear the old matrix title
        self.matrix_title.config(text="Nutrient Target Matrix - Generated!", fg=self.colors['success'])
        # Disable plan button after generation
        self.get_plan_btn.config(state=tk.DISABLED)
    # --- END OF NUTRI-PLANNER SECTION ---
    
    # --- NEW CHATBOT WINDOW AND LOGIC ---
    def show_chatbot_window(self):
        """Displays the FitBite AI Chatbot interface."""
        if not self.current_user:
            self.show_error("Access Denied", "Please log in to use the AI Assistant.")
            return

        chat_window = tk.Toplevel(self.root)
        chat_window.title("FitBite AI Assistant 💬")
        chat_window.geometry("500x700")
        chat_window.configure(bg=self.colors['bg_primary'])
        chat_window.transient(self.root)
        chat_window.grab_set()
        
        # Center the chat window relative to the main window
        self.root.update_idletasks()
        main_x = self.root.winfo_x()
        main_y = self.root.winfo_y()
        main_width = self.root.winfo_width()
        chat_width = chat_window.winfo_reqwidth()
        chat_height = chat_window.winfo_reqheight()

        # Place at bottom-right corner of the main window
        new_x = main_x + main_width - chat_width - 10
        new_y = main_y + self.root.winfo_height() - chat_height - 10
        
        chat_window.geometry(f'+{new_x}+{new_y}')


        # Main frame (bg_secondary for contrast)
        main_frame = tk.Frame(chat_window, bg=self.colors['bg_secondary'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Header
        tk.Label(main_frame, text="FitBite AI 🍏", font=self.fonts['heading'], fg=self.colors['accent_primary'], bg=self.colors['bg_secondary']).pack(pady=(0, 10))
        
        # Chat History Display Area (ScrolledText)
        self.chat_history = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, state=tk.DISABLED, 
                                                     font=self.fonts['chat_bot'], 
                                                     bg=self.colors['bg_tertiary'], # Using tertiary for chat background for a cool look
                                                     fg=self.colors['text_primary'],
                                                     insertbackground=self.colors['accent_primary'],
                                                     relief='sunken', bd=3,
                                                     padx=10, pady=10)
        self.chat_history.tag_config('user', foreground=self.colors['accent_secondary'], font=self.fonts['chat_user'])
        self.chat_history.tag_config('bot', foreground=self.colors['text_primary'], font=self.fonts['chat_bot'])
        self.chat_history.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.append_chat_message("FitBite AI", "Hello! I am your Personal AI Assistant. Ask me anything about nutrition, recipes, or using the app!", is_user=False)


        # Input Frame (bg_secondary)
        input_frame = tk.Frame(main_frame, bg=self.colors['bg_secondary'])
        input_frame.pack(fill=tk.X, pady=(5, 0))
        input_frame.grid_columnconfigure(0, weight=1)

        # User Input Entry
        self.chat_input_entry = tk.Entry(input_frame, font=self.fonts['body'], bg=self.colors['bg_tertiary'],
                                         fg=self.colors['text_primary'], relief='flat', bd=10,
                                         insertbackground=self.colors['accent_primary'])
        self.chat_input_entry.grid(row=0, column=0, sticky='ew', padx=(5, 5), ipady=5)
        self.chat_input_entry.bind('<Return>', lambda e: self.send_chat_message())

        # Send Button
        self.send_chat_button = self.create_modern_button(input_frame, "Send", self.send_chat_message, style='accent')
        self.send_chat_button.config(pady=5)
        self.send_chat_button.grid(row=0, column=1, sticky='e', padx=(0, 5))
        
    def append_chat_message(self, speaker, message, is_user):
        """Helper function to format and append messages to the chat history."""
        tag = 'user' if is_user else 'bot'
        
        self.chat_history.config(state=tk.NORMAL)
        
        # Format: Speaker Name (tagged) + Message Content (tagged)
        self.chat_history.insert(tk.END, f"\n{speaker}: ", tag)
        self.chat_history.insert(tk.END, f"{message}", 'bot')

        self.chat_history.config(state=tk.DISABLED)
        self.chat_history.yview(tk.END) # Auto scroll to bottom

    def send_chat_message(self):
        """Triggers the API call to OpenAI and displays response."""
        user_message = self.chat_input_entry.get().strip()
        if not user_message: return

        # 1. Display user message
        self.append_chat_message(self.current_user, user_message, is_user=True)
        self.chat_input_entry.delete(0, tk.END)

        # Disable input/button while waiting
        self.send_chat_button.config(state=tk.DISABLED, text="Thinking...")
        self.chat_input_entry.config(state=tk.DISABLED)

        # 2. Start API call thread
        threading.Thread(target=self._api_chat_thread, args=(user_message,), daemon=True).start()

    def _api_chat_thread(self, user_message):
        """Threaded function to call the backend chat API."""
        try:
            data = {
                "message": user_message,
                "username": self.current_user or "Guest" 
            }
            # This route must be implemented in app.py to use the OpenAI API
            response = requests.post(f"{self.server_url}/fitbite_ai_chat", json=data, timeout=30)
            result = response.json()
            
            # Check for Rate Limit specifically (HTTP 429)
            if response.status_code == 429:
                ai_response = "I'm experiencing high traffic right now (Rate Limit). Please check your server's API usage or wait a moment!"
                success = False
            elif response.status_code == 200 and result.get("success"):
                ai_response = result.get("response", "I received your message, but the response was empty.")
                success = True
            else:
                # General API or logic error
                ai_response = result.get("response", "Could not process your request. Check the server logs for API errors.")
                success = False
                
        except requests.exceptions.ConnectionError:
            ai_response = "Connection Error: Could not connect to the Flask server. Please ensure the backend is running."
            success = False
        except Exception as e:
            ai_response = f"Unexpected Error: {str(e)}"
            success = False
        
        # 3. Update GUI on the main thread
        self.root.after(0, lambda: self._complete_chat_response(ai_response))

    def _complete_chat_response(self, ai_response):
        """Updates the chat window after the API call finishes."""
        self.append_chat_message("FitBite AI", ai_response, is_user=False)
        
        # Re-enable controls
        self.send_chat_button.config(state=tk.NORMAL, text="Send")
        self.chat_input_entry.config(state=tk.NORMAL)
        self.chat_input_entry.focus()
    # --- END NEW CHATBOT WINDOW AND LOGIC ---

    
    def listen_for_ingredients(self):
        """Use speech recognition to get ingredients."""
        r = sr.Recognizer()
        with sr.Microphone() as source:
            self.show_loading("Listening...")
            try:
                r.adjust_for_ambient_noise(source, duration=0.5)
                audio = r.listen(source, timeout=5)
                self.hide_loading()

                self.show_loading("Recognizing...")
                text = r.recognize_google(audio)
                self.hide_loading()

                processed_text = text.replace(" and ", ", ").replace(" ", ", ")
                self.ingredients_entry.delete(0, tk.END)
                self.ingredients_entry.insert(0, processed_text)
                self.show_success("Voice Input", f"Recognized: {text}")

            except sr.WaitTimeoutError:
                self.hide_loading()
                self.show_error("Voice Input Error", "Listening timed out. Please try again.")
            except sr.UnknownValueError:
                self.hide_loading()
                self.show_error("Voice Input Error", "Could not understand audio. Please speak clearly.")
            except sr.RequestError as e:
                self.hide_loading()
                self.show_error("Voice Service Error", f"Could not request results; {e}")
            except Exception as e:
                self.hide_loading()
                self.show_error("Error", f"An unexpected error occurred: {e}")

    def create_filter_entry(self, parent, label_text, attr_name, column):
        """Create a filter text entry with modern styling"""
        filter_frame = tk.Frame(parent, bg=self.colors['bg_secondary'])
        filter_frame.grid(row=0, column=column, padx=10, sticky='ew')
        
        parent.grid_columnconfigure(column, weight=1)
        
        label = tk.Label(filter_frame, text=label_text, font=self.fonts['small'], fg=self.colors['text_muted'], bg=self.colors['bg_secondary'])
        label.pack(anchor='w', pady=(0, 5))
        
        entry = tk.Entry(filter_frame, font=self.fonts['body'], bg=self.colors['bg_tertiary'], fg=self.colors['text_primary'], relief='flat', bd=5, insertbackground=self.colors['accent_primary'])
        entry.pack(fill=tk.X, ipady=4)
        setattr(self, attr_name, entry)

    def create_filter_dropdown(self, parent, label_text, var_name, options, column):
        """Create filter dropdown with modern styling"""
        filter_frame = tk.Frame(parent, bg=self.colors['bg_secondary'])
        filter_frame.grid(row=0, column=column, padx=10, sticky='ew')
        
        parent.grid_columnconfigure(column, weight=1)
        
        label = tk.Label(filter_frame, text=label_text, font=self.fonts['small'], fg=self.colors['text_muted'], bg=self.colors['bg_secondary'])
        label.pack(anchor='w', pady=(0, 5))
        
        var = tk.StringVar(value=options[0])
        setattr(self, var_name, var)
        
        combo = ttk.Combobox(filter_frame, textvariable=var, values=options, state='readonly', style='Modern.TCombobox', font=self.fonts['body'])
        combo.pack(fill=tk.X)
    
    def search_recipes(self, event=None):
        """Search for recipes and show results in new window"""
        ingredients = self.ingredients_entry.get().strip()
        if not ingredients:
            self.show_error("Error", "Please enter ingredients")
            return
        
        prep_time = getattr(self, 'prep_time_entry', tk.Entry()).get().strip()
        diet = getattr(self, 'diet_var', tk.StringVar()).get()
        cuisine = getattr(self, 'cuisine_var', tk.StringVar()).get()
        meal_type = getattr(self, 'meal_var', tk.StringVar()).get()
        
        self.show_loading("Searching for recipes...")
        
        def search_thread():
            try:
                data = {"ingredients": ingredients, "username": self.current_user}
                if prep_time: data["prep_time"] = prep_time
                if diet != "Any": data["dietary_preference"] = diet
                if cuisine != "Any": data["cuisine"] = cuisine
                if meal_type != "Any": data["meal_type"] = meal_type
                
                response = requests.post(f"{self.server_url}/recommend", json=data, timeout=30)
                
                self.root.after(0, self.hide_loading)
                
                if response.status_code == 200:
                    result = response.json()
                    recipes = result.get("recommendations", [])
                    self.current_recipes = recipes
                    self.root.after(0, lambda: self.show_recipe_results(recipes, ingredients))
                else:
                    error_msg = response.json().get("error", "Search failed")
                    self.root.after(0, lambda: self.show_error("Search Failed", error_msg))
                    
            except Exception as e:
                self.root.after(0, self.hide_loading)
                self.root.after(0, lambda: self.show_error("Error", f"Search failed: {str(e)}"))
        
        threading.Thread(target=search_thread, daemon=True).start()
        
    def show_recipe_results(self, recipes, search_ingredients):
        """Display recipe search results in new window"""
        results_window = tk.Toplevel(self.root)
        results_window.title("Recipe Results - FitBite")
        results_window.geometry("1000x700")
        results_window.configure(bg=self.colors['bg_primary'])
        
        header_frame = tk.Frame(results_window, bg=self.colors['bg_secondary'])
        header_frame.pack(fill=tk.X, padx=20, pady=20)
        
        header_inner = tk.Frame(header_frame, bg=self.colors['bg_secondary'])
        header_inner.pack(padx=20, pady=15)
        
        title = tk.Label(header_inner, text=f"Found {len(recipes)} recipes", font=self.fonts['title'], fg=self.colors['text_primary'], bg=self.colors['bg_secondary'])
        title.pack(anchor='w')
        
        subtitle = tk.Label(header_inner, text=f"Based on: {search_ingredients}", font=self.fonts['body'], fg=self.colors['text_secondary'], bg=self.colors['bg_secondary'])
        subtitle.pack(anchor='w', pady=(5, 0))
        
        canvas = tk.Canvas(results_window, bg=self.colors['bg_primary'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(results_window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['bg_primary'])
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=(20, 0), pady=(0, 20))
        scrollbar.pack(side="right", fill="y", padx=(0, 20), pady=(0, 20))
        
        if not recipes:
            empty_label = tk.Label(scrollable_frame, text="No recipes found matching your criteria.", font=self.fonts['subtitle'], fg=self.colors['text_muted'], bg=self.colors['bg_primary'])
            empty_label.pack(pady=50)
        else:
            for i, recipe in enumerate(recipes):
                self.create_recipe_card(scrollable_frame, recipe, i)
        
        def _on_mousewheel(event):
            try:
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            except tk.TclError:
                # Catch TclError if canvas is destroyed during scroll
                pass
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    def create_recipe_card(self, parent, recipe, index):
        """Create recipe card with modern styling"""
        card_frame = tk.Frame(parent, bg=self.colors['bg_secondary'], relief='solid', bd=1)
        card_frame.pack(fill=tk.X, padx=0, pady=10)
        
        card_inner = tk.Frame(card_frame, bg=self.colors['bg_secondary'])
        card_inner.pack(fill=tk.X, padx=20, pady=20)
        
        header_row = tk.Frame(card_inner, bg=self.colors['bg_secondary'])
        header_row.pack(fill=tk.X, pady=(0, 10))
        
        title = tk.Label(header_row, text=recipe.get('name', 'Unknown Recipe'), font=self.fonts['heading'], fg=self.colors['text_primary'], bg=self.colors['bg_secondary'])
        title.pack(side=tk.LEFT)
        
        actions_frame = tk.Frame(header_row, bg=self.colors['bg_secondary'])
        actions_frame.pack(side=tk.RIGHT)
        
        rating = recipe.get('avg_rating', '0.0')
        num_ratings = recipe.get('num_ratings', 0)
        rating_text = f"★ {rating} ({num_ratings} reviews)"
        rating_label = tk.Label(actions_frame, text=rating_text, font=self.fonts['small'], fg=self.colors['text_secondary'], bg=self.colors['bg_secondary'])
        rating_label.pack(side=tk.LEFT, padx=(0, 15))
        
        is_favorited = recipe.get('is_favorited', False)
        fav_text = "❤️" if is_favorited else "🤍"
        fav_btn = tk.Button(actions_frame, text=fav_text, font=self.fonts['body'], bg=self.colors['bg_secondary'], fg=self.colors['accent_primary'], relief='flat', bd=0, cursor='hand2')
        fav_btn.configure(command=lambda r_id=recipe['id'], b=fav_btn: self.toggle_favorite(r_id, b))
        fav_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        info_row = tk.Frame(card_inner, bg=self.colors['bg_secondary'])
        info_row.pack(fill=tk.X, pady=(0, 10))
        
        prep_time = recipe.get('prep_time', 0)
        time_label = tk.Label(info_row, text=f"🕒 {prep_time} min", font=self.fonts['small'], fg=self.colors['text_muted'], bg=self.colors['bg_secondary'])
        time_label.pack(side=tk.LEFT, padx=(0, 20))
        
        ingredients_count = len(recipe.get('ingredients', []))
        ingredients_label = tk.Label(info_row, text=f"🥘 {ingredients_count} ingredients", font=self.fonts['small'], fg=self.colors['text_muted'], bg=self.colors['bg_secondary'])
        ingredients_label.pack(side=tk.LEFT)
        
        description = recipe.get('description', '')[:150]
        if len(recipe.get('description', '')) > 150:
            description += "..."
            
        desc_label = tk.Label(card_inner, text=description, font=self.fonts['body'], fg=self.colors['text_secondary'], bg=self.colors['bg_secondary'], wraplength=800, justify=tk.LEFT)
        desc_label.pack(anchor='w', pady=(0, 15))
        
        buttons_frame = tk.Frame(card_inner, bg=self.colors['bg_secondary'])
        buttons_frame.pack(fill=tk.X)
        
        view_btn = self.create_modern_button(buttons_frame, "View Recipe", lambda r=recipe: self.show_recipe_detail(r), style='accent')
        view_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        rate_btn = self.create_modern_button(buttons_frame, "Rate Recipe", lambda r=recipe: self.show_rating_dialog(r))
        rate_btn.pack(side=tk.LEFT)
    
    def toggle_favorite(self, recipe_id, button):
        """Toggle favorite status of a recipe"""
        def favorite_thread():
            try:
                data = {"username": self.current_user, "recipe_id": recipe_id, "action": "toggle"}
                response = requests.post(f"{self.server_url}/favorite_recipe", json=data, timeout=10)
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("success"):
                        is_favorited = result.get("is_favorited", False)
                        new_text = "❤️" if is_favorited else "🤍"
                        self.root.after(0, lambda: button.configure(text=new_text))
                    else:
                        self.root.after(0, lambda: self.show_error("Error", result.get("message", "Could not update favorite.")))
                else:
                    self.root.after(0, lambda: self.show_error("Server Error", f"Failed to update favorite (Code: {response.status_code})"))
            except Exception as e:
                self.root.after(0, lambda: self.show_error("Error", f"Error toggling favorite: {e}"))
        
        threading.Thread(target=favorite_thread, daemon=True).start()
        
    def show_recipe_detail(self, recipe):
        """Show detailed recipe view in new window"""
        detail_window = tk.Toplevel(self.root)
        detail_window.title(f"{recipe.get('name', 'Recipe')} - FitBite")
        detail_window.geometry("800x600")
        detail_window.configure(bg=self.colors['bg_primary'])
        
        canvas = tk.Canvas(detail_window, bg=self.colors['bg_primary'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(detail_window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['bg_primary'])
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        header_frame = tk.Frame(scrollable_frame, bg=self.colors['bg_secondary'])
        header_frame.pack(fill=tk.X, padx=20, pady=20)
        
        header_inner = tk.Frame(header_frame, bg=self.colors['bg_secondary'])
        header_inner.pack(padx=20, pady=20)
        
        title = tk.Label(header_inner, text=recipe.get('name', 'Unknown Recipe'), font=self.fonts['title'], fg=self.colors['text_primary'], bg=self.colors['bg_secondary'], wraplength=700, justify=tk.LEFT)
        title.pack(anchor='w')
        
        info_frame = tk.Frame(header_inner, bg=self.colors['bg_secondary'])
        info_frame.pack(anchor='w', pady=(10, 0))
        
        rating = recipe.get('avg_rating', '0.0')
        prep_time = recipe.get('prep_time', 0)
        info_text = f"★ {rating} • 🕒 {prep_time} min"
        
        info_label = tk.Label(info_frame, text=info_text, font=self.fonts['body'], fg=self.colors['text_secondary'], bg=self.colors['bg_secondary'])
        info_label.pack(anchor='w')
        
        ingredients_frame = tk.Frame(scrollable_frame, bg=self.colors['bg_secondary'])
        ingredients_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        ingredients_inner = tk.Frame(ingredients_frame, bg=self.colors['bg_secondary'])
        ingredients_inner.pack(padx=20, pady=20)
        
        ingredients_title = tk.Label(ingredients_inner, text="Ingredients", font=self.fonts['subtitle'], fg=self.colors['text_primary'], bg=self.colors['bg_secondary'])
        ingredients_title.pack(anchor='w', pady=(0, 10))
        
        ingredients = recipe.get('ingredients', [])
        # --- FIX: Ensure ingredients are always treated as a list (backend fix ensures list conversion) ---
        if not isinstance(ingredients, list):
             # Fallback just in case backend data is outdated/corrupted, though backend fix should handle this.
             ingredients = [str(ingredients)] 
            
        for ingredient in ingredients:
            ing_label = tk.Label(ingredients_inner, text=f"• {ingredient}", font=self.fonts['body'], fg=self.colors['text_secondary'], bg=self.colors['bg_secondary'])
            ing_label.pack(anchor='w', pady=2)
        # --- END FIX ---
        
        if recipe.get('steps'):
            instructions_frame = tk.Frame(scrollable_frame, bg=self.colors['bg_secondary'])
            instructions_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
            
            instructions_inner = tk.Frame(instructions_frame, bg=self.colors['bg_secondary'])
            instructions_inner.pack(padx=20, pady=20)
            
            instructions_title = tk.Label(instructions_inner, text="Instructions", font=self.fonts['subtitle'], fg=self.colors['text_primary'], bg=self.colors['bg_secondary'])
            instructions_title.pack(anchor='w', pady=(0, 10))
            
            steps = recipe.get('steps', [])
            # --- FIX: Ensure steps are always treated as a list ---
            if not isinstance(steps, list):
                steps = [str(steps)]
            
            for i, step in enumerate(steps, 1):
                step_label = tk.Label(instructions_inner, text=f"{i}. {step}", font=self.fonts['body'], fg=self.colors['text_secondary'], bg=self.colors['bg_secondary'], wraplength=700, justify=tk.LEFT)
                step_label.pack(anchor='w', pady=5)
            # --- END FIX ---
        
        if recipe.get('nutrition'):
            nutrition_frame = tk.Frame(scrollable_frame, bg=self.colors['bg_secondary'])
            nutrition_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
            
            nutrition_inner = tk.Frame(nutrition_frame, bg=self.colors['bg_secondary'])
            nutrition_inner.pack(padx=20, pady=20)
            
            nutrition_title = tk.Label(nutrition_inner, text="Nutrition Information", font=self.fonts['subtitle'], fg=self.colors['text_primary'], bg=self.colors['bg_secondary'])
            nutrition_title.pack(anchor='w', pady=(0, 10))
            
            nutrition = recipe.get('nutrition', [])
            nutrition_labels = ['Calories', 'Fat (g)', 'Saturated Fat (g)', 'Cholesterol (mg)', 'Sodium (mg)', 'Carbs (g)', 'Fiber (g)', 'Sugar (g)', 'Protein (g)']
            
            for i, value in enumerate(nutrition):
                if i < len(nutrition_labels):
                    nutrition_text = f"{nutrition_labels[i]}: {value}"
                    nutr_label = tk.Label(nutrition_inner, text=nutrition_text, font=self.fonts['body'], fg=self.colors['text_secondary'], bg=self.colors['bg_secondary'])
                    nutr_label.pack(anchor='w', pady=2)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        def _on_mousewheel(event):
            try:
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            except tk.TclError:
                # Catch TclError if canvas is destroyed during scroll
                pass
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    def show_rating_dialog(self, recipe):
        """Show rating dialog for a recipe"""
        rating_window = tk.Toplevel(self.root)
        rating_window.title("Rate Recipe")
        rating_window.geometry("400x300")
        rating_window.configure(bg=self.colors['bg_primary'])
        rating_window.resizable(False, False)
        
        rating_window.transient(self.root)
        rating_window.grab_set()
        
        main_frame = tk.Frame(rating_window, bg=self.colors['bg_secondary'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        inner_frame = tk.Frame(main_frame, bg=self.colors['bg_secondary'])
        inner_frame.pack(expand=True, padx=20, pady=20)
        
        title = tk.Label(inner_frame, text="Rate this Recipe", font=self.fonts['heading'], fg=self.colors['text_primary'], bg=self.colors['bg_secondary'])
        title.pack(pady=(0, 10))
        
        recipe_name = tk.Label(inner_frame, text=recipe.get('name', 'Unknown Recipe'), font=self.fonts['body'], fg=self.colors['text_secondary'], bg=self.colors['bg_secondary'])
        recipe_name.pack(pady=(0, 20))
        
        rating_frame = tk.Frame(inner_frame, bg=self.colors['bg_secondary'])
        rating_frame.pack(pady=20)
        
        rating_var = tk.IntVar(value=0)
        star_buttons = []
        
        def update_stars(rating):
            rating_var.set(rating)
            for i, btn in enumerate(star_buttons):
                btn.configure(text="★" if i < rating else "☆", fg=self.colors['accent_primary'] if i < rating else self.colors['text_muted'])
        
        for i in range(5):
            star_btn = tk.Button(rating_frame, text="☆", font=('Helvetica', 20), fg=self.colors['text_muted'], bg=self.colors['bg_secondary'], relief='flat', bd=0, cursor='hand2', command=lambda r=i+1: update_stars(r))
            star_btn.pack(side=tk.LEFT, padx=2)
            star_buttons.append(star_btn)
        
        button_frame = tk.Frame(inner_frame, bg=self.colors['bg_secondary'])
        button_frame.pack(pady=(20, 0), fill=tk.X)
        
        def submit_rating():
            rating = rating_var.get()
            if rating == 0:
                messagebox.showwarning("No Rating", "Please select a rating", parent=rating_window)
                return
            
            def rating_thread():
                try:
                    data = {"username": self.current_user, "recipe_id": recipe['id'], "rating": rating}
                    response = requests.post(f"{self.server_url}/rate_recipe", json=data, timeout=10)
                    result = response.json()

                    if response.status_code == 200 and result.get("success"):
                        self.root.after(0, lambda: self.show_success("Success", "Rating saved successfully!"))
                        self.root.after(0, rating_window.destroy)
                    else:
                        self.root.after(0, lambda: self.show_error("Error", result.get("message", "Failed to save rating")))
                        
                except Exception as e:
                    self.root.after(0, lambda: self.show_error("Error", f"Error saving rating: {str(e)}"))
            
            threading.Thread(target=rating_thread, daemon=True).start()
        
        submit_btn = self.create_modern_button(button_frame, "Submit Rating", submit_rating, style='accent')
        submit_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        cancel_btn = self.create_modern_button(button_frame, "Cancel", rating_window.destroy)
        cancel_btn.pack(side=tk.RIGHT)
    
    def show_favorites(self):
        """Display user's favorite recipes"""
        self.clear_main_frame()
        self.create_navigation_bar()
        self.create_floating_chat_button() # Re-add floating button
        self.show_loading("Loading favorites...")
        
        def load_favorites_thread():
            try:
                data = {"username": self.current_user}
                response = requests.post(f"{self.server_url}/get_favorites", json=data, timeout=10)
                
                self.root.after(0, self.hide_loading)
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("success"):
                        self.root.after(0, lambda: self.display_favorites(result.get("favorites", [])))
                    else:
                        self.root.after(0, lambda: self.show_error("Error", result.get("message", "Failed to load favorites")))
                else:
                    self.root.after(0, lambda: self.show_error("Error", "Failed to load favorites"))
                    
            except Exception as e:
                self.root.after(0, self.hide_loading)
                self.root.after(0, lambda: self.show_error("Error", f"Error loading favorites: {str(e)}"))
        
        threading.Thread(target=load_favorites_thread, daemon=True).start()
    
    def display_favorites(self, favorites):
        """Display the favorites list"""
        content_frame = tk.Frame(self.main_frame, bg=self.colors['bg_primary'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        header_frame = tk.Frame(content_frame, bg=self.colors['bg_secondary'])
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        header_inner = tk.Frame(header_frame, bg=self.colors['bg_secondary'])
        header_inner.pack(padx=30, pady=20)
        
        back_btn = self.create_link_button(header_inner, "← Back to Dashboard", self.show_main_dashboard)
        back_btn.pack(anchor='w', pady=(0, 15))
        
        title = tk.Label(header_inner, text=f"My Favorites ({len(favorites)} recipes)", font=self.fonts['title'], fg=self.colors['text_primary'], bg=self.colors['bg_secondary'])
        title.pack(anchor='w')
        
        if not favorites:
            empty_frame = tk.Frame(content_frame, bg=self.colors['bg_secondary'])
            empty_frame.pack(fill=tk.BOTH, expand=True)
            empty_inner = tk.Frame(empty_frame, bg=self.colors['bg_secondary'])
            empty_inner.pack(expand=True)
            empty_label = tk.Label(empty_inner, text="No favorite recipes yet", font=self.fonts['subtitle'], fg=self.colors['text_muted'], bg=self.colors['bg_secondary'])
            empty_label.pack()
            empty_desc = tk.Label(empty_inner, text="Start exploring recipes and add them to your favorites!", font=self.fonts['body'], fg=self.colors['text_secondary'], bg=self.colors['bg_secondary'])
            empty_desc.pack(pady=(10, 0))
            find_btn = self.create_modern_button(empty_inner, "Find Recipes", self.show_recipe_finder, style='accent')
            find_btn.pack(pady=20)
        else:
            canvas = tk.Canvas(content_frame, bg=self.colors['bg_primary'], highlightthickness=0)
            scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg=self.colors['bg_primary'])
            scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            for i, recipe in enumerate(favorites):
                # Ensure is_favorited is set to True for favorites list
                recipe['is_favorited'] = True 
                self.create_recipe_card(scrollable_frame, recipe, i)
            def _on_mousewheel(event):
                try:
                    canvas.yview_scroll(int(-1*(event.delta/120)), "units")
                except tk.TclError:
                    # Catch TclError if canvas is destroyed during scroll
                    pass
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    def show_meal_planner(self):
        """Display meal planner interface"""
        self.clear_main_frame()
        self.create_navigation_bar()
        self.create_floating_chat_button() # Re-add floating button
        content_frame = tk.Frame(self.main_frame, bg=self.colors['bg_primary'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        header_frame = tk.Frame(content_frame, bg=self.colors['bg_secondary'])
        header_frame.pack(fill=tk.X, pady=(0, 20))
        header_inner = tk.Frame(header_frame, bg=self.colors['bg_secondary'])
        header_inner.pack(padx=30, pady=20)
        back_btn = self.create_link_button(header_inner, "← Back to Dashboard", self.show_main_dashboard)
        back_btn.pack(anchor='w', pady=(0, 15))
        title = tk.Label(header_inner, text="Meal Planner", font=self.fonts['title'], fg=self.colors['text_primary'], bg=self.colors['bg_secondary'])
        title.pack(anchor='w')
        subtitle = tk.Label(header_inner, text="Generate a 7-day meal plan based on your search history", font=self.fonts['body'], fg=self.colors['text_secondary'], bg=self.colors['bg_secondary'])
        subtitle.pack(anchor='w', pady=(5, 0))
        generator_frame = tk.Frame(content_frame, bg=self.colors['bg_secondary'])
        generator_frame.pack(fill=tk.X, pady=(0, 20))
        generator_inner = tk.Frame(generator_frame, bg=self.colors['bg_secondary'])
        generator_inner.pack(padx=30, pady=20)
        generate_btn = self.create_modern_button(generator_inner, "Generate 7-Day Meal Plan", self.generate_meal_plan, style='accent')
        generate_btn.pack()
        self.meal_plan_frame = tk.Frame(content_frame, bg=self.colors['bg_primary'])
        self.meal_plan_frame.pack(fill=tk.BOTH, expand=True)
    
    def generate_meal_plan(self):
        """Generate a 7-day meal plan."""
        for widget in self.meal_plan_frame.winfo_children():
            widget.destroy()
        self.show_loading("Generating your meal plan...")
        
        def generate_thread():
            try:
                data = {"username": self.current_user, "days": 7}
                response = requests.post(f"{self.server_url}/generate_meal_plan", json=data, timeout=30)
                self.root.after(0, self.hide_loading)
                if response.status_code == 200:
                    result = response.json()
                    if result.get("success"):
                        self.root.after(0, lambda: self.display_meal_plan(result.get("meal_plan", []), result.get("based_on_ingredients", [])))
                    else:
                        self.root.after(0, lambda: self.show_error("Error", result.get("message", "Failed to generate meal plan")))
                else:
                    self.root.after(0, lambda: self.show_error("Error", f"Server returned status {response.status_code}"))
            except Exception as e:
                self.root.after(0, self.hide_loading)
                self.root.after(0, lambda: self.show_error("Error", f"Error generating meal plan: {str(e)}"))
        
        threading.Thread(target=generate_thread, daemon=True).start()
    
    def display_meal_plan(self, meal_plan, ingredients_used):
        """Display the generated meal plan"""
        plan_header = tk.Frame(self.meal_plan_frame, bg=self.colors['bg_secondary'])
        plan_header.pack(fill=tk.X, pady=(0, 20))
        plan_header_inner = tk.Frame(plan_header, bg=self.colors['bg_secondary'])
        plan_header_inner.pack(padx=30, pady=15)
        plan_title = tk.Label(plan_header_inner, text=f"Your {len(meal_plan)}-Day Meal Plan", font=self.fonts['subtitle'], fg=self.colors['text_primary'], bg=self.colors['bg_secondary'])
        plan_title.pack(anchor='w')
        if ingredients_used:
            ingredients_text = f"Based on your favorite ingredients: {', '.join(ingredients_used)}"
            ingredients_label = tk.Label(plan_header_inner, text=ingredients_text, font=self.fonts['small'], fg=self.colors['text_secondary'], bg=self.colors['bg_secondary'])
            ingredients_label.pack(anchor='w', pady=(5, 0))
        canvas = tk.Canvas(self.meal_plan_frame, bg=self.colors['bg_primary'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.meal_plan_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['bg_primary'])
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        for day_plan in meal_plan:
            self.create_day_card(scrollable_frame, day_plan)
        def _on_mousewheel(event):
            try:
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            except tk.TclError:
                # Catch TclError if canvas is destroyed during scroll
                pass
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    def create_day_card(self, parent, day_plan):
        """Create a card for each day's meal plan"""
        day_frame = tk.Frame(parent, bg=self.colors['bg_secondary'], relief='solid', bd=1)
        day_frame.pack(fill=tk.X, padx=0, pady=10)
        day_inner = tk.Frame(day_frame, bg=self.colors['bg_secondary'])
        day_inner.pack(fill=tk.X, padx=20, pady=20)
        day_header = tk.Frame(day_inner, bg=self.colors['bg_secondary'])
        day_header.pack(fill=tk.X, pady=(0, 15))
        day_title = tk.Label(day_header, text=f"Day {day_plan['day']} - {day_plan['date']}", font=self.fonts['heading'], fg=self.colors['text_primary'], bg=self.colors['bg_secondary'])
        day_title.pack(anchor='w')
        meals, meal_types = day_plan.get('meals', {}), ['breakfast', 'lunch', 'dinner']
        for meal_type in meal_types:
            if meal_type in meals and meals[meal_type]:
                self.create_meal_item(day_inner, meal_type.capitalize(), meals[meal_type])
    
    def create_meal_item(self, parent, meal_type, recipe):
        """Create a meal item within a day card"""
        meal_frame = tk.Frame(parent, bg=self.colors['bg_tertiary'])
        meal_frame.pack(fill=tk.X, pady=5)
        meal_inner = tk.Frame(meal_frame, bg=self.colors['bg_tertiary'])
        meal_inner.pack(fill=tk.X, padx=15, pady=10)
        meal_header = tk.Frame(meal_inner, bg=self.colors['bg_tertiary'])
        meal_header.pack(fill=tk.X)
        meal_type_label = tk.Label(meal_header, text=f"{meal_type}:", font=self.fonts['body'], fg=self.colors['accent_primary'], bg=self.colors['bg_tertiary'])
        meal_type_label.pack(side=tk.LEFT)
        recipe_name_label = tk.Label(meal_header, text=recipe.get('name', 'Unknown Recipe'), font=self.fonts['body'], fg=self.colors['text_primary'], bg=self.colors['bg_tertiary'])
        recipe_name_label.pack(side=tk.LEFT, padx=(10, 0))
        view_btn = tk.Button(meal_header, text="View", font=self.fonts['small'], bg=self.colors['accent_primary'], fg=self.colors['bg_primary'], relief='flat', bd=0, cursor='hand2', command=lambda r=recipe: self.show_recipe_detail(r))
        view_btn.pack(side=tk.RIGHT)
        info_text = f"Time: {recipe.get('prep_time', 0)} min | Rating: {recipe.get('avg_rating', '0.0')}"
        info_label = tk.Label(meal_inner, text=info_text, font=self.fonts['small'], fg=self.colors['text_muted'], bg=self.colors['bg_tertiary'])
        info_label.pack(anchor='w', pady=(5, 0))
    
    def show_user_stats(self):
        """Display user statistics"""
        self.clear_main_frame()
        self.create_navigation_bar()
        self.create_floating_chat_button() # Re-add floating button
        self.show_loading("Loading your statistics...")
        
        def load_stats_thread():
            try:
                data = {"username": self.current_user}
                response = requests.post(f"{self.server_url}/user_stats", json=data, timeout=10)
                self.root.after(0, self.hide_loading)
                if response.status_code == 200:
                    result = response.json()
                    if result.get("success"):
                        self.root.after(0, lambda: self.display_user_stats(result.get("stats", {})))
                    else:
                        self.root.after(0, lambda: self.show_error("Error", result.get("error", "Failed to load statistics")))
                else:
                    self.root.after(0, lambda: self.show_error("Error", "Failed to load statistics"))
            except Exception as e:
                self.root.after(0, self.hide_loading)
                self.root.after(0, lambda: self.show_error("Error", f"Error loading statistics: {str(e)}"))
        
        threading.Thread(target=load_stats_thread, daemon=True).start()
    
    def display_user_stats(self, stats):
        """Display user statistics"""
        content_frame = tk.Frame(self.main_frame, bg=self.colors['bg_primary'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        header_frame = tk.Frame(content_frame, bg=self.colors['bg_secondary'])
        header_frame.pack(fill=tk.X, pady=(0, 20))
        header_inner = tk.Frame(header_frame, bg=self.colors['bg_secondary'])
        header_inner.pack(padx=30, pady=20)
        back_btn = self.create_link_button(header_inner, "← Back to Dashboard", self.show_main_dashboard)
        back_btn.pack(anchor='w', pady=(0, 15))
        title = tk.Label(header_inner, text=f"Statistics for {self.current_user}", font=self.fonts['title'], fg=self.colors['text_primary'], bg=self.colors['bg_secondary'])
        title.pack(anchor='w')
        
        # --- FIX: Added NutriPlanner Stats ---
        stats_grid = tk.Frame(content_frame, bg=self.colors['bg_primary'])
        stats_grid.pack(fill=tk.BOTH, expand=True)
        
        for i in range(3): # Now 3 rows
            stats_grid.grid_rowconfigure(i, weight=1)
            stats_grid.grid_columnconfigure(i, weight=1)
            
        # Row 0: Rating & Favorites
        self.create_stat_card(stats_grid, "Total Ratings", str(stats.get('total_ratings', 0)), 0, 0)
        self.create_stat_card(stats_grid, "Favorite Recipes", str(stats.get('total_favorites', 0)), 0, 1)
        self.create_stat_card(stats_grid, "Recipe Searches", str(stats.get('total_searches', 0)), 0, 2)
        
        # Row 1: Averages
        avg_rating = stats.get('average_rating_given', 0)
        avg_text = f"{avg_rating}/5.0" if avg_rating > 0 else "No ratings yet"
        self.create_stat_card(stats_grid, "Average Rating Given", avg_text, 1, 0)
        
        # New NutriPlanner Stats
        total_plans = stats.get('total_meal_plans_generated', 0)
        avg_cal = stats.get('average_target_calories', 'N/A')
        
        self.create_stat_card(stats_grid, "Meal Plans Generated", str(total_plans), 1, 1)
        self.create_stat_card(stats_grid, "Average Calorie Goal", f"{avg_cal} Cal", 1, 2)

        info_frame = tk.Frame(content_frame, bg=self.colors['bg_secondary'])
        info_frame.pack(fill=tk.X, pady=(20, 0))
        info_inner = tk.Frame(info_frame, bg=self.colors['bg_secondary'])
        info_inner.pack(padx=30, pady=20)
        top_ingredients = stats.get('top_ingredients', [])
        
        if top_ingredients:
            ingredients_title = tk.Label(info_inner, text="Your Most Searched Ingredients:", font=self.fonts['heading'], fg=self.colors['text_primary'], bg=self.colors['bg_secondary'])
            ingredients_title.pack(anchor='w', pady=(0, 10))
            ingredients_text = ", ".join(top_ingredients[:10])
            ingredients_label = tk.Label(info_inner, text=ingredients_text, font=self.fonts['body'], fg=self.colors['text_secondary'], bg=self.colors['bg_secondary'], wraplength=800)
            ingredients_label.pack(anchor='w')
            
        member_since = stats.get('member_since', '')
        if member_since:
            try:
                from datetime import datetime
                member_date = datetime.fromisoformat(member_since.replace('Z', '+00:00'))
                member_text = f"Member since {member_date.strftime('%B %d, %Y')}"
                member_label = tk.Label(info_inner, text=member_text, font=self.fonts['small'], fg=self.colors['text_muted'], bg=self.colors['bg_secondary'])
                member_label.pack(anchor='w', pady=(20, 0))
            except: pass
        # --- END FIX ---
    
    def create_stat_card(self, parent, title, value, row, col):
        """Create a statistics card"""
        card_frame = tk.Frame(parent, bg=self.colors['bg_secondary'], relief='solid', bd=1)
        card_frame.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
        card_inner = tk.Frame(card_frame, bg=self.colors['bg_secondary'])
        card_inner.pack(expand=True, padx=30, pady=30)
        value_label = tk.Label(card_inner, text=value, font=('Helvetica', 24, 'bold'), fg=self.colors['accent_primary'], bg=self.colors['bg_secondary'])
        value_label.pack()
        title_label = tk.Label(card_inner, text=title, font=self.fonts['body'], fg=self.colors['text_secondary'], bg=self.colors['bg_secondary'])
        title_label.pack(pady=(10, 0))
    
    def logout(self):
        """Handle user logout"""
        self.current_user, self.user_favorites, self.current_recipes = None, [], []
        
        # --- NEW: Hide floating button on logout ---
        if hasattr(self, 'floating_chat_canvas') and self.floating_chat_canvas and self.floating_chat_canvas.winfo_exists():
            self.floating_chat_canvas.place_forget()
        # --- END NEW ---
        
        self.show_login_screen()
    
    def show_loading(self, message="Loading..."):
        """Show loading overlay"""
        self.hide_loading()
        self.loading_overlay = tk.Toplevel(self.root)
        self.loading_overlay.overrideredirect(True)
        self.loading_overlay.geometry("300x150")
        self.loading_overlay.configure(bg=self.colors['bg_secondary'])
        self.loading_overlay.transient(self.root)
        self.loading_overlay.grab_set()
        
        self.loading_overlay.geometry(f"+{int(self.root.winfo_x() + (self.root.winfo_width()/2) - 150)}+{int(self.root.winfo_y() + (self.root.winfo_height()/2) - 75)}")
        
        loading_frame = tk.Frame(self.loading_overlay, bg=self.colors['bg_secondary'])
        loading_frame.pack(expand=True, fill=tk.BOTH)
        
        self.loading_label = tk.Label(loading_frame, text=message, font=self.fonts['body'], fg=self.colors['text_primary'], bg=self.colors['bg_secondary'])
        self.loading_label.pack(expand=True)
        
        self.animation_id = self.root.after(500, self.animate_loading)
    
    def animate_loading(self):
        """Animate loading text"""
        if hasattr(self, 'loading_label') and self.loading_label.winfo_exists():
            current_text = self.loading_label.cget('text')
            base_text = current_text.split('.')[0]
            dots = (current_text.count('.') + 1) % 4
            self.loading_label.config(text=f"{base_text}{'.' * dots}")
            self.animation_id = self.root.after(500, self.animate_loading)
    
    def hide_loading(self):
        """Hide loading overlay"""
        if hasattr(self, 'animation_id') and self.animation_id:
            self.root.after_cancel(self.animation_id)
            self.animation_id = None
        if hasattr(self, 'loading_overlay') and self.loading_overlay.winfo_exists():
            self.loading_overlay.destroy()

    def show_error(self, title, message):
        messagebox.showerror(title, message)
    
    def show_success(self, title, message):
        messagebox.showinfo(title, message)

if __name__ == "__main__":
    root = tk.Tk()
    app = FitBiteGUI(root)
    root.mainloop()