from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from fire.models import Locations, Incident, FireStation, Firefighters, FireTruck, WeatherConditions

from django.db import connection
from django.http import JsonResponse
from django.db.models.functions import ExtractMonth

from django.db.models import Count
from datetime import datetime
from django.urls import reverse_lazy

from fire.forms import LocationForm, IncidentForm, FireStationForm, FirefighterForm, FireTruckForm, WeatherConditionForm

from django.contrib import messages

class HomePageView(ListView):
    model = Locations
    context_object_name = 'home'
    template_name = "home.html"
class ChartView (ListView):
    template_name = 'chart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
    
    def get_queryset(self, *args, **kwargs):
        pass

def PieCountbySeverity(request):
    query = '''
    SELECT severity_level, COUNT(*) as count
    FROM fire_incident
    GROUP BY severity_level
    '''
    data = {}
    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    if rows:
        data = {severity: count for severity, count in rows}
    else:
        data = {}

    return JsonResponse(data)

def LineCountbyMonth(request):

    current_year = datetime.now().year

    result = {month: 0 for month in range(1, 13)}

    incidents_per_month = Incident.objects.filter(date_time__year=current_year) \
        .values_list('date_time', flat=True)

    for date_time in incidents_per_month:
        month = date_time.month
        result[month] += 1

    month_names = {
        1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
        7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
    }

    result_with_month_names = {
        month_names[int(month)]: count for month, count in result.items()
    }

    return JsonResponse(result_with_month_names)

def map_station(request):
    fireStations = FireStation.objects.values('name', 'latitude', 'longitude')

    for fs in fireStations:
        fs['latitude'] = float(fs['latitude'])
        fs['longitude'] = float(fs['longitude'])
    
    fireStations_list = list(fireStations)

    context = {
        'fireStations': fireStations_list
    }

    return render(request, 'map_station.html', context)

def map_incidents(request):
    fireIncidents = Incident.objects.select_related('location').values(
        'location__city',
        'location__latitude',
        'location__longitude',
        'description',
        'date_time',
        'severity_level'
    )

    incident_list = []
    for fi in fireIncidents:
        incident_list.append({
            'city': fi['location__city'],
            'latitude': float(fi['location__latitude']),
            'longitude': float(fi['location__longitude']),
            'description': fi['description'],
            'date': fi['date_time'].strftime('%Y-%m-%d %H:%M') if fi['date_time'] else 'N/A',
            'severity': fi['severity_level']
        })

    cities = Incident.objects.select_related('location') \
        .values_list('location__city', flat=True).distinct()

    context = {
        'fireIncidents': incident_list, 
        'cities': cities,
    }

    return render(request, 'map_incidents.html', context)


def MultilineIncidentTop3Country(request):
    query = '''
    SELECT 
        fl.country, 
        strftime('%m', fi.date_time) AS month, 
        COUNT(fi.id) AS incident_count
    FROM 
        fire_incident fi
    JOIN 
        fire_locations fl ON fi.location_id = fl.id
    WHERE 
    fl.country IN (
        SELECT 
            fl_top.country
        FROM 
            fire_incident fi_top
        JOIN 
            fire_locations fl_top ON fi_top.location_id = fl_top.id
        WHERE 
            strftime('%Y', fi_top.date_time) = strftime('%Y', 'now')
        GROUP BY 
            fl_top.country
        ORDER BY 
            COUNT(fi_top.id) DESC
        LIMIT 3
    ) 
        AND strftime('%Y', fi.date_time) = strftime('%Y', 'now')
    GROUP BY 
        fl.country, month
    ORDER BY 
        fl.country, month;
    '''
    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    # Initialize a dictionary to store the result
    result = {}

    # Initialize a set of months from January to December
    months = set(str(i).zfill(2) for i in range(1, 13))

    # Loop through the query results
    for row in rows:
        country = row[0]
        month = row[1]
        total_incidents = row[2]

        # If the country is not in the result dictionary, initialize it with all months set to zero
        if country not in result:
            result[country] = {month: 0 for month in months}

        # Update the incident count for the corresponding month
        result[country][month] = total_incidents

    # Ensure there are always 3 countries in the result
    while len(result) < 3:
        # Placeholder name for missing countries
        missing_country = f"Country {len(result) + 1}"
        result[missing_country] = {month: 0 for month in months}

    # Sort months for each country
    for country in result:
        result[country] = dict(sorted(result[country].items()))

    return JsonResponse(result)


def multipleBarbySeverity(request):
    query = '''
        SELECT
            fi.severity_level,
            strftime('%m', fi.date_time) AS month,
            COUNT(fi.id) AS incident_count
        FROM
            fire_incident fi
        GROUP BY fi.severity_level, month
        '''

    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    result = {}
    months = set(str(i).zfill(2) for i in range(1, 13))

    for row in rows:
        level = str(row[0])  # Ensure the severity level is a string
        month = row[1]
        total_incidents = row[2]

        if level not in result:
            result[level] = {month: 0 for month in months}

        result[level][month] = total_incidents

    # Sort months within each severity level
    for level in result:
        result[level] = dict(sorted(result[level].items()))

    return JsonResponse(result)

# LOCATION TOAST
class LocationList(ListView):
    model = Locations
    context_object_name = 'location'
    template_name = 'location_list.html'
    paginate_by = 5

class LocationCreateView(CreateView):
    model = Locations
    form_class = LocationForm
    template_name = 'location_add.html'
    success_url = reverse_lazy('location-list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Location added successfully!')
        return response

class LocationUpdateView(UpdateView):
    model = Locations
    form_class = LocationForm
    template_name = "location_edit.html"
    success_url = reverse_lazy('location-list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Location updated successfully!')
        return response

class LocationDeleteView(DeleteView):
    model = Locations
    template_name = "location_del.html"
    success_url = reverse_lazy('location-list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Location deleted successfully!')
        return response

#INCIDENT TOAST
class IncidentList(ListView):
    model = Incident
    context_object_name = 'incident'
    template_name = 'incident_list.html'
    paginate_by = 5

class IncidentCreateView(CreateView):
    model = Incident
    form_class = IncidentForm
    template_name = 'incident_add.html'
    success_url = reverse_lazy('incident-list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Incident added successfully!')
        return response

class IncidentUpdateView(UpdateView):
    model = Incident
    form_class = IncidentForm
    template_name = "incident_edit.html"
    success_url = reverse_lazy('incident-list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Incident updated successfully!')
        return response

class IncidentDeleteView(DeleteView):
    model = Incident
    template_name = "incident_del.html"
    success_url = reverse_lazy('incident-list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Incident deleted successfully!')
        return response

#FIRE STATION TOAST
class FireStationtList(ListView):
    model = FireStation
    context_object_name = 'firestation'
    template_name = 'firestation_list.html'
    paginate_by = 5

class FireStationCreateView(CreateView):
    model = FireStation
    form_class = FireStationForm
    template_name = 'firestation_add.html'
    success_url = reverse_lazy('firestation-list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Fire Station added successfully!')
        return response

class FireStationUpdateView(UpdateView):
    model = FireStation
    form_class = FireStationForm
    template_name = "firestation_edit.html"
    success_url = reverse_lazy('firestation-list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Fire Station updated successfully!')
        return response

class FireStationDeleteView(DeleteView):
    model = FireStation
    template_name = "firestation_del.html"
    success_url = reverse_lazy('firestation-list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Fire Station deleted successfully!')
        return response

#FIREFIGHTER TOAST
class FireFighterstList(ListView):
    model = Firefighters
    context_object_name = 'firefighters'
    template_name = 'firefighters_list.html'
    paginate_by = 5

class FireFightersCreateView(CreateView):
    model = Firefighters
    form_class = FirefighterForm
    template_name = 'firefighters_add.html'
    success_url = reverse_lazy('firefighters-list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Firefighter added successfully!')
        return response

class FireFightersUpdateView(UpdateView):
    model = Firefighters
    form_class = FirefighterForm
    template_name = "firefighters_edit.html"
    success_url = reverse_lazy('firefighters-list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Firefighter updated successfully!')
        return response
    
class FireFightersDeleteView(DeleteView):
    model = Firefighters
    template_name = "firefighters_del.html"
    success_url = reverse_lazy('firefighters-list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Firefighter deleted successfully!')
        return response

#FIRETRUCK TOAST
class FireTruckList(ListView):
    model = FireTruck
    context_object_name = 'firetruck'
    template_name = 'firetruck_list.html'
    paginate_by = 5

class FireTruckCreateView(CreateView):
    model = FireTruck
    form_class = FireTruckForm
    template_name = 'firetruck_add.html'
    success_url = reverse_lazy('firetruck-list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Firetruck added successfully!')
        return response

class FireTruckUpdateView(UpdateView):
    model = FireTruck
    form_class = FireTruckForm
    template_name = "firetruck_edit.html"
    success_url = reverse_lazy('firetruck-list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Firetruck updated successfully!')
        return response

class FireTruckDeleteView(DeleteView):
    model = FireTruck
    template_name = "firetruck_del.html"
    success_url = reverse_lazy('firetruck-list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Firetruck deleted successfully!')
        return response

#WEATHER TOAST
class WeatherList(ListView):
    model = WeatherConditions
    context_object_name = 'weathercondition'
    template_name = 'weather_list.html'
    paginate_by = 5

class WeatherCreateView(CreateView):
    model = WeatherConditions
    form_class = WeatherConditionForm
    template_name = 'weather_add.html'
    success_url = reverse_lazy('weather-list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Weather added successfully!')
        return response

class WeatherUpdateView(UpdateView):
    model = WeatherConditions
    form_class = WeatherConditionForm
    template_name = "weather_edit.html"
    success_url = reverse_lazy('weather-list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Weather updated successfully!')
        return response

class WeatherDeleteView(DeleteView):
    model = WeatherConditions
    template_name = "weather_del.html"
    success_url = reverse_lazy('weather-list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Weather deleted successfully!')
        return response
