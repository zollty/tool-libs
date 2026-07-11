import os
from concurrent.futures import ThreadPoolExecutor

from music_analysis_and_processing.loudness_meter_with_essentia import audio_loudness_meter, compute_loudness_statistics, \
    print_loudness_statistics

DRAWING_EXECUTOR = ThreadPoolExecutor(max_workers=1)


def batch_process_audio(base_dir, output_folder="./loudness_plots/"):
    """批量处理文件夹中的音频文件"""
    from matplotlib_tools2 import draw_picture
    import csv

    sample_rate = 44100
    hop_size = 1024 / 44100  # 默认为0.1
    start_at_zero = True  # 默认为False
    low_thresh, high_thresh = -15, -12

    os.makedirs(output_folder, exist_ok=True)

    # audio_files = [f for f in os.listdir(folder_path)
    #                if f.endswith(('.wav', '.mp3', '.flac'))]

    # 定义CSV文件路径
    csv_file = "output.csv"
    # 写入表头（仅第一次）
    write_header = not os.path.exists(csv_file)

    with open(csv_file, mode='a', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["歌单", "歌曲名", "歌手", "响度", "LRA", "STD", "CV"])
        if write_header:
            writer.writeheader()

        # 获取base_dir下的所有歌词文件内容，包括子目录
        i = 0
        for root, dirs, files in os.walk(base_dir):
            for file in files:
                if file.endswith(".flac") or file.endswith(".mp3") or file.endswith(".wav"):
                    i = i + 1
                    audio_file = os.path.join(root, file)
                    song_name = os.path.splitext(file)[0]
                    playlist = os.path.basename(root)  # 获取当前文件所在目录名
                    output_img = os.path.join(output_folder, f"{song_name}-{i}.png")
                    names = song_name.split(' - ')
                    if len(names) > 1:
                        song_name = names[1]
                        songer = names[0]
                    else:
                        songer = '??'

                    # print(f"处理中: {audio_file} ({i + 1}/{len(audio_files)})")
                    print(f"处理中: {i} {audio_file} -----------------------------")
                    try:
                        result = audio_loudness_meter(audio_file, sample_rate, hop_size, start_at_zero)
                        stats = compute_loudness_statistics(result, low_thresh, high_thresh)
                        # print_loudness_statistics(stats, low_thresh, high_thresh)

                        row = {
                            "歌单": playlist,
                            "歌曲名": song_name,
                            "歌手": songer,
                            "响度": round(stats["integrated"], 1),
                            "LRA": round(stats["lra"], 1),
                            "STD": round(stats["momentary_std"], 1),
                            "CV": round(stats["momentary_cv"], 1)
                        }
                        writer.writerow(row)
                        f.flush()  # 立即写入磁盘
                        print(f"已追加写入：{i} {song_name}")

                    except Exception as e:
                        print(f"处理失败 {audio_file}: {str(e)}")

    print(f"完成! {i}个文件处理完毕，图像保存在{output_folder}")
    DRAWING_EXECUTOR.shutdown(wait=True)


if __name__ == "__main__":
    base_dir = "/mnt/g/__SYNC4/music"
    output_folder = "/root/my-notebook/loudness_plots/"
    batch_process_audio(base_dir, output_folder)
