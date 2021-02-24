from django.shortcuts import render
from .models import Review,Loc,Cafe
import csv,io
from django.views.decorators.csrf import csrf_exempt


def mainpage(request):
    review = Review.objects.all()
    context = {
        'all_reviews':review,
    }
    return render(request, 'main/mainpage.html', context=context)

@csrf_exempt
def search(request):
    cafe = Cafe.objects.all()
    context = {
        'all_cafes':cafe,
    }
    return render(request, 'main/search.html', context=context)

@csrf_exempt
def cafedetail(request,pk):
    cafes = Cafe.objects.all()
    cafe = Cafe.objects.get(pk=pk)
    cafeid = cafe.id

    reviews = Review.objects.filter(Cafe=cafeid)
    allreviewnum = len(reviews)
    score5 = len(Review.objects.filter(Cafe=cafeid, star_correction=5))
    score4 = len(Review.objects.filter(Cafe=cafeid, star_correction=4))
    score3 = len(Review.objects.filter(Cafe=cafeid, star_correction=3))
    score2 = len(Review.objects.filter(Cafe=cafeid, star_correction=2))
    score1 = len(Review.objects.filter(Cafe=cafeid, star_correction=1))
    score0 = len(Review.objects.filter(Cafe=cafeid, star_correction=0))

    keyword_coffee = Review.objects.filter(Cafe=cafeid, keyword='커피맛')
    keyword_dessert = Review.objects.filter(Cafe=cafeid, keyword='디저트맛')
    keyword_study = Review.objects.filter(Cafe=cafeid, keyword='공부')
    keyword_photo = Review.objects.filter(Cafe=cafeid, keyword='사진')
    keyword_vibe = Review.objects.filter(Cafe=cafeid, keyword='분위기')
    keyword_none = Review.objects.filter(Cafe=cafeid, keyword='단순')

    try:
        keyword_none_proportion = round(len(keyword_none)/allreviewnum,3)*100
    except ZeroDivisionError:
        keyword_none_proportion = 0.0

    keyword_coffee_num = len(Review.objects.filter(Cafe=cafeid, keyword='커피맛'))
    keyword_dessert_num = len(Review.objects.filter(Cafe=cafeid, keyword='디저트맛'))
    keyword_study_num = len(Review.objects.filter(Cafe=cafeid, keyword='공부'))
    keyword_photo_num = len(Review.objects.filter(Cafe=cafeid, keyword='사진'))
    keyword_vibe_num = len(Review.objects.filter(Cafe=cafeid, keyword='분위기'))

    keyword_coffee_num_5 = len(Review.objects.filter(Cafe=cafeid, keyword='커피맛', star_correction=5))
    keyword_coffee_num_4 = len(Review.objects.filter(Cafe=cafeid, keyword='커피맛', star_correction=4))
    keyword_coffee_num_3 = len(Review.objects.filter(Cafe=cafeid, keyword='커피맛', star_correction=3))
    keyword_coffee_num_2 = len(Review.objects.filter(Cafe=cafeid, keyword='커피맛', star_correction=2))
    keyword_coffee_num_1 = len(Review.objects.filter(Cafe=cafeid, keyword='커피맛', star_correction=1))
    keyword_coffee_num_0 = len(Review.objects.filter(Cafe=cafeid, keyword='커피맛', star_correction=0))

    keyword_coffee_good = keyword_coffee_num_5 + keyword_coffee_num_4
    keyword_coffee_bad = keyword_coffee_num_2 + keyword_coffee_num_1 + keyword_coffee_num_0

    keyword_dessert_num_5 = len(Review.objects.filter(Cafe=cafeid, keyword='디저트맛', star_correction=5))
    keyword_dessert_num_4 = len(Review.objects.filter(Cafe=cafeid, keyword='디저트맛', star_correction=4))
    keyword_dessert_num_3 = len(Review.objects.filter(Cafe=cafeid, keyword='디저트맛', star_correction=3))
    keyword_dessert_num_2 = len(Review.objects.filter(Cafe=cafeid, keyword='디저트맛', star_correction=2))
    keyword_dessert_num_1 = len(Review.objects.filter(Cafe=cafeid, keyword='디저트맛', star_correction=1))
    keyword_dessert_num_0 = len(Review.objects.filter(Cafe=cafeid, keyword='디저트맛', star_correction=0))

    keyword_dessert_good = keyword_dessert_num_5 + keyword_dessert_num_4
    keyword_dessert_bad = keyword_dessert_num_2 + keyword_dessert_num_1 + keyword_dessert_num_0
    
    keyword_study_num_5 = len(Review.objects.filter(Cafe=cafeid, keyword='공부', star_correction=5))
    keyword_study_num_4 = len(Review.objects.filter(Cafe=cafeid, keyword='공부', star_correction=4))
    keyword_study_num_3 = len(Review.objects.filter(Cafe=cafeid, keyword='공부', star_correction=3))
    keyword_study_num_2 = len(Review.objects.filter(Cafe=cafeid, keyword='공부', star_correction=2))
    keyword_study_num_1 = len(Review.objects.filter(Cafe=cafeid, keyword='공부', star_correction=1))
    keyword_study_num_0 = len(Review.objects.filter(Cafe=cafeid, keyword='공부', star_correction=0))

    keyword_study_good = keyword_study_num_5 + keyword_study_num_4
    keyword_study_bad = keyword_study_num_2 + keyword_study_num_1 + keyword_study_num_0

    keyword_photo_num_5 = len(Review.objects.filter(Cafe=cafeid, keyword='사진', star_correction=5))
    keyword_photo_num_4 = len(Review.objects.filter(Cafe=cafeid, keyword='사진', star_correction=4))
    keyword_photo_num_3 = len(Review.objects.filter(Cafe=cafeid, keyword='사진', star_correction=3))
    keyword_photo_num_2 = len(Review.objects.filter(Cafe=cafeid, keyword='사진', star_correction=2))
    keyword_photo_num_1 = len(Review.objects.filter(Cafe=cafeid, keyword='사진', star_correction=1))
    keyword_photo_num_0 = len(Review.objects.filter(Cafe=cafeid, keyword='사진', star_correction=0))

    keyword_photo_good = keyword_photo_num_5 + keyword_photo_num_4
    keyword_photo_bad = keyword_photo_num_2 + keyword_photo_num_1 + keyword_photo_num_0

    keyword_vibe_num_5 = len(Review.objects.filter(Cafe=cafeid, keyword='분위기', star_correction=5))
    keyword_vibe_num_4 = len(Review.objects.filter(Cafe=cafeid, keyword='분위기', star_correction=4))
    keyword_vibe_num_3 = len(Review.objects.filter(Cafe=cafeid, keyword='분위기', star_correction=3))
    keyword_vibe_num_2 = len(Review.objects.filter(Cafe=cafeid, keyword='분위기', star_correction=2))
    keyword_vibe_num_1 = len(Review.objects.filter(Cafe=cafeid, keyword='분위기', star_correction=1))
    keyword_vibe_num_0 = len(Review.objects.filter(Cafe=cafeid, keyword='분위기', star_correction=0))

    keyword_vibe_good = keyword_vibe_num_5 + keyword_vibe_num_4
    keyword_vibe_bad = keyword_vibe_num_2 + keyword_vibe_num_1 + keyword_vibe_num_0


    scorelist=[]
    coffee_scorelist=[]
    dessert_scorelist=[]
    study_scorelist=[]
    photo_scorelist=[]
    vibe_scorelist=[]


    for review in reviews:
        scorelist.append(review.score)
    for review in keyword_coffee:
        coffee_scorelist.append(review.score)
    for review in keyword_dessert:
        dessert_scorelist.append(review.score)
    for review in keyword_study:
        study_scorelist.append(review.score)
    for review in keyword_photo:
        photo_scorelist.append(review.score)
    for review in keyword_vibe:
        vibe_scorelist.append(review.score)

    try:
        averagescore = round(sum(scorelist)/len(scorelist),2)
    except:
        averagescore = "-"

    try:
        coffee_averagescore = round(sum(coffee_scorelist)/len(coffee_scorelist),2)
    except:
        coffee_averagescore = "-"
    

    try:
        dessert_averagescore = round(sum(dessert_scorelist)/len(dessert_scorelist),2)
    except:
        dessert_averagescore = "-"

    try:
        study_averagescore = round(sum(study_scorelist)/len(study_scorelist),2)
    except:
        study_averagescore = "-"
    
    try:
        photo_averagescore = round(sum(photo_scorelist)/len(photo_scorelist),2)
    except:
        photo_averagescore = "-"
    
    try:
        vibe_averagescore = round(sum(vibe_scorelist)/len(vibe_scorelist),2)
    except:
        vibe_averagescore = "-"

    averagescorelist = [i for i in [coffee_averagescore, dessert_averagescore, study_averagescore, photo_averagescore, vibe_averagescore] if i != '-']


    try:
        if coffee_averagescore == max(averagescorelist):
            bestkeyword = "커피맛"
        if dessert_averagescore == max(averagescorelist):
            bestkeyword = "디저트맛"
        if study_averagescore == max(averagescorelist):
            bestkeyword = "스터디"
        if photo_averagescore == max(averagescorelist):
            bestkeyword = "사진"
        if vibe_averagescore == max(averagescorelist):
            bestkeyword = "분위기"
    except ValueError:
        bestkeyword = '-'

    
    #thiscafe
    thiscafereviewnum = allreviewnum #실제 쓰임
    thiscafereviewplus = score5 + score4
    try:
        thiscafeproportion = thiscafereviewplus / allreviewnum
    except ZeroDivisionError:
            thiscafeproportion = -1

    samelocCafes = Cafe.objects.filter(Loc=cafe.Loc.id)

    betterthanthiscafe1 = 0
    betterthanthiscafe2 = 0
    betterthanthiscafe3 = 0



    for sameloccafe in samelocCafes:
        samelocreviewnum = len(Review.objects.filter(Cafe=sameloccafe.id)) #실제 쓰임
        samelocreviewnum5 = len(Review.objects.filter(Cafe=sameloccafe.id, star_correction=5))
        samelocreviewnum4 = len(Review.objects.filter(Cafe=sameloccafe.id, star_correction=4))

        samelocreviewplus = samelocreviewnum5 + samelocreviewnum4 #실제 쓰임

        try:
            samelocproportion = samelocreviewplus / samelocreviewnum #실제 쓰임
        except ZeroDivisionError:
            samelocproportion = -1

        if samelocreviewnum > thiscafereviewnum:
            betterthanthiscafe1 += 1
        if samelocreviewplus > thiscafereviewplus:
            betterthanthiscafe2 += 1
        if samelocproportion > thiscafeproportion:
            betterthanthiscafe3 += 1

    ranking1 = betterthanthiscafe1 + 1
    ranking2 = betterthanthiscafe2 + 1
    ranking3 = betterthanthiscafe3 + 1



    context = {
        'cafe' : cafe,
        'reviews':reviews,
        'all_cafes':cafes,
        'allreviewnum':allreviewnum,
        'score5':score5,
        'score4':score4,
        'score3':score3,
        'score2':score2,
        'score1':score1,
        'score0':score0,
        'averagescore':averagescore,
        'coffee_averagescore':coffee_averagescore,
        'dessert_averagescore':dessert_averagescore,
        'study_averagescore':study_averagescore,
        'photo_averagescore':photo_averagescore,
        'vibe_averagescore':vibe_averagescore,

        'keyword_coffee_num':keyword_coffee_num,
        'keyword_dessert_num':keyword_dessert_num,
        'keyword_study_num':keyword_study_num,
        'keyword_photo_num':keyword_photo_num,
        'keyword_vibe_num':keyword_vibe_num,

        'keyword_none_num':len(keyword_none),



        'keyword_coffee_good':keyword_coffee_good,
        'keyword_coffee_bad':keyword_coffee_bad,

        'keyword_dessert_good':keyword_dessert_good,
        'keyword_dessert_bad':keyword_dessert_bad,

        'keyword_study_good':keyword_study_good,
        'keyword_study_bad':keyword_study_bad,

        'keyword_photo_good':keyword_photo_good,
        'keyword_photo_bad':keyword_photo_bad,

        'keyword_vibe_good':keyword_vibe_good,
        'keyword_vibe_bad':keyword_vibe_bad,

        'bestkeyword':bestkeyword,
        'keyword_none_proportion':keyword_none_proportion,

        'ranking1':ranking1,
        'ranking2':ranking2,
        'ranking3':ranking3,
        
    }
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