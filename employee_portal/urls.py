from django.urls import path
from .views import index_portal , edit_profile, confirm_password_change,change_password, my_renditions

urlpatterns = [
    path('', index_portal, name='profile'),
    path('perfil/editar/', edit_profile, name='edit_profile'),
    path('perfil/cambiar-contraseña/confirmacion/', confirm_password_change, name='confirm_password_change'),
    path('perfil/cambiar-contraseña/', change_password, name='change_password'),
    path('my-renditions/', my_renditions, name='my_renditions'),

]
