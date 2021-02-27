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
import matplotlib.pyplot as plt
import urllib.request
import json
from keras.models import load_model


nltk.download('punkt')
nltk.download('wordnet')
nltk.download('stopwords')

def forsave(request):
    cafes = Cafe.objects.all()
    num=0
    for cafe in cafes:
        cafeid = cafe.id
        reviews = Review.objects.filter(Cafe=cafeid)

        scorelist=[]
        vibe_scorelist=[]
        coffee_scorelist=[]
        service_scorelist=[]
        price_scorelist=[]
        etc_scorelist=[]

        reviews = Review.objects.filter(Cafe=cafeid)

        keyword_vibe = Review.objects.filter(Cafe=cafeid, keyword='분위기')
        keyword_coffee = Review.objects.filter(Cafe=cafeid, keyword='커피&디저트')
        keyword_service = Review.objects.filter(Cafe=cafeid, keyword='서비스')
        keyword_price = Review.objects.filter(Cafe=cafeid, keyword='가격')
        keyword_etc = Review.objects.filter(Cafe=cafeid, keyword='기타')

        lenlist = [len(keyword_vibe), len(keyword_coffee), len(keyword_service), len(keyword_price)]

        if max(lenlist) == len(keyword_vibe):
            bestkeyword = "분위기"
        if len(keyword_coffee) == max(lenlist):
            bestkeyword = "커피&디저트"
        if len(keyword_service) == max(lenlist):
            bestkeyword = "서비스"
        if len(keyword_price) == max(lenlist):
            bestkeyword = "가격"
        
        for review in reviews:
            scorelist.append(review.score)
        for review in keyword_vibe:
            vibe_scorelist.append(review.score)
        for review in keyword_coffee:
            coffee_scorelist.append(review.score)
        for review in keyword_service:
            service_scorelist.append(review.score)
        for review in keyword_price:
            price_scorelist.append(review.score)

        try:
            averagescore = round(sum(scorelist)/len(scorelist),2)
        except:
            averagescore = 0

        try:
            vibe_averagescore = round(sum(vibe_scorelist)/len(vibe_scorelist),2)
        except:
            vibe_averagescore = 0
        

        try:
            coffee_averagescore = round(sum(coffee_scorelist)/len(coffee_scorelist),2)
        except:
            coffee_averagescore = 0

        try:
            service_averagescore = round(sum(service_scorelist)/len(service_scorelist),2)
        except:
            service_averagescore = 0
        
        try:
            price_averagescore = round(sum(price_scorelist)/len(price_scorelist),2)
        except:
            price_averagescore = 0
        

        cafe.first_keyword = bestkeyword
        cafe.vibescore = vibe_averagescore
        cafe.coffeescore = coffee_averagescore
        cafe.servicescore = service_averagescore
        cafe.pricescore = price_averagescore
        cafe.save()
        num +=1


    return render(request, 'main/mainpage.html')


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




##############################감성분석 함수들#####################################
def grammar_check(text):
  spelled_sent = spell_checker.check(text)
  hanspell_sent = spelled_sent.checked
  return hanspell_sent

def clean_punc(text, punct, mapping): 
  for p in mapping: 
    text = text.replace(p, mapping[p]) 
  for p in punct: 
    text = text.replace(p, f' {p} ') 
    specials = {'\u200b': ' ', '…': ' ... ', '\ufeff': '', 'करना': '', 'है': ''} 
  for s in specials: 
    text = text.replace(s, specials[s]) 
   
  return text.strip() 



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
    review = re.sub(r'♥','',review)
    review = re.sub(r'~','',review)
    review = re.sub(r'&','',review)
    review = re.sub(r'😱','',review)
    corpus.append(review) 
  return corpus


def rmEmoji(text):
  review = text.encode('utf-8', 'ignore').decode('utf-8')
  return review

def rmEmoji_ascii(inputString):
  review = example.encode('ascii','ignore').decode('ascii')
  return review

def tokenize_tagged(text):
  okt = Okt()
  stop_words = open('static/txt/korean_stopwords.txt').read()

  stop_words=stop_words.split('\n')

  temp_X = okt.pos(text, norm=True, stem=True) # 토큰화
  temp_X = [word for word in temp_X if not word in stop_words] # 불용어 제거
  return ['/'.join(t) for t in temp_X]



def sentiment_predict(new_sentence):
  
  punct = "/-'?!.,#$%\'()*+-/:;<=>@[\\]^_`{|}~" + '""“”’' + '∞θ÷α•à−β∅³π‘₹´°£€\×™√²—–&' 
  punct_mapping = {"‘": "'", "₹": "e", "´": "'", "°": "", "€": "e", "™": "tm", "√": " sqrt ", "×": "x", "²": "2",
                 "—": "-", "–": "-", "’": "'", "_": "-", "`": "'", '“': '"', '”': '"', '“': '"', "£": "e", '∞': 'infinity', 
                 'θ': 'theta', '÷': '/', 'α': 'alpha', '•': '.', 'à': 'a', '−': '-', 'β': 'beta', '∅': '', '³': '3', 'π': 'pi'} 
  text1 = clean_punc(new_sentence, punct, punct_mapping)
  text2 = ''.join(clean_text(text1))
  text3 = spacing(text2)
  text4 = grammar_check(text3)
  text_ = tokenize_tagged(text4)

  tokenizer = Tokenizer(5542)

  with open('static/json/wordIndex(BiLSTM).json') as json_file:
    word_index = json.load(json_file)
  tokenizer.word_index = word_index
  model = load_model('static/model/BiLSTM_model(sigmoid).h5')

  print(text_)
  encoded = tokenizer.texts_to_sequences([text_]) # 정수 인코딩
  print(encoded)
  pad_new = pad_sequences(encoded, maxlen = 30) # 패딩
  print(pad_new)
  score = float(model.predict(pad_new)) # 예측
  print("{:.2f}% 확률로 긍정 리뷰입니다.".format(score * 100))
  
  return "{:.2f}% 확률로 긍정 리뷰입니다.".format(score * 100)

#############################################################################


def ajax(request):
    cafeid = request.POST.get("cafeid")
    message = request.POST.get("message")
    exceptcafe = Cafe.objects.get(pk=cafeid)

    ### 키워드 분석 ###
    exp_sent = preprocessing(message)
    print(exp_sent)
    scorelist = keyword_scoring(exp_sent)
    print(scorelist)
    keywordlist = ["커피&디저트","가격","서비스","분위기"]
    bestindex = scorelist.index(max(scorelist))
    
    for i in range(4):
        if bestindex == i:
            reviewkeyword = keywordlist[i]

    print(reviewkeyword)


    filteringcafe = Cafe.objects.filter(Loc=exceptcafe.Loc.id) #여기 논의 해봐야함.

    viberanking = Cafe.objects.filter(Loc=exceptcafe.Loc.id).order_by('-vibescore').exclude(id=exceptcafe.id)  # 내림차순
    coffeeranking = Cafe.objects.filter(Loc=exceptcafe.Loc.id).order_by('-coffeescore').exclude(id=exceptcafe.id)  # 내림차순
    serviceranking = Cafe.objects.filter(Loc=exceptcafe.Loc.id).order_by('-servicescore').exclude(id=exceptcafe.id)  # 내림차순
    priceranking = Cafe.objects.filter(Loc=exceptcafe.Loc.id).order_by('-pricescore').exclude(id=exceptcafe.id)  # 내림차순



    if reviewkeyword == "분위기":
        ranking = viberanking
    if reviewkeyword == "커피&디저트":
        ranking = coffeeranking
    if reviewkeyword == "서비스":
        ranking = serviceranking
    if reviewkeyword == "가격":
        ranking = priceranking
    
    recommendlist = []


    for i, cafe in enumerate(ranking):
        if len(cafe.review.filter(keyword=reviewkeyword)) > 10: #여기도
            recommendlist.append(cafe.name)
            recommendlist.append(cafe.id)
        if len(recommendlist) == 10:
            break
    


    firstcafename = "-"
    firstcafeid = "-"
    secondcafename = "-"
    secondcafeid = "-"
    thirdcafename = "-"
    thirdcafeid = "-"
    fourthcafename = "-"
    fourthcafeid = "-"
    fifthcafename = "-"
    fifthcafeid = "-"

    try:
        firstcafename = recommendlist[0]
        firstcafeid = recommendlist[1]
        secondcafename = recommendlist[2]
        secondcafeid = recommendlist[3]
        thirdcafename = recommendlist[4]
        thirdcafeid = recommendlist[5]
        fourthcafename = recommendlist[6]
        fourthcafeid = recommendlist[7]
        fifthcafename = recommendlist[8]
        fifthcafeid = recommendlist[9]
    except IndexError:
        pass
            

    ### 감성 분석 ###
    result = sentiment_predict(message)

    context = {
        "reviewkeyword":reviewkeyword,
        "goodorbadresult":result,
        "firstcafename":firstcafename,
        "secondcafename":secondcafename,
        "thirdcafename":thirdcafename,
        "fourthcafename":fourthcafename,
        "fifthcafename":fifthcafename,
        "firstcafeid":firstcafeid,
        "secondcafeid":secondcafeid,
        "thirdcafeid":thirdcafeid,
        "fourthcafeid":fourthcafeid,
        "fifthcafeid":fifthcafeid,
    }
    return JsonResponse(context)

@csrf_exempt
def reviewdetail(request,pk):

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

    keyword_vibe = Review.objects.filter(Cafe=cafeid, keyword='분위기')
    keyword_coffee = Review.objects.filter(Cafe=cafeid, keyword='커피&디저트')
    keyword_service = Review.objects.filter(Cafe=cafeid, keyword='서비스')
    keyword_price = Review.objects.filter(Cafe=cafeid, keyword='가격')
    keyword_etc = Review.objects.filter(Cafe=cafeid, keyword='기타')

    try:
        keyword_none_proportion = round(len(keyword_etc)/allreviewnum,3)*100
    except ZeroDivisionError:
        keyword_none_proportion = 0.0

    keyword_vibe_num = len(Review.objects.filter(Cafe=cafeid, keyword='분위기'))
    keyword_coffee_num = len(Review.objects.filter(Cafe=cafeid, keyword='커피&디저트'))
    keyword_service_num = len(Review.objects.filter(Cafe=cafeid, keyword='서비스'))
    keyword_price_num = len(Review.objects.filter(Cafe=cafeid, keyword='가격'))
    keyword_etc_num = len(Review.objects.filter(Cafe=cafeid, keyword='기타'))

    keyword_vibe_num_5 = len(Review.objects.filter(Cafe=cafeid, keyword='분위기', star_correction=5))
    keyword_vibe_num_4 = len(Review.objects.filter(Cafe=cafeid, keyword='분위기', star_correction=4))
    keyword_vibe_num_3 = len(Review.objects.filter(Cafe=cafeid, keyword='분위기', star_correction=3))
    keyword_vibe_num_2 = len(Review.objects.filter(Cafe=cafeid, keyword='분위기', star_correction=2))
    keyword_vibe_num_1 = len(Review.objects.filter(Cafe=cafeid, keyword='분위기', star_correction=1))
    keyword_vibe_num_0 = len(Review.objects.filter(Cafe=cafeid, keyword='분위기', star_correction=0))

    keyword_vibe_good = keyword_vibe_num_5 + keyword_vibe_num_4
    keyword_vibe_bad = keyword_vibe_num_2 + keyword_vibe_num_1 + keyword_vibe_num_0

    keyword_coffee_num_5 = len(Review.objects.filter(Cafe=cafeid, keyword='커피&디저트', star_correction=5))
    keyword_coffee_num_4 = len(Review.objects.filter(Cafe=cafeid, keyword='커피&디저트', star_correction=4))
    keyword_coffee_num_3 = len(Review.objects.filter(Cafe=cafeid, keyword='커피&디저트', star_correction=3))
    keyword_coffee_num_2 = len(Review.objects.filter(Cafe=cafeid, keyword='커피&디저트', star_correction=2))
    keyword_coffee_num_1 = len(Review.objects.filter(Cafe=cafeid, keyword='커피&디저트', star_correction=1))
    keyword_coffee_num_0 = len(Review.objects.filter(Cafe=cafeid, keyword='커피&디저트', star_correction=0))

    keyword_coffee_good = keyword_coffee_num_5 + keyword_coffee_num_4
    keyword_coffee_bad = keyword_coffee_num_2 + keyword_coffee_num_1 + keyword_coffee_num_0
    
    keyword_service_num_5 = len(Review.objects.filter(Cafe=cafeid, keyword='서비스', star_correction=5))
    keyword_service_num_4 = len(Review.objects.filter(Cafe=cafeid, keyword='서비스', star_correction=4))
    keyword_service_num_3 = len(Review.objects.filter(Cafe=cafeid, keyword='서비스', star_correction=3))
    keyword_service_num_2 = len(Review.objects.filter(Cafe=cafeid, keyword='서비스', star_correction=2))
    keyword_service_num_1 = len(Review.objects.filter(Cafe=cafeid, keyword='서비스', star_correction=1))
    keyword_service_num_0 = len(Review.objects.filter(Cafe=cafeid, keyword='서비스', star_correction=0))

    keyword_service_good = keyword_service_num_5 + keyword_service_num_4
    keyword_service_bad = keyword_service_num_2 + keyword_service_num_1 + keyword_service_num_0

    keyword_price_num_5 = len(Review.objects.filter(Cafe=cafeid, keyword='가격', star_correction=5))
    keyword_price_num_4 = len(Review.objects.filter(Cafe=cafeid, keyword='가격', star_correction=4))
    keyword_price_num_3 = len(Review.objects.filter(Cafe=cafeid, keyword='가격', star_correction=3))
    keyword_price_num_2 = len(Review.objects.filter(Cafe=cafeid, keyword='가격', star_correction=2))
    keyword_price_num_1 = len(Review.objects.filter(Cafe=cafeid, keyword='가격', star_correction=1))
    keyword_price_num_0 = len(Review.objects.filter(Cafe=cafeid, keyword='가격', star_correction=0))

    keyword_price_good = keyword_price_num_5 + keyword_price_num_4
    keyword_price_bad = keyword_price_num_2 + keyword_price_num_1 + keyword_price_num_0

    keyword_etc_num_5 = len(Review.objects.filter(Cafe=cafeid, keyword='기타', star_correction=5))
    keyword_etc_num_4 = len(Review.objects.filter(Cafe=cafeid, keyword='기타', star_correction=4))
    keyword_etc_num_3 = len(Review.objects.filter(Cafe=cafeid, keyword='기타', star_correction=3))
    keyword_etc_num_2 = len(Review.objects.filter(Cafe=cafeid, keyword='기타', star_correction=2))
    keyword_etc_num_1 = len(Review.objects.filter(Cafe=cafeid, keyword='기타', star_correction=1))
    keyword_etc_num_0 = len(Review.objects.filter(Cafe=cafeid, keyword='기타', star_correction=0))

    keyword_etc_good = keyword_etc_num_5 + keyword_etc_num_4
    keyword_etc_bad = keyword_etc_num_2 + keyword_etc_num_1 + keyword_etc_num_0


    scorelist=[]
    vibe_scorelist=[]
    coffee_scorelist=[]
    service_scorelist=[]
    price_scorelist=[]
    etc_scorelist=[]


    for review in reviews:
        scorelist.append(review.score)
    for review in keyword_vibe:
        vibe_scorelist.append(review.score)
    for review in keyword_coffee:
        coffee_scorelist.append(review.score)
    for review in keyword_service:
        service_scorelist.append(review.score)
    for review in keyword_price:
        price_scorelist.append(review.score)
    for review in keyword_etc:
        etc_scorelist.append(review.score)

    try:
        averagescore = round(sum(scorelist)/len(scorelist),2)
    except:
        averagescore = "-"

    try:
        vibe_averagescore = round(sum(vibe_scorelist)/len(vibe_scorelist),2)
    except:
        vibe_averagescore = "-"
    

    try:
        coffee_averagescore = round(sum(coffee_scorelist)/len(coffee_scorelist),2)
    except:
        coffee_averagescore = "-"

    try:
        service_averagescore = round(sum(service_scorelist)/len(service_scorelist),2)
    except:
        service_averagescore = "-"
    
    try:
        price_averagescore = round(sum(price_scorelist)/len(price_scorelist),2)
    except:
        price_averagescore = "-"
    
    try:
        etc_averagescore = round(sum(etc_scorelist)/len(etc_scorelist),2)
    except:
        etc_averagescore = "-"

    averagescorelist = [i for i in [vibe_averagescore, coffee_averagescore, service_averagescore, price_averagescore] if i != '-']


    try:
        if vibe_averagescore == max(averagescorelist):
            bestkeyword = "분위기"
        if coffee_averagescore == max(averagescorelist):
            bestkeyword = "커피&디저트"
        if service_averagescore == max(averagescorelist):
            bestkeyword = "서비스"
        if price_averagescore == max(averagescorelist):
            bestkeyword = "가격"
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
        'vibe_averagescore':vibe_averagescore,
        'coffee_averagescore':coffee_averagescore,
        'service_averagescore':service_averagescore,
        'price_averagescore':price_averagescore,
        'etc_averagescore':etc_averagescore,

        'keyword_vibe':keyword_vibe,
        'keyword_coffee':keyword_coffee,
        'keyword_service':keyword_service,
        'keyword_price':keyword_price,
        'keyword_etc':keyword_etc,

        'keyword_vibe_num':keyword_vibe_num,
        'keyword_coffee_num':keyword_coffee_num,
        'keyword_service_num':keyword_service_num,
        'keyword_price_num':keyword_price_num,
        'keyword_etc_num':keyword_etc_num,


        'keyword_vibe_good':keyword_vibe_good,
        'keyword_vibe_bad':keyword_vibe_bad,

        'keyword_coffee_good':keyword_coffee_good,
        'keyword_coffee_bad':keyword_coffee_bad,

        'keyword_service_good':keyword_service_good,
        'keyword_service_bad':keyword_service_bad,

        'keyword_price_good':keyword_price_good,
        'keyword_price_bad':keyword_price_bad,

        'keyword_etc_good':keyword_etc_good,
        'keyword_etc_bad':keyword_etc_bad,

        'bestkeyword':bestkeyword,
        'keyword_none_proportion':keyword_none_proportion,

        'ranking1':ranking1,
        'ranking2':ranking2,
        'ranking3':ranking3,
        
    }
    return render(request, 'main/reviewpage.html', context=context)


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

    keyword_vibe = Review.objects.filter(Cafe=cafeid, keyword='분위기')
    keyword_coffee = Review.objects.filter(Cafe=cafeid, keyword='커피&디저트')
    keyword_service = Review.objects.filter(Cafe=cafeid, keyword='서비스')
    keyword_price = Review.objects.filter(Cafe=cafeid, keyword='가격')
    keyword_etc = Review.objects.filter(Cafe=cafeid, keyword='기타')

    try:
        keyword_none_proportion = round(len(keyword_etc)/allreviewnum,3)*100
    except ZeroDivisionError:
        keyword_none_proportion = 0.0

    keyword_vibe_num = len(Review.objects.filter(Cafe=cafeid, keyword='분위기'))
    keyword_coffee_num = len(Review.objects.filter(Cafe=cafeid, keyword='커피&디저트'))
    keyword_service_num = len(Review.objects.filter(Cafe=cafeid, keyword='서비스'))
    keyword_price_num = len(Review.objects.filter(Cafe=cafeid, keyword='가격'))
    keyword_etc_num = len(Review.objects.filter(Cafe=cafeid, keyword='기타'))

    keyword_vibe_num_5 = len(Review.objects.filter(Cafe=cafeid, keyword='분위기', star_correction=5))
    keyword_vibe_num_4 = len(Review.objects.filter(Cafe=cafeid, keyword='분위기', star_correction=4))
    keyword_vibe_num_3 = len(Review.objects.filter(Cafe=cafeid, keyword='분위기', star_correction=3))
    keyword_vibe_num_2 = len(Review.objects.filter(Cafe=cafeid, keyword='분위기', star_correction=2))
    keyword_vibe_num_1 = len(Review.objects.filter(Cafe=cafeid, keyword='분위기', star_correction=1))
    keyword_vibe_num_0 = len(Review.objects.filter(Cafe=cafeid, keyword='분위기', star_correction=0))

    keyword_vibe_good = keyword_vibe_num_5 + keyword_vibe_num_4
    keyword_vibe_bad = keyword_vibe_num_2 + keyword_vibe_num_1 + keyword_vibe_num_0

    keyword_coffee_num_5 = len(Review.objects.filter(Cafe=cafeid, keyword='커피&디저트', star_correction=5))
    keyword_coffee_num_4 = len(Review.objects.filter(Cafe=cafeid, keyword='커피&디저트', star_correction=4))
    keyword_coffee_num_3 = len(Review.objects.filter(Cafe=cafeid, keyword='커피&디저트', star_correction=3))
    keyword_coffee_num_2 = len(Review.objects.filter(Cafe=cafeid, keyword='커피&디저트', star_correction=2))
    keyword_coffee_num_1 = len(Review.objects.filter(Cafe=cafeid, keyword='커피&디저트', star_correction=1))
    keyword_coffee_num_0 = len(Review.objects.filter(Cafe=cafeid, keyword='커피&디저트', star_correction=0))

    keyword_coffee_good = keyword_coffee_num_5 + keyword_coffee_num_4
    keyword_coffee_bad = keyword_coffee_num_2 + keyword_coffee_num_1 + keyword_coffee_num_0
    
    keyword_service_num_5 = len(Review.objects.filter(Cafe=cafeid, keyword='서비스', star_correction=5))
    keyword_service_num_4 = len(Review.objects.filter(Cafe=cafeid, keyword='서비스', star_correction=4))
    keyword_service_num_3 = len(Review.objects.filter(Cafe=cafeid, keyword='서비스', star_correction=3))
    keyword_service_num_2 = len(Review.objects.filter(Cafe=cafeid, keyword='서비스', star_correction=2))
    keyword_service_num_1 = len(Review.objects.filter(Cafe=cafeid, keyword='서비스', star_correction=1))
    keyword_service_num_0 = len(Review.objects.filter(Cafe=cafeid, keyword='서비스', star_correction=0))

    keyword_service_good = keyword_service_num_5 + keyword_service_num_4
    keyword_service_bad = keyword_service_num_2 + keyword_service_num_1 + keyword_service_num_0

    keyword_price_num_5 = len(Review.objects.filter(Cafe=cafeid, keyword='가격', star_correction=5))
    keyword_price_num_4 = len(Review.objects.filter(Cafe=cafeid, keyword='가격', star_correction=4))
    keyword_price_num_3 = len(Review.objects.filter(Cafe=cafeid, keyword='가격', star_correction=3))
    keyword_price_num_2 = len(Review.objects.filter(Cafe=cafeid, keyword='가격', star_correction=2))
    keyword_price_num_1 = len(Review.objects.filter(Cafe=cafeid, keyword='가격', star_correction=1))
    keyword_price_num_0 = len(Review.objects.filter(Cafe=cafeid, keyword='가격', star_correction=0))

    keyword_price_good = keyword_price_num_5 + keyword_price_num_4
    keyword_price_bad = keyword_price_num_2 + keyword_price_num_1 + keyword_price_num_0

    keyword_etc_num_5 = len(Review.objects.filter(Cafe=cafeid, keyword='기타', star_correction=5))
    keyword_etc_num_4 = len(Review.objects.filter(Cafe=cafeid, keyword='기타', star_correction=4))
    keyword_etc_num_3 = len(Review.objects.filter(Cafe=cafeid, keyword='기타', star_correction=3))
    keyword_etc_num_2 = len(Review.objects.filter(Cafe=cafeid, keyword='기타', star_correction=2))
    keyword_etc_num_1 = len(Review.objects.filter(Cafe=cafeid, keyword='기타', star_correction=1))
    keyword_etc_num_0 = len(Review.objects.filter(Cafe=cafeid, keyword='기타', star_correction=0))

    keyword_etc_good = keyword_etc_num_5 + keyword_etc_num_4
    keyword_etc_bad = keyword_etc_num_2 + keyword_etc_num_1 + keyword_etc_num_0


    scorelist=[]
    vibe_scorelist=[]
    coffee_scorelist=[]
    service_scorelist=[]
    price_scorelist=[]
    etc_scorelist=[]


    for review in reviews:
        scorelist.append(review.score)
    for review in keyword_vibe:
        vibe_scorelist.append(review.score)
    for review in keyword_coffee:
        coffee_scorelist.append(review.score)
    for review in keyword_service:
        service_scorelist.append(review.score)
    for review in keyword_price:
        price_scorelist.append(review.score)
    for review in keyword_etc:
        etc_scorelist.append(review.score)

    try:
        averagescore = round(sum(scorelist)/len(scorelist),2)
    except:
        averagescore = "-"

    try:
        vibe_averagescore = round(sum(vibe_scorelist)/len(vibe_scorelist),2)
    except:
        vibe_averagescore = "-"
    

    try:
        coffee_averagescore = round(sum(coffee_scorelist)/len(coffee_scorelist),2)
    except:
        coffee_averagescore = "-"

    try:
        service_averagescore = round(sum(service_scorelist)/len(service_scorelist),2)
    except:
        service_averagescore = "-"
    
    try:
        price_averagescore = round(sum(price_scorelist)/len(price_scorelist),2)
    except:
        price_averagescore = "-"
    
    try:
        etc_averagescore = round(sum(etc_scorelist)/len(etc_scorelist),2)
    except:
        etc_averagescore = "-"

    averagescorelist = [i for i in [vibe_averagescore, coffee_averagescore, service_averagescore, price_averagescore] if i != '-']


    try:
        if vibe_averagescore == max(averagescorelist):
            bestkeyword = "분위기"
        if coffee_averagescore == max(averagescorelist):
            bestkeyword = "커피&디저트"
        if service_averagescore == max(averagescorelist):
            bestkeyword = "서비스"
        if price_averagescore == max(averagescorelist):
            bestkeyword = "가격"
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
        'vibe_averagescore':vibe_averagescore,
        'coffee_averagescore':coffee_averagescore,
        'service_averagescore':service_averagescore,
        'price_averagescore':price_averagescore,
        'etc_averagescore':etc_averagescore,

        'keyword_vibe_num':keyword_vibe_num,
        'keyword_coffee_num':keyword_coffee_num,
        'keyword_service_num':keyword_service_num,
        'keyword_price_num':keyword_price_num,
        'keyword_etc_num':keyword_etc_num,


        'keyword_vibe_good':keyword_vibe_good,
        'keyword_vibe_bad':keyword_vibe_bad,

        'keyword_coffee_good':keyword_coffee_good,
        'keyword_coffee_bad':keyword_coffee_bad,

        'keyword_service_good':keyword_service_good,
        'keyword_service_bad':keyword_service_bad,

        'keyword_price_good':keyword_price_good,
        'keyword_price_bad':keyword_price_bad,

        'keyword_etc_good':keyword_etc_good,
        'keyword_etc_bad':keyword_etc_bad,

        'bestkeyword':bestkeyword,
        'keyword_none_proportion':keyword_none_proportion,

        'ranking1':ranking1,
        'ranking2':ranking2,
        'ranking3':ranking3,
        
    }
    return render(request, 'main/cafepage.html', context=context)


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
        loc = Loc.objects.get(name=column[2])
        cafe = Cafe.objects.filter(name=column[3], Loc=loc.id)
        
        try:
            created = Review.objects.create(
                Loc=loc,
                Cafe=cafe[0],
                text=column[4],
                star=column[7],
                score=column[6],
                keyword=column[5],
                star_correction = column[7],
            )
        except ValueError:
            pass

    context = {}
    return render(request,template,context)