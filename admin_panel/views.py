from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.contrib import messages as dj_messages
from django.utils import timezone
from django.db.models import Q
from django.core.cache import cache
from django.http import HttpResponseForbidden
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordResetView
from .forms import AdminPasswordResetForm
from django.views.decorators.csrf import csrf_protect
from website.models import (
    SiteSettings, Program, News, Event, DonationMethod,
    Gallery, ContactMessage
)
import time
# ---------------------------
# Auth
# ---------------------------
ATTEMPT_LIMIT = 5
LOCKOUT_SECONDS = 180
ATTEMPT_WINDOW_SECONDS = 900  # how long we remember attempts before resetting (15 min)

def _client_ip(request):
    # best-effort IP retrieval
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '0.0.0.0')

def _attempts_key(ip, username):
    u = (username or 'anon').lower()
    return f'admin_login_attempts:{ip}:{u}'

def _lockout_key(ip, username):
    u = (username or 'anon').lower()
    return f'admin_login_lockout:{ip}:{u}'

@csrf_protect
def admin_login(request):
    if request.method == 'POST':
        username = (request.POST.get('username') or '').strip()
        password = request.POST.get('password') or ''
        ip = _client_ip(request)

        # 1) If currently locked, show remaining time and stay on the same page
        lkey = _lockout_key(ip, username)
        unlock_at = cache.get(lkey)  # we store the unlock epoch here
        now = time.time()
        if unlock_at and unlock_at > now:
            remaining = int(unlock_at - now)
            mins, secs = divmod(remaining, 60)
            dj_messages.error(
                request,
                f'Too many attempts. Try again in {mins}m {secs}s.'
            )
            return render(request, 'admin_panel/login.html')  # no redirect

        # 2) Try to authenticate
        user = authenticate(request, username=username, password=password)
        if user and user.is_active and user.is_staff:
            # success -> clear counters and proceed
            cache.delete(_attempts_key(ip, username))
            cache.delete(lkey)
            login(request, user)
            return redirect('admin_panel:dashboard')

        # 3) Failed attempt -> increment counter and maybe lock
        akey = _attempts_key(ip, username)
        count = cache.get(akey, 0) + 1
        cache.set(akey, count, ATTEMPT_WINDOW_SECONDS)
        remaining_attempts = ATTEMPT_LIMIT - count

        if remaining_attempts <= 0:
            # set a 3-minute lock; keep the unlock timestamp as value for messaging
            unlock_at = now + LOCKOUT_SECONDS
            cache.set(lkey, unlock_at, LOCKOUT_SECONDS)
            cache.delete(akey)
            dj_messages.error(request, 'Too many attempts. Try again in 3 minutes.')
        else:
            dj_messages.error(
                request,
                f'Invalid credentials. {remaining_attempts} attempt(s) left before a 3-minute lock.'
            )

    # GET or after message: render same page
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
        settings.youtube_url = request.POST.get('youtube_url', '')

        # NEW: impact numbers (optional ints)
        def to_int(val):
            try:
                return int(val)
            except (TypeError, ValueError):
                return None

        settings.lives_touched = to_int(request.POST.get('lives_touched'))
        settings.regions_served = to_int(request.POST.get('regions_served'))
        settings.years_of_service = to_int(request.POST.get('years_of_service'))
        settings.founded_year = to_int(request.POST.get('founded_year'))

        settings.impact_orphans_supported = to_int(request.POST.get('impact_orphans_supported'))
        settings.impact_women_empowered = to_int(request.POST.get('impact_women_empowered'))
        settings.impact_mosques_developed = to_int(request.POST.get('impact_mosques_developed'))
        settings.impact_babies_assisted = to_int(request.POST.get('impact_babies_assisted'))

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
    q = request.GET.get('q', '').strip()
    status = request.GET.get('status', '')  # "", "read", "unread"

    qs = ContactMessage.objects.all().order_by('-created_at')

    if q:
        qs = qs.filter(
            Q(subject__icontains=q) |
            Q(message__icontains=q) |
            Q(name__icontains=q) |
            Q(email__icontains=q)
        )

    if status == 'read':
        qs = qs.filter(is_read=True)
    elif status == 'unread':
        qs = qs.filter(is_read=False)

    unread_count = ContactMessage.objects.filter(is_read=False).count()
    notifications = ContactMessage.objects.filter(is_read=False).order_by('-created_at')[:4]

    return render(request, "admin_panel/messages_list.html", {
        "inbox": qs,
        "unread_count": ContactMessage.objects.filter(is_read=False).count(),
        "notifications": ContactMessage.objects.filter(is_read=False).order_by("-created_at")[:4],
        "q": q, "status": status,
    })

@login_required
@permission_required('website.view_contactmessage', raise_exception=True)
def message_detail(request, pk):
    message_obj = get_object_or_404(ContactMessage, pk=pk)
    return render(request, 'admin_panel/messages_detail.html', {'message': message_obj})

@login_required
@permission_required('website.change_contactmessage', raise_exception=True)
def messages_mark_read(request, pk):
    m = get_object_or_404(ContactMessage, pk=pk)
    if not m.is_read:
        m.is_read = True
        m.read_at = timezone.now()
        m.save(update_fields=['is_read', 'read_at'])
    dj_messages.success(request, 'Marked as read.')
    return redirect('admin_panel:messages_detail', pk=pk)

@login_required
@permission_required('website.change_contactmessage', raise_exception=True)
def messages_mark_unread(request, pk):
    m = get_object_or_404(ContactMessage, pk=pk)
    if m.is_read:
        m.is_read = False
        m.read_at = None
        m.save(update_fields=['is_read', 'read_at'])
    dj_messages.success(request, 'Marked as unread.')
    return redirect('admin_panel:messages_detail', pk=pk)

@login_required
@permission_required('website.change_contactmessage', raise_exception=True)
def messages_mark_all_read(request):
    ContactMessage.objects.filter(is_read=False).update(is_read=True, read_at=timezone.now())
    dj_messages.success(request, 'All messages marked as read.')
    return redirect('admin_panel:messages_list')

@login_required
@permission_required('website.delete_contactmessage', raise_exception=True)
def message_delete(request, pk):
    m = get_object_or_404(ContactMessage, pk=pk)
    m.delete()
    dj_messages.success(request, 'Message deleted successfully!')
    return redirect('admin_panel:messages_list')

class AdminPasswordResetView(PasswordResetView):
    template_name = "admin_panel/auth/password_reset_form.html"
    email_template_name = "admin_panel/auth/password_reset_email.txt"
    subject_template_name = "admin_panel/auth/password_reset_subject.txt"
    success_url = reverse_lazy("admin_panel:password_reset_done")
    form_class = AdminPasswordResetForm