import ffmpeg
import os
import time
from datetime import datetime
from multiprocessing import Process
import re
import threading

CHANNELS = {
    "Dunya_News": "udp://@239.1.1.7:1111",
    "ARY_News": "udp://@239.1.1.9:1111",
    "Neo_News": "udp://@239.1.1.13:1111",
    "Samaa_News": "udp://@239.1.1.6:1111",
    "Dawn_News": "udp://@239.1.1.27:1111",
    "GTV_News_HD": "udp://@239.1.1.45:1111",
    "ABN_News": "udp://@239.1.1.57:1111",
    "Such_News_HD": "udp://@239.1.1.15:1111",
    # "PNN_News_HD": "udp://@239.1.1.38:1111",
    # "News_24_HD": "udp://@239.1.1.17:1111",
    # "Capital_TV": "udp://@239.1.1.11:1111",
    # "Bol_News_HD": "udp://@239.1.1.19:1111",
    # "Abb_Takk": "udp://@239.1.1.26:1111",
    # "Public_TV_HD": "udp://@239.1.1.25:1111",
    # "News_92_HD": "udp://@239.1.1.14:1111",
    # "Suno_TV": "udp://@239.1.1.10:1111",
    # "Aaj_News": "udp://@239.1.1.12:1111",
    # "GNN_HD": "udp://@239.1.1.30:1111",
    # "Roze_News": "udp://@239.1.1.33:1111",
    # "Khyber_News": "udp://@239.1.1.34:1111",
    # "Lahore_News_HD": "udp://@239.1.1.35:1111",
    # "TV_Today": "udp://@239.1.1.40:1111",
    # "Talon_News": "udp://@239.1.1.41:1111",
    # "News_One": "udp://@239.1.1.28:1111",
    # "PTV_World": "udp://@239.1.1.61:1111",
    # "CNN": "udp://@239.1.1.62:1111",
    # "BBC_World_News": "udp://@239.1.1.63:1111",
    # "Euronews": "udp://@239.1.1.64:1111",
    # "Sky_News": "udp://@239.1.1.66:1111",
    # "CGTN_News_HD": "udp://@239.1.1.71:1111",
    # "Channel_News_Asia_HD": "udp://@239.1.1.72:1111",
    # "Al_Jazeera_HD": "udp://@239.1.1.73:1111",
    # "TRT_World_HD": "udp://@239.1.1.74:1111",
    # "NHK_World_HD": "udp://@239.1.1.75:1111",
    # "DW_English_HD": "udp://@239.1.1.76:1111",
    # "CNBC_HD": "udp://@239.1.1.85:1111",
    # "PTV_News": "udp://@239.1.1.5:1111",
    # "Hum_News": "udp://@239.1.1.18:1111",
    # "Geo_News": "udp://@239.1.1.8:1111",
    # "Express_News": "udp://@239.1.1.16:1111"
}

def _capture_stats(name, proc, metrics_path):
    pattern_stats = re.compile(r"frame=\s*(\d+).*?fps=\s*([\d\.]+).*?time=\s*([\d:\.]+).*?speed=\s*([\d\.]+)x", re.IGNORECASE)
    # pattern_missing = re.compile(r"(missing|dropped?|drop).*frame", re.IGNORECASE)

    if not getattr(proc, "stderr", None):
        return

    with open(metrics_path, "a", encoding="utf-8") as f:
        while True:
            line = proc.stderr.readline()
            
            if not line:
                if proc.poll() is not None:
                    break
                time.sleep(0.1)
                continue

            text = line.decode(errors='replace').strip()

            m = pattern_stats.search(text)
            if m:
                ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                frame, fps, tstamp, speed = m.groups()
                msg = f"{ts} level=info channel={name} frame={frame} fps={fps} time={tstamp} speed={speed}"
                f.write(msg + "\n"); f.flush()
                print(f"[{name}] frame={frame} fps={fps} time={tstamp} speed={speed}", flush=True)
                

            # if pattern_missing.search(text) or ("error" in text.lower()):
            #     ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            #     level = "error" if "error" in text.lower() else "warning"
            #     msg = f"{ts} level={level} channel={name} msg={text}"
            #     f.write(msg + "\n"); f.flush()
            #     print(f"[{name}] {level}: {text}", flush=True)

def _metrics_path_for(date_str):
    base = os.path.join("logs")
    os.makedirs(base, exist_ok=True)
    return os.path.join(base, f"logs_{date_str}.log")  # one file per day (all channels)

def start_stream_for_date(name, url, date_str, base_dir="streams"):
    """Start FFmpeg process for one channel and one date"""
    output_dir = os.path.join(base_dir, name, date_str)
    os.makedirs(output_dir, exist_ok=True)

    metrics_file = _metrics_path_for(date_str)
    output_file = os.path.join(output_dir, f"{name}_stream.m3u8")
    print(f"🎥 [{name}] Starting stream for {date_str} -> {output_dir}")


    try:
        process = (
            ffmpeg
            .input(
                url,
                f='mpegts',
                loglevel='verbose',
                stats=None,         # emit "frame= ... fps= ..." progress lines
                hide_banner=None
                
            )
            .output(
                output_file,
                vcodec='copy',
                acodec='copy',
                f='hls',
                hls_time=10,
                hls_list_size=0,
                hls_flags='append_list',
                hls_segment_filename=os.path.join(output_dir, f"{name}_segment_%03d.ts")
                
            )
            .overwrite_output()
            .run_async(pipe_stderr=True)
        )
        print(process.stderr.readline().strip())
        # ff_log_dir = os.path.join("logs", "ffmpeg", name, date_str)
        # os.makedirs(ff_log_dir, exist_ok=True)
        # metrics_file = os.path.join(ff_log_dir, "metrics.log")
        threading.Thread(target=_capture_stats, args=(name, process, metrics_file), daemon=True).start()

        return process
    except Exception as e:
        print(f"❌ [{name}] Error starting stream: {e}")
        return None
    


def run_channel_until_midnight(name, url):
    """Run channel until 23:59:59, then restart for new date"""
    base_dir = "streams"
    
    while True:
        # Get current date
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Calculate time until midnight (23:59:59)
        now = datetime.now()
        midnight = now.replace(hour=23, minute=59, second=59, microsecond=0)
        
        # If it's already past 23:59, wait until tomorrow
        # Calculate sleep time until 23:59:59
        sleep_seconds = (midnight - now).total_seconds()
        
        # If sleep time is negative (past 23:59:59), wait 1 second and restart
        if sleep_seconds <= 0:
            print(f"⏰ [{name}] Past 23:59:59, waiting 1 second for new day...")
            time.sleep(1)
            continue  # Restart the loop with new date
        
        
        print(f"🎥 [{name}] Starting stream for {today}")
        print(f"⏰ [{name}] Will run until {midnight.strftime('%H:%M:%S')} ({sleep_seconds/3600:.1f} hours)")
        
        # Start stream for current date
        process = start_stream_for_date(name, url, today, base_dir)
        
        if process:
            try:
                # Sleep until 23:59:59
                time.sleep(sleep_seconds)
            except KeyboardInterrupt:
                print(f"🛑 [{name}] Received interrupt signal")
                break
            finally:
                # Stop the process at 23:59:59
                print(f"🛑 [{name}] Stopping stream at 23:59:59")
                try:
                    process.terminate()
                    process.wait(timeout=10)
                except:
                    process.kill()
                    process.wait()
        else:
            print(f"❌ [{name}] Failed to start stream, retrying in 30 seconds")
            time.sleep(30)

def run_all_channels():
    """Run all channels with midnight restarts"""
    processes = {}
    
    try:
        for name, url in CHANNELS.items():
            p = Process(target=run_channel_until_midnight, args=(name, url))
            p.start()
            processes[name] = p
            print(f"🚀 Started process for {name}")
            time.sleep(0.5)

        for name, p in processes.items():
            p.join()

    except KeyboardInterrupt:
        print("\n🛑 Shutting down all processes...")
        for name, p in processes.items():
            if p.is_alive():
                p.terminate()
                p.join(timeout=10)
                if p.is_alive():
                    p.kill()
        print("✅ All processes stopped")


if __name__ == "__main__":
    run_all_channels()
