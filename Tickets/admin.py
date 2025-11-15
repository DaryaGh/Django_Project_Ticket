from django.contrib import admin
from Tickets.models import *

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('subject',)
    fieldsets = (
        (None,{
        'fields': ('subject','description','category'),
    }),
        ("Timeline",{
            "fields":("max_replay_date","closed_at")
        }),
        ("User Info",{
            "fields":("created_at","updated_at")
        }),
    )

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('assignee_id','seen_at','status')

admin.site.register(SearchLogSignal)
# admin.site.register(Ticket)
admin.site.register(Category)
# admin.site.register(Tag)
# admin.site.register(Assignment)

# راه دوم برای ساخت logSearch
# admin.site.register(LogSearch)
