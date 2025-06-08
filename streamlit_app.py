import streamlit as st
import json
import time
from datetime import datetime
import re # Import regex for HTML extraction

from trigger_shop_crew import trigger_shop_crew

# Import CrewAI components
from crewai import Agent, Task, Crew, Process

# --- Configure page settings ---
st.set_page_config(
    page_title="Instagram Seller Webpage Generator",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Dark Theme Configuration ---
DARK_THEME = {
    "primary-color": "#E91E63",  # Pink - Vibrant, attention-grabbing
    "secondary-color": "#FFC107",   # Amber - Warm, inviting
    "accent-color": "#03A9F4",       # Light Blue - Modern
    "success-color": "#8BC34A",
    "warning-color": "#FFD54F",
    "danger-color": "#E57373",       # Lighter Red
    "dark-bg": "#1E1E1E",            # Dark charcoal for components
    "light-bg": "#262730",           # Dark slate background for main content
    "main-bg": "#121212",            # Very dark gray overall background
    "text-color": "#E0E0E0",         # Light text
    "secondary-text-color": "#A0A0A0", # Medium light text
    "card-bg-gradient-light": "#2A2A2A",
    "card-bg-gradient-dark": "#333333",
}

# Initialize processing state
if "is_processing" not in st.session_state:
    st.session_state.is_processing = False

def apply_dark_theme():
    """Applies the dark theme's CSS variables."""
    theme_colors = DARK_THEME
    root_css_vars = ""
    for prop, value in theme_colors.items():
        root_css_vars += f"--{prop}: {value};\n"

    st.markdown(f"""
    <style>
        /* Google Fonts - Poppins for a modern, clean look */
        @import url('https://fonts.com/css2?family=Poppins:wght@300;400;600;700&display=swap');

        :root {{
            {root_css_vars}
        }}

        /* Force dark theme on Streamlit elements */
        .stApp {{
            background-color: var(--main-bg) !important;
            color: var(--text-color) !important;
        }}

        body {{
            font-family: 'Poppins', sans-serif !important;
            background-color: var(--main-bg) !important;
            color: var(--text-color) !important;
        }}

        /* Hide default Streamlit styling */
        #MainMenu {{visibility: hidden;}}
        header {{visibility: hidden;}}
        
        /* General container styling */
        .main .block-container {{
            padding-top: 1rem;
            padding-right: 2rem;
            padding-left: 2rem;
            padding-bottom: 2rem;
            background-color: var(--main-bg) !important;
        }}
        
        /* Custom header */
        .main-header {{
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            padding: 3rem 2rem;
            border-radius: 20px;
            margin-bottom: 2.5rem;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            color: white;
            text-align: center;
            position: relative;
            overflow: hidden;
        }}
        
        .main-header h1 {{
            font-size: 3.5rem;
            font-weight: 700;
            margin: 0;
            text-shadow: 3px 3px 6px rgba(0,0,0,0.4);
            letter-spacing: -1px;
        }}
        
        .main-header p {{
            font-size: 1.3rem;
            opacity: 0.95;
            margin: 0.75rem 0 0 0;
            line-height: 1.5;
        }}

        /* Input section styling */
        .input-section {{
            background: var(--dark-bg) !important;
            padding: 2.5rem;
            border-radius: 18px;
            box-shadow: 0 6px 25px rgba(0,0,0,0.3);
            margin-bottom: 2.5rem;
            border: 1px solid var(--dark-bg);
            color: var(--text-color) !important;
        }}

        .input-section h3 {{
            color: var(--primary-color) !important;
            font-weight: 600;
            margin-bottom: 1.5rem;
        }}
        
        /* Text Area Styling */
        .stTextArea > div > div > textarea {{
            background-color: var(--dark-bg) !important;
            color: var(--text-color) !important;
            border: 2px solid var(--dark-bg) !important;
            border-radius: 15px !important;
            padding: 1rem !important;
            font-size: 1.1rem !important;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2) !important;
        }}
        .stTextArea > div > div > textarea:focus {{
            border-color: var(--secondary-color) !important;
            box-shadow: 0 0 0 0.2rem var(--secondary-color)40 !important;
        }}

        /* Buttons */
        .stButton > button {{
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color)) !important;
            color: white !important;
            border: none !important;
            padding: 0.85rem 2.5rem !important;
            border-radius: 30px !important;
            font-weight: 600 !important;
            margin-top: 1.1rem !important;
            font-size: 1.15rem !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 5px 20px rgba(233, 30, 99, 0.3) !important; /* Adjusted shadow color */
            cursor: pointer !important;
        }}
        
        .stButton > button:hover {{
            transform: translateY(-3px) !important;
            box-shadow: 0 8px 25px rgba(233, 30, 99, 0.4) !important; /* Adjusted shadow color */
            filter: brightness(1.05) !important;
            color: white !important;
        }}

        .stButton > button:disabled {{
            background: var(--secondary-text-color) !important;
            color: var(--dark-bg) !important;
            cursor: not-allowed !important;
            transform: none !important;
            box-shadow: none !important;
        }}

        .stDownloadButton > button {{
            background: linear-gradient(135deg, var(--accent-color), var(--primary-color)) !important; /* Adjusted gradient for download */
            color: white !important;
            border: none !important;
            padding: 0.85rem 2.5rem !important;
            border-radius: 30px !important;
            font-weight: 600 !important;
            margin-top: 1.1rem !important;
            font-size: 1.15rem !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 5px 20px rgba(3, 169, 244, 0.3) !important; /* Adjusted shadow */
            cursor: pointer !important;
        }}
        .stDownloadButton > button:hover {{
            transform: translateY(-3px) !important;
            box-shadow: 0 8px 25px rgba(3, 169, 244, 0.4) !important; /* Adjusted shadow */
            filter: brightness(1.05) !important;
            color: white !important;
        }}

        /* Metric Cards - Removed as they are not relevant to this app */
        
        /* Progress bar styling */
        .stProgress > div > div > div > div {{
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color)) !important;
        }}
        .stProgress > div > div {{
            background-color: var(--dark-bg) !important;
        }}
        
        /* General text styling */
        .stMarkdown, .stText, p, div, span {{
            color: var(--text-color) !important;
        }}

        h1, h2, h3, h4, h5, h6 {{
            color: var(--text-color) !important;
        }}

        /* Info box styling */
        .stInfo {{
            background-color: var(--dark-bg) !important;
            color: var(--text-color) !important;
            border-left: 4px solid var(--secondary-color) !important;
        }}

        /* Warning box styling */
        .stWarning {{
            background-color: var(--dark-bg) !important;
            color: var(--text-color) !important;
            border-left: 4px solid var(--warning-color) !important;
        }}

        /* Error box styling */
        .stError {{
            background-color: var(--dark-bg) !important;
            color: var(--text-color) !important;
            border-left: 4px solid var(--danger-color) !important;
        }}

        /* Success box styling */
        .stSuccess {{
            background-color: var(--dark-bg) !important;
            color: var(--text-color) !important;
            border-left: 4px solid var(--success-color) !important;
        }}

        /* Specific styling for HTML code block output */
        [data-testid="stCodeBlock"] > code {{
            background-color: var(--dark-bg) !important;
            color: var(--text-color) !important;
            border: 1px solid var(--secondary-text-color) !important;
            border-radius: 10px !important;
            padding: 1.5rem !important;
            font-size: 0.95rem !important;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2) !important;
            overflow-x: auto;
        }}
    </style>
    """, unsafe_allow_html=True)

def create_header():
    """Create the main application header with a modern design."""
    st.markdown("""
    <div class="main-header">
        <h1>🛍️ Instagram Seller Webpage Generator</h1>
        <p>Effortlessly create stunning landing pages for your products</p>
    </div>
    """, unsafe_allow_html=True)

def extract_html_block(text):
    """
    Extracts the content of an HTML code block delimited by ```html and ```.

    Args:
        text (str): The input string containing the HTML block.

    Returns:
        str or None: The extracted HTML content if found, otherwise None.
    """
    # The regex pattern:
    # r"```html\n"     : Matches the literal opening ```html followed by a newline.
    # (.*?)             : Matches any character (including newlines due to re.DOTALL)
    #                   : non-greedily (.*?) to stop at the first closing marker.
    # r"\n```"         : Matches a newline followed by the literal closing ```.
    pattern = r"```html\n(.*?)```"

    # re.DOTALL flag is crucial: It makes '.' match any character, including newline.
    match = re.search(pattern, text, re.DOTALL)

    if match:
        # Group 1 (the content inside the parentheses in the pattern)
        return match.group(1).strip() # .strip() removes leading/trailing whitespace/newlines
    else:
        return None

def main():
    """Main application function to run the Webpage Generator interface."""
    # Apply dark theme CSS
    apply_dark_theme()

    # --- Main Content ---
    create_header()

    st.markdown("### 📝 Describe Your Products")
    
    user_input = st.text_area(
        label="Please describe your products and the type of webpage you'd like:",
        label_visibility="collapsed",
        height=180,
        placeholder="e.g., 'I sell handmade ceramic mugs. I need a simple, cozy, and rustic landing page. It should feature a main hero section for 'Artisanal Mugs' and then a gallery of 3 different mug styles: a 'Blue Glaze Mug', a 'Rustic Earth Tone Mug', and a 'Minimalist White Mug'. Each mug should have its own image, a short description, its price (around 800-1200 INR), and options to 'Buy Now' or 'Add to Cart' with quantity controls. There should also be a 'View Cart' button to proceed with all selected items to Pinelabs. Target audience is people who appreciate artisanal crafts.'",
        key="user_input_textarea",
        disabled=st.session_state.is_processing
    )

    # Initialize execution_time to ensure it's always defined
    execution_time_str = "0.00s"
    
    # Action button centered - only show when not processing
    col_empty1, col_btn, col_empty2 = st.columns([1, 2, 1])
    with col_btn:
        if not st.session_state.is_processing:
            generate_button = st.button("Generate Webpage", use_container_width=True, key="generate_webpage_btn")
        else:
            st.button("✨ Generating...", use_container_width=True, disabled=True, key="generating_btn")
            generate_button = False
    
    # Process webpage generation
    if generate_button and user_input.strip():
        st.session_state.is_processing = True
        st.rerun()
    
    if st.session_state.is_processing and user_input.strip():
        st.markdown("---")
        
        # Progress bar with status message
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Simulate progress updates
            progress_steps = [
                (10, "✨ Understanding your product needs..."),
                (30, "🎨 Designing webpage layout and elements..."),
                (50, "✍️ Crafting compelling product content..."),
                (70, "📸 Suggesting relevant images..."),
                (85, "🛒 Integrating cart & payment functionality..."),
                (95, "📦 Assembling the final webpage..."),
                (100, "✅ Webpage generated!")
            ]
            
            # Record start time
            start_time = time.time()
            
            # Update progress bar in steps
            for progress, message in progress_steps:
                progress_bar.progress(progress)
                status_text.text(message)
                time.sleep(1.0) # Reduced delay for faster visual feedback
            
            # Call the webpage generation crew
            result = trigger_shop_crew(user_input)

            # Extract HTML content using regex
            generated_html = extract_html_block(result) # Assuming crew_result directly contains the ```html...``` block
            
            # Record end time and calculate duration
            end_time = time.time()
            execution_time_raw = end_time - start_time
            execution_time_str = f"{execution_time_raw:.2f}s"
            
            # Clear progress indicators
            progress_bar.empty()
            status_text.empty()
            
            # Reset processing state
            st.session_state.is_processing = False
            
            # Display results
            st.markdown("## 🌐 Your Generated Webpage")
            if generated_html:
                st.info(f"Webpage generation complete in: **{execution_time_str}**")
                st.success("Your webpage HTML code is ready! You can copy it below or download it.")
                
                # Display HTML code
                st.markdown("### HTML Code:")
                st.code(generated_html, language="html", height=500)
                
                # Export options
                col_download, col_copy_html = st.columns([1, 1])
                
                with col_download:
                    st.download_button(
                        label="⬇️ Download Webpage (HTML)",
                        data=generated_html.encode("utf-8"),
                        file_name=f"instagram_seller_page_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                        mime="text/html",
                        key="download_html_btn",
                        use_container_width=True
                    )
                
                # This button copies to clipboard (requires specific Streamlit components or external JS for true clipboard copy,
                # here we just display it in an info box as Streamlit doesn't natively support direct clipboard write from server-side)
                with col_copy_html:
                    if st.button("📋 Copy HTML to Clipboard (Manual)", key="copy_html_btn", use_container_width=True):
                        st.code(generated_html, language="html") # Re-display for easy copy
                        st.success("HTML code displayed above for manual copy!")

            else:
                st.error("Failed to extract HTML content from the CrewAI output. Please try again.")
                st.code(result, language="json", height=300) # Show full crew result for debugging
                
        except Exception as e:
            # Clear progress indicators on error
            progress_bar.empty()
            status_text.empty()
            st.session_state.is_processing = False
            
            st.error(f"An error occurred during webpage generation: {e}")
            st.warning("Please try again or refine your input.")
            st.exception(e)

    elif st.session_state.is_processing and not user_input.strip():
        st.session_state.is_processing = False
        st.warning("Please enter a product description to generate your webpage.")

if __name__ == "__main__":
    main()
