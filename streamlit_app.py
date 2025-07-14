import streamlit as st
import datetime
from datetime import timedelta
import asyncio
import hashlib
from utils.data import UK_CITIES, get_travel_options, calculate_budget
from utils.prompts import (
    SYSTEM_PROMPT, 
    ITINERARY_PROMPT_TEMPLATE, 
    PACKING_LIST_PROMPT_TEMPLATE,
    DINING_PROMPT_TEMPLATE,
    create_user_context
)
from utils.llm import (
    init_openai_client, 
    get_ai_response_async, 
    get_ai_recommendations_cached,
    stream_response
)
from utils.rate_limiter import RateLimiter

# Page configuration
st.set_page_config(
    page_title="AI-Powered UK Vacation Planner", 
    page_icon="🇬🇧", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize components
rate_limiter = RateLimiter(max_requests=10, window_minutes=5)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Check OpenAI client
client = init_openai_client()
if not client:
    st.stop()

# Sidebar - Rate limit info
with st.sidebar:
    st.subheader("API Usage")
    remaining = rate_limiter.get_remaining_requests()
    st.metric("Remaining Requests", f"{remaining}/10")
    st.caption("Resets every 5 minutes")
    
    # Debug options
    with st.expander("🔧 Debug Options"):
        show_context = st.checkbox("Show Context", value=False)
        use_cache = st.checkbox("Use Cached Responses", value=True)

# Main App
st.title("🇬🇧 AI-Powered UK Vacation Planner")
st.markdown("Plan your perfect UK getaway with AI-powered personalised recommendations!")

# Step 1: City Selection
st.header("1. Choose Your Destination(s)")
selected_cities = st.multiselect(
    "Select UK cities to visit:",
    options=list(UK_CITIES.keys()),
    default=["London"],
    help="You can select multiple cities for a multi-city trip"
)

if not selected_cities:
    st.warning("Please select at least one city to continue.")
    st.stop()

# Show selected cities info
with st.expander("ℹ️ About Your Selected Cities"):
    for city in selected_cities:
        city_info = UK_CITIES[city]
        st.write(f"**{city}, {city_info['region']}**: {city_info['description']}")

# Step 2: Travel Group Information
st.header("2. Travel Group Details")
col1, col2 = st.columns([1, 2])

with col1:
    group_type = st.selectbox("Who are you traveling with?", ["Solo", "Friends", "Family"])

group_size = 1
ages = []

with col2:
    if group_type == "Friends":
        group_size = st.number_input("Number of friends (including yourself):", min_value=1, max_value=10, value=2)
    elif group_type == "Family":
        subcol1, subcol2 = st.columns(2)
        with subcol1:
            adults = st.number_input("Number of adults:", min_value=1, max_value=10, value=2)
        with subcol2:
            children = st.number_input("Number of children:", min_value=0, max_value=10, value=0)
        group_size = adults + children
        
        if children > 0:
            st.write("Ages of children:")
            ages_cols = st.columns(min(children, 4))
            ages = []
            for i in range(children):
                with ages_cols[i % 4]:
                    age = st.number_input(f"Child {i+1}:", min_value=0, max_value=17, value=8, key=f"child_{i}")
                    ages.append(age)

# Step 3: Dates and Duration
st.header("3. Travel Dates & Duration")
col1, col2 = st.columns(2)

with col1:
    start_date = st.date_input(
        "Start Date:",
        min_value=datetime.date.today(),
        value=datetime.date.today() + timedelta(days=30)
    )

with col2:
    duration = st.number_input("Duration (days):", min_value=1, max_value=30, value=5)

end_date = start_date + timedelta(days=duration-1)
travel_dates = (start_date, end_date)

# Step 4: Travel Preferences
st.header("4. Travel Preferences")
col1, col2 = st.columns(2)

with col1:
    travel_style = st.selectbox(
        "Travel Style:",
        ["budget", "mid", "luxury"],
        format_func=lambda x: {"budget": "Budget-friendly", "mid": "Mid-range", "luxury": "Luxury"}[x]
    )

with col2:
    interests = st.multiselect(
        "Interests (optional):",
        ["History", "Art & Culture", "Food & Drink", "Nature & Parks", "Shopping", 
         "Nightlife", "Sports", "Architecture", "Music", "Literature"],
        help="Select your interests for personalised recommendations"
    )

# Generate Results Button
if st.button("🚀 Generate AI-Powered Vacation Plan", type="primary", use_container_width=True):
    # Check rate limit
    if not rate_limiter.check_rate_limit():
        st.stop()
    
    # Create user context
    user_context = create_user_context(
        selected_cities, group_type, group_size, ages, 
        duration, travel_style, start_date, interests
    )
    
    # Show context in debug mode
    if show_context:
        with st.expander("Debug: User Context"):
            st.code(user_context)
    
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Destination Research
    status_text.text("Analysing destinations...")
    progress_bar.progress(10)
    
    st.header("🏛️ Destination Research")
    for city in selected_cities:
        with st.expander(f"{city}, {UK_CITIES[city]['region']}"):
            st.write(f"**Description:** {UK_CITIES[city]['description']}")
            st.write(f"**Top Highlights:** {', '.join(UK_CITIES[city]['highlights'])}")
            st.write(f"**Local Transport:** {UK_CITIES[city]['transport']}")
    
    # Travel Options
    status_text.text("Calculating travel options...")
    progress_bar.progress(20)
    
    st.header("🚗 Travel Options")
    travel_options = get_travel_options(selected_cities)
    for option, details in travel_options.items():
        st.write(f"**{option}:** {details}")
    
    # Budget Calculator
    status_text.text("Calculating budget...")
    progress_bar.progress(30)
    
    st.header("💰 Budget Estimate")
    budget = calculate_budget(selected_cities, duration, group_size, travel_style)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Daily Cost per Person", f"£{budget['daily_per_person']}")
    with col2:
        st.metric("Total Trip Cost", f"£{budget['total_trip']}")
    
    with st.expander("Cost Breakdown"):
        for category, amount in budget['breakdown'].items():
            st.write(f"- {category}: £{amount}")
    
    # AI-Generated Itinerary
    status_text.text("Creating personalised itinerary...")
    progress_bar.progress(50)
    
    st.header("🤖 AI-Generated Itinerary")
    
    # Prepare city descriptions
    city_descriptions = []
    for city in selected_cities:
        city_info = UK_CITIES[city]
        city_descriptions.append(
            f"{city}: {city_info['description']}. Key attractions: {', '.join(city_info['highlights'][:4])}"
        )
    
    itinerary_prompt = ITINERARY_PROMPT_TEMPLATE.format(
        duration=duration,
        cities=', '.join(selected_cities),
        city_descriptions='\n'.join(city_descriptions)
    )
    
    if use_cache:
        # Create a hash for caching
        prompt_hash = hashlib.md5(f"{itinerary_prompt}{user_context}".encode()).hexdigest()
        with st.spinner("Creating your personalised itinerary..."):
            ai_itinerary = get_ai_recommendations_cached(prompt_hash, itinerary_prompt, user_context, SYSTEM_PROMPT)
        st.write(ai_itinerary)
    else:
        # Stream the response
        with st.chat_message("assistant", avatar="🤖"):
            response = asyncio.run(
                get_ai_response_async(itinerary_prompt, user_context, SYSTEM_PROMPT)
            )
            if isinstance(response, str):
                st.error(response)
            else:
                st.write_stream(stream_response(response))
    
    # AI-Generated Dining Recommendations
    status_text.text("Finding the best restaurants...")
    progress_bar.progress(70)
    
    st.header("🍽️ AI Dining Recommendations")
    
    dining_prompt = DINING_PROMPT_TEMPLATE.format(cities=', '.join(selected_cities))
    
    if use_cache:
        prompt_hash = hashlib.md5(f"{dining_prompt}{user_context}".encode()).hexdigest()
        with st.spinner("Finding the best restaurants and dining experiences..."):
            ai_dining = get_ai_recommendations_cached(prompt_hash, dining_prompt, user_context, SYSTEM_PROMPT)
        st.write(ai_dining)
    else:
        with st.chat_message("assistant", avatar="🍴"):
            response = asyncio.run(
                get_ai_response_async(dining_prompt, user_context, SYSTEM_PROMPT)
            )
            if isinstance(response, str):
                st.error(response)
            else:
                st.write_stream(stream_response(response))
    
    # AI-Generated Packing List
    status_text.text("Creating packing list...")
    progress_bar.progress(90)
    
    st.header("🎒 AI-Generated Packing List")
    
    season = "winter" if start_date.month in [12, 1, 2] else "summer" if start_date.month in [6, 7, 8] else "spring/autumn"
    
    packing_prompt = PACKING_LIST_PROMPT_TEMPLATE.format(
        duration=duration,
        cities=', '.join(selected_cities),
        season=season
    )
    
    if use_cache:
        prompt_hash = hashlib.md5(f"{packing_prompt}{user_context}".encode()).hexdigest()
        with st.spinner("Creating your personalized packing list..."):
            ai_packing = get_ai_recommendations_cached(prompt_hash, packing_prompt, user_context, SYSTEM_PROMPT)
        st.write(ai_packing)
    else:
        with st.chat_message("assistant", avatar="🎒"):
            response = asyncio.run(
                get_ai_response_async(packing_prompt, user_context, SYSTEM_PROMPT)
            )
            if isinstance(response, str):
                st.error(response)
            else:
                st.write_stream(stream_response(response))
    
    # Complete
    status_text.text("✨ Your vacation plan is ready!")
    progress_bar.progress(100)
    
    # Success notification
    st.toast("Your UK vacation plan has been generated! 🎉", icon="✅")
    
    # Add to session state for history
    if 'plans' not in st.session_state:
        st.session_state.plans = []
    
    st.session_state.plans.append({
        'timestamp': datetime.datetime.now(),
        'cities': selected_cities,
        'duration': duration,
        'group_size': group_size,
        'travel_style': travel_style
    })

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("*🤖 Powered by OpenAI GPT-4*")
with col2:
    st.markdown("*🇬🇧 Have a wonderful trip!*")
with col3:
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()