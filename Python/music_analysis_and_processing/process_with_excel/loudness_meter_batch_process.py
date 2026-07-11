import os
import pandas as pd
import sys

# 获取当前脚本的绝对路径
__current_script_path = os.path.abspath(__file__)
# 将项目根目录添加到sys.path
runtime_root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__current_script_path)))
sys.path.append(runtime_root_dir)

from music_analysis_and_processing.loudness_meter_with_essentia import audio_loudness_meter, compute_loudness_statistics


# 从Excel文件的所有sheet中读取响度数据
def read_loudness_data_from_all_sheets(filename):
    """
    从Excel文件的所有sheet中读取响度数据

    参数:
        filename (str): Excel文件名

    返回:
        dict: 以sheet名为键，响度值列表为值的字典
    """
    try:
        # 读取Excel文件中的所有sheet名称
        sheet_names = pd.ExcelFile(filename).sheet_names

        # 存储每个sheet的响度数据
        sheet_data = {}

        # 遍历每个sheet
        for sheet_name in sheet_names:
            # 读取特定sheet
            df = pd.read_excel(filename, sheet_name=sheet_name)

            # 检查是否存在"响度"列
            if "GAIN" in df.columns:
                gain_values = pd.to_numeric(df["GAIN"], errors='coerce').dropna().tolist()
                sheet_data[sheet_name] = {
                    "playlist": df["歌单"].tolist(),
                    "song_name": df["歌曲名"].tolist(),
                    "songer": df["歌手"].tolist(),
                    "gain_values": gain_values,
                }
            else:
                print(f"Sheet '{sheet_name}' 中未找到'响度'列")

        return sheet_data

    except FileNotFoundError:
        print(f"文件 {filename} 未找到")
        return {}
    except Exception as e:
        print(f"读取Excel文件时出错: {e}")
        return {}


if __name__ == "__main__":
    import time
    excel_file_path = "./output4.xlsx"
    # 从Excel文件的所有sheet读取响度数据
    all_sheet_data = read_loudness_data_from_all_sheets(excel_file_path)

    # base_path = "/mnt/g/__SYNC4/music/"
    base_path = "/mnt/g/__SYNC4/output/"

    sample_rate = 44100
    hop_size = 1024 / 44100  # 默认为0.1
    start_at_zero = True  # 默认为False
    low_thresh, high_thresh = -15, -12

    if all_sheet_data:
        flag = False
        # 处理每个sheet的数据
        for sheet_name, obj in all_sheet_data.items():
            base_value = 0 - int(sheet_name.split("+")[1])
            playlist_dir = sheet_name.split("+")[0]
            print(f"\n{'=' * 50}")
            print(f"处理 Sheet: {sheet_name} 》》 base_value: {base_value}")
            print(f"{'=' * 50}")
            print("歌单:", obj["playlist"])
            print("歌曲名:", obj["song_name"])
            print("歌手:", obj["songer"])
            print("原始值列表:", obj["gain_values"])
            compensated_values = []
            title = f"歌单, 整体响度, 获得增益, 响度范围, 瞬时响度标准差, 瞬时响度变异系数, 歌曲名, 歌手"
            print(title)
            for i, playlist in enumerate(obj["playlist"]):
                songer = str(obj["songer"][i])
                song_name = str(obj["song_name"][i])
                gain_value = obj["gain_values"][i]
                # 处理文件名
                file_name = playlist_dir + "/" + songer + " - " + song_name
                idx = f"{i + 1:03d}_"
                indexed_file_name = playlist_dir + "/" + idx + songer + " - " + song_name
                if os.path.isfile(base_path + file_name + ".flac"):
                    file_name += ".flac"
                    indexed_file_name += ".flac"
                elif os.path.isfile(base_path + file_name + ".mp3"):
                    file_name += ".mp3"
                    indexed_file_name += ".mp3"
                else:
                    print(f"{file_name} 文件不存在!!")
                    continue

                try:
                    if song_name == "牵牛花":
                        flag = True
                    if not flag:
                        continue

                    audio_file = base_path + file_name
                    # output_full_path = output_path + "/" + playlist_dir

                    result = audio_loudness_meter(audio_file, sample_rate, hop_size, start_at_zero)
                    stats = compute_loudness_statistics(result)

                    # print_with_csv(stats)
                    row = f"{playlist}, {stats['integrated']:.1f}, {gain_value:.1f}, {stats['lra']:.1f}, {stats['momentary_std']:.1f}, {stats['momentary_cv']:.1f}%, {song_name}, \"{songer}\""
                    print(row)
                    # os.rename(audio_file, base_path + indexed_file_name)
                    # 显式更新文件的访问时间和修改时间为当前时间
                    current_time = time.time()
                    os.utime(audio_file, (current_time, current_time))

                except Exception as e:
                    print(f"处理{file_name}时出错: {e}")
