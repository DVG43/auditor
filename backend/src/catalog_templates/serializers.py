from rest_framework import serializers
from collections import OrderedDict
from rest_framework.fields import set_value

from .models import Template, CategoryForTemplate


class CategoryForTemplateSerializer(serializers.ModelSerializer):
    slug = serializers.CharField(read_only=True)

    class Meta:
        model = CategoryForTemplate
        fields = [
            'id',
            'name',
            'slug',
        ]



class TemplateSerializer(serializers.ModelSerializer):
    favourite = serializers.BooleanField(required=False)
    is_common = serializers.BooleanField(read_only=True)
    categories = CategoryForTemplateSerializer(many=True, required=False, read_only=True)
    categories_input = serializers.ListField(child=serializers.IntegerField(required=False), write_only=True, required=False, allow_empty=True)

    class Meta:
        model = Template
        fields = [
            'id',
            'name',
            'template_text',
            'example',
            'result',
            'is_common',
            'favourite',
            'categories_input',
            'categories',
        ]

    def create(self, validated_data):
        instance = super().create(validated_data)
        if hasattr(instance, "perms"):
            instance.owner.grant_object_perm(instance, 'own')
        return instance

    def to_representation(self, instance):
        is_favourite = instance.favourite.filter(id=self.context.get("request").user.id).exists()
        instance_ordereddict = super().to_representation(instance)
        instance_ordereddict.update({'favourite': is_favourite})
        return instance_ordereddict

    def super_to_internal_value(self, data):
        """
        Dict of native values <- Dict of primitive datatypes.
        """

        ret = OrderedDict()
        fields = self._writable_fields
        for field in fields:
            validate_method = getattr(self, 'validate_' + field.field_name, None)
            primitive_value = field.get_value(data)
            try:
                validated_value = field.run_validation(primitive_value)
                if validate_method is not None:
                    validated_value = validate_method(validated_value)
            except:
                pass
            else:
                set_value(ret, field.source_attrs, validated_value)

        return ret

    def to_internal_value(self, data):
        data['categories_input'] = data['categories_input'].split(',') if data.get('categories_input') else []
        return self.super_to_internal_value(data)


