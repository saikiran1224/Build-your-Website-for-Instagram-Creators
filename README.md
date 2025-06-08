# 🛍️ Instagram Seller Webpage Generator

This project provides an intelligent tool to help Instagram sellers effortlessly generate professional, single-page product websites from natural language descriptions. Leveraging the power of AI agents orchestrated by CrewAI, it automates the process of design, content creation, image suggestions, and even integrates a simulated shopping cart with Pinelabs payment redirection.

✨ Features
- **Natural Language Input:** Describe your products and desired webpage style in plain English.

- **Dynamic Webpage Generation:** Creates a complete, self-contained HTML page including CSS and JavaScript.

- **Multi-Product Display:** Generates an e-commerce-like gallery to showcase multiple product items with individual details.

- **Real Image Suggestions:** Intelligent suggestions for relevant, high-quality images (simulated via public domain image URLs or descriptive placeholders).

- **Interactive Cart Functionality:**

 - "Buy Now" button for immediate single-item purchase.

 - "Add to Cart" button that transforms into a dynamic quantity controller (-, quantity, +).

 - Quantity management ensures positive integer quantities and allows removal from cart.

- Floating "View Cart / Checkout" button dynamically updates with total items and value.

- INR Cost Calculation: Prices are automatically calculated and displayed in Indian Rupees (INR).

- **Pinelabs Payment Gateway Integration (In progress):** Simulates redirection to a Pinelabs-like payment gateway URL with dynamic amount, item IDs, and a unique order ID for both "Buy Now" and consolidated "Checkout" actions.

- **Responsive Design:** Utilizes Tailwind CSS to ensure the generated webpage looks great on all devices (mobile, tablet, desktop).

- **Production-Ready Output:** Generates clean, deployable HTML code.

- **Streamlit UI:** A user-friendly Streamlit interface for seamless interaction and generation.