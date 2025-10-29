import ffmpeg
import os
from gevent import monkey
monkey.patch_all()


from celery_app import celery_app

@celery_app.task(name="tasks.process_stream")
def process_stream(channel_name, url):
    output_dir = os.path.join("streams", channel_name)
    os.makedirs(output_dir, exist_ok=True)

    output_file = os.path.join(output_dir, f"{channel_name}.m3u8")
    print(f"🎥 Starting {channel_name} stream from {url}")

    try:
        (
            ffmpeg
            .input(url, f='mpegts')
            .output(
                output_file,
                vcodec='copy',
                acodec='copy',
                f='hls',
                hls_time=5,
                hls_list_size=0,
                hls_flags='delete_segments',
               
            )
            .overwrite_output()
            .run(quiet=True)
        )
    except ffmpeg.Error as e:
        print(f"❌ Error with {channel_name}: {e.stderr.decode() if e.stderr else e}")
