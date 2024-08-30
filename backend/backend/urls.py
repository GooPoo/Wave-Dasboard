from django.conf import settings
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import include, path
from two_factor.gateways.twilio.urls import urlpatterns as tf_twilio_urls
from two_factor.urls import urlpatterns as tf_urls
from .views import (
    CombinedView, PredictionView, ForecastView, BuoyView, HomeView, RegistrationCompleteView, RegistrationView, LoggingView, WindView, log_request, file_arrival_times, prediction_12hours, forecast_12hours, buoy_12hours, wind_12hours, registration_disabled_page
)

urlpatterns = [
    path(
        '',
        HomeView.as_view(),
        name='home',
    ),
    path(
        'account/logout/',
        LogoutView.as_view(),
        name='logout',
    ),
    path(
        'combined/',
        CombinedView.as_view(),
        name='combined',
    ),
    path(
        'prediction/',
        PredictionView.as_view(),
        name='prediction',
    ),
    path(
        'forecast/',
        ForecastView.as_view(),
        name='forecast',
    ),
    path(
        'buoy/',
        BuoyView.as_view(),
        name='buoy',
    ),
    path(
        'wind/',
        WindView.as_view(),
        name='wind',
    ),
    path(
        'account/register/',
        RegistrationView.as_view(),
        name='registration',
    ),
    path(
        'account/register/done/',
        RegistrationCompleteView.as_view(),
        name='registration_complete',
    ),
     path(
        'registration_disabled/',  # Add this path for the Registration Disabled page
        registration_disabled_page,
        name='registration_disabled_page',
    ),
    path('logging/', LoggingView.as_view(), name='logging'),
    path('', include(tf_urls)),
    path('', include(tf_twilio_urls)),
    path('', include('user_sessions.urls', 'user_sessions')),
    path('prediction_12hours/', prediction_12hours, name='prediction_12hours'),
    path('forecast_12hours/', forecast_12hours, name='forecast_12hours'),
    path('buoy_12hours/', buoy_12hours, name='buoy_12hours'),
    path('wind_12hours/', wind_12hours, name='wind_12hours'),
    path('log_request/', log_request, name='log_request'),
    path('file_arrival_times/', file_arrival_times, name='file_arrival_times'),
    path('logging/', LoggingView.as_view(), name='logging'),
    path('admin/', admin.site.urls),
    path('', include(tf_urls)),
    path('', include(tf_twilio_urls)),
    path('', include('user_sessions.urls', 'user_sessions')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]
