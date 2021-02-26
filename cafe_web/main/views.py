from django.shortcuts import render
from .models import Review,Loc,Cafe
import csv,io
from django.views.decorators.csrf import csrf_exempt
import pandas as pd
import numpy as np
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from hanspell import spell_checker
from pykospacing import spacing
from konlpy.tag import Okt
import nltk
from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize 

okt = Okt()

import regex as re
from django.http import JsonResponse


nltk.download('punkt')
nltk.download('wordnet')
nltk.download('stopwords')


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
def write_recommend(request):
    cafe = Cafe.objects.all()
    context = {
        'all_cafes':cafe,
    }
    return render(request, 'main/write_recommend.html', context=context)


def keyword_scoring(exp_sent):
    data = pd.read_csv('static/csv/final_keyword_scoring_data.csv')
    data = data.rename(columns= {'Unnamed: 0' : 'token'})
    coffeedessertscore = 0
    pricescore = 0
    manscore = 0
    vibescore = 0
    for i, word in enumerate(data['token']):
        if word in exp_sent:
            coffeedessertscore += data['커피/Noun'][i]
            pricescore += data['가격/Noun'][i]
            manscore += data['직원/Noun'][i]
            vibescore += data['분위기/Noun'][i]
    scorelist = [coffeedessertscore, pricescore, manscore, vibescore]
    return scorelist

# 전처리 함수들
def clean_text(texts): 
  corpus = [] 
  for i in range(0, len(texts)): 
    review = re.sub(r'[@%\\*=()/~#&\+á?\xc3\xa1\-\|\.\:\;\!\-\,\_\~\$\'\"]', '',str(texts[i])) #remove punctuation 
    review = re.sub(r'\d+','', str(texts[i]))# remove number 
    review = review.lower() #lower case 
    review = re.sub(r'\s+', ' ', review) #remove extra space 
    review = re.sub(r'<[^>]+>','',review) #remove Html tags 
    review = re.sub(r'\s+', ' ', review) #remove spaces 
    review = re.sub(r"^\s+", '', review) #remove space from start 
    review = re.sub(r'\s+$', '', review) #remove space from the end 
    review = re.sub(r'&', '', review)

    corpus.append(review) 
  return corpus

def grammar_check(text):
  spelled_sent = spell_checker.check(text)
  hanspell_sent = spelled_sent.checked
  return hanspell_sent

def tokenize_tagged(text):
  temp_X = okt.pos(text, norm=True, stem=True) # 토큰화
  stop_words = open('static/txt/korean_stopwords.txt').read()
  stop_words=stop_words.split('\n')
  temp_X = [word for word in temp_X if not word in stop_words] # 불용어 제거
  return ['/'.join(t) for t in temp_X]

def preprocess(crude_text):
  token_list = []
  txt = ''.join(clean_text(crude_text))
  txt1 = spacing(txt)
  txt2 = grammar_check(txt1)
  txt3 = tokenize_tagged(txt2)
  regex1 = re.compile('Josa$')
  regex2 = re.compile('Punctuation$')
  regex3 = re.compile('Suffix$')
  regex4 = re.compile('KoreanParticle$')
  regex5 = re.compile('Alpha$')
  regex6 = re.compile('Foreign$')
  text_nj = []
  for item in txt3:
    mo1 = regex1.search(item)
    mo2 = regex2.search(item)
    mo3 = regex3.search(item)
    mo4 = regex4.search(item)
    mo5 = regex5.search(item)
    mo6 = regex6.search(item)
    if mo1 == None and mo2 == None and mo3 == None and mo4 == None and  mo5 == None and mo6 == None:
      text_nj.append(item)

  return text_nj



def preprocessing(txt):
    preprocessed = preprocess(txt)
    return preprocessed


def ajax(request):
    cafeid = request.POST.get("cafeid")
    message = request.POST.get("message")
    exceptcafe = Cafe.objects.get(pk=cafeid)
    exp_sent = preprocessing(message)
    print(exp_sent)
    scorelist = keyword_scoring(exp_sent)
    print(scorelist)
    keywordlist = ["커피/디저트","가격","직원","분위기"]
    bestindex = scorelist.index(max(scorelist))
    for i in range(4):
        if bestindex == i:
            reviewkeyword = keywordlist[i]


    print(reviewkeyword)

    context = {
        "reviewkeyword":reviewkeyword,
    }
    return JsonResponse(context)




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
    cafes = Cafe.objects.all()
    cafe = Cafe.objects.get(pk=pk)
    context = {
        'all_cafes':cafes,
        'cafe':cafe,
    }
    return render(request, 'main/reviewpage.html', context=context)

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