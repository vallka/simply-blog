import json
import csv
import requests
import os
import time
from django.views import generic
from django.conf import settings




# Create your views here.
class WeatherView(generic.TemplateView):
    template_name = 'weather/page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        store_path = settings.MEDIA_ROOT + '/weather/good_forecast.json'
        
        try:
            tm = os.path.getmtime(store_path) 
            if int(time.time())-int(tm) > 1 * 60 * 60:
                raise Exception("Cache expired")

            with open(store_path) as json_file:
                context['good_forecast'] = json.load(json_file) 

        except Exception as e:
            with open(settings.MEDIA_ROOT + '/weather/ScottishTowns.csv', 'r') as file:
                cities = []
                reader = csv.reader(file)

                for row in reader:
                    cities.append(row)

            print(cities)        

            forecast = {}
            dates = []
            for p in cities:
                r=requests.get(f'https://api.open-meteo.com/v1/forecast?latitude={p[1]}&longitude={p[2]}' + 
                               '&daily=temperature_2m_max,precipitation_sum,weather_code,wind_speed_10m_max' +
                               '&wind_speed_unit=ms&timezone=Europe%2FLondon&forecast_days=14')
                data = json.loads(r.text)
                print(p[0], data)
                forecast[p[0]] = {}
                forecast[p[0]]['daily'] = data['daily']

                if not dates: dates = data['daily']['time']

            good_forecast = {
                    'dates':dates,
                    'forecast':{}}

            for city,f in forecast.items():
                print(city)
                good_periods = []
                good = 0
                temp_max=0
                wind_max=0
                ix = 0
                for i,w in enumerate(f['daily']['weather_code']):
                    good_periods.append({})
                    if good:
                        if w>=10:
                            good_periods[i] = {'good':0}
                            if good>1: good_periods[ix]= {'good':1,'date':start,'length':good,'temp_max':temp_max,'wind_max':wind_max}
                            else: good_periods[ix] = {'good':0,'length':1}
                            good = 0
                        else:
                            good_periods[i] = {'good':2}
                            good += 1
                            if f['daily']['temperature_2m_max'][i]>temp_max: temp_max = f['daily']['temperature_2m_max'][i]
                            if f['daily']['wind_speed_10m_max'][i]>wind_max: wind_max = f['daily']['wind_speed_10m_max'][i]

                            if i==len(f['daily']['weather_code'])-1: good_periods[ix]= {'good':1,'date':start,'length':good,'temp_max':temp_max,'wind_max':wind_max}
                    else:
                        good_periods[i] = {'good':0,'length':1}
                        if w<10:
                            good = 1
                            ix = i
                            start = f['daily']['time'][i]
                            temp_max = f['daily']['temperature_2m_max'][i]
                            wind_max = f['daily']['wind_speed_10m_max'][i]

                    #print(i,w)

                good_forecast['forecast'][city] = good_periods

                #print(good_periods)    

            with open(store_path, 'w') as json_file:
                json.dump(good_forecast, json_file, indent=4)    

            context['good_forecast'] = good_forecast

        return context 