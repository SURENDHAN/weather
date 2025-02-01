import pandas as pd
import requests

def city(city_name):
    url = "https://weatherapi-com.p.rapidapi.com/forecast.json"
    querystring = {"q": city_name, "days": "3"}

    headers = {
        "x-rapidapi-key": "caae8a9fafmsh6b86fdd6f63a901p11c47fjsn47e96f6f45c1", 
        "x-rapidapi-host": "weatherapi-com.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    data = response.json()

    if 'error' not in data:
        weather_data = {
            'City': [data['location']['name']],
            'Region': [data['location']['region']],
            'Heat Index':[data['current']['heatindex_c']],
            'Temperature (°C)': [data['current']['temp_c']],
            'Humidity (%)': [data['current']['humidity']],
            'Wind Speed (mph)': [data['current']['wind_mph']],
            'Condition': [data['current']['condition']['text']],
            'Last Updated':[data['current']['last_updated']]
        }
        df = pd.DataFrame(weather_data)
        
        
        lat = data['location']['lat']
        lon = data['location']['lon']
        
        return df, {'lat': lat, 'lon': lon}
    else:
        df = pd.DataFrame() 
        return df, None 


import requests

def get_weather_news_for_place(place, country_code='IN'):
    news_api_key = '568f66032bf6460e9dcdb60954ee4ade'
    
    query = f'{place} AND {country_code} AND (rain OR storm OR cyclone OR flood)'
    
    url = f'https://newsapi.org/v2/everything?q={query}&apiKey={news_api_key}'
    
    try:
        response = requests.get(url)
        response.raise_for_status() 
        news_data = response.json()
        
        if news_data['status'] == 'ok':
            filtered_articles = [
                article for article in news_data['articles'] 
                if place.lower() in article['title'].lower()
                and not any(
                    term in article['title'].lower() or term in article['description'].lower()
                    for term in ["removed", "this article is no longer available", "out of service", "deleted", "irrelevant"]
                )
                and article['description'].strip() not in ["", "removed", "this article is no longer available"]
            ]
            
            return [{'title': article['title'], 'description': article['description'], 'url': article['url']} for article in filtered_articles]
        else:
            return []
    except requests.exceptions.RequestException as e:
        print(f"Error fetching news: {e}")
        return []


