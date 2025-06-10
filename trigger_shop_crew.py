import os
from crewai import Agent, Task, Crew, Process, LLM
from crewai_tools import JSONSearchTool

# loading environment variables
from dotenv import load_dotenv
load_dotenv()

import re

def trigger_shop_crew(user_input):
    # --- Configuration ---
    llm = LLM(
            model="gemini/gemini-2.0-flash", # call model by provider/model_name
            temperature=0.8, # 0.8 is default
            api_key=os.getenv('GEMINI_API_KEY')
        )

    # --- Agents Definition ---
    # 1. Product Page Analyst Agent
    product_analyst = Agent(
        role='Product Page Analyst',
        goal='Understand and interpret natural language product descriptions to extract key requirements for a webpage, including potential variations or multiple items.',
        backstory=(
            "You are an expert market researcher and content strategist, skilled at dissecting "
            "user inputs to uncover the core essence of a product and its selling points. "
            "Your insights drive the entire webpage creation process, now also considering "
            "how to showcase multiple product items effectively."
        ),
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

    # 2. UI/UX Designer Agent
    ui_ux_designer = Agent(
        role='UI/UX Designer',
        goal='Design the visual layout and user experience for a product landing page, including sections to display multiple product items, ensuring aesthetics and responsiveness.',
        backstory=(
            "You are a seasoned UI/UX architect with an eye for clean, modern, and user-friendly "
            "web design. You specialize in creating appealing layouts optimized for conversion, "
            "especially for mobile-first Instagram sellers. You are adept at creating product "
            "galleries and listings using Tailwind CSS."
        ),
        verbose=True,
        allow_delegation=True,
        llm=llm
    )

    # 3. Content Generator Agent
    content_generator = Agent(
        role='Content Generator',
        goal='Craft compelling, concise, and persuasive textual content for the product landing page, including individual product item descriptions.',
        backstory=(
            "You are a master wordsmith and copywriter, experienced in writing sales-driven "
            "content that resonates with online audiences. Your words turn visitors into customers. "
            "You can generate descriptions for multiple product variations or items."
        ),
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

    # 4. Image Suggester Agent
    image_suggester = Agent(
        role='Image Suggester',
        goal='Propose relevant and high-quality image URLs for multiple product items based on their descriptions, utilizing image search tools.',
        backstory=(
            "You are a visual strategist, adept at envisioning the perfect imagery for products. "
            "You are skilled at finding or suggesting actual relevant image URLs that truly represent the product "
            "and fit the theme and requirements for a range of product items by utilizing image search tools."
        ),
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

    # 5. Payment Gateway Integrator Agent
    payment_integrator = Agent(
        role='Payment Gateway Integrator',
        goal='Design and implement the HTML and JavaScript for functional "Buy Now" and "Add to Cart" buttons, including dynamic cost calculation in INR and redirection to the Pinelabs gateway.',
        backstory=(
            "You are a meticulous web developer specializing in e-commerce integrations. "
            "You are equipped with the `pinelabs_api_collection` JSON, which provides the necessary endpoints for payment processing in form of JSON."
            "You ensure that payment calls to action are clear, prominent, function as expected, "
            "and correctly handle dynamic product data for redirection to a payment gateway like Pinelabs, "
            "supporting both direct purchase and cart functionalities."
        ),
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

    # 6. Code Assembler Agent
    code_assembler = Agent(
        role='Code Assembler',
        goal='Combine all generated components (HTML structure, CSS, JS, content, images) into a complete, valid, and runnable HTML webpage.',
        backstory=(
            "You are the master builder, bringing together all the pieces created by other agents "
            "into a cohesive and functional web page. You ensure correct syntax, responsiveness, "
            "and adherence to web standards."
        ),
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

    # --- Tasks Definition ---

    # 1. Product Analysis Task (Modified)
    analyze_product_task = Task(
        description=(
            "You are tasked with deeply analyzing the '{product_description}' provided by a layman user without any technical knowledge. "
            "The product description will be related to Instagram sellers, who want to create a website for their product having the list of items they sell, along with a payment gateway. "
            "Extract the main product name, its key features, primary benefits, "
            "target audience, desired brand tone (e.g., rustic, modern, luxurious), "
            "and any specific call-to-action text requested. "
            "Crucially, identify characteristics that could lead to *multiple distinct product items* or variations "
            "to be displayed (e.g., different styles, sizes, or related products). "
            "For each identified product item, also assign a *dummy price in INR*. "
            "Identify themes for images for both the overall page and individual items. "
            "If the above information is not explicitly provided in the user's description, generate reasonable defaults "
            "or infer them based on the general context of selling products."
            "Output this information as a JSON object."
        ),
        expected_output=(
            "A JSON object with keys: `main_product_name`, `main_key_features` (list of strings), "
            "`main_benefits` (list of strings), `target_audience`, `tone`, "
            "`call_to_action_text`, `overall_image_theme`, "
            "`product_items` (list of dictionaries, each containing `item_name`, `item_keywords`, `item_image_theme`, `item_id`, `item_price_inr`). "
            "The `item_id` should be a unique slug (e.g., 'blue-glaze-mug'). "
            "Example: {'main_product_name': 'Handmade Ceramic Mugs', 'product_items': [{'item_name': 'Blue Glaze Mug', 'item_keywords': ['blue', 'unique glaze'], 'item_image_theme': 'blue ceramic mug', 'item_id': 'blue-glaze-mug', 'item_price_inr': 799}, ...]}"
        ),
        agent=product_analyst,
        verbose=True, # Enable verbose output for debugging
        llm=llm
    )

    # 2. UI/UX Design Task (Modified for Buy Now/Add to Cart)
    design_page_task = Task(
        description=(
            "Based on the product analysis (which now includes potential `product_items` and their prices), "
            "design the complete HTML structure for a single landing page. "
            "This MUST include a main hero section (for overall product/brand), and then "
            "a prominent section for displaying *multiple product items*. "
            "For the product items section, design a responsive grid or flexbox layout "
            "where each item has a related image, title, short description, the **price in INR**, "
            "a 'Buy Now' button, and an 'Add to Cart' button. " # Updated requirement
            "Also include a visible (e.g., floating) 'View Cart / Checkout' button that dynamically updates "
            "to reflect items in the cart and initiates a consolidated payment. " # New Cart UI element
            "Suggest a cohesive Tailwind CSS-friendly color palette, font styles, "
            "and overall responsive layout guidelines (e.g., using `grid`, `flex`, `gap`, `p`, `m`, `rounded-*`). "
            "The HTML structure should include appropriate image tags (`<img>`) with `src` attributes "
            "that will be filled with actual product image URLs. "
            "Use fonts from Google Fonts (e.g., `<link href=\"https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap\" rel=\"stylesheet\">`) "
            "or similar services. "
            "Ensure the design is mobile-friendly and highly responsive across all devices (using Tailwind's `sm:`, `md:`, `lg:` prefixes). "
            "The design should be modern, clean, and suitable for an Instagram seller's audience. "
            "Ensure to use Tailwind CSS classes for styling and plan for JavaScript interactivity (e.g., button clicks to initiate payment or add to cart)."
            "The complete webpage structure should be production friendly and ready to be deployed and can be used in a production environment immediately."

            """When delegating tasks, STRICTLY ENSURE the following fields are provided:
            - task: A string describing the specific task to be delegated
            - context: A string providing the relevant context for the task
            - coworker: A string specifying the role/name of the team member to delegate to
            Example:
            {
                "task": "Extract job details from the LinkedIn",
                "context": "The job ad is located at the following URL xxxxx",
                "coworker": "Data Extraction Specialist"
            }"""
        ),
        expected_output=(
            "A complete HTML string representing the page structure. "
            "This HTML string should include a main hero section AND a section for multiple product items. "
            "Each product item in the HTML structure should have unique `id` attributes (matching `item_id` from product analysis) "
            "or distinct classes that can be targeted for content, image, price, and the two button types ('Buy Now', 'Add to Cart'). "
            "Include a placeholder HTML element for the 'View Cart / Checkout' button (e.g., `<button id=\"view-cart-btn\" class=\"hidden ...\">View Cart (0)</button>`)." # Updated output
            "Also include suggested Tailwind CSS classes (e.g., `grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6`) "
            "and the Google Fonts link in the `<head>`. "
            "Ensure responsiveness is thoroughly implemented using Tailwind's responsive prefixes (sm:, md:, lg:)."
        ),
        agent=ui_ux_designer,
        context=[analyze_product_task],  # Provide context from the product analysis task
        llm=llm
    )

    # 3. Content Generation Task (Modified)
    generate_content_task = Task(
        description=(
            "Using the product analysis (especially `main_product_name`, `main_benefits`, `product_items` and their `item_price_inr`) "
            "and the designed page structure (for context), generate compelling and concise textual content. "
            "This includes: "
            "1. A catchy headline for the overall page. "
            "2. A short overall product description. "
            "3. 3-5 bullet points highlighting main benefits. "
            "4. **For EACH item in `product_items`**: Generate a concise `item_title` and `item_description`. "
            "5. The exact text for the overall call-to-action button, and 'Buy Now' and 'Add to Cart' texts for individual product item buttons. " # Updated button texts
            "Adhere to the specified tone."
        ),
        expected_output=(
            "A JSON object containing: `overall_headline`, `overall_description`, `overall_benefits_list` (list of strings), "
            "`overall_button_text`, `product_items_content` (list of dictionaries, each with `item_id`, `item_title`, `item_description`, `buy_now_button_text`, `add_to_cart_button_text`, `item_price_inr`)." # Updated button texts
        ),
        agent=content_generator,
        llm=llm
    )

    # 4. Image Suggestion Task (Modified)
    suggest_images_task = Task(
        description=(
            "Based on the `overall_image_theme` and especially the `item_image_theme` for each "
            "item in `product_items` from the product analysis, find or suggest relevant "
            "and high-quality image URLs that represent the products. "
            "Provide one main image URL for the hero section and at least one image URL for EACH product item. "
            "These should be actual relevant image URLs from reputable public domain image sites (e.g., Unsplash, Pexels, Pixabay). "
            "Ensure appropriate dimensions (e.g., main: 900x400; items: 400x300) and that they are visually appealing. "
            "If actual image URLs are not feasible within the environment, use `https://placehold.co/` with highly descriptive text to indicate the intended image content (e.g., `https://placehold.co/900x400/D3D3D3/000000?text=Artisanal+Ceramic+Mugs+Collection`)."
        ),
        expected_output=(
            "A JSON object with keys: `main_hero_image_url`, `product_item_image_urls` (list of dictionaries, each with `item_id` and `image_url`)."
        ),
        agent=image_suggester,
        llm=llm
    )

    # 5. Payment Gateway Integrator Agent (Modified for Cart Functionality)
    payment_integrator = Agent(
        role='Payment Gateway Integrator',
        goal='Design and implement the HTML and JavaScript for functional "Buy Now" and "Add to Cart" buttons, including dynamic cost calculation in INR and redirection to a placeholder Pinelabs gateway.',
        backstory=(
            "You are a meticulous web developer specializing in e-commerce integrations. "
            "You ensure that payment calls to action are clear, prominent, function as expected, "
            "and correctly handle dynamic product data for redirection to a payment gateway like Pinelabs, "
            "supporting both direct purchase and cart functionalities."
        ),
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

    create_payment_button_task = Task(
        description=(
           """ "Create the JavaScript functions and initial state logic to handle 'Buy Now', 'Add to Cart', quantity updates, and 'Checkout Cart' actions. "
            "**Strict Guidelines for Quantity Control and Cart Logic:** "
            "1.  **Global Cart State:** Initialize a global `cartItems` object (e.g., itemId: quantity: N, price: P, ...}) to store selected product IDs, their quantities, and prices. "
            "2.  **`buyNow(itemId, itemPriceInr)` Function:** "
            "    -   This function should immediately redirect to Pinelabs for a single item. "
            "    -   Construct the URL: `https://pay.pinelabs.com/checkout?amount=amount_in_paise&currency=INR&item_id=item_id&order_id=unique_order_id`. "
            "    -   Convert `itemPriceInr` to paise (amount * 100). "
            "    -   Generate a `unique_order_id` in the format `order_timestamp_random_number` (timestamp in milliseconds, random number between 1000-9999). "
            "    -   STRICTLY CREATE A FUNCTION DEFINITION IN the `buyNow(itemId, itemPriceInr)` at the end titled "callPineLabs(amount_in_paise, item_id, order_id)` that constructs the URL. "
            "3.  **`addToCart(itemId, itemPriceInr)` Function:** "
            "    -   When initially clicked, it should: "
            "        -   STRICTLY Set the quantity for `itemId` in `cartItems` to 1. "
            "        -   **Visually transform** the 'Add to Cart' button for that specific product into a quantity control display: a '-' button, a `<span>` to show the quantity (e.g., '1'), and a '+' button. Use unique IDs/classes to target these elements for each product. "
            "        -   Hide the initial 'Add to Cart' button and show the quantity control. "
            "    -   If the item is already in the cart and `addToCart` is called (e.g., by clicking the main add-to-cart button again, if it were visible), it should simply increment the quantity by '1' from the earlier quantity. "
            "    -   Update the quantity displayed in the product card's UI. "
            "    -   Call `updateOverallCartDisplay()` after any change. "
            "4.  **`decrementQuantity(itemId)` Function (triggered by '-' button):** "
            "    -   Decrement the quantity for `itemId` in `cartItems`. "
            "    -   **Rule**: If the quantity becomes 0 (after decrement from 1), remove the item from `cartItems`. "
            "    -   **Visually transform back**: If quantity becomes 0, hide the quantity control for that product and show the original 'Add to Cart' button again. "
            "    -   **Rule**: Quantity must not go below 0 (i.e., if current quantity is 1 and '-' is clicked, it becomes 0, then reverts to 'Add to Cart'). No negative quantities allowed. "
            "    -   Update the quantity displayed in the product card's UI. "
            "    -   Call `updateOverallCartDisplay()` after any change. "
            "5.  **`incrementQuantity(itemId)` Function (triggered by '+' button):** "
            "    -   Increment the quantity for `itemId` in `cartItems`. "
            "    -   Update the quantity displayed in the product card's UI. "
            "    -   Call `updateOverallCartDisplay()` after any change. "
            "6.  **`updateOverallCartDisplay()` Function:** "
            "    -   Calculate the *total count of unique items* (number of entries in `cartItems`) and the *total sum of all quantities* (sum of all `quantity` values in `cartItems`). "
            "    -   Update the 'View Cart / Checkout' button's text (e.g., 'View Cart (3 items)' or 'View Cart (Total: ₹XXXX)'). Consider showing total items. "
            "    -   Make the 'View Cart / Checkout' button visible if the cart has items, hide it if empty. "
            "7.  **`checkoutCart()` Function:** "
            "    -   Calculate the `total_amount_in_paise` from all items in `cartItems` (sum of `itemPriceInr * quantity` for all items). "
            "    -   Collect all `item_id`s from `cartItems` (e.g., `item_ids=mug1,mug2`). "
            "    -   Generate a `unique_order_id` in the format `order_timestamp_random_number`. "
            "    -   Clear the `cartItems` and reset all product quantity UIs to their initial 'Add to Cart' button state. "
            "    -   Create a function named 'callPineAPI(amount_in_paise, item_ids, order_id)' that constructs the URL. The function definition is already written"
            "**HTML Structure for Buttons:** "
            "Provide the HTML structure for 'Buy Now' and 'Add to Cart' buttons, ensuring they have appropriate `onclick` events "
            "and `data-item-id`, `data-price-inr` attributes for easy JavaScript access. "
            "The 'Add to Cart' button structure should be flexible to switch between a simple button and the quantity control. "
            "Also provide the HTML for the 'View Cart / Checkout' button, ensuring its initial state (hidden/0 items) is correct, and it calls `checkoutCart()`."
"""        ),
        expected_output=(
            "A JSON object containing: "
            "`javascript_functions_string` (a string of the complete JavaScript functions for buy now, add to cart, quantity updates, and checkout, including global `cartItems` initialization and all necessary DOM manipulation logic for button state and cart counter updates), "
            "`buy_now_button_html_template` (HTML string for a 'Buy Now' button with placeholder `onclick` and `data-` attributes), "
            "`add_to_cart_control_html_template` (HTML string representing the initial 'Add to Cart' button and the *hidden* quantity control elements for one product, structured to be easily shown/hidden/updated, with placeholder `onclick`s and `data-` attributes), "
            "`view_cart_button_html_template` (HTML string for the 'View Cart / Checkout' button, initially hidden and showing a count, with its `onclick` event)."
        ),
        agent=payment_integrator,
        llm=llm,
        context=[analyze_product_task, design_page_task], # Needs product info for price/id and page structure for button placement
    )

    # 6. Code Assembler Agent
    code_assembler = Agent(
        role='Code Assembler',
        goal='Combine all generated components (HTML structure, CSS, JS, content, images) into a complete, valid, and runnable HTML webpage.',
        backstory=(
            "You are the master builder, bringing together all the pieces created by other agents "
            "into a cohesive and functional web page. You ensure correct syntax, responsiveness, "
            "and adherence to web standards."
        ),
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

    assemble_webpage_task = Task(
        description=(
            "Combine all the generated outputs (HTML structure, CSS styles, content, image URLs, "
            "and the complete JavaScript for 'Buy Now', 'Add to Cart', and 'Checkout Cart' functionality) "
            "into a single, complete, self-contained HTML file. "
            "Carefully insert the generated content (overall headline, description, benefits, individual item titles, descriptions, prices) "
            "and image URLs into the correct placeholders within the HTML structure and make sure the images are loading successfully."
            "For each product item, populate its specific content, image, price, and integrate **both** the 'Buy Now' and 'Add to Cart' buttons "
            "with their respective dynamic JavaScript calls, passing `data-item-id` and `data-price-inr` attributes. "
            "Ensure the Google Fonts link and Tailwind CSS CDN are correctly included in the `<head>`. "
            "Place all generated JavaScript (including the payment/cart functions) within a single `<script>` tag at the end of the `<body>` for proper loading. "
            "Integrate the 'View Cart / Checkout' button HTML, ensuring its initial state (hidden/0 items) is correct. "
            "Ensure all elements are correctly structured, visually appealing with Tailwind CSS, and fully responsive across all devices. "
            "The output MUST be a complete, runnable HTML string that can be saved as an `.html` file and opened directly in a browser. "
            "It should be production friendly and ready for immediate deployment." \
            "MANDATORY: Make sure the Images are loading correctly without any errors, and the payment gateway integration is functional. "
        ),
        expected_output=(
            "A single, complete HTML string representing the fully assembled landing page, "
            "incorporating all content, images, prices, and interactive 'Buy Now'/'Add to Cart'/Checkout functionality. "
            "The HTML should be well-formatted, responsive, and ready for deployment."
            "Make sure the html is embedded like ```html\n...HTML content...\n``` to ensure proper formatting."
        ),
        agent=code_assembler,
        context=[
            analyze_product_task,
            design_page_task,
            generate_content_task,
            suggest_images_task,
            create_payment_button_task
        ],
        llm=llm
    )

    # --- Crew Definition ---
    webpage_crew = Crew(
        agents=[
            product_analyst,
            ui_ux_designer,
            content_generator,
            image_suggester,
            payment_integrator,
            code_assembler
        ],
        tasks=[
            analyze_product_task,
            design_page_task,
            generate_content_task,
            suggest_images_task,
            create_payment_button_task,
            assemble_webpage_task
        ],
        process=Process.sequential # Tasks run in the order defined
    )

    print("--- Running Webpage Generation Crew ---")

    result = webpage_crew.kickoff(inputs={"product_description": user_input})

    print("\n--- Webpage Generation Complete! ---")
    print("\nFinal HTML Output:\n")
    print(result, "Token usage: ",result.token_usage)

    # # Creating the REGEX to extract the HTML content from the result
    # pattern = r"```html\n(.*?)```"
    
    # # re.DOTALL flag is crucial: It makes '.' match any character, including newline.
    # match = re.search(pattern, result.raw, re.DOTALL)

    # if match:
    #     # Group 1 (the content inside the parentheses in the pattern)
    #     with open("instagram_seller_page.html", "w") as f:
    #         f.write(match.group(1).strip())

    #         print("\nWebpage saved to instagram_seller_page.html")
    
    # else:
    #     print("No content found in the result.")

    return result.raw


