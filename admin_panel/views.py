from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone

from website.models import (
    SiteSettings, Program, News, Event, DonationMethod,
    Gallery, ContactMessage
)

# ---------------------------
# Auth
# ---------------------------

def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_active and user.is_staff:
            login(request, user)
            return redirect('admin_panel:dashboard')
        messages.error(request, 'Invalid credentials or no admin access.')
    return render(request, 'admin_panel/login.html')


def admin_logout(request):
    logout(request)
    return redirect('admin_panel:login')

# keep legacy name if URLs expect it
logout_view = admin_logout


# ---------------------------
# Dashboard
# ---------------------------

@login_required
def dashboard(request):
    # Counts (also provide individually so templates can access directly)
    programs_count = Program.objects.count()
    news_count = News.objects.count()
    events_count = Event.objects.count()
    gallery_count = Gallery.objects.count()
    messages_unread_count = ContactMessage.objects.filter(is_read=False).count()
    messages_total_count = ContactMessage.objects.count()

    # Recent items
    recent_news = News.objects.filter(is_published=True).order_by('-updated_at', '-id')[:5]
    recent_events = Event.objects.filter(is_published=True).order_by('-event_date', '-id')[:5]
    recent_messages = ContactMessage.objects.order_by('-created_at')[:5]

    # Staff users snapshot (for dashboard table)
    staff_users = User.objects.filter(is_staff=True).order_by('-is_superuser', 'username')

    context = {
        # for old templates using stats dict
        'stats': {
            'programs_count': programs_count,
            'news_count': news_count,
            'events_count': events_count,
            'gallery_count': gallery_count,
            'messages_count': messages_unread_count,
            'messages_total_count': messages_total_count,
        },
        # for templates accessing directly
        'programs_count': programs_count,
        'news_count': news_count,
        'events_count': events_count,
        'gallery_count': gallery_count,
        'messages_count': messages_unread_count,
        'messages_total_count': messages_total_count,

        'recent_news': recent_news,
        'recent_events': recent_events,
        'recent_messages': recent_messages,

        'staff_users': staff_users,
        'now': timezone.now(),
    }
    return render(request, 'admin_panel/dashboard.html', context)


# ---------------------------
# Site settings
# ---------------------------

@login_required
def site_settings(request):
    settings, _ = SiteSettings.objects.get_or_create(pk=1)

    if request.method == 'POST':
        settings.site_name = request.POST.get('site_name', '')
        settings.tagline = request.POST.get('tagline', '')
        settings.description = request.POST.get('description', '')
        settings.phone = request.POST.get('phone', '')
        settings.email = request.POST.get('email', '')
        settings.address = request.POST.get('address', '')
        settings.facebook_url = request.POST.get('facebook_url', '')
        settings.twitter_url = request.POST.get('twitter_url', '')
        settings.instagram_url = request.POST.get('instagram_url', '')
        settings.whatsapp_number = request.POST.get('whatsapp_number', '')
        settings.google_maps_embed = request.POST.get('google_maps_embed', '')
        settings.save()
        messages.success(request, 'Site settings updated successfully!')
        return redirect('admin_panel:site_settings')

    return render(request, 'admin_panel/site_settings.html', {'settings': settings})


# ---------------------------
# Programs
# ---------------------------

@login_required
def programs_list(request):
    programs = Program.objects.order_by('-updated_at', 'title')
    return render(request, 'admin_panel/programs_list.html', {'programs': programs})

@login_required
def program_add(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '')
        image = request.FILES.get('image')
        is_active = request.POST.get('is_active') == 'on'

        Program.objects.create(
            title=title,
            description=description,
            image=image,
            is_active=is_active
        )
        messages.success(request, 'Program added successfully!')
        return redirect('admin_panel:programs_list')

    return render(request, 'admin_panel/program_form.html', {'action': 'Add'})

@login_required
def program_edit(request, pk):
    program = get_object_or_404(Program, pk=pk)
    if request.method == 'POST':
        program.title = request.POST.get('title', '').strip()
        program.description = request.POST.get('description', '')
        if request.FILES.get('image'):
            program.image = request.FILES.get('image')
        program.is_active = request.POST.get('is_active') == 'on'
        program.save()
        messages.success(request, 'Program updated successfully!')
        return redirect('admin_panel:programs_list')

    return render(request, 'admin_panel/program_form.html', {'action': 'Edit', 'program': program})

@login_required
def program_delete(request, pk):
    program = get_object_or_404(Program, pk=pk)
    program.delete()
    messages.success(request, 'Program deleted successfully!')
    return redirect('admin_panel:programs_list')


# ---------------------------
# News
# ---------------------------

@login_required
def news_list(request):
    news = News.objects.order_by('-updated_at', 'title')
    return render(request, 'admin_panel/news_list.html', {'news': news})

@login_required
def news_add(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '')
        image = request.FILES.get('image')
        is_published = request.POST.get('is_published') == 'on'

        News.objects.create(
            title=title,
            content=content,
            image=image,
            is_published=is_published
        )
        messages.success(request, 'News article added successfully!')
        return redirect('admin_panel:news_list')

    return render(request, 'admin_panel/news_form.html', {'action': 'Add'})

@login_required
def news_edit(request, pk):
    news = get_object_or_404(News, pk=pk)
    if request.method == 'POST':
        news.title = request.POST.get('title', '').strip()
        news.content = request.POST.get('content', '')
        if request.FILES.get('image'):
            news.image = request.FILES.get('image')
        news.is_published = request.POST.get('is_published') == 'on'
        news.save()
        messages.success(request, 'News article updated successfully!')
        return redirect('admin_panel:news_list')

    return render(request, 'admin_panel/news_form.html', {'action': 'Edit', 'news': news})

@login_required
def news_delete(request, pk):
    news = get_object_or_404(News, pk=pk)
    news.delete()
    messages.success(request, 'News article deleted successfully!')
    return redirect('admin_panel:news_list')


# ---------------------------
# Events
# ---------------------------

@login_required
def events_list(request):
    # IMPORTANT: your Event model has 'event_date' but not 'start_datetime'
    events = Event.objects.order_by('-event_date', 'title')
    return render(request, 'admin_panel/events_list.html', {'events': events})

@login_required
def events_add(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '')
        event_date = request.POST.get('event_date')  # YYYY-MM-DD
        location = request.POST.get('location', '')
        image = request.FILES.get('image')
        is_published = request.POST.get('is_published') == 'on'

        Event.objects.create(
            title=title,
            description=description,
            event_date=event_date,
            location=location,
            image=image,
            is_published=is_published
        )
        messages.success(request, 'Event added successfully!')
        return redirect('admin_panel:events_list')

    return render(request, 'admin_panel/event_form.html', {'action': 'Add'})

@login_required
def events_edit(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        event.title = request.POST.get('title', '').strip()
        event.description = request.POST.get('description', '')
        event.event_date = request.POST.get('event_date')
        event.location = request.POST.get('location', '')
        if request.FILES.get('image'):
            event.image = request.FILES.get('image')
        event.is_published = request.POST.get('is_published') == 'on'
        event.save()
        messages.success(request, 'Event updated successfully!')
        return redirect('admin_panel:events_list')

    return render(request, 'admin_panel/event_form.html', {'action': 'Edit', 'event': event})

@login_required
def events_delete(request, pk):
    event = get_object_or_404(Event, pk=pk)
    event.delete()
    messages.success(request, 'Event deleted successfully!')
    return redirect('admin_panel:events_list')


# ---------------------------
# Donations
# ---------------------------

@login_required
def donations_list(request):
    donations = DonationMethod.objects.order_by('order', 'name')
    return render(request, 'admin_panel/donations_list.html', {'donations': donations})

@login_required
def donations_add(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        account_number = request.POST.get('account_number', '').strip()
        bank_name = request.POST.get('bank_name', '').strip()
        description = request.POST.get('description', '')
        is_active = request.POST.get('is_active') == 'on'
        order = int(request.POST.get('order', 0) or 0)

        DonationMethod.objects.create(
            name=name,
            account_number=account_number,
            bank_name=bank_name,
            description=description,
            is_active=is_active,
            order=order
        )
        messages.success(request, 'Donation method added successfully!')
        return redirect('admin_panel:donations_list')

    return render(request, 'admin_panel/donation_form.html', {'action': 'Add'})

@login_required
def donations_edit(request, pk):
    donation = get_object_or_404(DonationMethod, pk=pk)
    if request.method == 'POST':
        donation.name = request.POST.get('name', '').strip()
        donation.account_number = request.POST.get('account_number', '').strip()
        donation.bank_name = request.POST.get('bank_name', '').strip()
        donation.description = request.POST.get('description', '')
        donation.is_active = request.POST.get('is_active') == 'on'
        donation.order = int(request.POST.get('order', 0) or 0)
        donation.save()
        messages.success(request, 'Donation method updated successfully!')
        return redirect('admin_panel:donations_list')

    return render(request, 'admin_panel/donation_form.html', {'action': 'Edit', 'donation': donation})

@login_required
def donations_delete(request, pk):
    donation = get_object_or_404(DonationMethod, pk=pk)
    donation.delete()
    messages.success(request, 'Donation method deleted successfully!')
    return redirect('admin_panel:donations_list')


# ---------------------------
# Gallery
# ---------------------------

@login_required
def gallery_list(request):
    gallery = Gallery.objects.order_by('-updated_at', 'title')
    return render(request, 'admin_panel/gallery_list.html', {'gallery': gallery})

@login_required
def gallery_add(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        image = request.FILES.get('image')
        description = request.POST.get('description', '')
        is_published = request.POST.get('is_published') == 'on'

        Gallery.objects.create(
            title=title,
            image=image,
            description=description,
            is_published=is_published
        )
        messages.success(request, 'Gallery item added successfully!')
        return redirect('admin_panel:gallery_list')

    return render(request, 'admin_panel/gallery_form.html', {'action': 'Add'})

@login_required
def gallery_edit(request, pk):
    gallery_item = get_object_or_404(Gallery, pk=pk)
    if request.method == 'POST':
        gallery_item.title = request.POST.get('title', '').strip()
        if request.FILES.get('image'):
            gallery_item.image = request.FILES.get('image')
        gallery_item.description = request.POST.get('description', '')
        gallery_item.is_published = request.POST.get('is_published') == 'on'
        gallery_item.save()
        messages.success(request, 'Gallery item updated successfully!')
        return redirect('admin_panel:gallery_list')

    return render(request, 'admin_panel/gallery_form.html', {'action': 'Edit', 'gallery_item': gallery_item})

@login_required
def gallery_delete(request, pk):
    gallery_item = get_object_or_404(Gallery, pk=pk)
    gallery_item.delete()
    messages.success(request, 'Gallery item deleted successfully!')
    return redirect('admin_panel:gallery_list')


# ---------------------------
# Contact messages
# ---------------------------

@login_required
def messages_list(request):
    messages_qs = ContactMessage.objects.order_by('-created_at')
    return render(request, 'admin_panel/messages_list.html', {'messages': messages_qs})

@login_required
def message_detail(request, pk):
    message_obj = get_object_or_404(ContactMessage, pk=pk)
    if not message_obj.is_read:
        message_obj.is_read = True
        message_obj.save(update_fields=['is_read'])
    return render(request, 'admin_panel/message_detail.html', {'message': message_obj})

@login_required
def message_delete(request, pk):
    message_obj = get_object_or_404(ContactMessage, pk=pk)
    message_obj.delete()
    messages.success(request, 'Message deleted successfully!')
    return redirect('admin_panel:messages_list')
