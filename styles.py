import streamlit as st
from typing import Optional, Dict, Any
from dataclasses import dataclass

@dataclass
class ThemeConfig:
    """Configuration class for theme customization."""
    primary_color: str = "#026607"
    secondary_color: str = "#035509"
    accent_color: str = "#014405"
    background_light: str = "#f8f9fa"
    background_dark: str = "#e9ecef"
    text_color: str = "#333"
    border_radius: str = "15px"
    button_radius: str = "25px"
    shadow_color: str = "rgba(2, 102, 7, 0.3)"
    # New background image properties
    background_image_url: Optional[str] = None
    background_opacity: float = 0.1
    background_size: str = "cover"
    background_position: str = "center"
    background_repeat: str = "no-repeat"
    background_attachment: str = "fixed"

class StreamlitChatTheme:
    """A reusable CSS theme class for Streamlit chat applications."""
    
    def __init__(self, config: Optional[ThemeConfig] = None):
        """Initialize the theme with custom configuration."""
        self.config = config or ThemeConfig()
    
    def _hex_to_rgb(self, hex_color: str) -> tuple:
        """Convert hex color to RGB tuple."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def apply_theme(self, hide_streamlit_branding: bool = True) -> None:
        """Apply the complete theme to the Streamlit app."""
        css = self._build_css(hide_streamlit_branding)
        st.markdown(css, unsafe_allow_html=True)
    
    def _build_css(self, hide_branding: bool) -> str:
        """Build the complete CSS string."""
        css_parts = []
        
        if hide_branding:
            css_parts.append(self._get_branding_css())
        
        css_parts.extend([
            self._get_background_css(),
            self._get_main_container_css(),
            self._get_chat_message_css(),
            self._get_form_css(),
            self._get_button_css(),
            self._get_title_css(),
            self._get_tab_css(),
            self._get_file_uploader_css(),
            self._get_responsive_css()
        ])
        
        return f"<style>{''.join(css_parts)}</style>"
    
    def _get_branding_css(self) -> str:
        """CSS to hide Streamlit branding."""
        return """
        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        """
    
    def _get_background_css(self) -> str:
        """CSS for background image styling."""
        if not self.config.background_image_url:
            return ""
        
        # Extract RGB values from primary color for green overlay
        primary_rgb = self._hex_to_rgb(self.config.primary_color)
        
        return f"""
        /* Background image styling */
        .stApp {{
            background: linear-gradient(
                rgba({primary_rgb[0]}, {primary_rgb[1]}, {primary_rgb[2]}, {1 - self.config.background_opacity}),
                rgba({primary_rgb[0]}, {primary_rgb[1]}, {primary_rgb[2]}, {1 - self.config.background_opacity})
            ), url('{self.config.background_image_url}');
            background-size: {self.config.background_size};
            background-position: {self.config.background_position};
            background-repeat: {self.config.background_repeat};
            background-attachment: {self.config.background_attachment};
        }}
        
        /* Ensure content is readable over background */
        .main .block-container {{
            background: rgba({primary_rgb[0]}, {primary_rgb[1]}, {primary_rgb[2]}, 0.92);
            border-radius: 20px;
            padding: 2rem;
            margin: 1rem;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
            border: 1px solid rgba({primary_rgb[0]}, {primary_rgb[1]}, {primary_rgb[2]}, 0.3);
        }}
        """
    
    def _get_main_container_css(self) -> str:
        """CSS for main container styling."""
        return """
        /* Main container styling */
        .main > div {
            padding-top: 1rem;
        }
        """
    
    def _get_chat_message_css(self) -> str:
        """CSS for chat message styling."""
        return f"""
        /* Chat message styling - consistent for both light and dark modes */
        .user-message {{
            background: {self.config.secondary_color};
            color: white;
            padding: 15px 20px;
            border-radius: 20px 20px 5px 20px;
            margin: 10px 0 10px 20%;
            backdrop-filter: none;
        }}
        
        .bot-message {{
            background: {self.config.background_dark};
            color: #000000 !important;
            padding: 15px 20px;
            border-radius: 20px 20px 20px 5px;
            margin: 10px 20% 10px 0;
            border-left: 4px solid #026607;
            box-shadow: none !important;
            backdrop-filter: none !important;
            text-shadow: none !important;
        }}
        
        /* Ensure ALL text in bot messages is black with no effects */
        .bot-message *,
        .bot-message p,
        .bot-message div,
        .bot-message span,
        .bot-message li,
        .bot-message ul,
        .bot-message ol,
        .bot-message h1,
        .bot-message h2,
        .bot-message h3,
        .bot-message h4,
        .bot-message h5,
        .bot-message h6,
        .bot-message strong,
        .bot-message em,
        .bot-message code,
        .bot-message pre {{
            color: #000000 !important;
            text-shadow: none !important;
            backdrop-filter: none !important;
            filter: none !important;
        }}
        
        .message-header {{
            font-weight: bold;
            font-size: 0.8em;
            margin-bottom: 8px;
            opacity: 0.9;
        }}
        
        /* User message header should remain white */
        .user-message .message-header {{
            color: white !important;
        }}
        
        /* Bot message header should be black */
        .bot-message .message-header {{
            color: #000000 !important;
            text-shadow: none !important;
        }}
        
        .message-content {{
            line-height: 1.5;
            word-wrap: break-word;
        }}
        
        /* Bot message content should be black */
        .bot-message .message-content,
        .bot-message .message-content * {{
            color: #000000 !important;
            text-shadow: none !important;
        }}
        """
    
    def _get_form_css(self) -> str:
        """CSS for form styling."""
        return f"""
        /* Form styling - consistent for both light and dark modes */
        .stTextArea textarea {{
            border: 2px solid {self.config.primary_color};
            border-radius: {self.config.border_radius};
            padding: 15px;
            font-size: 12px;
            transition: all 0.3s ease;
            background: #e8f5e8 !important;
            backdrop-filter: blur(5px);
            color: #000000 !important;
            caret-color: #000000 !important;
        }}
        
        .stTextArea textarea::placeholder {{
            color: #666666 !important;
            opacity: 0.7;
        }}
        
        .stTextArea textarea:focus {{
            border-color: {self.config.secondary_color};
            box-shadow: 0 0 0 3px rgba(2, 102, 7, 0.1);
            background: #e8f5e8 !important;
            caret-color: #000000 !important;
        }}
        
        .stTextInput input {{
            border: 2px solid {self.config.primary_color};
            border-radius: 10px;
            padding: 12px 15px;
            font-size: 12px;
            transition: all 0.3s ease;
            background: #e8f5e8 !important;
            backdrop-filter: blur(5px);
            color: #000000 !important;
            caret-color: #000000 !important;
        }}
        
        .stTextInput input::placeholder {{
            color: #666666 !important;
            opacity: 0.7;
        }}
        
        .stTextInput input:focus {{
            border-color: {self.config.secondary_color};
            box-shadow: 0 0 0 3px rgba(2, 102, 7, 0.1);
            background: #e8f5e8 !important;
            caret-color: #000000 !important;
        }}
        """
    
    def _get_button_css(self) -> str:
        """CSS for button styling with uniform sizing and alignment."""
        return f"""
        /* Button styling with uniform sizing */
        .stButton button {{
            border-radius: {self.config.button_radius};
            border: none !important;
            font-weight: 600;
            padding: 12px 24px;
            transition: all 0.3s ease;
            cursor: pointer;
            backdrop-filter: none;
            /* Ensure uniform sizing */
            height: 50px !important;
            min-height: 50px !important;
            max-height: 50px !important;
            box-sizing: border-box !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            white-space: nowrap !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
        }}
        
        /* Primary buttons (default green styling) */
        .stButton button[kind="primary"] {{
            background: {self.config.secondary_color};
            color: white !important;
            box-shadow: 0 4px 15px {self.config.shadow_color};
            border: none !important;
        }}
        
        .stButton button[kind="primary"]:hover {{
            background: {self.config.secondary_color};
            transform: translateY(-3px);
            box-shadow: 0 6px 20px rgba(2, 102, 7, 0.4);
            border: none !important;
        }}
        
        /* Secondary buttons (mint-green background with green text) */
        .stButton button[kind="secondary"] {{
            background: mint-green !important;
            color: {self.config.secondary_color} !important;
            border: 2px solid {self.config.secondary_color} !important;
            width: 100%;
            text-align: center !important;
            margin: 5px 0;
            text-shadow: none !important;
        }}
        
        .stButton button[kind="secondary"]:hover {{
            background: {self.config.secondary_color} !important;
            color: white !important;
            transform: translateY(-2px);
            box-shadow: 0 4px 15px {self.config.shadow_color};
            border: 2px solid {self.config.secondary_color} !important;
        }}
        
        /* FAQ/Suggestion buttons - Uniform sizing and alignment */
        .stButton button,
        .stButton > button,
        .stButton button[data-testid="baseButton-secondary"] {{
            background: white !important;
            color: {self.config.secondary_color} !important;
            border: 2px solid {self.config.secondary_color} !important;
            text-shadow: none !important;
            box-shadow: none !important;
            /* Force uniform dimensions */
            width: 100% !important;
            height: 50px !important;
            min-height: 50px !important;
            max-height: 50px !important;
            font-size: 12px !important;
            line-height: 1.2 !important;
            padding: 8px 16px !important;
            margin: 2px 0 !important;
            text-align: center !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            box-sizing: border-box !important;
            word-wrap: break-word !important;
            white-space: normal !important;
            overflow: hidden !important;
        }}
        
        /* Hover state for all buttons */
        .stButton button:hover {{
            background: {self.config.secondary_color} !important;
            color: white !important;
            border: 2px solid {self.config.secondary_color} !important;
            text-shadow: none !important;
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(2, 102, 7, 0.3) !important;
        }}
        
        /* Container for buttons in columns */
        .stButton {{
            width: 100% !important;
        }}
        
        /* Ensure buttons in columns have equal width */
        div[data-testid="column"] .stButton {{
            width: 100% !important;
        }}
        
        div[data-testid="column"] .stButton button {{
            width: 100% !important;
            margin: 2px 0 !important;
        }}
        
        /* Form submit button - Special styling for Start Chatting and Send Message */
        .stForm button {{
            background: {self.config.secondary_color} !important;
            color: white !important;
            border: none !important;
            border-radius: {self.config.button_radius};
            padding: 12px 30px;
            font-weight: 600;
            font-size: 12px;
            width: 100%;
            height: 50px !important;
            transition: all 0.3s ease;
            backdrop-filter: none;
        }}
        
        .stForm button:hover {{
            background: {self.config.secondary_color} !important;
            transform: translateY(-3px);
            box-shadow: 0 6px 20px rgba(2, 102, 7, 0.4);
            border: none !important;
        }}
        """
    
    def _get_tab_css(self) -> str:
        """CSS for tab styling."""
        return f"""
        /* Tab styling - consistent for both light and dark modes */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            height: 40px;
            padding-left: 20px;
            padding-right: 20px;
            background-color: transparent;
            border-radius: 10px 10px 0 0;
            border: none;
            color: white !important;
            font-weight: 600;
            transition: all 0.3s ease;
            text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.7);
        }}
        
        .stTabs [data-baseweb="tab"]:hover {{
            transform: translateY(-2px);
            background-color: rgba(255, 255, 255, 0.1);
        }}
        
        .stTabs [aria-selected="true"] {{
            background-color: {self.config.secondary_color} !important;
            color: white !important;
            border: none !important;
            border-bottom: 2px solid white !important;
            text-shadow: none;
        }}
        
        .stTabs [data-baseweb="tab-panel"] {{
            padding: 20px;
            border: none;
            border-radius: 0 10px 10px 10px;
            background-color: rgba(255, 255, 255, 0.05);
        }}
        
        /* Remove any red borders from tabs */
        .stTabs [data-baseweb="tab"]:focus {{
            outline: none !important;
            border: none !important;
        }}
        
        .stTabs [data-baseweb="tab"]:active {{
            outline: none !important;
            border: none !important;
        }}
        """
    
    def _get_file_uploader_css(self) -> str:
        """CSS for file uploader styling."""
        return f"""
        /* File uploader styling */
        .stFileUploader > div > div > div > div {{
            border: 2px dashed {self.config.primary_color};
            border-radius: {self.config.border_radius};
            background: rgba(255, 255, 255, 0.9);
            padding: 20px;
            text-align: center;
            transition: all 0.3s ease;
        }}
        
        .stFileUploader > div > div > div > div:hover {{
            border-color: {self.config.secondary_color};
            background: rgba(255, 255, 255, 0.95);
        }}
        
        /* Browse files button */
        .stFileUploader button {{
            background: {self.config.secondary_color} !important;
            color: white !important;
            border: none !important;
            border-radius: {self.config.button_radius} !important;
            padding: 8px 16px !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
        }}
        
        .stFileUploader button:hover {{
            background: {self.config.secondary_color} !important;
            color: white !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 4px 15px rgba(2, 102, 7, 0.4) !important;
        }}
        
        /* File uploader text - No blur or shadow effects */
        .stFileUploader small {{
            color: #000000 !important;
            text-shadow: none !important;
            backdrop-filter: none !important;
            filter: none !important;
        }}
        
        /* File uploader drag text - No blur or shadow */
        .stFileUploader > div > div > div > div > div {{
            color: #000000 !important;
            text-shadow: none !important;
            backdrop-filter: none !important;
            filter: none !important;
        }}
        
        /* Main file uploader text - No blur or shadow */
        .stFileUploader span {{
            color: #000000 !important;
            text-shadow: none !important;
            backdrop-filter: none !important;
            filter: none !important;
        }}
        
        /* All file uploader text elements - Remove all effects */
        .stFileUploader * {{
            text-shadow: none !important;
            backdrop-filter: none !important;
            filter: none !important;
        }}
        
        /* For dark mode - when background is dark */
        @media (prefers-color-scheme: dark) {{
            .stFileUploader small {{
                color: white !important;
                text-shadow: none !important;
            }}
            
            .stFileUploader > div > div > div > div > div {{
                color: white !important;
                text-shadow: none !important;
            }}
            
            .stFileUploader span {{
                color: white !important;
                text-shadow: none !important;
            }}
        }}
        
        /* Streamlit's dark theme class detection */
        [data-theme="dark"] .stFileUploader small,
        [data-theme="dark"] .stFileUploader > div > div > div > div > div,
        [data-theme="dark"] .stFileUploader span {{
            color: white !important;
            text-shadow: none !important;
        }}
        
        /* Light theme explicit styling */
        [data-theme="light"] .stFileUploader small,
        [data-theme="light"] .stFileUploader > div > div > div > div > div,
        [data-theme="light"] .stFileUploader span {{
            color: #000000 !important;
            text-shadow: none !important;
        }}
        """
    
    def _get_title_css(self) -> str:
        """CSS for title styling."""
        return f"""
        /* Title styling - consistent for both light and dark modes */
        h1 {{
            color: white !important;
            text-align: center;
            margin-bottom: 0.5rem;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8);
        }}
        
        h2 {{
            color: white !important;
            text-align: center;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8);
        }}
        
        h3 {{
            color: white !important;
            text-align: center;
            margin-bottom: 2rem;
            font-weight: 400;
            text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.8);
        }}
        
        /* General text styling for consistent appearance */
        .stMarkdown p, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {{
            color: white !important;
            text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.7);
        }}
        
        /* Form labels and text */
        .stForm label, .stForm p, .stForm div {{
            color: white !important;
            text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.7);
        }}
        
        /* Subheader styling - Enhanced for better visibility */
        .stSubheader, .stSubheader > div, .stSubheader p {{
            color: white !important;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8) !important;
        }}
        
        /* Any div containing text should be white */
        div[data-testid="stMarkdownContainer"] p {{
            color: white !important;
            text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.7);
        }}
        
        /* Ensure all paragraph text is white with shadow */
        p {{
            color: white !important;
            text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.7);
        }}
        """
    
    def _get_responsive_css(self) -> str:
        """CSS for responsive design."""
        return """
        /* Responsive design */
        @media (max-width: 768px) {
            .user-message, .bot-message {
                margin-left: 5%;
                margin-right: 5%;
            }
            
            .stButton button {
                font-size: 12px !important;
                padding: 8px 16px !important;
                height: 45px !important;
                min-height: 45px !important;
                max-height: 45px !important;
            }
            
            .main .block-container {
                margin: 0.5rem;
                padding: 1rem;
            }
            
            .stTabs [data-baseweb="tab"] {
                height: 35px;
                padding-left: 15px;
                padding-right: 15px;
                font-size: 12px;
            }
        }
        
        /* Additional responsive adjustments for very small screens */
        @media (max-width: 480px) {
            .stButton button {
                font-size: 10px !important;
                padding: 6px 12px !important;
                height: 40px !important;
                min-height: 40px !important;
                max-height: 40px !important;
            }
        }
        """
    
    def display_chat_message(self, user_msg: str, bot_reply: str, user_name: str, bot_name: str = "Assistant") -> None:
        """Display a chat message pair with the theme styling."""
        # User message
        st.markdown(
            f"""
            <div class="user-message">
                <div class="message-header">👤 {user_name}</div>
                <div class="message-content">{user_msg}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
        # Bot reply
        st.markdown(
            f"""
            <div class="bot-message">
                <div class="message-header">🤖 {bot_name}</div>
                <div class="message-content">{bot_reply}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# Predefined theme configurations
class ThemePresets:
    """Predefined theme configurations for different use cases."""
    
    @staticmethod
    def green_farm_theme() -> ThemeConfig:
        """Original green farm theme with forest background."""
        return ThemeConfig(
            primary_color="#000000",
            secondary_color="#035509",
            accent_color="#014405",
            background_image_url="https://images.unsplash.com/photo-1441974231531-c6227db76b6e?ixlib=rb-4.0.3&auto=format&fit=crop&w=2560&q=80",
            background_opacity=0.15,
            shadow_color="rgba(2, 102, 7, 0.3)"
        )
    
    @staticmethod
    def green_farm_field_theme() -> ThemeConfig:
        """Green farm theme with agricultural field background."""
        return ThemeConfig(
            primary_color="#026607",
            secondary_color="#035509",
            accent_color="#014405",
            background_image_url="https://images.unsplash.com/photo-1500595046743-cd271d694d30?ixlib=rb-4.0.3&auto=format&fit=crop&w=2574&q=80",
            background_opacity=0.12,
            shadow_color="rgba(2, 102, 7, 0.3)"
        )
    
    @staticmethod
    def green_meadow_theme() -> ThemeConfig:
        """Green theme with meadow background."""
        return ThemeConfig(
            primary_color="#026607",
            secondary_color="#035509",
            accent_color="#014405",
            background_image_url="https://images.unsplash.com/photo-1506905925346-21bda4d32df4?ixlib=rb-4.0.3&auto=format&fit=crop&w=2570&q=80",
            background_opacity=0.1,
            shadow_color="rgba(2, 102, 7, 0.3)"
        )
    
    @staticmethod
    def blue_tech_theme() -> ThemeConfig:
        """Blue tech theme."""
        return ThemeConfig(
            primary_color="#2196F3",
            secondary_color="#1976D2",
            accent_color="#0D47A1",
            shadow_color="rgba(33, 150, 243, 0.3)"
        )
    
    @staticmethod
    def purple_creative_theme() -> ThemeConfig:
        """Purple creative theme."""
        return ThemeConfig(
            primary_color="#9C27B0",
            secondary_color="#7B1FA2",
            accent_color="#4A148C",
            shadow_color="rgba(156, 39, 176, 0.3)"
        )
    
    @staticmethod
    def orange_energy_theme() -> ThemeConfig:
        """Orange energy theme."""
        return ThemeConfig(
            primary_color="#FF9800",
            secondary_color="#F57C00",
            accent_color="#E65100",
            shadow_color="rgba(255, 152, 0, 0.3)"
        )

# Usage example
def example_usage():
    """Example of how to use the StreamlitChatTheme class with background images."""
    
    # Option 1: Use green farm theme with forest background
    theme = StreamlitChatTheme(ThemePresets.green_farm_theme())
    theme.apply_theme()
    
    # Option 2: Use green farm field theme
    field_theme = StreamlitChatTheme(ThemePresets.green_farm_field_theme())
    field_theme.apply_theme()
    
    # Option 3: Create custom theme with your own background
    custom_config = ThemeConfig(
        primary_color="#026607",
        secondary_color="#035509",
        accent_color="#014405",
        background_image_url="https://your-custom-image-url.jpg",
        background_opacity=0.15,
        background_size="cover",
        background_position="center",
        background_attachment="fixed"
    )
    custom_theme = StreamlitChatTheme(custom_config)
    custom_theme.apply_theme()
    
    # Option 4: No background image (original theme)
    no_bg_theme = StreamlitChatTheme()
    no_bg_theme.apply_theme()
    
    # Display chat messages
    theme.display_chat_message(
        "Hello, how can I help you with your farming questions today?",
        "Hi! I'm here to assist you with agricultural advice, crop management, and farming best practices.",
        "Farmer John"
    )

if __name__ == "__main__":
    example_usage()