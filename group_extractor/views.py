
from django.shortcuts import render
from .forms import GroupLinkForm
from .models import Group, GroupMember

# Dummy groups with numbers
dummy_groups = {
    "BanglaFans": [
        "+8801711000001",
        "+8801711000002",
        "+8801711000003",
        "+8801711000004",
        "+8801711000005",
    ],
    "PythonLovers": [
        "+8801812000001",
        "+8801812000002",
        "+8801812000003",
        "+8801812000004",
        "+8801812000005",
    ],
    "TechGeeks": [
        "+8801913000001",
        "+8801913000002",
        "+8801913000003",
        "+8801913000004",
        "+8801913000005",
    ],
}

def extract_group_name(link):
    # Example: "https://chat.whatsapp.com/XYZGroupName123"
    return link.rstrip('/').split('/')[-1]

def extract_numbers_from_group(link):
    group_name = extract_group_name(link)
    # Return dummy numbers if group exists, else 3 default numbers
    return dummy_groups.get(group_name, ["+8801000000001", "+8801000000002", "+8801000000003"])

def group_input_view(request):
    link = None
    numbers = []

    if request.method == 'POST':
        form = GroupLinkForm(request.POST)
        if form.is_valid():
            link = form.cleaned_data.get('link')
            group_name = extract_group_name(link)

            # Save group to DB
            group, created = Group.objects.get_or_create(name=group_name, link=link)

            # Get numbers
            numbers = extract_numbers_from_group(link)

            # Save numbers to DB
            for num in numbers:
                GroupMember.objects.get_or_create(group=group, phone_number=num)
    else:
        form = GroupLinkForm()

    return render(request, "group_extractor/group_form.html", {
        "form": form,
        "link": link,
        "numbers": numbers
    })


# https://chat.whatsapp.com/BanglaFans
# https://chat.whatsapp.com/PythonLovers
# https://chat.whatsapp.com/TechGeeks