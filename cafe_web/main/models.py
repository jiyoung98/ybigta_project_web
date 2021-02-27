from django.db import models

class Loc(models.Model):
    name = models.CharField(max_length=30)

    class Meta:
        app_label = 'main'

    def __str__(self):
        return self.name


class Cafe(models.Model):
    name = models.CharField(max_length=30)
    Loc = models.ForeignKey(Loc, on_delete=models.CASCADE)
    first_keyword = models.CharField(null=True, blank=True, max_length=20)
    vibescore = models.FloatField(null=True, blank=True)
    coffeescore = models.FloatField(null=True, blank=True)
    servicescore = models.FloatField(null=True, blank=True)
    pricescore = models.FloatField(null=True, blank=True)

    class Meta:
        app_label = 'main'

    def __str__(self):
        return self.name


class Review(models.Model):
    Loc = models.ForeignKey(Loc, on_delete=models.CASCADE,default=0)
    text = models.TextField(max_length=500)
    score = models.FloatField()
    keyword = models.CharField(max_length=30)
    Cafe = models.ForeignKey(Cafe, on_delete=models.CASCADE,related_name="review")
    star = models.IntegerField(default=0)
    star_correction = models.IntegerField(default=0)


    class Meta:
        app_label = 'main'    

    def __str__(self):
        return self.text