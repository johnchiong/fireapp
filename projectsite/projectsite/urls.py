from django.contrib import admin
from django.urls import path
from fire import views
from fire.views import HomePageView, ChartView, PieCountbySeverity, LineCountbyMonth, MultilineIncidentTop3Country, multipleBarbySeverity
from fire.views import LocationList, LocationCreateView, LocationUpdateView, LocationDeleteView
from fire.views import IncidentList, IncidentCreateView, IncidentUpdateView, IncidentDeleteView
from fire.views import FireStationtList, FireStationCreateView, FireStationUpdateView, FireStationDeleteView
from fire.views import FireFighterstList, FireFightersCreateView, FireFightersUpdateView, FireFightersDeleteView
from fire.views import FireTruckList, FireTruckCreateView, FireTruckUpdateView, FireTruckDeleteView
from fire.views import WeatherList, WeatherCreateView, WeatherUpdateView, WeatherDeleteView

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', HomePageView.as_view(), name='home'),
    path('dashboard_chart', ChartView.as_view(), name='dashboard-charts'),
    path('chart/', PieCountbySeverity, name='chart'),
    path('lineChart/', LineCountbyMonth, name='chart'),
    path('multilineChart/', MultilineIncidentTop3Country, name='chart'),
    path('multiBarChart/', multipleBarbySeverity, name='chart'),

    path('stations', views.map_station, name='map-station'),
    path('incidents', views.map_incidents, name='map-incidents'),

    path('location_list', LocationList.as_view(), name='location-list'),
    path('location_list/add', LocationCreateView.as_view(), name='location-add'),
    path('location_list/<pk>', LocationUpdateView.as_view(), name='location-update'),
    path('location_list/<pk>/delete', LocationDeleteView.as_view(), name='location-delete'),

    path('incident_list', IncidentList.as_view(), name='incident-list'),
    path('incident_list/add', IncidentCreateView.as_view(), name='incident-add'),
    path('incident_list/<pk>', IncidentUpdateView.as_view(), name='incident-update'),
    path('incident_list/<pk>/delete', IncidentDeleteView.as_view(), name='incident-delete'),

    path('firestation_list', FireStationtList.as_view(), name='firestation-list'),
    path('firestation_list/add', FireStationCreateView.as_view(), name='firestation-add'),
    path('firestation_list/<pk>', FireStationUpdateView.as_view(), name='firestation-update'),
    path('firestation_list/<pk>/delete', FireStationDeleteView.as_view(), name='firestation-delete'),

    path('firefighters_list', FireFighterstList.as_view(), name='firefighters-list'),
    path('firefighters_list/add', FireFightersCreateView.as_view(), name='firefighters-add'),
    path('firefighters_list/<pk>', FireFightersUpdateView.as_view(), name='firefighters-update'),
    path('firefighters_list/<pk>/delete', FireFightersDeleteView.as_view(), name='firefighters-delete'),

    path('firetruck_list', FireTruckList.as_view(), name='firetruck-list'),
    path('firetruck_list/add', FireTruckCreateView.as_view(), name='firetruck-add'),
    path('firetruck_list/<pk>', FireTruckUpdateView.as_view(), name='firetruck-update'),
    path('firetruck_list/<pk>/delete', FireTruckDeleteView.as_view(), name='firetruck-delete'),

    path('weather_list', WeatherList.as_view(), name='weather-list'),
    path('weather_list/add', WeatherCreateView.as_view(), name='weather-add'),
    path('weather_list/<pk>', WeatherUpdateView.as_view(), name='weather-update'),
    path('weather_list/<pk>/delete', WeatherDeleteView.as_view(), name='weather-delete'),
]
