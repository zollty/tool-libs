import os
from collections import defaultdict

from mutagen import File
from mutagen.flac import FLAC
from mutagen.wave import WAVE
from mutagen.mp3 import MP3
from mutagen.id3 import ID3


def get_audio_info(file_path, debug=True):
    audio_info = {
        # 采样率(sample_rate): 一般 44100 或者 48000（44.1/48 kHz），少用96 kHz/192 kHz（一般用于后期处理）
        'samplerate': None,
        'sample_width': None,
        'subtype': None,
        'channels': None,
        'duration': None,
        'format': None,
        'bitrate': None
    }

    try:
        audio = File(file_path)
        if not audio:
            raise ValueError("Unsupported audio format")

        # 获取基础信息
        audio_info['format'] = audio.mime[0].split('/')[1].upper()  # 如'mp3','flac','wav'
        audio_info['duration'] = audio.info.length
        audio_info['bitrate'] = audio.info.bitrate // 1000 if hasattr(audio.info, 'bitrate') else None

        # 处理不同格式
        if isinstance(audio, FLAC):
            audio_info['samplerate'] = audio.info.sample_rate
            audio_info['channels'] = audio.info.channels
            audio_info['sample_width'] = audio.info.bits_per_sample // 8
            audio_info['subtype'] = f"PCM_{audio.info.bits_per_sample}"

        elif isinstance(audio, WAVE):
            audio_info['samplerate'] = audio.info.sample_rate
            audio_info['channels'] = audio.info.channels
            audio_info['sample_width'] = audio.info.bits_per_sample // 8
            audio_info['subtype'] = f"PCM_{audio.info.bits_per_sample}"

        elif isinstance(audio, MP3):
            audio_info['samplerate'] = audio.info.sample_rate
            audio_info['channels'] = 2  # MP3通常是立体声
            audio_info['subtype'] = 'MPEG_LAYER_III'
            # MP3没有sample_width概念，默认设置为2
            audio_info['sample_width'] = 2

        if debug:
            print(audio_info)
            print(f"成功读取{file_path}")
            print(f"采样率 (Sample Rate): {audio_info['samplerate']} Hz")
            print(f"类型 (subtype): {audio_info['subtype']}")
            print(f"声道数 (Channels): {audio_info['channels']}")
            print(f"时长 (Duration): {audio_info['duration']:.2f} 秒")

        return audio_info

    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
        return None

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

                    audio_info = get_audio_info(audio_file, debug=False)
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
    # batch_process_audio(base_path)
    # 示例
    get_audio_info("./陈奕迅 - 孤勇者.flac")
