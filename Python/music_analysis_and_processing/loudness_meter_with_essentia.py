import numpy as np
import os
import essentia.standard as es
from essentia.standard import MetadataReader


def audio_loudness_meter(audio_file_path, sample_rate=44100, hop_size=0.1, start_at_zero=False):
    """
    LoudnessEBUR128 requires stereo立体声 in 44100 Hz sample rate
    :param audio_vector_stereo_sample: VECTOR_STEREOSAMPLE 格式的音频数据
    """
    # 1. 计算音频总长度
    # 使用MetadataReader避免加载整个音频
    metadata = MetadataReader(filename=audio_file_path)()
    # print(metadata)
    total_duration = metadata[8]  # 音频总时长(秒)

    # 2. 设置裁剪参数
    start_time = 5
    skip_end = 10
    SEGMENT_LENGTH = total_duration - skip_end if total_duration > start_time + skip_end else total_duration

    # 加载音频
    # LoudnessEBUR128 requires stereo立体声 in 44100 Hz sample rate
    audio, _, _, _, _, _ = es.AudioLoader(filename=audio_file_path)()
    audio_stereo = es.StereoTrimmer(startTime=start_time, endTime=SEGMENT_LENGTH)(audio)
    # audio = MonoLoader(filename=filename, sampleRate=sample_rate)()
    # audio_stereo = StereoMuxer()(audio, audio)  # 单声道转立体声

    # 创建算法实例
    loudness = es.LoudnessEBUR128(
        sampleRate=sample_rate,
        hopSize=hop_size,
        startAtZero=start_at_zero
    )

    # 计算响度指标
    momentary, short_term, integrated, lra = loudness(audio_stereo)

    # 使用完 audio 后可以手动设为 None 或 del
    del audio

    return {
        'integrated': integrated,
        'lra': lra,
        'momentary': momentary,
        'short_term': short_term
    }


def compute_loudness_statistics(results):
    """计算详细响度统计信息"""
    # 计算样本总数用于比例计算
    momentary_total = len(results['momentary'])
    momentary_mean = np.mean(results['momentary'])
    momentary_std = np.std(results['momentary'])

    # 计算变异系数 (Coefficient of Variation, CV)
    # CV = (标准差 / 平均值) * 100
    momentary_cv = (momentary_std / abs(momentary_mean)) * 100 if momentary_mean != 0 else 0
    stats = {
        "integrated": results['integrated'],
        "lra": results['lra'],
        # 瞬时时长统计
        "momentary_mean": momentary_mean,
        "momentary_std": momentary_std,  # 标准差
        "momentary_cv": momentary_cv,  # 变异系数
    }
    return stats


def print_loudness_statistics(stats, low_thresh=-14, high_thresh=-10):
    """以结构化格式打印响度统计信息"""
    # 1. 整体响度统计
    print("=" * 50)
    print("📊 整体响度统计".center(45))
    print("-" * 50)
    print(f"• 综合响度 (Integrated): {stats['integrated']:.1f} LUFS")
    print(f"• 响度范围 (LRA): {stats['lra']:.1f} LU")

    # 2. 瞬时时长统计
    print("\n" + "=" * 50)
    print("⏱️ 瞬时响度 (Momentary (400ms))统计".center(45))
    print("-" * 50)
    print(f"• 平均值: {stats['momentary_mean']:.1f} LUFS")
    print(f"• 标准差: {stats['momentary_std']:.1f}")
    print(f"• 变异系数(CV): {stats['momentary_cv']:.1f}%")


def test(audio_file_path='F.I.R.飞儿乐团 - 雨樱花.flac'):
    sample_rate = 44100
    hop_size = 1024 / 44100  # (0.023) 默认为0.1
    start_at_zero = True  # 默认为False
    low_thresh, high_thresh = -15, -12

    result = audio_loudness_meter(audio_file_path, sample_rate, hop_size, start_at_zero)
    stats = compute_loudness_statistics(result)
    print_loudness_statistics(stats, low_thresh, high_thresh)


if __name__ == '__main__':
    # 使用示例
    test('陈红&景岗山 - 好年头好兆头.mp3')
    test('蔡淳佳 - 依恋.mp3')
    test('汪峰 - 光明.flac')
    test('信乐团 - 海阔天空.flac')
    test('张靓颖 - 天下无双.flac')
    test('韦唯 - 爱的奉献.flac')
    test('周杰伦 - 退后.flac')
