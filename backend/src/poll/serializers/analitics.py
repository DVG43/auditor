from rest_framework import serializers
from django.db.models import Avg

from poll.models.analitics import PollAnalitics
from poll.models.surveypassing import SurveyPassing

class PollAnaliticsSerializer(serializers.ModelSerializer):

    percent_before_18_total = serializers.SerializerMethodField()
    percent_in_18_24_total = serializers.SerializerMethodField()
    percent_in_25_35_total = serializers.SerializerMethodField()
    percent_in_36_45_total = serializers.SerializerMethodField()
    percent_older_46_total = serializers.SerializerMethodField()
    percent_from_desktop = serializers.SerializerMethodField()
    percent_from_mobile = serializers.SerializerMethodField()
    percent_from_other = serializers.SerializerMethodField()
    total = serializers.SerializerMethodField()
    percent_women_before_18 = serializers.SerializerMethodField()
    percent_men_before_18 = serializers.SerializerMethodField()
    percent_women_in_18_24 = serializers.SerializerMethodField()
    percent_men_in_18_24 = serializers.SerializerMethodField()
    percent_women_in_25_35 = serializers.SerializerMethodField()
    percent_men_in_25_35 = serializers.SerializerMethodField()
    percent_women_in_36_45 = serializers.SerializerMethodField()
    percent_men_in_36_45 = serializers.SerializerMethodField() 
    percent_women_older_46 = serializers.SerializerMethodField()
    percent_men_older_46 = serializers.SerializerMethodField()

    percent_men_total = serializers.SerializerMethodField()
    percent_women_total = serializers.SerializerMethodField()
    avarage_age = serializers.IntegerField(read_only=True)
    men_total = serializers.IntegerField(read_only=True)
    women_total = serializers.IntegerField(read_only=True)
    women_before_18 = serializers.IntegerField(read_only=True)
    men_before_18 = serializers.IntegerField(read_only=True)
    women_in_18_24 = serializers.IntegerField(read_only=True)
    men_in_18_24 = serializers.IntegerField(read_only=True)
    women_in_25_35 = serializers.IntegerField(read_only=True)
    men_in_25_35 = serializers.IntegerField(read_only=True)
    women_in_36_45 = serializers.IntegerField(read_only=True)
    men_in_36_45 = serializers.IntegerField(read_only=True) 
    women_older_46 = serializers.IntegerField(read_only=True)
    men_older_46 = serializers.IntegerField(read_only=True)


    def get_percent_women_total(self, obj):
        if (obj.men_total + obj.women_total) == 0:
            return '0%'
        else:
            return str(round(obj.women_total/
                       (obj.men_total + obj.women_total)*100)) + '%'
    
    def get_percent_men_total(self, obj):
        if (obj.men_total + obj.women_total) == 0:
            return '0%'
        else:
            return str(round(obj.men_total/
                       (obj.men_total + obj.women_total)*100)) + '%'

    def get_percent_before_18_total(self, obj):
        if (obj.men_total + obj.women_total) == 0:
            return '0%'
        else:
            return str(round((obj.women_before_18 + obj.men_before_18)/
                       (obj.men_total + obj.women_total)*100)) + '%'

    def get_percent_in_18_24_total(self, obj):
        if (obj.men_total + obj.women_total) == 0:
            return '0%'
        else:
            return str(round((obj.women_in_18_24 + obj.men_in_18_24)/
                       (obj.men_total + obj.women_total)*100)) + '%'

    def get_percent_in_25_35_total(self, obj):
        if (obj.men_total + obj.women_total) == 0:
            return '0%'
        else:
            return str(round((obj.women_in_25_35 + obj.men_in_25_35)/
                       (obj.men_total + obj.women_total)*100)) + '%'

    def get_percent_in_36_45_total(self, obj):
        if (obj.men_total + obj.women_total) == 0:
            return '0%'
        else:
            return str(round((obj.women_in_36_45 + obj.men_in_36_45)/
                       (obj.men_total + obj.women_total)*100)) + '%'

    def get_percent_older_46_total(self, obj):
        if (obj.men_total + obj.women_total) == 0:
            return '0%'
        else:
            return str(round((obj.women_older_46 + obj.men_older_46)/
                       (obj.men_total + obj.women_total)*100)) + '%'

    def get_percent_from_desktop(self, obj):
        if (obj.men_total + obj.women_total) == 0:
            return '0%'
        else:
            return str(round(obj.from_desktop/
                      (obj.men_total + obj.women_total)*100)) + '%'

    def get_percent_from_mobile(self, obj):
        if (obj.men_total + obj.women_total) == 0:
            return '0%'
        else:
            return str(round(obj.from_mobile/
                      (obj.men_total + obj.women_total)*100)) + '%'

    def get_percent_from_other(self, obj):
        if (obj.men_total + obj.women_total) == 0:
            return '0%'
        else:
            return str(round(obj.from_other/
                      (obj.men_total + obj.women_total)*100)) + '%'

    def get_percent_women_before_18(self, obj):
        if (obj.men_before_18 + obj.women_before_18) == 0:
            return '0%'
        else:
            return str(round(obj.women_before_18/
                      (obj.men_before_18 + obj.women_before_18)*100)) + '%'

    def get_percent_men_before_18(self, obj):
        if (obj.men_before_18 + obj.women_before_18) == 0:
            return '0%'
        else:
            return str(round(obj.men_before_18/
                      (obj.men_before_18 + obj.women_before_18)*100)) + '%'

    def get_percent_women_in_18_24(self, obj):
        if (obj.men_in_18_24 + obj.women_in_18_24) == 0:
            return '0%'
        else:
            return str(round(obj.women_in_18_24/
                      (obj.men_in_18_24 + obj.women_in_18_24)*100)) + '%'

    def get_percent_men_in_18_24(self, obj):
        if (obj.men_in_18_24 + obj.women_in_18_24) == 0:
            return '0%'
        else:
            return str(round(obj.men_in_18_24/
                      (obj.men_in_18_24 + obj.women_in_18_24)*100)) + '%'

    def get_percent_women_in_25_35(self, obj):
        if (obj.men_in_25_35 + obj.women_in_25_35) == 0:
            return '0%'
        else:
            return str(round(obj.women_in_25_35/
                      (obj.men_in_25_35 + obj.women_in_25_35)*100)) + '%'

    def get_percent_men_in_25_35(self, obj):
        if (obj.men_in_25_35 + obj.women_in_25_35) == 0:
            return '0%'
        else:
            return str(round(obj.men_in_25_35/
                      (obj.men_in_25_35 + obj.women_in_25_35)*100)) + '%'

    def get_percent_women_in_36_45(self, obj):
        if (obj.men_in_36_45 + obj.women_in_36_45) == 0:
            return '0%'
        else:
            return str(round(obj.women_in_36_45/
                      (obj.men_in_36_45 + obj.women_in_36_45)*100)) + '%'

    def get_percent_men_in_36_45(self, obj):
        if (obj.men_in_36_45 + obj.women_in_36_45) == 0:
            return '0%'
        else:
            return str(round(obj.men_in_36_45/
                      (obj.men_in_36_45 + obj.women_in_36_45)*100)) + '%'

    def get_percent_women_older_46(self, obj):
        if (obj.men_older_46 + obj.women_older_46) == 0:
            return '0%'
        else:
            return str(round(obj.women_older_46/
                      (obj.men_older_46 + obj.women_older_46)*100)) + '%'

    def get_percent_men_older_46(self, obj):
        if (obj.men_older_46 + obj.women_older_46) == 0:
            return '0%'
        else:
            return str(round(obj.men_older_46/
                      (obj.men_older_46 + obj.women_older_46)*100)) + '%'

    def get_total(self, obj):
        return int(round(obj.men_total + obj.women_total))

    class Meta:
        model = PollAnalitics
        fields = ['url', 'id', 'poll_id', 'survey_id', 'avarage_age', 
                  'men_total', 'women_total', 'total',
                  'percent_men_total', 'percent_women_total',
                  'women_before_18', 'men_before_18', 'percent_women_before_18', 
                  'percent_men_before_18','percent_before_18_total', 
                  'women_in_18_24', 'men_in_18_24', 'percent_women_in_18_24', 
                  'percent_men_in_18_24','percent_in_18_24_total',
                  'women_in_25_35', 'men_in_25_35', 'percent_women_in_25_35', 
                  'percent_men_in_25_35','percent_in_25_35_total', 
                  'women_in_36_45', 'men_in_36_45', 'percent_women_in_36_45', 
                  'percent_men_in_36_45','percent_in_36_45_total', 
                  'women_older_46', 'men_older_46', 'percent_women_older_46', 
                  'percent_men_older_46','percent_older_46_total',
                  'percent_from_desktop', 'percent_from_mobile', 'percent_from_other']


    def create(self, *args, **kwargs):

        poll_analitics = PollAnalitics.objects.create(poll_id=args[0]['poll_id'])
        survey_passing_list = SurveyPassing.objects.filter(poll=args[0]['poll_id'])
        total = len(survey_passing_list)

        total_men_list = survey_passing_list.filter(sex='male')
        total_women_list = survey_passing_list.filter(sex='female')

        poll_analitics.men_total = len(total_men_list)
        poll_analitics.women_total = len(total_women_list)

        poll_analitics.women_before_18 = len(total_women_list.filter(age__lt=18))
        poll_analitics.men_before_18 = len(total_men_list.filter(age__lt=18))
        poll_analitics.women_in_18_24 = len(total_women_list.filter(age__gte=18).filter(age__lte=24))
        poll_analitics.men_in_18_24 = len(total_men_list.filter(age__gte=18).filter(age__lte=24))
        poll_analitics.women_in_25_35 = len(total_women_list.filter(age__gte=25).filter(age__lte=35))
        poll_analitics.men_in_25_35 = len(total_men_list.filter(age__gte=25).filter(age__lte=35))
        poll_analitics.women_in_36_45 = len(total_women_list.filter(age__gte=36).filter(age__lte=45))
        poll_analitics.men_in_36_45 = len(total_men_list.filter(age__gte=36).filter(age__lte=45))
        poll_analitics.women_older_46 = len(total_women_list.filter(age__gte=46))
        poll_analitics.men_older_46 = len(total_men_list.filter(age__gte=46))

        poll_analitics.from_desktop = len(survey_passing_list.filter(platform='Desktop'))
        poll_analitics.from_mobile = len(survey_passing_list.filter(platform='Mobile'))
        poll_analitics.from_other = len(survey_passing_list) - (poll_analitics.from_desktop + 
                                                                poll_analitics.from_mobile)
        if len(survey_passing_list) != 0:
            poll_analitics.avarage_age = int(survey_passing_list.aggregate(Avg('age'))['age__avg'])
        else:
        	poll_analitics.avarage_age = 0

        for el in survey_passing_list:
            poll_analitics.survey_id.add(el)

        poll_analitics.save()
        return poll_analitics

    def update(self, pk, *args, **kwargs):

        poll_analitics = PollAnalitics.objects.get(poll_id=args[0]['poll_id'])
        if args[0]['survey_id'][0] not in poll_analitics.survey_id.all():
            survey_passing = SurveyPassing.objects.get(id=args[0]['survey_id'][0].id)
            poll_analitics.avarage_age = (poll_analitics.avarage_age*(poll_analitics.men_total + 
            	poll_analitics.women_total) + survey_passing.age)/(poll_analitics.men_total + 
                poll_analitics.women_total + 1)
            if survey_passing.sex == 'male':
                poll_analitics.men_total += 1
                if survey_passing.age < 18:
                    poll_analitics.men_before_18 += 1
                elif 18<=survey_passing.age<=24:
                    poll_analitics.men_in_18_24 += 1
                elif 25<=survey_passing.age<=35:
                    poll_analitics.men_in_25_35 += 1
                elif 36<=survey_passing.age<=45:
                    poll_analitics.men_in_36_45 += 1
                elif survey_passing.age >= 46:
                    poll_analitics.men_older_46 += 1
            elif survey_passing.sex == 'female':
                poll_analitics.women_total += 1
                if survey_passing.age < 18:
                    poll_analitics.women_before_18 += 1
                elif 18<=survey_passing.age<=24:
                    poll_analitics.women_in_18_24 += 1
                elif 25<=survey_passing.age<=35:
                    poll_analitics.women_in_25_35 += 1
                elif 36<=survey_passing.age<=45:
                    poll_analitics.women_in_36_45 += 1
                elif survey_passing.age >= 46:
                    poll_analitics.women_older_46 += 1

            if survey_passing.platform == 'Desktop':
                poll_analitics.from_desktop += 1
            elif survey_passing.platform == 'Mobile':
                poll_analitics.from_mobile += 1
            else:
                poll_analitics.from_other += 1

            poll_analitics.survey_id.add(args[0]['survey_id'][0])
            poll_analitics.save()
        return poll_analitics
