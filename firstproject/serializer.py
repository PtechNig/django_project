from rest_framework import serializers
from datetime import datetime

class BlogSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    author = serializers.CharField(max_length=100)
    title = serializers.CharField(max_length=200)
    content = serializers.CharField()
    created_at = serializers.DateTimeField(default=datetime.now)

    def to_representation(self, instance):
        """
        Customize the serialization to handle MongoDB's _id field.
        """
        ret = super().to_representation(instance)
        # Convert MongoDB's ObjectId to string and map it to id
        ret['id'] = str(instance.get('_id', ''))
        return ret