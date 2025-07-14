import streamlit as st
import time
from datetime import datetime, timedelta

class RateLimiter:
    def __init__(self, max_requests: int = 10, window_minutes: int = 5):
        self.max_requests = max_requests
        self.window_minutes = window_minutes
        
    def check_rate_limit(self):
        """Check if user has exceeded rate limit"""
        current_time = datetime.now()
        
        # Initialize rate limit tracking in session state
        if 'api_requests' not in st.session_state:
            st.session_state.api_requests = []
        
        # Remove old requests outside the window
        cutoff_time = current_time - timedelta(minutes=self.window_minutes)
        st.session_state.api_requests = [
            req_time for req_time in st.session_state.api_requests 
            if req_time > cutoff_time
        ]
        
        # Check if limit exceeded
        if len(st.session_state.api_requests) >= self.max_requests:
            remaining_time = (st.session_state.api_requests[0] + timedelta(minutes=self.window_minutes) - current_time).seconds // 60
            st.warning(f"⚠️ Rate limit reached! Please wait {remaining_time} minutes before making more requests.")
            return False
        
        # Add current request
        st.session_state.api_requests.append(current_time)
        return True
    
    def get_remaining_requests(self):
        """Get number of remaining requests"""
        if 'api_requests' not in st.session_state:
            return self.max_requests
        
        current_time = datetime.now()
        cutoff_time = current_time - timedelta(minutes=self.window_minutes)
        valid_requests = [
            req_time for req_time in st.session_state.api_requests 
            if req_time > cutoff_time
        ]
        return self.max_requests - len(valid_requests)