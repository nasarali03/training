from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from .serializers import MediaSerializer
from .utils import convert
import ffmpeg
import os
from.tasks import test_celery_task,process_video
from converter.celery import app  # import your Celery app instance
from celery.result import AsyncResult

class MediaView(APIView):
    serializer_class = MediaSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            video_instance = serializer.save()
            file_path = str(video_instance.video_file.path).replace("\\", "/")


            try:
                media_root = str(settings.MEDIA_ROOT).replace("\\", "/")

                rel_path = os.path.relpath(file_path, media_root).replace("\\", "/")

                converted_rel_dir = os.path.join(
                    "converted_videos", os.path.dirname(rel_path).split("/", 1)[-1]
                )
                converted_abs_dir = os.path.join(media_root, converted_rel_dir)
                os.makedirs(converted_abs_dir, exist_ok=True)

                converted_filename = os.path.splitext(os.path.basename(file_path))[0] + ".mp4"
                converted_file_path = os.path.join(
                    converted_abs_dir, converted_filename
                ).replace("\\", "/")

                print(f"Input file: {file_path}")
                print(f"Output file: {converted_file_path}")

                if convert(file_path, converted_file_path):
                    video_instance.converted_video.name = os.path.join(
                        converted_rel_dir, converted_filename
                    ).replace("\\", "/")
                    video_instance.save(update_fields=["converted_video"])
                else:
                    raise Exception("Conversion failed")

                probe_original = ffmpeg.probe(file_path)
                probe_converted = ffmpeg.probe(converted_file_path)
                formated_info_converted = probe_converted.get("format", {})
                format_info = probe_original.get("format", {})

                title = os.path.basename(file_path)
                size_bytes = float(formated_info_converted.get("size", 0))
                size_mb = round(size_bytes / (1024 * 1024), 2)

                video_instance.title = title
                video_instance.size = size_mb
                video_instance.save(update_fields=["title", "size"])

                return Response(
                    {
                        "message": "Video uploaded and converted successfully",
                        "title": title,
                        "original_file": video_instance.video_file.url,
                        "converted_file": video_instance.converted_video.url,
                        "size_mb": size_mb,
                    },
                    status=status.HTTP_201_CREATED,
                )

            except Exception as e:
                print("FFmpeg Error:", e)
                video_instance.delete()
                return Response({"error": "Invalid or failed video conversion."}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CeleryTestView(APIView):
    def get(self,request):
        task = test_celery_task.delay(10, 10)
        return Response(
            {"message": "Task submitted!", "task_id": task.id},
            status=status.HTTP_202_ACCEPTED
        )

class TaskStatusView(APIView):
    def get(self, request, task_id):
        result = AsyncResult(task_id, app=app)
        return Response({
            "task_id": task_id,
            "status": result.status,
            "result": result.result if result.ready() else None,
        }, status=status.HTTP_200_OK)
        
        
class ProcessVideo(APIView):
    serializer_class = MediaSerializer
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        
        if serializer.is_valid():
            video_instance = serializer.save()
            file_path = str(video_instance.video_file.path).replace("\\", "/")

            try:
                media_root = str(settings.MEDIA_ROOT).replace("\\", "/")

                rel_path = os.path.relpath(file_path, media_root).replace("\\", "/")

                converted_rel_dir = os.path.join(
                    "converted_videos", os.path.dirname(rel_path).split("/", 1)[-1]
                )
                converted_abs_dir = os.path.join(media_root, converted_rel_dir)
                os.makedirs(converted_abs_dir, exist_ok=True)

                converted_filename = os.path.splitext(os.path.basename(file_path))[0] + ".mp4"
                converted_file_path = os.path.join(
                    converted_abs_dir, converted_filename
                ).replace("\\", "/")

                print(f"Input file: {file_path}")
                print(f"Output file: {converted_file_path}")

                if process_video.delay(file_path, converted_file_path):
                    video_instance.converted_video.name = os.path.join(
                        converted_rel_dir, converted_filename
                    ).replace("\\", "/")
                    video_instance.save(update_fields=["converted_video"])
                else:
                    raise Exception("Conversion failed")
                
                return Response({"msg":"Video coverted successfully", "status":status.HTTP_201_CREATED})
            except Exception as e:
                print("FFmpeg Error:", e)
                video_instance.delete()
                return Response({"error": "Invalid or failed video conversion."}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)