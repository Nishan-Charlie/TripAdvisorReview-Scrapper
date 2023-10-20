from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import time

app = Flask(__name__)

import requests

def get_tripadvisor_reviews(api_key, hotel_name):
    base_url = "https://api.content.tripadvisor.com/api/v1"
    search_url = f"{base_url}/location/search?key={api_key}&searchQuery={hotel_name}&key={api_key}&language=en"
    
    try:
        headers = {"accept": "application/json"}
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()
        data = response.json()
        if "data" in data and data["data"]:
            location_id = data["data"][0]["location_id"]
        else:
            return None
    except requests.exceptions.RequestException as e:
        print("Error:", e)
        return None
    
    reviews_url = f"{base_url}/location/{location_id}/reviews?key={api_key}&language=en"
    
    try:
        response = requests.get(reviews_url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data["data"]
    except requests.exceptions.RequestException as e:
        print("Error:", e)
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        start_time = time.time()  # Record the start time
        hotel_names = request.form.get('hotel_names')  # Get hotel names as a comma-separated string
        print(hotel_names)
        if hotel_names:
            hotel_names_list = hotel_names.split(',')  # Split string into a list of hotel names
            api_key = "3B2DAB65777045B4AF4A946D2E6C92F6"  # Replace with your TripAdvisor API key
            print(hotel_names_list)
            all_reviews = []
            for hotel_name in hotel_names_list:
                reviews_data = get_tripadvisor_reviews(api_key, hotel_name)  # Remove whitespace

                if reviews_data:
                    # Extract relevant review information for rendering
                    reviews = []
                    for review in reviews_data:  # Get the first 5 reviews
                        review_info = {
                            "hotel": hotel_name,
                            "title": review["title"],
                            "rating": review["rating"],
                            "text": review["text"],
                            "user": {
                                "username": review["user"]["username"],
                                "user_location": review["user"]["user_location"].get("name", "Unknown Location"),
                                "avatar": review["user"]["avatar"]["thumbnail"]
                            },
                            "url": review["url"],
                            "travel_date": review["travel_date"]
                        }
                        reviews.append(review_info)
                    all_reviews.append((hotel_name, reviews))
            end_time = time.time()  # Record the end time
            total_run_time = end_time - start_time
            print(f"Total run time: {total_run_time} seconds")
            return render_template('index.html', hotel_reviews=all_reviews)
    
    return render_template('index.html', hotel_reviews=None)


if __name__ == '__main__':
    app.run(debug=True)
