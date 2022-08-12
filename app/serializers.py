from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import ModelSerializer

from db.models import (AttendanceSession, AttendanceRecord, Student, Department, Staff, )


class AttendanceSessionSerializer(ModelSerializer):
    class Meta:
        model = AttendanceSession
        fields = "__all__"


class AttendanceRecordSerializer(ModelSerializer):
    class Meta:
        model = AttendanceRecord
        fields = "__all__"


class StudentSerializer(ModelSerializer):
    class Meta:
        model = Student
        fields = "__all__"


class StaffSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150, )
    first_name = serializers.CharField(max_length=150, )
    last_name = serializers.CharField(max_length=150, )
    other_names = serializers.CharField(max_length=255, allow_null=True, allow_blank=True, )
    sex = serializers.IntegerField()
    password = serializers.CharField(max_length=128, )
    face_encodings = serializers.CharField(allow_null=True, allow_blank=True)
    fingerprint_template = serializers.CharField(default='', allow_null=True, allow_blank=True)
    department = PrimaryKeyRelatedField(
        queryset=Department.objects.all(), many=False
    )

    # staff_titles = PrimaryKeyRelatedField(
    #     queryset=StaffTitle.objects.all(), many=True
    # )

    def create(self, validated_data):
        staff_no = validated_data.get('username')
        instance = Staff.objects.filter(staff_number=staff_no).first()

        if instance is not None:
            return instance

        instance = Staff(staff_number=staff_no, **validated_data)
        instance.set_password(validated_data.get('password'))
        instance.save()
        return instance
