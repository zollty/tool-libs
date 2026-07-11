import os
from mutagen import File
from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from mutagen.wave import WAVE

def copy_audio_metadata(src_path, dest_path):
    """
    复制音频文件的元数据（标签、专辑封面等）到新文件
    支持格式：MP3, FLAC, WAV
    """
    src_ext = os.path.splitext(src_path)[1].lower()

    # 使用 pydub 只读取文件信息，不加载音频数据
    # from pydub.utils import mediainfo
    #
    # # 在函数开始处添加
    # media_info = mediainfo(src_path)
    # print(media_info)
    try:
        # 根据文件类型处理元数据
        if src_ext == '.mp3':
            # MP3文件
            src_tags = MP3(src_path)
            dest_tags = MP3(dest_path)

            # 复制所有标签
            for tag in src_tags.keys():
                dest_tags[tag] = src_tags[tag]

            dest_tags.save()

        elif src_ext == '.flac':
            # FLAC文件
            src_tags = FLAC(src_path)
            dest_tags = FLAC(dest_path)

            # 复制所有标签
            for tag in src_tags.keys():
                dest_tags[tag] = src_tags[tag]

            # 复制专辑封面
            if src_tags.pictures:
                dest_tags.clear_pictures()
                for picture in src_tags.pictures:
                    dest_tags.add_picture(picture)

            dest_tags.save()

        elif src_ext == '.wav':
            # WAV文件 - 使用更简单的方法
            try:
                # 直接复制所有可识别的元数据
                src_metadata = File(src_path, easy=True)
                dest_metadata = File(dest_path, easy=True)
                # 复制所有标签
                if src_metadata.tags:
                    dest_metadata.tags = src_metadata.tags
                    dest_metadata.save()

                # 尝试复制专辑封面（如果存在）
                if hasattr(src_metadata, 'pictures'):
                    if dest_metadata.pictures:
                        dest_metadata.delete()
                    for pic in src_metadata.pictures:
                        dest_metadata.add_picture(pic)
                    dest_metadata.save()

                # 复制INFO标签（RIFF INFO）
                # 在Mutagen中，INFO标签存储在info属性中，但Mutagen目前没有提供直接访问INFO标签的方法
                # 所以这里我们无法直接复制INFO标签，实际上，Mutagen的WAVE类主要处理ID3标签。
                # 因此，对于INFO标签，我们可能需要使用其他方法，或者暂时放弃复制。
                # 由于Mutagen对WAV的INFO标签支持有限，我们这里只复制ID3标签。
                # 对于需要复制INFO标签的情况，可能需要使用其他工具，或者接受这个限制。
                # 打印警告
                if hasattr(src_metadata, 'info') and src_metadata.info:
                    print("警告：WAV文件的INFO标签（RIFF INFO）无法通过Mutagen复制，将被忽略。")
                    # ffmetadata = extract_metadata_with_ffmpeg(src_path)
                    # apply_metadata_with_ffmpeg(dest_path, ffmetadata)

                return True
            except Exception as e:
                print(f"WAV元数据复制失败: {str(e)}")
                return False

        return True
    except Exception as e:
        print(f"警告：无法复制元数据 - {str(e)}")
        return False