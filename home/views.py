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
    print(message)
    send_mail(
        "Reason submited",
        message,
        "reasons.to.live.herokuapp@gmail.com",
        [email],
        fail_silently=True,
    )


def email_approved(reason, email, display_name):
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


def email_denined(reason, reason_denied, email, display_name):
    message = f"""Dear {display_name},
                Your reason: '{reason}' has been denied
                It was denied for the following reason:\n {reason_denied}
                Sincerly 
                The team at resons to live"""
    send_mail(
        "Reasons denied",
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


def approved(request, id):
    if request.user.is_authenticated:
        reason = reason_unapproved.objects.filter(id=id)
        q = reason_approved(
            reason=reason.values("reason"),
            email=reason.values("email"),
            display_name=reason.values("display_name"),
        )
        q.save()
        ob = reason_unapproved.objects.filter(id=id)
        async_task(
            email_approved,
            ob.values("reason"),
            reason,
            ob.values("email"),
            reason,
            ob.values("display_name"),
        )
        reason = reason_unapproved.objects.filter(id=id).delete()
        return redirect("/modrate")
    else:
        HttpResponse("you must login first!")


def denied(request, id):
    if request.user.is_authenticated:
        if request.method == "POST":
            reason = request.POST["reason"]
            ob = reason_unapproved.objects.filter(id=id)
            async_task(
                email_denined,
                ob.values("reason"),
                reason,
                ob.values("email"),
                reason,
                ob.values("display_name"),
            )
            reason_unapproved.objects.filter(id=id).delete()
            return redirect("/modrate")
        else:
            return render(request, "deined.html")
    else:
        HttpResponse("you must login first!")
