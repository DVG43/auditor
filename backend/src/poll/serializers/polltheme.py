from rest_framework import serializers
from drf_base64.fields import Base64ImageField
from poll.models.poll import Poll
from poll.models.polltheme import PollTheme


class PollThemeSerializerBase(serializers.ModelSerializer):
    pollId = serializers.PrimaryKeyRelatedField(queryset=Poll.objects.all(), source='poll', required=False, allow_null=True)
    userId = serializers.PrimaryKeyRelatedField(source='user', read_only=True)

    logo = Base64ImageField(required=False, allow_null=True)
    logoName = serializers.CharField(source='logo_name', required=False)
    logoColorActive = serializers.BooleanField(source='logo_color_active', required=False)
    logoBgColor = serializers.CharField(source='logo_bg_color', required=False)

    backgroundImage = Base64ImageField(source='background_image', required=False, allow_null=True)
    backgroundName = serializers.CharField(source='background_name', required=False)
    backgroundOpacity = serializers.FloatField(source='background_opacity', required=False)

    settingsFontFamily = serializers.CharField(source='setting_font_family', required=False)
    settingsTextColor = serializers.CharField(source='setting_text_color', required=False)
    settingsElementColor = serializers.CharField(source='setting_element_color', required=False)
    settingsBgColor = serializers.CharField(source='setting_background_color', required=False)
    settingsProgressActive = serializers.BooleanField(source='settings_progress_active', required=False)

    standard = serializers.BooleanField(source='is_standard', read_only=True)
    isActive = serializers.BooleanField(source='is_active', required=False)

    class Meta:
        model = PollTheme
        fields = ['id', 'pollId', 'userId', 'name', 'article', 'logo', 'logoName', 'logoColorActive', 'logoBgColor',
                  'backgroundImage', 'backgroundName', 'backgroundOpacity', 'settingsFontFamily', 'settingsTextColor',
                  'settingsElementColor', 'settingsBgColor', 'settingsProgressActive', 'standard', 'isActive']
        read_only_fields = ['userId', 'standard', 'isActive']

    def validate(self, data):
        user = self.user

        logo = data.get('logo')
        background_image = data.get('background_image')
        profile = user.secretguestprofile
        size = 0

        if logo:
            size += logo.size
        if background_image:
            size += background_image.size

        current_disk_space = profile.current_disk_space
        max_disk_space = profile.max_disk_space
        free_disk_space = max_disk_space - current_disk_space

        if size > free_disk_space:
            raise serializers.ValidationError({'result': 'not enough space'})

        profile.current_disk_space_increment(size)
        return data

    def to_representation(self, instance):
        resp = super(PollThemeSerializerBase, self).to_representation(instance)
        return {
            'id': instance.pk,
            'standard': instance.is_standard,
            'isActive': instance.is_active,
            'article': instance.article,
            'name': instance.name,
            'logo': {
                'name': instance.logo_name,
                'image': resp['logo'],
                'ColorActive': instance.logo_color_active,
                'BgColor': instance.logo_bg_color,
            },
            'BgImage': {
                'name': instance.background_name,
                'image': resp['backgroundImage'],
                'opacity': instance.background_opacity,
            },
            'settings': {
                'FontFamily': instance.setting_font_family,
                'textColor': instance.setting_text_color,
                'elementColor': instance.setting_element_color,
                'bgColor': instance.setting_background_color,
                'progressActive': instance.settings_progress_active
            }
        }


class PollThemeSerializer(PollThemeSerializerBase):
    def __init__(self, *args, **kwargs):
        self.user = None
        super(PollThemeSerializer, self).__init__(*args, **kwargs)
        if 'request' in self.context:
            self.user = self.context.get('request').user

    def update(self, instance, validated_data):
        validated_data['user'] = self.user
        is_active = validated_data.get('is_active', False)
        if is_active and instance.poll:
            poll_thems = PollTheme.objects.filter(poll_id=instance.poll.pk, is_active=True)
            poll_thems.update(is_active=False)
        return super(PollThemeSerializer, self).update(instance, validated_data)

    def create(self, validated_data):
        validated_data['user'] = self.user
        poll = validated_data.get('poll')
        is_active = validated_data.get('is_active', False)
        if is_active and poll:
            poll_thems = PollTheme.objects.filter(poll_id=poll.pk, is_active=True)
            poll_thems.update(is_active=False)
        return super().create(validated_data)

    def to_representation(self, instance):
        resp = super(PollThemeSerializer, self).to_representation(instance)
        return resp


class PollThemeListSerializer(PollThemeSerializerBase):
    def to_representation(self, instance):
        resp = super(PollThemeListSerializer, self).to_representation(instance)
        return resp
