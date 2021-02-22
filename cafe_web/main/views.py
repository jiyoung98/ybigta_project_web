from django.shortcuts import render
from .models import Review,Loc,Cafe
import csv,io

def mainpage(request):
    review = Review.objects.all()
    # sinchon_review = Review.objects.select_related('Loc').filter(Loc=8)
    # print(len(sinchon_review))
    # print(len(review))
    context = {
        'all_reviews':review,
    }
    return render(request, 'main/mainpage.html', context=context)

def cafedetail(request,pk):
    # cafe = Cafe.objects.get(pk=pk)
    context = {}
    return render(request, 'main/cafepage.html', context=context)

def reviewdetail(request,pk):
    # cafe = Cafe.objects.get(pk=pk)
    context = {}
    return render(request, 'main/reviewpage.html', context=context)

def write_recommend(request):
    # cafe = Cafe.objects.get(pk=pk)
    context = {}
    return render(request, 'main/write_recommend.html', context=context)

def cafe_csv_upload(request):
    # declaring template
    template = "main/cafe_csv_upload.html"
    # prompt is a context variable that can have different values      depending on their context
    # prompt = {
    #     'order': 'Order of the CSV should be name',
    #     'profiles': cafe
    #           }
    # GET request returns the value of the data with the specified key.
    if request.method == "GET":
        return render(request, template)
    csv_file = request.FILES['file']
    # let's check if it is a csv file
    if not csv_file.name.endswith('.csv'):
        messages.error(request, 'THIS IS NOT A CSV FILE')
    dataset = csv_file.read().decode('UTF-8')

    io_string = io.StringIO(dataset)
    next(io_string)
    for column in csv.reader(io_string, delimiter=',', quotechar="|"):
        loc = Loc.objects.get(name=column[1])
        created = Cafe.objects.update_or_create(
            name=column[2],
            Loc=loc,
            #first_keyword=column[2],
        )
    context = {}
    return render(request,template,context)

def csv_upload(request):
    # declaring template
    template = "main/csv_upload.html"
    # review = Review.objects.all()
    # prompt is a context variable that can have different values      depending on their context
    # prompt = {
    #     'order': 'Order of the CSV should be name',
    #     'profiles': review
    #           }
    # GET request returns the value of the data with the specified key.
    if request.method == "GET":
        return render(request, template)
    csv_file = request.FILES['file']
    # let's check if it is a csv file
    if not csv_file.name.endswith('.csv'):
        messages.error(request, 'THIS IS NOT A CSV FILE')
    dataset = csv_file.read().decode('UTF-8')

    io_string = io.StringIO(dataset)
    next(io_string)
    for column in csv.reader(io_string, delimiter=',', quotechar="|"):
        cafe = Cafe.objects.get(name=column[2])
        loc = Loc.objects.get(name=column[1])
        created = Review.objects.create(
            Loc=loc,
            Cafe=cafe,
            text=column[3],
            star=column[4],
            score=column[5],
            keyword=column[6],
            star_correction = column[7],
        )
    context = {}
    return render(request,template,context)