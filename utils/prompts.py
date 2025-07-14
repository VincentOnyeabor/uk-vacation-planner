"""Prompt templates for the UK Vacation Planner"""

SYSTEM_PROMPT = """You are an expert UK travel planner. Provide detailed, personalised recommendations based on user preferences. Be specific and practical."""

ITINERARY_PROMPT_TEMPLATE = """
Create a detailed {duration}-day itinerary for visiting {cities}. 

Cities information:
{city_descriptions}

Please provide:
1. Daily schedule with specific activities and timings
2. Recommended restaurants and dining experiences
3. Transportation between activities
4. Group-specific recommendations
5. Local tips and hidden gems

Format as Day 1, Day 2, etc. with bullet points for each activity.
"""

PACKING_LIST_PROMPT_TEMPLATE = """
Create a comprehensive packing list for a {duration}-day trip to {cities} during {season}.

Consider:
1. Weather conditions for {season}
2. Activities available in the selected cities
3. Group composition and needs
4. UK-specific requirements
5. Trip duration and laundry availability

Organise by categories (clothing, electronics, documents, etc.) and include specific items with brief explanations where helpful.
"""

DINING_PROMPT_TEMPLATE = """
Recommend restaurants, cafes, and dining experiences for {cities}.

Include:
1. Must-try local specialties
2. Restaurant recommendations for different budgets
3. Family-friendly options if applicable
4. Unique dining experiences
5. Local food markets and street food
6. Pub recommendations for authentic British experience

Provide specific restaurant names and brief descriptions.
"""

def create_user_context(cities, group_type, group_size, ages, duration, travel_style, start_date, interests=None):
    """Create context string for AI recommendations"""
    context = f"""
    Selected UK cities: {', '.join(cities)}
    Travel group: {group_type}
    Group size: {group_size}
    Duration: {duration} days
    Travel style: {travel_style}
    Start date: {start_date}
    """
    
    if group_type == "Family" and ages:
        context += f"\nChildren ages: {', '.join(map(str, ages))}"
    
    if interests:
        context += f"\nInterests: {', '.join(interests)}"
    
    return context