from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import state_get
from . import data_import
import folium
import requests
def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Sign-up failed. Please correct the errors below.')
    else:
        form = UserCreationForm()

    return render(request, 'demo/signup.html', {'form': form})
def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'demo/login.html')

def get_weather_news(place, country_code='IN'):
    news_api_key = '568f66032bf6460e9dcdb60954ee4ade'
    query = f'{place} AND {country_code} AND (rain OR storm OR cyclone OR flood)'
    
    url = f'https://newsapi.org/v2/everything?q={query}&apiKey={news_api_key}'
    try:
        response = requests.get(url)
        response.raise_for_status()  
        news_data = response.json()
        
        if news_data['status'] == 'ok':
            return news_data['articles']
        else:
            return []
    except requests.exceptions.RequestException as e:
        messages.error(f"Error fetching news: {str(e)}")
        return []


@login_required
def home(request):
    form = state_get(request.POST or None)
    result = None
    folium_map = None 
    news_articles = None
    recommendation = None  

    try:
        if request.method == "POST" and form.is_valid():
            city_name = form.cleaned_data['name']
            
            
            df, coordinates = data_import.city(city_name)

            if not df.empty:
                result = df.to_html(classes="table table-bordered", index=False)

                
                temperature = df['Temperature (°C)'].iloc[0] 
                heat_index = df['Heat Index'].iloc[0]  
                humidity = df['Humidity (%)'].iloc[0] 
                wind_speed = df['Wind Speed (mph)'].iloc[0]  
                condition = df['Condition'].iloc[0]  

               
                if temperature < 15.0:
                    recommendation = "It's cold! Consider wearing a sweater."
                elif 15.0 <= temperature < 25.0:
                    recommendation = "The weather is mild. A light jacket should be fine."
                elif temperature >= 25.0:
                    recommendation = "It's warm outside. Dress lightly."

               
                if heat_index > 35.0:
                    recommendation += " The heat index is very high, stay hydrated and avoid direct sunlight."
                elif heat_index > 30.0:
                    recommendation += " It's quite hot outside, stay cool and drink plenty of water."

               
                if humidity > 80:
                    recommendation += " The humidity is high, consider wearing breathable clothing."
                elif humidity < 40:
                    recommendation += " The air is dry, make sure to stay hydrated and moisturize your skin."

                
                if wind_speed > 20:
                    recommendation += " Winds are strong, you may want to avoid outdoor activities."
                elif wind_speed < 5:
                    recommendation += " Winds are calm, perfect for outdoor activities."

                if "rain" in condition.lower():
                    recommendation += " It's raining, don't forget your umbrella!"
                elif "storm" in condition.lower():
                    recommendation += " A storm is expected, stay indoors if possible."
                elif "mist" in condition.lower():
                    recommendation += " There is mist, drive safely and be cautious."

            else:
                result = "No data found for the provided city/state."

            if coordinates:
                lat, lon = coordinates['lat'], coordinates['lon']
              
                folium_map = folium.Map(location=[lat, lon], zoom_start=10)
                folium.Marker([lat, lon], popup=f"<b>{city_name}</b>", tooltip="Click for more info").add_to(folium_map)
                folium_map = folium_map._repr_html_()  

           
            news_articles = get_weather_news(city_name)

    except Exception as e:
        result = f"An error occurred: {str(e)}"
        

    return render(request, 'demo/result.html', {
        'form': form,
        'result': result,
        'folium_map': folium_map,
        'news_articles': news_articles,
        'recommendation': recommendation,  
    })
