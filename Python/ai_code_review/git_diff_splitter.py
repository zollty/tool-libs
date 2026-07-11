# 如果代码提交信息的总长度为n，长度截断的参考阈值为k（只是参考，不是绝对，
# 每个分段必须包含一个或者多个以“diff --git”开头的完整的代码diff信息，不能一个diff信息从中间截断），
# 所以把n以k长度为参考值拆成几段（但是不能从任意位置截断，应该从以截断处为基准行的前面寻找最近的以“diff --git”开头的行，
# 以那一行的前一行末尾位置为真正的截断点。然后以第1个截断点+1为开始位置，按照这个算法依次再寻找第2、3、4……截断点）。
# 最后，全部截断完之后，需要特殊处理一下，判断拆分后得到的最后两段，如果最后一段长度不足k/4，
# 则将最后两段合并后取长度的平均值为新的k值，以这个k值对最后合并的两段重新进行拆分。
# ------------------
# 有两种特殊情况需要考虑一下，第一是，第一段的起始点一定是从0开始到离k前面最近的匹配点，
# 如果没有匹配点，则直接结束程序，返回空。第二是，如果以k为阈值寻找第2个截断点时，
# 发现往前搜索到的匹配点位置跟前一次寻找截断点时搜索到的匹配点是同一个，说明以匹配点为开始往后长度为k的位置，
# 都还没有出现第二个匹配点，这时应该往后推移k的位置直到字符串结束或者找到新的匹配点。
class GitDiffSplitter:
    def __init__(self, git_diff_text, threshold_k=4000):
        """
        初始化Git差异分割器

        Args:
            git_diff_text (str): git diff输出的完整文本
            threshold_k (int): 长度截断的参考阈值
        """
        self.git_diff_text = git_diff_text
        self.threshold_k = threshold_k
        self.lines = git_diff_text.split('\n')
        # 计算每行的起始位置
        self.line_starts = []
        pos = 0
        for line in self.lines:
            self.line_starts.append(pos)
            pos += len(line) + 1  # +1 for the newline character

    def find_all_diff_positions(self):
        """找到所有diff --git行的起始位置（只在行首匹配）"""
        diff_positions = []
        for i, line in enumerate(self.lines):
            if line.startswith("diff --git"):
                diff_positions.append(self.line_starts[i])
        return diff_positions

    def split_large_diff(self):
        """如果 git_diff_text 超过 max_length，按换行符截断为多个片段"""

        if len(self.git_diff_text) <= self.threshold_k:
            return [self.git_diff_text]  # 未超限，直接返回

        parts = self.git_diff_text.split("\n", 1)
        first_line = parts[0]
        content = parts[1]

        chunks = []
        current_chunk = [first_line]
        current_length = 0

        # 按行分割并处理
        for line in content.splitlines(keepends=True):  # keepends=True 保留换行符
            line_length = len(line)

            # 如果当前行会导致片段超限，先保存当前块
            if current_length + line_length > self.threshold_k:
                chunks.append("".join(current_chunk))
                current_chunk = [first_line]
                current_length = 0

            current_chunk.append(line)
            current_length += line_length

        # 添加最后一个块
        if current_chunk:
            chunks.append("".join(current_chunk))
        return chunks

    def split_git_diff(self):
        """
        分割Git差异文本

        Returns:
            list: 分割后的文本片段列表
        """
        # 找到所有diff位置
        diff_positions = self.find_all_diff_positions()

        # 特殊情况1: 没有diff --git的情况 - 直接返回空
        if not diff_positions:
            return []

        # 特殊情况2: 只有一个diff --git的情况 - 直接返回整个文本
        if len(diff_positions) == 1:
            return self.split_large_diff()

        segments = []
        current_pos = 0
        k = self.threshold_k

        # 第一阶段: 按照阈值k进行分割
        while current_pos < len(self.git_diff_text):
            # 计算目标结束位置
            target_end = current_pos + k

            # 如果目标结束位置已经超过文本长度，添加剩余部分并退出
            if target_end >= len(self.git_diff_text):
                segment = self.git_diff_text[current_pos:]
                if segment:
                    segments.append(segment)
                break

            # 找到在目标结束位置之前的所有diff位置
            candidate_positions = [pos for pos in diff_positions if current_pos < pos <= target_end]

            # 如果没有找到候选位置，寻找下一个可用的diff位置
            if not candidate_positions:
                # 寻找下一个diff位置（即使它超出了目标范围）
                next_diff_positions = [pos for pos in diff_positions if pos > current_pos]
                if not next_diff_positions:
                    # 没有更多diff位置，添加剩余部分并退出
                    segment = self.git_diff_text[current_pos:]
                    if segment:
                        segments.append(segment)
                    break

                # 使用下一个diff位置
                candidate = next_diff_positions[0]
            else:
                # 使用最接近目标结束位置的候选
                candidate = candidate_positions[-1]

            # 找到该diff行的前一行的末尾作为分割点
            # 我们需要找到这个diff行之前的一行的结束位置
            candidate_line_index = self.line_starts.index(candidate)
            if candidate_line_index > 0:
                # 前一行结束位置是当前行的开始位置减1
                prev_line_end = candidate - 1
            else:
                # 如果是第一行，没有前一行，直接使用当前位置
                prev_line_end = current_pos

            # 确保分割点不小于当前位置
            split_point = max(current_pos, prev_line_end + 1)

            # 如果分割点等于当前位置，说明无法分割，直接使用目标结束位置
            if split_point == current_pos:
                split_point = target_end

            segment = self.git_diff_text[current_pos:split_point]
            segments.append(segment)
            current_pos = split_point

        # 第二阶段：处理最后两段
        if len(segments) >= 2:
            last_segment = segments[-1]
            second_last_segment = segments[-2]

            # 如果最后一段长度不足k/4，则合并最后两段
            if len(last_segment) < k / 4:
                combined_segment = second_last_segment + last_segment
                segments = segments[:-2]
                segments.append(combined_segment)

        return segments

    def print_segments_info(self, segments):
        """打印分割段的信息"""
        print(f"原始文本长度: {len(self.git_diff_text)}")
        print(f"参考阈值 k: {self.threshold_k}")
        print(f"分割段数: {len(segments)}")
        print("-" * 50)

        for i, segment in enumerate(segments, 1):
            print(f"段 {i}: 长度 = {len(segment)}")
            # 显示每段的前几行作为预览
            preview_lines = segment.split('\n')[:3]
            preview = '\n'.join(preview_lines)
            if len(segment.split('\n')) > 3:
                preview += "\n..."
            print(f"预览:\n{segment}")
            print("-" * 30)


def split_git_diff_text(git_diff_text, threshold_k=4000):
    """
    便捷函数：直接分割Git差异文本

    Args:
        git_diff_text (str): git diff输出的完整文本
        threshold_k (int): 长度截断的参考阈值

    Returns:
        list: 分割后的文本片段列表
    """
    splitter = GitDiffSplitter(git_diff_text, threshold_k)
    return splitter.split_git_diff()