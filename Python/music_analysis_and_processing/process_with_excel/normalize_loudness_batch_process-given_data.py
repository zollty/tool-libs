import os
import pandas as pd
import sys

# 获取当前脚本的绝对路径
__current_script_path = os.path.abspath(__file__)
# 将项目根目录添加到sys.path
runtime_root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__current_script_path)))
sys.path.append(runtime_root_dir)

from music_analysis_and_processing.normalize_loudness import normalize_loudness

given_data_audio = """S3-Gentle/鲸鱼马戏团 - 落雨.flac
S3-Gentle/Della - 春风微风.flac
S3-Gentle/Della - 水蓝的梦.mp3
S3-Gentle/鲸鱼马戏团 - 烟火.flac
S3-Gentle/Andrew Fitzgerald - In the Distance.mp3
S3-Gentle/摇篮曲月亮摇篮曲河 - 勃拉姆斯摇篮曲.flac
S3-Gentle/Della - 水纹.flac
S3-Gentle/李娜 - 好人一生平安.flac
S3-Gentle/群星 - 竹枝词.flac
S3-Gentle/左小祖咒 - 决定住在汉庭酒店.flac
S3-Gentle/鲸鱼马戏团 - 风.flac
S3-Gentle/音乐治疗 - Ocean Blue.mp3
S3-Gentle/清生 - 清晨（班得瑞）.flac
S3-Gentle/Della - 飞舞之叶.mp3
S3-Gentle/CC Christy - 茉莉花 (古筝独奏).flac
S3-Gentle/元若蓝 - 半情歌.flac
S3-Gentle/羽肿 - Windy Hill.flac
S3-Gentle/Della - 小春气息.mp3
S3-Gentle/Dan Gibson - Nature's Path.flac
S3-Gentle/于秋璇 - 汉宫秋月.flac
S3-Gentle/林海 - 琵琶语.flac
S3-Gentle/天易音乐 - 琵琶语 （纯音乐）.flac
S3-Gentle/冯曦妤,陈永健 - 你的螃蟹去哪了.flac
S3-Gentle/水木年华 - 完美世界.mp3
S3-Gentle/张小斐 - 萱草花.flac
S3-Gentle/Della - 水中月.flac
S3-Gentle/The Milk Carton Kids - Michigan.flac
S3-Gentle/舒伯特摇篮曲 - 舒伯特摇篮曲.flac
S3-Gentle/蒋倩 - 水姻缘.flac
S3-Gentle/林诗影 - 紫竹调（徵音入心 养心安神）.flac
S3-Gentle/范晓萱 - 氧气(O1 缺氧版).flac
S3-Gentle/湖北编钟乐团 - 春江花月夜.flac
S3-Gentle/黑鸭子 - 听妈妈讲那过去的事情.flac
S3-Gentle/Dan Gibson - Morning Song.flac
S3-Gentle/姜苏,柏菲音乐 - 女儿情.flac
S3-Gentle/鲍比达 - 乡愁.mp3
S3-Gentle/李云迪 - 浏阳河.flac
S3-Gentle/Della - 晨渐.flac
S3-Gentle/Yiruma - 雨的印记.flac
S3-Gentle/中央民族乐团 - 梅花三弄.flac
S3-Gentle/裘海正 - 纠缠.mp3
S3-Gentle/群星 - 楚商.flac
S3-Gentle/吴丹古筝 - 琵琶语 吴丹古筝版.flac
S3-Gentle/罗大佑 - 追梦人.mp3
S3-Gentle/蔡琴 - 渡口.flac
S3-Gentle/华夏民族乐团 - 高山流水 (古筝独奏).flac
S3-Gentle/Richard Clayderman - 秋日私语.flac
S3-Gentle/黑鸭子组合 - 今天是你的生日.mp3
S3-Gentle/清生 - 安妮的仙境（班得瑞）.flac
S3-Gentle/Bandari - Snowdreams.flac
S3-Gentle/黑鸭子 - 让我们荡起双桨.flac
S3-Gentle/吴静 - 女儿情.flac
S3-Gentle/甘萍 - 潮湿的心.flac
S3-Gentle/黄莺莺 - 哭砂.flac
S3-Gentle/女声合唱 - 送别.flac
S3-Gentle/墨明棋妙 河图 陪人听海 乍雨初晴 墨虎蔷薇 - 墨-雨碎江南.印象.mp3
S3-Gentle/邓丽君 - 千言万语.flac
S3-Gentle/天易音乐 - 风之谷 钢琴.flac
S3-Gentle/星潮 - 亲爱的x.flac
S3-Gentle/dylanf - 催眠曲5分钟入睡，治愈重度失眠，灵魂放松轻音乐.flac
S3-Gentle/石进 - 夜的钢琴曲(五).flac
S3-Gentle/Kevin Kern - Sundial Dreams.flac
S3-Gentle/宋冬野 - 斑马，斑马.flac
S3-Gentle/卢冠廷,莫文蔚 - 一生所爱.flac"""


given_data_loudness = """-20.8
-18.4
-19.2
-21.2
-21.7
-21.9
-20.1
-21.8
-21.5
-20.4
-23.4
-21.6
-20.5
-21.8
-21.9
-17.3
-17.3
-18.8
-20.6
-21.1
-20.5
-23.1
-22.3
-21.9
-20.3
-20.5
-19
-20.5
-17.6
-21.9
-20.5
-22.9
-18.7
-22
-20
-22
-23.1
-20.1
-21.9
-21.9
-20.7
-22.3
-19
-22.6
-22.3
-22.6
-21.4
-21.1
-21.5
-21.1
-19.8
-21.1
-17.1
-20.7
-19.8
-21.9
-20.6
-18.4
-21.8
-21
-19.2
-20.9
-21.4
-20.3"""


def main():
    base_path = "/mnt/g/__SYNC4/output/"
    paths = given_data_audio.split("\n")
    loudnesses = given_data_loudness.split("\n")

    song_list = []

    min_ = -21
    max_ = -18
    base = -20

    def calculate_gain(loudness_val):
        if loudness_val <= min_:
            return min_
        gap = base - loudness_val
        result = loudness_val + (gap / 2)
        if result > max_:
            return max_
        return result


    assert abs(calculate_gain(-22) - -21) <= 0.01
    assert abs(calculate_gain(-21) - -21) <= 0.01
    assert abs(calculate_gain(-20.6) - -20.3) <= 0.01
    assert abs(calculate_gain(-18) - -19) <= 0.01
    assert abs(calculate_gain(-17) - -18.5) <= 0.01
    assert abs(calculate_gain(-16) - -18) <= 0.01

    for i in range(len(paths)):
        loudness = float(loudnesses[i])
        song_list.append({
            "path": paths[i],
            "loudness": loudness,
            "gain": calculate_gain(loudness) - loudness
        })

    output_path = "/mnt/g/__SYNC4/output/tmp/"

    # 处理每个sheet的数据
    for song in song_list:
        print("歌曲名:", song["path"])
        print("原始值列表:", song["loudness"])
        try:
            file_full_path = base_path + song["path"]
            normalize_loudness(file_full_path, song["gain"], output_dir=output_path)
        except Exception as e:
            print(f'处理{song["path"]}时出错: {e}')



if __name__ == "__main__":
    base_path = "/mnt/g/__SYNC4/output/"
    paths = given_data_audio.split("\n")
    loudnesses = given_data_loudness.split("\n")

    song_list = []

    min_ = -23
    max_ = -20
    base = -22

    def calculate_gain(loudness_val):
        if loudness_val <= min_:
            return min_
        gap = base - loudness_val
        result = loudness_val + (gap / 2)
        if result > max_:
            return max_
        return result

    for i in range(len(paths)):
        loudness = float(loudnesses[i])
        song = {
            "path": paths[i],
            "loudness": loudness,
            "gain": calculate_gain(loudness) - loudness
        }
        print("歌曲名:", song["path"])
        print("\t原始值列表:", song["loudness"])
        print("\t增益值:", song["gain"])
        print("\t增益后值:", song["loudness"] + song["gain"])
        song_list.append(song)

    output_path = "/mnt/g/__SYNC4/output/tmp2/"

    # 处理每个sheet的数据
    for song in song_list:
        print("歌曲名:", song["path"])
        print("原始值列表:", song["loudness"])
        try:
            file_full_path = base_path + song["path"]
            normalize_loudness(file_full_path, song["gain"], output_dir=output_path)
        except Exception as e:
            print(f'处理{song["path"]}时出错: {e}')