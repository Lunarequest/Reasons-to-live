from logging import disable
from django.shortcuts import render, redirect, HttpResponse
from .models import reason_unapproved, reason_approved
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.contrib import messages
from django_q.tasks import async_task

# Create your views here.
def index(request):
    all_reasons = reason_approved.objects.all()
    paginator = Paginator(all_reasons, 10)
    try:
        page = request.GET.get("page")
    except:
        page = 1
    page_obj = paginator.get_page(page)
    context = {"reasons": page_obj}
    return render(request, "home.html", context)


def email_added(reason, email, display_name):
    email = str(email)
    message = f"""Dear {display_name},
                Your reason: '{reason}' has been added to the moderation queued
                You wil recive a mail when it is approved
                Sincerly 
                The team at resons to live"""
    send_mail(
        "Reason submited",
        message,
        "reasons.to.live.herokuapp@gmail.com",
        [email],
        fail_silently=True,
    )


def email_approved(reason, email, display_name, reason_id):
    message = f"""Dear {display_name},
                Your reason: '{reason}' has been approved
                Sincerly 
                The team at resons to live"""
    send_mail(
        "Reason Approved",
        message,
        "reasons.to.live.herokuapp@gmail.com",
        [email],
        fail_silently=True,
    )
    reason = reason_unapproved.objects.filter(id=reason_id).delete()


def email_denined(reason, email, display_name, reason_id):
    reason = reason_unapproved.objects.filter(id=reason_id).delete()
    message = f"""Dear {display_name},
                Your reason: '{reason}' has been denied.
                Sincerly 
                The team at resons to live"""
    send_mail(
        "Reason denied",
        message,
        "reasons.to.live.herokuapp@gmail.com",
        [email],
        fail_silently=True,
    )


def submit_reason(request):
    if request.method == "POST":
        reason = request.POST["reason"]
        email = request.POST["email"]
        display_name = request.POST["displayName"]
        if reason and email and display_name:
            if (
                reason_approved.objects.filter(reason=reason).exists()
                or reason_unapproved.objects.filter(reason=reason).exists()
            ):
                messages.error(request, "This reason has already been submited")
            else:
                q = reason_unapproved(
                    reason=reason, email=email, display_name=display_name
                )
                q.save()
        else:
            messages.error(request, "All feilds must be filled")
            return redirect("/submit")
        async_task(email_added, reason, email, display_name)
        return render(request, "submited.html")
    else:
        return render(request, "submit_reason.html")


def modrate_reasons(request):
    if request.user.is_authenticated:
        reason = reason_unapproved.objects.first()
        if reason:
            context = {"reason": reason}
            return render(request, "approve.html", context)
        else:
            return render(request, "finshed.html")
    else:
        HttpResponse("you must login first!")


def approved(request, reason_id):
    if request.user.is_authenticated:
        reason = reason_unapproved.objects.filter(id=reason_id)
        q = reason_approved(
            reason=reason.values("reason"),
            email=reason.values("email"),
            display_name=reason.values("display_name"),
        )
        q.save()
        ob = reason_unapproved.objects.filter(id=reason_id)
        async_task(
            email_approved,
            reason,
            ob.values("email"),
            reason,
            ob.values("display_name"),
            reason_id,
        )
        return redirect("/modrate")
    else:
        HttpResponse("you must login first!")


def denied(request, reason_id):
    if request.user.is_authenticated:
        ob = reason_unapproved.objects.filter(id=reason_id).first()
        # email_denined(reason, email, display_name, reason_id):
        reason = ob.values("reason")
        email = ob.values("email")
        display_name = ob.values("display_name")
        async_task(email_denined, reason, email, display_name, reason_id)
        return redirect("/modrate")
    else:
        HttpResponse("you must login first!")
