import os
import numpy as np
import essentia.standard as ess
from pydub import AudioSegment
import shutil

from music_analysis_and_processing.copy_audio_metadata import copy_audio_metadata
from music_analysis_and_processing.get_audio_info_mutagen import get_audio_info


def normalize_loudness(input_file, target_gain, output_dir='./normalized_out'):
    """
    使用Essentia进行歌曲音频响度归一化，注意，我们的歌曲文件都是固定的参数：
    声道数(channels): 2 (固定)
    样本宽度(sample_width): 2（PCM_16）或者3（PCM_24）

    参数:
    input_file: 输入音频文件路径
    target_gain: 目标增益值(dB)
    output_dir: 输出目录
    sample_width: 样本宽度，支持2或3字节
    """
    # 检查文件格式
    ext = os.path.splitext(input_file)[1].lower()
    if ext not in ['.flac', '.mp3', '.wav']:
        raise ValueError("不支持的音频格式，仅支持 FLAC/MP3/WAV")

    # 创建输出目录
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 构造输出文件路径
    filename = os.path.basename(input_file)
    # name, ext = os.path.splitext(filename)
    output_file = os.path.join(output_dir, filename)
    output_ext = os.path.splitext(output_file)[1].lstrip('.').lower()
    if abs(target_gain) < 0.1:
        shutil.copy2(input_file, output_file)
        print(f"target_gain={target_gain}，跳过处理，文件已保存: {output_file}")
        return

    # 1. 计算音频总长度
    # 使用MetadataReader避免加载整个音频
    audio_info = get_audio_info(input_file, debug=False)
    # metadata[9] 通常包含比特率信息（根据 Essentia 文档）
    original_bitrate = audio_info["bitrate"]
    number_channels = audio_info["channels"]
    total_duration = audio_info["duration"]
    sample_rate = audio_info["samplerate"]
    sample_width = audio_info["sample_width"]
    # 检查样本宽度
    if sample_width not in [2, 3]:
        raise ValueError("样本宽度只支持2或3")
    if not original_bitrate or original_bitrate == 0:
        raise ValueError("无法获取音频比特率，请检查输入文件")
    if number_channels != 2:
        raise ValueError("声道数不为2，请检查输入文件")

    # 使用Essentia加载音频文件，得到VECTOR_STEREOSAMPLE格式的音频数据
    # 加载音频（使用指定的采样率）
    loader = ess.AudioLoader(filename=input_file)

    audio, _, _, _, _, _ = loader()

    # 计算增益
    gain_linear = 10 ** (target_gain / 20)
    # 应用增益
    processed_samples = audio * gain_linear

    # 使用PyDub保存处理后的音频
    # 根据指定的sample_width确定样本范围
    if sample_width == 2:
        # 16位样本范围在-32768到32767
        processed_audio = (processed_samples * 32767).astype(np.int16).tobytes()
    else:  # sample_width == 3
        # 24位样本范围在-8388608到8388607
        processed_audio = (processed_samples * 8388607).astype(np.int32).tobytes()
        # 只取每个样本的低3个字节
        processed_audio = b''.join(processed_audio[i:i + 3] for i in range(0, len(processed_audio), 4))

    # 创建新的AudioSegment
    processed_segment = AudioSegment(
        processed_audio,
        frame_rate=sample_rate,
        sample_width=sample_width,
        channels=number_channels
    )

    # 保持原始MP3比特率
    if output_ext == 'mp3':
        # 使用接近的标准化比特率
        standard_bitrates = [64, 96, 128, 160, 192, 224, 256, 320]
        closest_bitrate = min(standard_bitrates, key=lambda x: abs(x - original_bitrate))
        processed_segment.export(output_file, format=output_ext, bitrate=f"{closest_bitrate}k")
    elif output_ext == 'flac':
        flac_parameters = [
            # 压缩只影响文件大小及比特率，但FLAC作为无损格式，音质始终与原始文件一致，跟压缩等级无关，参见ffmpeg文档
            "-compression_level", "0",  # 0-最低压缩级别，最高为8，为0会禁用压缩算法、使输出文件尽可能接近原始WAV的大小
            # "-prediction_order_method", " Levinson",  # 预测方法
            # "-min_prediction_order", "1",  # 最小预测阶数
            # "-max_prediction_order", "12"  # 最大预测阶数
        ]
        processed_segment.export(output_file, format=output_ext, parameters=flac_parameters)
    else:
        processed_segment.export(output_file, format=output_ext)

    # print(f"原始响度: {measured_loudness:.2f} LUFS")
    # print(f"目标响度: {target_lufs:.2f} LUFS")
    # print(f"处理后响度: {new_loudness:.2f} LUFS")
    print(f"文件已保存: {output_file}")

    # 复制原始文件的元数据到新文件
    try:
        copy_audio_metadata(input_file, output_file)
    except Exception as e:
        print(f"处理元数据时出错: {e}")


if __name__ == "__main__":
    normalize_loudness('./陈奕迅 - 孤勇者.flac', -3.6)
    # normalize_loudness('./蔡淳佳 - 依恋.mp3')
    # normalize_loudness('./陈红&景岗山 - 好年头好兆头.wav')
    # normalize_loudness('./汪峰 - 春天里.mp3')
