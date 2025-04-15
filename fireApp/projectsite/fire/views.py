from django.shortcuts import render
from django.views.generic.list import ListView
from fire.models import Locations, Incident, FireStation

from django.db import connection
from django.http import JsonResponse
from django.db.models.functions import ExtractMonth

from django.db.models import Count
from datetime import datetime

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

