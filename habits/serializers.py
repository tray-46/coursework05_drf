from typing import Union

from django.db import transaction
from django.utils import timezone
from drf_spectacular.extensions import OpenApiSerializerFieldExtension, _SchemaType
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field, Direction
from rest_framework import serializers

from habits.models import Action, Location, Reward, Habit
from users.serializers import UserSerializer

@extend_schema_field({
    "oneOf": [
        { "type": "integer"} ,
        { "type": "object",
          "properties": {
              "name": { "type": "string"},
          }
        }
    ]
})
class FlexibleNestedField(serializers.RelatedField):

    def __init__(self, model, serializer_class, **kwargs):
        self.model = model
        self.serializer_class = serializer_class
        super().__init__(**kwargs)

    def to_representation(self, instance):
        return self.serializer_class(instance, context=self.context).data

    def to_internal_value(self, data):
        if isinstance(data, (int, str)) or getattr(data, "isdigit", lambda: False)():
            try:
                return self.model.objects.get(pk=data)
            except self.model.DoesNotExist:
                raise serializers.ValidationError(f"{self.model.__name__} with pk {data} does not exist.")

        if isinstance(data, dict):
            serializer = self.serializer_class(data=data, context=self.context)
            serializer.is_valid(raise_exception=True)
            return serializer.save()

        raise serializers.ValidationError(f"Invalid input. Expected an id or dictionary.")


# class FlexibleNestedFieldExtension(OpenApiSerializerFieldExtension):
#     target_class = "habits.serializers.FlexibleNestedField"
#
#     def map_serializer_field(self, auto_schema: "AutoSchema", direction: Direction) -> _SchemaType:
#         component = auto_schema.resolve_serializer(
#             self.target.serializer_class(),
#             direction
#         )
#
#         pk_schema = {"type": "integer"}
#
#         return {
#             "OneOf": [
#                 pk_schema,
#                 component.ref
#             ]
#         }


class ActionSerializer(serializers.ModelSerializer):
    """
    Serializer for Action model
    """

    class Meta:
        model = Action
        fields = ("name",)
        extra_kwargs = {"name": {"validators": []}}

    def create(self, validated_data):
        action, _ = Action.objects.get_or_create(**validated_data)
        return action


class LocationSerializer(serializers.ModelSerializer):
    """
    Serializer for Location model
    """

    class Meta:
        model = Location
        fields = ("name",)
        extra_kwargs = {"name": {"validators": []}}

    def create(self, validated_data):
        location, _ = Location.objects.get_or_create(**validated_data)
        return location


class RewardSerializer(serializers.ModelSerializer):
    """
    Serializer for Reward model
    """

    class Meta:
        model = Reward
        fields = ("name",)
        extra_kwargs = {"name": {"validators": []}}

    def create(self, validated_data):
        reward, _ = Reward.objects.get_or_create(**validated_data)
        return reward


class HabitSerializer(serializers.ModelSerializer):
    """
    Serializer for Habit model
    """
    user = UserSerializer(read_only=True)
    action = FlexibleNestedField(model=Action, serializer_class=ActionSerializer, queryset=Action.objects.all())
    location = FlexibleNestedField(model=Location, serializer_class=LocationSerializer, queryset=Location.objects.all())
    reward = FlexibleNestedField(model=Reward, serializer_class=RewardSerializer, queryset=Reward.objects.all(),
                                 required=False, allow_null=True)

    class Meta:
        model = Habit
        fields = ("id", "user", "action", "location", "duration", "execution_time", "period", "related_habit", "reward",
                  "is_pleasant", "is_public", "is_disabled",)
        extra_kwargs = {
            "related_habit": {
                "error_messages": {
                    "does_not_exist": "Selected choice is invalid or not allowed. Pleas select pleasant habit",
                }
            }
        }

    def create(self, validated_data):
        action = validated_data.pop("action", None)
        location = validated_data.pop("location", None)
        reward = validated_data.pop("reward", None)

        habit = Habit.objects.create(**validated_data, action=action, location=location, reward=reward)
        return habit

    def update(self, instance, validated_data):
        with transaction.atomic():
            action = validated_data.pop("action", None)
            location = validated_data.pop("location", None)
            reward = validated_data.pop("reward", None)

            instance.action = action if action else instance.action
            instance.location = location if location else instance.location
            instance.duration = validated_data.get("duration", instance.duration)
            instance.execution_time = validated_data.get("execution_time", instance.execution_time)
            instance.period = validated_data.get("period", instance.period)
            instance.related_habit = validated_data.get("related_habit", instance.related_habit)
            instance.reward = reward if reward else instance.reward
            instance.is_pleasant = validated_data.get("is_pleasant", instance.is_pleasant)
            instance.is_public = validated_data.get("is_public", instance.is_public)
            instance.is_disabled = validated_data.get("is_disabled", instance.is_disabled)

            instance.save()
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if instance.related_habit:
            representation["related_habit"] = self.__class__(instance.related_habit).data

        # return {key: value for key, value in representation.items() if value is not None}
        return representation

    def validate_execution_time(self, value):
        """Check that the execution_time value not in the past"""
        if value < timezone.now():
            raise serializers.ValidationError("execution_time cannot be in past")
        return value

    def validate_duration(self, value):
        """Check that the duration value is between 1 and 120"""
        if not 1 <= value <= 120:
            raise serializers.ValidationError("duration must be between 1 and 120 seconds")
        return value

    def validate_period(self, value):
        """Check that the period value is between 1 and 7"""
        if not 1 <= value <= 7:
            raise serializers.ValidationError("period must be between 1 and 7 days")
        return value

    def validate_related_habit(self, value):
        """Check that the related_habit is a pleasant habit"""
        if value and not value.is_pleasant:
            print(value.is_pleasant)
            raise serializers.ValidationError("related_habit must be a pleasant habit")
        return value

    def validate(self, data):
        """Cross field validation"""
        is_pleasant = data.get("is_pleasant")
        related_habit = data.get("related_habit")
        reward = data.get("reward")

        if related_habit is not None and reward is not None:
            raise serializers.ValidationError("habit cannot have both related_habit and reward.")

        if (is_pleasant is not None and is_pleasant == True) and (related_habit is not None or reward is not None):
            raise serializers.ValidationError("pleasant habit cannot have related_habit or reward.")

        if (is_pleasant is not None and is_pleasant == False) and (related_habit is None and reward is None):
            print(f"{is_pleasant=} and {related_habit=} and {reward=}")
            raise serializers.ValidationError("habit must have related_habit or reward.")

        return data


class PublicHabitSerializer(serializers.ModelSerializer):
    action = serializers.StringRelatedField(read_only=True)
    location = serializers.StringRelatedField(read_only=True)
    reward = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Habit
        fields = ("action", "location", "duration", "execution_time", "period", "related_habit", "reward",
                  "is_pleasant",)

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if instance.related_habit:
            representation["related_habit"] = self.__class__(instance.related_habit).data

        return {key: value for key, value in representation.items() if value is not None}
