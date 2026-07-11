import os
import soundfile as sf
from collections import defaultdict


def get_audio_info_soundfile(file_path, debug=True):
    info = sf.info(file_path)
    audio_info = {
        'samplerate': info.samplerate,
        'subtype': info.subtype,
        'channels': info.channels,
        'duration': info.duration,
        'format': info.format
    }
    if debug:
        print(info)
        print(f"采样率 (Sample Rate): {audio_info['samplerate']} Hz")
        print(f"类型 (subtype): {audio_info['subtype']}")
        print(f"声道数 (Channels): {audio_info['channels']}")
        print(f"时长 (Duration): {audio_info['duration']:.2f} 秒")
    return audio_info


def batch_process_audio(base_dir):
    """批量处理文件夹中的音频文件"""
    # 使用字典来存储具有相同特征的歌曲
    song_groups = defaultdict(list)

    # 获取base_dir下的所有歌词文件内容，包括子目录
    i = 0
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".flac") or file.endswith(".mp3") or file.endswith(".wav"):
                i = i + 1
                audio_file = os.path.join(root, file)
                song_name = os.path.splitext(file)[0]
                playlist = os.path.basename(root)  # 获取当前文件所在目录名
                print(f"处理中: {i} {audio_file} -----------------------------")
                try:

                    audio_info = get_audio_info_soundfile(audio_file, debug=False)
                    # 创建一个特征键用于分组
                    feature_key = (audio_info['samplerate'], audio_info['subtype'], audio_info['channels'])
                    song_groups[feature_key].append({
                        'name': file,
                        'playlist': playlist,
                        'song_name': song_name
                    })

                except Exception as e:
                    print(f"处理失败 {audio_file}: {str(e)}")

    print(f"完成! {i}个文件处理完毕")
    for feature_key, songs in song_groups.items():
        print(f"特征: {feature_key}, songs: {len(songs)}")
        for song in songs[:5]:
            print(f"  歌曲: {song['name']} - 歌单: {song['playlist']}")


if __name__ == "__main__":
    base_path = "/mnt/g/__SYNC4/music/S0-Serene"
    batch_process_audio(base_path)
    # 示例
    # get_audio_info_soundfile("audio.wav")
