<<<<<<< HEAD
"""
URL configuration for SmartExcel project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include ,path


urlpatterns = [
    path('api/admin/', admin.site.urls),
    path('api/x/', include('x.urls')),
    path('api/users/', include('users.urls')),
    path('api/excel/', include('excel.urls')),
    path('api/excelpremiere/', include('excelpremiere.urls')),
    path('api/retrieve/', include('retrieve.urls')),
    path('api/formulaire/', include('formulaire.urls')),
    path('api/Tunis/', include('Tunis.urls')),
]

=======
"""
URL configuration for SmartExcel project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include ,path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('x/', include('x.urls')),

]
>>>>>>> 05b98efc67f75b0e94f2311b07801f92443b2d3a
