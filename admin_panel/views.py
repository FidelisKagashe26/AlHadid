from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.contrib import messages as dj_messages
from django.utils import timezone
from django.db.models import Q
from django.http import HttpResponseForbidden

from website.models import (
    SiteSettings, Program, News, Event, DonationMethod,
    Gallery, ContactMessage
)

# ---------------------------
# Auth
# ---------------------------
def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username','').strip()
        password = request.POST.get('password','')
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_active and user.is_staff:
            login(request, user)
            return redirect('admin_panel:dashboard')
        dj_messages.error(request, 'Invalid credentials or no admin access.')
    return render(request, 'admin_panel/login.html')

def admin_logout(request):
    logout(request)
    return redirect('admin_panel:login')

logout_view = admin_logout  # legacy


# ---------------------------
# Dashboard
# ---------------------------
@login_required
def dashboard(request):
    programs_count = Program.objects.count()
    news_count = News.objects.count()
    events_count = Event.objects.count()
    gallery_count = Gallery.objects.count()
    messages_unread_count = ContactMessage.objects.filter(is_read=False).count()
    messages_total_count = ContactMessage.objects.count()

    recent_news = News.objects.filter(is_published=True).order_by('-updated_at', '-id')[:5]
    recent_events = Event.objects.filter(is_published=True).order_by('-event_date', '-id')[:5]
    recent_messages = ContactMessage.objects.order_by('-created_at')[:5]

    staff_users = User.objects.filter(is_staff=True).order_by('-is_superuser', 'username')

    context = {
        'stats': {
            'programs_count': programs_count,
            'news_count': news_count,
            'events_count': events_count,
            'gallery_count': gallery_count,
            'messages_count': messages_unread_count,
            'messages_total_count': messages_total_count,
        },
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
@permission_required('website.view_sitesettings', raise_exception=True)
def site_settings(request):
    settings, _ = SiteSettings.objects.get_or_create(pk=1)

    if request.method == 'POST':
        if not request.user.has_perm('website.change_sitesettings'):
            return HttpResponseForbidden("You don't have permission to change settings.")
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
        dj_messages.success(request, 'Site settings updated successfully!')
        return redirect('admin_panel:site_settings')

    return render(request, 'admin_panel/site_settings.html', {'settings': settings})


# ---------------------------
# Programs
# ---------------------------
@login_required
@permission_required('website.view_program', raise_exception=True)
def programs_list(request):
    q = request.GET.get('q','').strip()
    qs = Program.objects.all().order_by('-id')
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q))
    return render(request, 'admin_panel/programs_list.html', {'programs': qs, 'q': q})

@login_required
@permission_required('website.add_program', raise_exception=True)
def program_add(request):
    if request.method == 'POST':
        title = request.POST.get('title','').strip()
        description = request.POST.get('description','')
        image = request.FILES.get('image')
        is_active = request.POST.get('is_active') == 'on'
        Program.objects.create(title=title, description=description, image=image, is_active=is_active)
        dj_messages.success(request, 'Program added successfully!')
        return redirect('admin_panel:programs_list')
    return render(request, 'admin_panel/program_form.html', {'action':'Add'})

@login_required
@permission_required('website.change_program', raise_exception=True)
def program_edit(request, pk):
    program = get_object_or_404(Program, pk=pk)
    if request.method == 'POST':
        program.title = request.POST.get('title','').strip()
        program.description = request.POST.get('description','')
        if request.FILES.get('image'):
            program.image = request.FILES.get('image')
        program.is_active = request.POST.get('is_active') == 'on'
        program.save()
        dj_messages.success(request, 'Program updated successfully!')
        return redirect('admin_panel:programs_list')
    return render(request, 'admin_panel/program_form.html', {'action':'Edit','program':program})

@login_required
@permission_required('website.delete_program', raise_exception=True)
def program_delete(request, pk):
    program = get_object_or_404(Program, pk=pk)
    program.delete()
    dj_messages.success(request, 'Program deleted successfully!')
    return redirect('admin_panel:programs_list')


# ---------------------------
# News
# ---------------------------
@login_required
@permission_required('website.view_news', raise_exception=True)
def news_list(request):
    q = request.GET.get('q','').strip()
    qs = News.objects.all().order_by('-updated_at','-id')
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(content__icontains=q))
    return render(request, 'admin_panel/news_list.html', {'news': qs, 'q': q})

@login_required
@permission_required('website.add_news', raise_exception=True)
def news_add(request):
    if request.method == 'POST':
        title = request.POST.get('title','').strip()
        content = request.POST.get('content','')
        image = request.FILES.get('image')
        is_published = request.POST.get('is_published') == 'on'
        News.objects.create(title=title, content=content, image=image, is_published=is_published)
        dj_messages.success(request, 'News article added successfully!')
        return redirect('admin_panel:news_list')
    return render(request, 'admin_panel/news_form.html', {'action':'Add'})

@login_required
@permission_required('website.change_news', raise_exception=True)
def news_edit(request, pk):
    news = get_object_or_404(News, pk=pk)
    if request.method == 'POST':
        news.title = request.POST.get('title','').strip()
        news.content = request.POST.get('content','')
        if request.FILES.get('image'):
            news.image = request.FILES.get('image')
        news.is_published = request.POST.get('is_published') == 'on'
        news.save()
        dj_messages.success(request, 'News article updated successfully!')
        return redirect('admin_panel:news_list')
    return render(request, 'admin_panel/news_form.html', {'action':'Edit','news':news})

@login_required
@permission_required('website.delete_news', raise_exception=True)
def news_delete(request, pk):
    news = get_object_or_404(News, pk=pk)
    news.delete()
    dj_messages.success(request, 'News article deleted successfully!')
    return redirect('admin_panel:news_list')


# ---------------------------
# Events
# ---------------------------
@login_required
@permission_required('website.view_event', raise_exception=True)
def events_list(request):
    q = request.GET.get('q','').strip()
    qs = Event.objects.all().order_by('-event_date','-id')
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q) | Q(location__icontains=q))
    return render(request, 'admin_panel/events_list.html', {'events': qs, 'q': q})

@login_required
@permission_required('website.add_event', raise_exception=True)
def events_add(request):
    if request.method == 'POST':
        title = request.POST.get('title','').strip()
        description = request.POST.get('description','')
        event_date = request.POST.get('event_date')
        location = request.POST.get('location','')
        image = request.FILES.get('image')
        is_published = request.POST.get('is_published') == 'on'
        Event.objects.create(title=title, description=description, event_date=event_date,
                             location=location, image=image, is_published=is_published)
        dj_messages.success(request, 'Event added successfully!')
        return redirect('admin_panel:events_list')
    return render(request, 'admin_panel/event_form.html', {'action':'Add'})

@login_required
@permission_required('website.change_event', raise_exception=True)
def events_edit(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        event.title = request.POST.get('title','').strip()
        event.description = request.POST.get('description','')
        event.event_date = request.POST.get('event_date')
        event.location = request.POST.get('location','')
        if request.FILES.get('image'):
            event.image = request.FILES.get('image')
        event.is_published = request.POST.get('is_published') == 'on'
        event.save()
        dj_messages.success(request, 'Event updated successfully!')
        return redirect('admin_panel:events_list')
    return render(request, 'admin_panel/event_form.html', {'action':'Edit','event':event})

@login_required
@permission_required('website.delete_event', raise_exception=True)
def events_delete(request, pk):
    event = get_object_or_404(Event, pk=pk)
    event.delete()
    dj_messages.success(request, 'Event deleted successfully!')
    return redirect('admin_panel:events_list')


# ---------------------------
# Donations
# ---------------------------
@login_required
@permission_required('website.view_donationmethod', raise_exception=True)
def donations_list(request):
    q = request.GET.get('q','').strip()
    qs = DonationMethod.objects.all().order_by('order','name')
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(bank_name__icontains=q) |
                       Q(account_number__icontains=q) | Q(description__icontains=q))
    return render(request, 'admin_panel/donations_list.html', {'donations': qs, 'q': q})

@login_required
@permission_required('website.add_donationmethod', raise_exception=True)
def donations_add(request):
    if request.method == 'POST':
        name = request.POST.get('name','').strip()
        account_number = request.POST.get('account_number','').strip()
        bank_name = request.POST.get('bank_name','').strip()
        description = request.POST.get('description','')
        is_active = request.POST.get('is_active') == 'on'
        order = int(request.POST.get('order', 0) or 0)
        DonationMethod.objects.create(name=name, account_number=account_number, bank_name=bank_name,
                                      description=description, is_active=is_active, order=order)
        dj_messages.success(request, 'Donation method added successfully!')
        return redirect('admin_panel:donations_list')
    return render(request, 'admin_panel/donation_form.html', {'action':'Add'})

@login_required
@permission_required('website.change_donationmethod', raise_exception=True)
def donations_edit(request, pk):
    donation = get_object_or_404(DonationMethod, pk=pk)
    if request.method == 'POST':
        donation.name = request.POST.get('name','').strip()
        donation.account_number = request.POST.get('account_number','').strip()
        donation.bank_name = request.POST.get('bank_name','').strip()
        donation.description = request.POST.get('description','')
        donation.is_active = request.POST.get('is_active') == 'on'
        donation.order = int(request.POST.get('order', 0) or 0)
        donation.save()
        dj_messages.success(request, 'Donation method updated successfully!')
        return redirect('admin_panel:donations_list')
    return render(request, 'admin_panel/donation_form.html', {'action':'Edit','donation':donation})

@login_required
@permission_required('website.delete_donationmethod', raise_exception=True)
def donations_delete(request, pk):
    donation = get_object_or_404(DonationMethod, pk=pk)
    donation.delete()
    dj_messages.success(request, 'Donation method deleted successfully!')
    return redirect('admin_panel:donations_list')


# ---------------------------
# Gallery
# ---------------------------
@login_required
@permission_required('website.view_gallery', raise_exception=True)
def gallery_list(request):
    q = request.GET.get('q','').strip()
    qs = Gallery.objects.all().order_by('-created_at','-id')  # your model lacks updated_at
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q))
    return render(request, 'admin_panel/gallery_list.html', {'gallery': qs, 'q': q})

@login_required
@permission_required('website.add_gallery', raise_exception=True)
def gallery_add(request):
    if request.method == 'POST':
        title = request.POST.get('title','').strip()
        image = request.FILES.get('image')
        description = request.POST.get('description','')
        is_published = request.POST.get('is_published') == 'on'
        Gallery.objects.create(title=title, image=image, description=description, is_published=is_published)
        dj_messages.success(request, 'Gallery item added successfully!')
        return redirect('admin_panel:gallery_list')
    return render(request, 'admin_panel/gallery_form.html', {'action':'Add'})

@login_required
@permission_required('website.change_gallery', raise_exception=True)
def gallery_edit(request, pk):
    gallery_item = get_object_or_404(Gallery, pk=pk)
    if request.method == 'POST':
        gallery_item.title = request.POST.get('title','').strip()
        if request.FILES.get('image'):
            gallery_item.image = request.FILES.get('image')
        gallery_item.description = request.POST.get('description','')
        gallery_item.is_published = request.POST.get('is_published') == 'on'
        gallery_item.save()
        dj_messages.success(request, 'Gallery item updated successfully!')
        return redirect('admin_panel:gallery_list')
    return render(request, 'admin_panel/gallery_form.html', {'action':'Edit','gallery_item':gallery_item})

@login_required
@permission_required('website.delete_gallery', raise_exception=True)
def gallery_delete(request, pk):
    gallery_item = get_object_or_404(Gallery, pk=pk)
    gallery_item.delete()
    dj_messages.success(request, 'Gallery item deleted successfully!')
    return redirect('admin_panel:gallery_list')


# ---------------------------
# Contact messages
# ---------------------------
@login_required
@permission_required('website.view_contactmessage', raise_exception=True)
def messages_list(request):
    q = request.GET.get('q','').strip()
    status = request.GET.get('status','')  # "", "read", "unread"
    qs = ContactMessage.objects.all().order_by('-created_at')
    if q:
        qs = qs.filter(
            Q(subject__icontains=q) | Q(message__icontains=q) |
            Q(name__icontains=q) | Q(email__icontains=q)
        )
    if status == 'read':
        qs = qs.filter(is_read=True)
    elif status == 'unread':
        qs = qs.filter(is_read=False)
    return render(request, 'admin_panel/messages_list.html', {'messages': qs, 'q': q, 'status': status})

@login_required
@permission_required('website.view_contactmessage', raise_exception=True)
def message_detail(request, pk):
    message_obj = get_object_or_404(ContactMessage, pk=pk)
    # NOTE: hatu-mark read automatically; tumia buttons zilizo lindwa na change_contactmessage
    return render(request, 'admin_panel/message_detail.html', {'message': message_obj})

@login_required
@permission_required('website.change_contactmessage', raise_exception=True)
def messages_mark_read(request, pk):
    m = get_object_or_404(ContactMessage, pk=pk)
    m.is_read = True
    m.save(update_fields=['is_read'])
    dj_messages.success(request, 'Marked as read.')
    return redirect('admin_panel:message_detail', pk=pk)

@login_required
@permission_required('website.change_contactmessage', raise_exception=True)
def messages_mark_unread(request, pk):
    m = get_object_or_404(ContactMessage, pk=pk)
    m.is_read = False
    m.save(update_fields=['is_read'])
    dj_messages.success(request, 'Marked as unread.')
    return redirect('admin_panel:message_detail', pk=pk)

@login_required
@permission_required('website.delete_contactmessage', raise_exception=True)
def message_delete(request, pk):
    m = get_object_or_404(ContactMessage, pk=pk)
    m.delete()
    dj_messages.success(request, 'Message deleted successfully!')
    return redirect('admin_panel:messages_list')
