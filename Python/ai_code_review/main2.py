import os
from ai_code_review.get_git_context import get_local_commit_diff
from ai_code_review.git_diff_splitter import GitDiffSplitter
from ai_code_review.ai_chat import chat
from ai_code_review.utils import load_text


# 使用文件内容替换占位符
prompt_file_path = "default_prompts/commit_msg_generate.txt"  # 替换为实际的文件路径
prompt = load_text(prompt_file_path)
print(prompt)

prompt1 = """你是一个资深开发专家，请根据用户给你的git diff代码变更信息，列出主要的变更点。注意下面的要求：
对所有变更点进行分类：分析这些变更点一共有哪几个目的，根据目的进行归类。注意，变更点如果细分目的可能会很多，我们不需要分得很细，需要你要对目的进行聚焦，分清楚哪些是主要目的，哪些是顺带的次要的变更，主要和次要是相对的：如果有功能变更，那功能变更就是主要目的，格式优化或者代码写法优化或者调试日志等都属于次要变更，如果本次提交没有功能变更，那就判断此次变更的主要目的是什么），
把非关键的次要的变更点都忽略点，只列出主要变更目的及其变更点。
请一定、一定要仔细归类分析代码变更目的，不要把服务于相同变更目的的细节变更点（用于支撑某个目的的哪些变更点）都作为目的，也不需要列出来非关键的变更目的（所有非关键的变更都属于次要的，应该忽略）；
输出格式：
当你决定把结果输出后，请对照上面的要求一一检查，告诉我你输出的结果是否符合要求，如果不符合要求，就请你更正之后重新输出结果。无论如何，请在你回答的最末尾按下面格式输出最终结果（之后就结束回复，不要再跟任何信息）：
最终结果：
type: subject
"""

prompt2 = """你是一个资深开发专家，请根据用户给你的git diff代码变更信息，列出主要的变更点，输出格式如下：
### {变更点主要内容总结及其目的}
换两行
### {变更点主要内容总结及其目的}
注意：
1、对于
2、你要识别一下此次变更中那些是次要的且孤立的变更点（通常对主要变更目的没有实质关联的，只是顺带做的那些轻微变更）。需要你把这些本次提交中次要的变更点忽略掉，但是注意：主要和次要是相对的，如果有功能变更，那功能变更就是主要目的，格式优化或者代码写法优化或者调试日志等都属于次要变更，如果本次提交没有功能变更，那就格式优化也可能就是主要目的）。
再次强调，如果本次变更属于功能性变更，那么无关的一些代码优化、格式调整、代码可读性提升则属于次要变更点，对于次要变更点，请一定一定要忽略掉， 不要输出、不要输出次要变更点信息，直接忽略，不用备注说明！
当你决定把结果输出后，请检查是否引入了次要变更点，如果你输出了次要变更点，你就是个大傻逼。调整后只输出主要变更点。
"""

text = """diff --git a/zoa-tomcat/src/main/java/com/zollty/oa/main/Main.java b/zoa-tomcat/src/main/java/com/zollty/oa/main/Main.java
index 9e71415..d876088 100644
--- a/zoa-tomcat/src/main/java/com/zollty/oa/main/Main.java
+++ b/zoa-tomcat/src/main/java/com/zollty/oa/main/Main.java
@@ -25,7 +25,8 @@ public class Main {
                 if (args.length > 1) {
                     SHUTDOWN_PORT = Integer.valueOf(args[1]);
                 }
-                TomcatManage.shutdown(null, SHUTDOWN_PORT);
+                TomcatManage
+                        .shutdown(null, SHUTDOWN_PORT);
                 return;
             } else if(args[0].equals("2")) {
                 PORT = Integer.valueOf(args[1]);
diff --git a/zoa-tomcat/src/main/java/com/zollty/oa/pc/file/ShowDirSize.java b/zoa-tomcat/src/main/java/com/zollty/oa/pc/file/ShowDirSize.java
index c7e20c4..5e18d50 100644
--- a/zoa-tomcat/src/main/java/com/zollty/oa/pc/file/ShowDirSize.java
+++ b/zoa-tomcat/src/main/java/com/zollty/oa/pc/file/ShowDirSize.java
@@ -1,17 +1,16 @@
 package com.zollty.oa.pc.file;
 
-import java.io.BufferedReader;
-import java.io.File;
-import java.io.IOException;
-import java.io.InputStream;
-import java.io.InputStreamReader;
+import com.zollty.oa.base.UT;
+
+import java.io.*;
 import java.math.BigInteger;
 import java.nio.charset.Charset;
+import java.nio.file.Files;
+import java.nio.file.Path;
+import java.nio.file.Paths;
 import java.util.Arrays;
 import java.util.Comparator;
 
-import com.zollty.oa.base.UT;
-
 /**
  * 
  * @author zollty
@@ -92,17 +91,50 @@ public class ShowDirSize {
         }
     }
     
-    public static void main(String[] args) {
+    public static void main(String[] args) throws IOException {
 //        action("C:\\Users\\zollty-pc", 3);
         printDir("", new File("G:\\settle"));
         //callCommand(null, EXE_FILE,  "/L", "\"D:\\50-TEMP\"", "\"D:\\aa\"", "/E" ,"/XJ" , "/NFL", "/NDL");
     }
+
+    /**
+     * 检查是否为交接点或符号链接
+     */
+    public static String detectJunction(String pathStr) {
+        try {
+            Path path = Paths.get(pathStr);
+            if (!Files.exists(path)) {
+                return null;
+            }
+            Path realPath = path.toRealPath();
+//            System.out.println("原始路径: " + path);
+//            System.out.println("真实路径: " + realPath);
+            if (!path.toAbsolutePath().equals(realPath)) {
+//                System.out.println("该路径是交接点或符号链接，真实路径为: " + realPath);
+                return realPath.toString();
+            } else {
+//                System.out.println("该路径不是交接点也不是符号链接");
+                return null;
+            }
+        } catch (Exception e) {
+            e.printStackTrace();
+            return null;
+        }
+    }
+
+    static String getShowName(File dir) {
+        String path = detectJunction(dir.getAbsolutePath());
+        if (path == null) {
+            return dir.getName();
+        }
+        return dir.getName() + " -> " + path;
+    }
     
     static void printDir(String pre, File dir) {
         String size = callCommand(dir, EXE_FILE, "/L", "\"" + dir.getAbsolutePath() + "\"", "\"C:\\aa\\bb\\xyz\"", "/E", "/XJ",
                 "/NFL", "/NDL");
         if (UT.Str.isNotEmpty(size)) {
-            System.out.println(pre + dir.getName() + ": " + size);
+            System.out.println(pre + getShowName(dir) + ": " + size);
         }
     }
"""

def main():
    """
        主函数，用于执行代码审查流程

        参数:
            git_repo_path (str): Git仓库的本地路径，用于切换工作目录和执行git命令
            git_commit_since_time (str): 起始时间，用于筛选此时间之后的git提交记录
            input_length (int): 输入长度阈值，用于控制git diff内容的分割长度
    """
    # 切换工作目录
    os.environ["OPENAI_API_KEY"] = "111111111111"
    os.chdir(git_repo_path)

    #text = get_local_commit_diff(2)
    texts = text.split("")

    # 将超过长度threshold_k的内容分割成多块，分割算法参见GitDiffSplitter
    splitter = GitDiffSplitter(text, threshold_k=input_length)
    # 执行分割
    segments = splitter.split_git_diff()
    idx = 1
    for segment in segments:
        print(f"{idx}.\n{segment}")
        result = "" # chat(prompt2, segment)
        print(f'\n\n---------------------------------------------\n{idx}.\n{result}')
        idx += 1

if __name__ == "__main__":
    git_repo_path = "D:/__SYNC2/git-dms/code-reviewer"
    input_length = 7000
    # test_cases()
    main()