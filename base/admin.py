from django.contrib import admin
from .models import CatVaccination , DogVaccination , Pet , AdoptionPost , BreedingPost , Product, Store, Doctor, DoctorPost , CustomUser


from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'country', 'is_staff', 'is_active')
    list_filter = ('country', 'is_staff', 'is_active', 'is_superuser')

    fieldsets = UserAdmin.fieldsets + (
        (_('Extra Info'), {'fields': ('country', 'user_photo')}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (_('Extra Info'), {'fields': ('country', 'user_photo')}),
    )

    search_fields = ('username', 'email', 'country')
    ordering = ('username',)


admin.site.register(Pet)
admin.site.register(CatVaccination)
admin.site.register(DogVaccination)
admin.site.register(AdoptionPost)
admin.site.register(BreedingPost)
admin.site.register(Product)
admin.site.register(Store)
admin.site.register(Doctor)
admin.site.register(DoctorPost)
