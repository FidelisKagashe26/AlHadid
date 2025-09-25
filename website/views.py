from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .models import Program, News, Event, DonationMethod, Gallery, ContactMessage, SiteSettings
from website.forms import ContactForm

def home(request):
    programs = Program.objects.filter(is_active=True)[:3]
    news = News.objects.filter(is_published=True)[:3]
    events = Event.objects.filter(is_published=True)[:3]
    gallery = Gallery.objects.filter(is_published=True)[:6]
    
    context = {
        'programs': programs,
        'news': news,
        'events': events,
        'gallery': gallery,
        'page_title': 'Home',
    }
    return render(request, 'website/home.html', context)

def about(request):
    context = {
        'page_title': 'About Us',
    }
    return render(request, 'website/about.html', context)

def programs(request):
    programs_list = Program.objects.filter(is_active=True)
    context = {
        'programs': programs_list,
        'page_title': 'Programs & Projects',
    }
    return render(request, 'website/programs.html', context)

def donate(request):
    methods = DonationMethod.objects.filter(is_active=True).order_by('order', 'name')
    return render(request, 'website/donate.html', {'methods': methods})

def program_detail(request, pk):
    program = get_object_or_404(Program, pk=pk, is_active=True)
    context = {
        'program': program,
        'page_title': program.title,
    }
    return render(request, 'website/program_detail.html', context)

def news_events(request):
    news_list = News.objects.filter(is_published=True)
    events_list = Event.objects.filter(is_published=True)
    
    context = {
        'news': news_list,
        'events': events_list,
        'page_title': 'News & Events',
    }
    return render(request, 'website/news_events.html', context)

def news_detail(request, pk):
    news_item = get_object_or_404(News, pk=pk, is_published=True)
    context = {
        'news': news_item,
        'page_title': news_item.title,
    }
    return render(request, 'website/news_detail.html', context)

def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk, is_published=True)
    context = {
        'event': event,
        'page_title': event.title,
    }
    return render(request, 'website/event_detail.html', context)

def donate(request):
    donation_methods = DonationMethod.objects.filter(is_active=True)
    context = {
        'donation_methods': donation_methods,
        'page_title': 'Donate',
    }
    return render(request, 'website/donate.html', context)

def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            cm = form.save(commit=False)
            cm.ip_address = request.META.get("REMOTE_ADDR")  # optional if you have these fields
            cm.user_agent = (request.META.get("HTTP_USER_AGENT") or "")[:255]
            cm.save()
            messages.success(
                request,
                "Thank you! Your message has been received. We’ll reply within 24–48 hours in shaa’Allah."
            )
            return redirect("website:contact")
    else:
        form = ContactForm()

    return render(request, "website/contact.html", {"form": form})

def gallery_view(request):
    gallery_items = Gallery.objects.filter(is_published=True)
    context = {
        'gallery': gallery_items,
        'page_title': 'Gallery',
    }
    return render(request, 'website/gallery.html', context)

@csrf_exempt
@require_POST
def toggle_theme(request):
    theme = request.POST.get('theme', 'light')
    request.session['theme'] = theme
    return JsonResponse({'success': True})