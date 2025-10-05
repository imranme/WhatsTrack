
# from django.shortcuts import render
# from .forms import GroupLinkForm
# from .models import Group, GroupMember

# # Dummy groups with numbers
# dummy_groups = {
#     "BanglaFans": [
#         "+8801711000001",
#         "+8801711000002",
#         "+8801711000003",
#         "+8801711000004",
#         "+8801711000005",
#     ],
#     "PythonLovers": [
#         "+8801812000001",
#         "+8801812000002",
#         "+8801812000003",
#         "+8801812000004",
#         "+8801812000005",
#     ],
#     "TechGeeks": [
#         "+8801913000001",
#         "+8801913000002",
#         "+8801913000003",
#         "+8801913000004",
#         "+8801913000005",
#     ],
# }

# def extract_group_name(link):
#     # Example: "https://chat.whatsapp.com/XYZGroupName123"
#     return link.rstrip('/').split('/')[-1]

# def extract_numbers_from_group(link):
#     group_name = extract_group_name(link)
#     # Return dummy numbers if group exists, else 3 default numbers
#     return dummy_groups.get(group_name, ["+8801000000001", "+8801000000002", "+8801000000003"])

# def group_input_view(request):
#     link = None
#     numbers = []

#     if request.method == 'POST':
#         form = GroupLinkForm(request.POST)
#         if form.is_valid():
#             link = form.cleaned_data.get('link')
#             group_name = extract_group_name(link)

#             # Save group to DB
#             group, created = Group.objects.get_or_create(name=group_name, link=link)

#             # Get numbers
#             numbers = extract_numbers_from_group(link)

#             # Save numbers to DB
#             for num in numbers:
#                 GroupMember.objects.get_or_create(group=group, phone_number=num)
#     else:
#         form = GroupLinkForm()

#     return render(request, "group_extractor/group_form.html", {
#         "form": form,
#         "link": link,
#         "numbers": numbers
#     })


# https://chat.whatsapp.com/BanglaFans
# https://chat.whatsapp.com/PythonLovers
# https://chat.whatsapp.com/TechGeeks

# group_extractor/views.py
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json

from .forms import GroupLinkForm
from .models import Group, GroupMember

# --- existing form view (UI) ---
def extract_group_name(link):
    return link.rstrip('/').split('/')[-1]

def extract_numbers_from_group_dummy(link):
    # your safe dummy fallback (keeps app usable if not posting real members)
    group_name = extract_group_name(link)
    dummy_groups = {
        "BanglaFans": [f"+8801711{str(i).zfill(6)}" for i in range(1, 51)],
        "PythonLovers": [f"+8801812{str(i).zfill(6)}" for i in range(1, 101)],
        "TechGeeks": [f"+8801913{str(i).zfill(6)}" for i in range(1, 76)],
    }
    return dummy_groups.get(group_name, ["+8801000000001", "+8801000000002", "+8801000000003"])

def group_input_view(request):
    link = None
    numbers = []
    form = GroupLinkForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        link = form.cleaned_data.get('link')
        group_name = extract_group_name(link)
        group, _ = Group.objects.get_or_create(name=group_name, link=link)
        numbers = extract_numbers_from_group_dummy(link)
        for num in numbers:
            GroupMember.objects.get_or_create(group=group, phone_number=num)
    return render(request, "group_extractor/group_form.html", {
        "form": form,
        "link": link,
        "numbers": numbers
    })

# --- API endpoint to receive scraped members from Selenium script ---
@csrf_exempt
def save_members_api(request):
    """
    Expect JSON:
    {
      "group_name": "BanglaFans",
      "link": "https://chat.whatsapp.com/BanglaFans",
      "numbers": [
         {"phone":"+88017...", "name":"Name1"},
         ...
      ]
    }
    """
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)
    try:
        payload = json.loads(request.body.decode('utf-8'))
    except Exception as e:
        return JsonResponse({"error": "invalid json", "detail": str(e)}, status=400)

    group_name = payload.get("group_name") or extract_group_name(payload.get("link","") or "")
    link = payload.get("link") or ""
    members = payload.get("numbers", [])

    group, _ = Group.objects.get_or_create(name=group_name, link=link)
    saved = 0
    for m in members:
        phone = (m.get("phone") or "").strip()
        name = m.get("name") or ""
        if not phone:
            continue
        obj, created = GroupMember.objects.get_or_create(group=group, phone_number=phone)
        if created:
            saved += 1

    return JsonResponse({"status": "ok", "saved": saved, "received": len(members)})
