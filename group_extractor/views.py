# group_extractor/views.py
from django.shortcuts import render
from .forms import GroupLinkForm
from .models import Group, GroupMember

def group_input_view(request):
    link = None  # Default value
    numbers = []

    if request.method == 'POST':
        form = GroupLinkForm(request.POST)
        if form.is_valid():
            link = form.cleaned_data.get('link')  # safe get
            group_name = extract_group_name(link)

            # Save group
            group, created = Group.objects.get_or_create(name=group_name, link=link)

            # Extract numbers (dummy)
            numbers = extract_numbers_from_group(link)

            # Save numbers to DB
            for num in numbers:
                GroupMember.objects.get_or_create(group=group, phone_number=num)
    else:
        form = GroupLinkForm()

    return render(request, "group_extractor/group_form.html", {
        "form": form,
        "link": link,   # always defined
        "numbers": numbers
    })
