# website/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.utils import timezone

from .models import Program, News, Event, DonationMethod, Gallery, ContactMessage, SiteSettings
from website.forms import ContactForm

def home(request):
    programs = Program.objects.filter(is_active=True).order_by('-id')[:3]
    gallery  = Gallery.objects.filter(is_published=True).order_by('-id')[:6]

    latest_news = News.objects.filter(is_published=True).order_by('-created_at')[:3]

    events_qs = Event.objects.filter(is_published=True)
    now = timezone.now()
    upcoming_events = events_qs.filter(event_date__gte=now).order_by('event_date')[:3]
    latest_events = events_qs.order_by('-event_date')[:3]

    context = {
        'page_title': 'Home',
        'active': 'home',
        'programs': programs,
        'gallery': gallery,
        'latest_news': latest_news,
        'upcoming_events': upcoming_events,
        'latest_events': latest_events,
        'news': latest_news,
        'events': latest_events,
    }
    return render(request, 'website/home.html', context)


def about(request):
    settings = SiteSettings.objects.first()
    context = {
        'page_title': 'About Us',
        'active': 'about',
        'settings': settings,
    }
    return render(request, 'website/about.html', context)


def programs(request):
    programs_list = Program.objects.filter(is_active=True)
    context = {
        'programs': programs_list,
        'page_title': 'Programs & Projects',
        'active': 'programs',
    }
    return render(request, 'website/programs.html', context)


def donate(request):
    donation_methods = DonationMethod.objects.filter(is_active=True).order_by('order','name')
    context = {
        'donation_methods': donation_methods,
        'page_title': 'Donate',
        'active': 'donate',
    }
    return render(request, 'website/donate.html', context)


def program_detail(request, pk):
    program = get_object_or_404(Program, pk=pk, is_active=True)
    context = {
        'program': program,
        'page_title': program.title,
        'active': 'programs',
    }
    return render(request, 'website/program_detail.html', context)


def news_events(request):
    news_list = News.objects.filter(is_published=True).order_by('-created_at')
    events_list = Event.objects.filter(is_published=True).order_by('-event_date')
    context = {
        'news': news_list,
        'events': events_list,
        'page_title': 'News & Events',
        'active': 'news_events',
    }
    return render(request, 'website/news_events.html', context)


def news_detail(request, pk):
    news_item = get_object_or_404(News, pk=pk, is_published=True)
    context = {
        'news': news_item,
        'page_title': news_item.title,
        'active': 'news_events',
    }
    return render(request, 'website/news_detail.html', context)


def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk, is_published=True)
    context = {
        'event': event,
        'page_title': event.title,
        'active': 'news_events',
    }
    return render(request, 'website/event_detail.html', context)


def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            cm = form.save(commit=False)
            cm.ip_address = request.META.get("REMOTE_ADDR")
            cm.user_agent = (request.META.get("HTTP_USER_AGENT") or "")[:255]
            cm.save()
            messages.success(
                request,
                "Thank you! Your message has been received. We’ll reply within 24–48 hours in shaa’Allah."
            )
            return redirect("website:contact")
    else:
        form = ContactForm()

    return render(request, "website/contact.html", {"form": form, "active": "contact", "page_title": "Contact"})


def gallery_view(request):
    """
    Server-side filtering, searching, and pagination.
    Params:
      - ?category=orphans|women|mosques|healthcare|events|other|all
      - ?q=search terms
      - ?page=1
    """
    q = (request.GET.get('q') or "").strip()
    category = (request.GET.get('category') or "all").lower()

    qs = Gallery.objects.filter(is_published=True)
    if category and category != 'all':
        qs = qs.filter(category=category)

    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q))

    qs = qs.order_by('-created_at', '-id')

    paginator = Paginator(qs, 12)  # 12 per page
    page = request.GET.get('page', 1)
    try:
        items = paginator.page(page)
    except PageNotAnInteger:
        items = paginator.page(1)
    except EmptyPage:
        items = paginator.page(paginator.num_pages)

    context = {
        'gallery': items,  # NB: template iterates page object the same way
        'page_title': 'Gallery',
        'active': 'gallery',
        'category': category,
        'q': q,
        'categories': [
            ('all', 'All'),
            ('orphans', 'Orphans'),
            ('women', 'Women'),
            ('mosques', 'Mosques'),
            ('healthcare', 'Healthcare'),
            ('events', 'Events'),
            ('other', 'Other'),
        ],
    }
    return render(request, 'website/gallery.html', context)


@csrf_exempt
@require_POST
def toggle_theme(request):
    theme = request.POST.get('theme', 'light')
    request.session['theme'] = theme
    return JsonResponse({'success': True})
