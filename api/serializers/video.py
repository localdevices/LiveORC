from rest_framework import serializers

from api.models import Video


class VideoSerializer(serializers.ModelSerializer):
    # camera_config = serializers.IntegerField(write_only=True, required=False)
    # Write-only fields for result file uploads
    result_1d = serializers.FileField(write_only=True, required=False, help_text="1D result file (NetCDF)")
    result_2d = serializers.FileField(write_only=True, required=False, help_text="2D result file (NetCDF)")
    result_2d_mask = serializers.FileField(write_only=True, required=False, help_text="2D mask result file (NetCDF)")
    result_2d_ugrid = serializers.FileField(write_only=True, required=False, help_text="2D UGRID result file (NetCDF-UGRID)")
    log_file = serializers.FileField(write_only=True, required=False, help_text="ORC processing log file (text file)")
    
    parent_lookup_kwargs = {
        # "site_pk": "camera_config__site__pk",
        "site_pk": "video_config__site__pk",
    }

    # file conventions for standard result files. Only modify this here!

    result_key_values = {
        'result_1d': "1d.nc",
        'result_2d': "2d.nc",
        'result_2d_mask': "2d_mask.nc",
        'result_2d_ugrid': "2d_ugrid.nc",
        'log_file': "orc.log"
    }


    # def validate(self, attrs):
    #     video_config = attrs.get("video_config", None)
        # camera_config_id = attrs.pop("camera_config", None)

        # if video_config is None and camera_config_id is not None:
        #     video_config = VideoConfig.objects.filter(camera_config_id=camera_config_id).order_by("id").first()
        # if video_config is None:
        #     raise serializers.ValidationError("No VideoConfig exists for provided camera_config")
        # attrs["video_config"] = video_config

        # if attrs.get("video_config") is None:
        #     raise serializers.ValidationError("video_config is required")
        # return attrs

    class Meta:
        model = Video
        fields = "__all__"
        # fields = ['created_at', 'file', 'thumbnail', 'water_level', 'status', 'camera_config']

    def _save_result_files(self, instance, validated_data):
        """Extract and save result files from validated data"""
        for field_name in self.result_key_values.keys():
            if field_name in validated_data:
                file_obj = validated_data.pop(field_name)
                if file_obj:
                    result_fn = self.result_key_values.get(field_name, None)
                    instance.save_result_file(result_fn, file_obj.read())
        return validated_data

    def create(self, validated_data):
        # self._save_result_files(None, validated_data)  # Extract result files
        result_files = {}
        # first split off any files from validated_data, so we can create the instance first
        for field_name in self.result_key_values.keys():
            if field_name in validated_data:
                result_files[field_name] = validated_data.pop(field_name)
        
        # Create the instance with remaining fields
        instance = super().create(validated_data)
        
        # Save result files after instance is created (so we have ID, timestamp, etc.)
        for field_name, file_obj in result_files.items():
            if file_obj:
                result_fn = self.result_key_values.get(field_name, None)
                instance.save_result_file(result_fn, file_obj.read())
    
        return instance

    def update(self, instance, validated_data):
        validated_data = self._save_result_files(instance, validated_data)
        return super().update(instance, validated_data)