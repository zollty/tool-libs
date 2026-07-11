from ai_code_review.git_diff_splitter import GitDiffSplitter

# 测试函数
def test_special_cases():
    """测试特殊情况的函数"""

    # 测试用例1: 没有diff --git的情况
    print("测试用例1: 没有diff --git的情况")
    no_diff_text = "This is a text without any diff --git lines.\n" * 100
    splitter1 = GitDiffSplitter(no_diff_text, threshold_k=500)
    result1 = splitter1.split_git_diff()
    print(f"结果段数: {len(result1)} (期望: 0)")
    print(f"结果: {result1}")
    print()

    # 测试用例2: 只有一个diff --git的情况
    print("测试用例2: 只有一个diff --git的情况")
    few_diff_text = "diff --git a/file1.txt b/file1.txt\n" + "some content\n" * 1000
    splitter2 = GitDiffSplitter(few_diff_text, threshold_k=500)
    result2 = splitter2.split_git_diff()
    print(f"结果段数: {len(result2)} (期望: 1)")
    if result2:
        print(f"第一段长度: {len(result2[0])}")
    print(f"结果: {result2}")
    print()

    # 测试用例3: 正常有多个diff的情况
    print("测试用例3: 正常有多个diff的情况")
    normal_diff_text = "diff --git a/file1.txt b/file1.txt\ncontent1\n" * 5 + \
                       "diff --git a/file2.txt b/file2.txt\ncontent2\n" * 5 + \
                       "diff --git a/file3.txt b/file3.txt\ncontent3\n" * 5
    splitter3 = GitDiffSplitter(normal_diff_text, threshold_k=200)
    result3 = splitter3.split_git_diff()
    print(f"结果段数: {len(result3)}")
    splitter3.print_segments_info(result3)


# 测试用例
def test_cases():
    # 运行测试
    test_special_cases()

    # 示例Git差异文本（这里用简化的示例，实际使用时替换为真实的git diff输出）
    sample_git_diff = """diff --git a/file1.java b/file1.java
index 1234567..890abcd 100644
--- a/file1.java
+++ b/file1.java
@@ -1,5 +1,5 @@
 public class Example {
-    private String oldMethod() {
-        return "old";
+    private String newMethod() {
+        return "new";
     }
 }
diff --git a/file2.java b/file2.java
index abcdefg..hijklmn 100644
--- a/file2.java
+++ b/file2.java
@@ -1,3 +1,3 @@
 public class Another {
-    // old comment
+    // new comment
+    // new comment
+    // new comment
+    // new comment
+    // new comment
+    // new comment
+    // new comment
+    // new comment
+    // new comment
+    // new comment
+    // new comment
+    // new comment
+    // new comment
+    // new comment
+    // new comment
+    // new comment
+    // new comment
+    // new comment
+    // new comment
+    // new comment
+    // new comment
+    // new comment
+    // new comment
+    // new comment
+    // new comment
+    // new comment
+    // new comment
+    // new comment
+    // new comment
+    // new comment
 }
"""

    # 创建分割器实例
    splitter = GitDiffSplitter(sample_git_diff * 10, threshold_k=500)

    # 执行分割
    segments = splitter.split_git_diff()

    # 打印分割结果信息
    splitter.print_segments_info(segments)

    # -------------------------------------
    # --------------真实测试用例-------------
    # -------------------------------------
    text3 = """commit 2ad5edd52de38e4a87e9067296546cee12c2fb50
Author: 202217799-jiangruixin <202217799@any3.com>
Date:   Fri Aug 22 10:25:25 2025 +0800

    feat:<E5><B8><81><E7><A7><8D><E4><B8><8E><E5><B7><A5><E5><8D><95>

diff --git a/dms.services/aftersales-service/src/main/java/com/gaci/dms/aftersales/service/dto/rule/TtAsWrRulemappingDTO.java b/dms.services/aftersales-service/src/main/java/com/gaci/dms/aftersales/service/dto/rule/TtAsWrRulemappingDTO.java
index c4f01bd85f..d490da235f 100644
--- a/dms.services/aftersales-service/src/main/java/com/gaci/dms/aftersales/service/dto/rule/TtAsWrRulemappingDTO.java
+++ b/dms.services/aftersales-service/src/main/java/com/gaci/dms/aftersales/service/dto/rule/TtAsWrRulemappingDTO.java
@@ -155,4 +155,7 @@ public class TtAsWrRulemappingDTO extends DMSBaseDTO implements Serializable {

     /** <E5><87><A1><E6><98><AF> dbSupport <E5><8F><98><E9><87><8F><E9><83><BD><E6><98><AF><E4><B8><BA><E4><BA><86><E6><8B><86><E5><88><86><E8><B7><A8><E5>
<BA><93>SQL<E7><AD><80><89><E7><9A><84><EF><BC><8C><E5><85><B6><E4><BB><96><E4><B8><9A><E5><8A><A1><E8><AF><B7><E5><8B><BF><E4><BD><BF><E7><94><A8> -- <E5>
<B8><81><E7><A7><8D> <E7><9A><84> tc_code.id */
     private List<Integer> dbSupportCurrencyTypes;
+
+    /** <E5><87><A1><E6><98><AF> dbSupport <E5><8F><98><E9><87><8F><E9><83><BD><E6><98><AF><E4><B8><BA><E4><BA><86><E6><8B><86><E5><88><86><E8><B7><A8><E5>
<BA><93>SQL<E7><AD><80><89><E7><9A><84><EF><BC><8C><E5><85><B6><E4><BB><96><E4><B8><9A><E5><8A><A1><E8><AF><B7><E5><8B><BF><E4><BD><BF><E7><94><A8> -- <E5>
<B7><A5><E5><8D><95><E7><B1><BB><E5><9E><8B> <E6><95><B0><E6><8D><AE><E5><AD><97><E5><85><B8>8270 <E7><9A><84> tc_code.id */
+    private List<Integer> dbSupportRoTypes;
 }
diff --git a/dms.services/aftersales-service/src/main/java/com/gaci/dms/aftersales/service/service/impl/rule/TtAsWrRulemappingServiceImpl.java b/dms.services/aftersales-service/src/main/java/com/gaci/dms/aftersales/service/service/impl/rule/TtAsWrRulemappingServiceImpl.java
index 6218645e1f..9bf4b438bf 100644
--- a/dms.services/aftersales-service/src/main/java/com/gaci/dms/aftersales/service/service/impl/rule/TtAsWrRulemappingServiceImpl.java
+++ b/dms.services/aftersales-service/src/main/java/com/gaci/dms/aftersales/service/service/impl/rule/TtAsWrRulemappingServiceImpl.java
             dto.setDbSupportCurrencyTypes(currencyCodeId);

             // <E5><AD><97><E5><85><B8><E8><B7><A8><E5><BA><93><EF><BC><9A><E6><8E><88><E6><9D><83><E9><A1><B9><E5><B7><A5><E5><8D><95><E7><B1><BB><E5><9E>
<8B> , <E8><AF><AD><E8><A8><80><EF><BC><9A><E9><9C><80><E8><A6><81>  10001001 <E8><BF><99><E6><A0><B7><E7><9A><84>
+            List<Integer> roTypeCodeId = dbSupportHelper.getCodeIdByLikeDesc(8270, dto.getSearchRemark(), languageCode);
+            dto.setDbSupportRoTypes(roTypeCodeId);
         }

         IPage<TtAsWrRulemappingVo> poPage = ttAsWrRulemappingMapper.selectRuleMappingPageList(page,dto);
diff --git a/dms.services/aftersales-service/src/main/resources/mybatis/mapper/rule/ttAsWrRulemappingPOMapper.xml b/dms.services/aftersales-service/src/main/esources/mybatis/mapper/rule/ttAsWrRulemappingPOMapper.xml
index cda0fe7051..024c9997b8 100644
--- a/dms.services/aftersales-service/src/main/resources/mybatis/mapper/rule/ttAsWrRulemappingPOMapper.xml
+++ b/dms.services/aftersales-service/src/main/resources/mybatis/mapper/rule/ttAsWrRulemappingPOMapper.xml
@@ -92,6 +92,7 @@
                                         </otherwise>
                                     </choose>
                                          ))
+                <!--
                 or tawrd.currency_type in (select a.CODE_ID from dms_basedata.tc_code a where 1=1 and a.TYPE = 8050
                 <choose>
                     <when test="dto.language == null or dto.language == '' or dto.language == 'zh'">
@@ -118,6 +119,19 @@
                     </otherwise>
                 </choose>
                 )
+                -->
+                <if test="dto.dbSupportCurrencyTypes != null and dto.dbSupportCurrencyTypes.size > 0">
+                    or tawrd.currency_type in
+                    <foreach collection="dto.dbSupportCurrencyTypes" index="index" item="item" separator="," open="(" close=")">
+                        #{item}
+                    </foreach>
+                </if>
+                <if test="dto.dbSupportROTypes != null and dto.dbSupportROTypes.size > 0">
+                    or tawrd.ro_type in
+                    <foreach collection="dto.dbSupportROTypes" index="index" item="item" separator="," open="(" close=")">
+                        #{item}
+                    </foreach>
+                </if>
                 or (tawrd.dealer_type = 12151002 and tawrd.id in (select b.rulemapping_detail_id from  tt_as_wr_rulemapping_dealer b
                                     left join dms_sysmanage.tm_dealer_info tdi ON b.DEALER_ID = tdi.DEALER_ID
                                     where b.IS_DELETED = 0 and (b.DEALER_CODE like CONCAT('%', #{dto.searchRemark}, '%')) or tdi.DEALER_NAME like CONCAT('%' #{dto.searchRemark}, '%'))))
(END)
             dto.setDbSupportCurrencyTypes(currencyCodeId);
             // <E5><AD><97><E5><85><B8><E8><B7><A8><E5><BA><93><EF><BC><9A><E6><8E><88><E6><9D><83><E9><A1><B9><E5><B7><A5><E5><8D><95><E7><B1><BB><E5><9E>

<8B> , <E8><AF><AD><E8><A8><80><EF><BC><9A><E9><9C><80><E8><A6><81>  10001001 <E8><BF><99><E6><A0><B7><E7><9A><84>
+            List<Integer> roTypeCodeId = dbSupportHelper.getCodeIdByLikeDesc(8270, dto.getSearchRemark(), languageCode);
+            dto.setDbSupportRoTypes(roTypeCodeId);
         }

         IPage<TtAsWrRulemappingVo> poPage = ttAsWrRulemappingMapper.selectRuleMappingPageList(page,dto);
diff --git a/dms.services/aftersales-service/src/main/resources/mybatis/mapper/rule/ttAsWrRulemappingPOMapper.xml b/dms.services/aftersales-service/src/main//resources/mybatis/mapper/rule/ttAsWrRulemappingPOMapper.xml
index cda0fe7051..024c9997b8 100644
--- a/dms.services/aftersales-service/src/main/resources/mybatis/mapper/rule/ttAsWrRulemappingPOMapper.xml
+++ b/dms.services/aftersales-service/src/main/resources/mybatis/mapper/rule/ttAsWrRulemappingPOMapper.xml
@@ -92,6 +92,7 @@
                                         </otherwise>
                                     </choose>
                                          ))
+                <!--
                 or tawrd.currency_type in (select a.CODE_ID from dms_basedata.tc_code a where 1=1 and a.TYPE = 8050
                 <choose>
                     <when test="dto.language == null or dto.language == '' or dto.language == 'zh'">
@@ -118,6 +119,19 @@
                     </otherwise>
                 </choose>
                 )
+                -->
+                <if test="dto.dbSupportCurrencyTypes != null and dto.dbSupportCurrencyTypes.size > 0">
+                    or tawrd.currency_type in
+                    <foreach collection="dto.dbSupportCurrencyTypes" index="index" item="item" separator="," open="(" close=")">
+                        #{item}
+                    </foreach>
+                </if>
+                <if test="dto.dbSupportROTypes != null and dto.dbSupportROTypes.size > 0">
+                    or tawrd.ro_type in
+                    <foreach collection="dto.dbSupportROTypes" index="index" item="item" separator="," open="(" close=")">
+                        #{item}
+                    </foreach>
+                </if>
                 or (tawrd.dealer_type = 12151002 and tawrd.id in (select b.rulemapping_detail_id from  tt_as_wr_rulemapping_dealer b
                                     left join dms_sysmanage.tm_dealer_info tdi ON b.DEALER_ID = tdi.DEALER_ID
                                     where b.IS_DELETED = 0 and (b.DEALER_CODE like CONCAT('%', #{dto.searchRemark}, '%')) or tdi.DEALER_NAME like CONCAT('%'', #{dto.searchRemark}, '%'))))
~
(END)
             dto.setDbSupportCurrencyTypes(currencyCodeId);

             // <E5><AD><97><E5><85><B8><E8><B7><A8><E5><BA><93><EF><BC><9A><E6><8E><88><E6><9D><83><E9><A1><B9><E5><B7><A5><E5><8D><95><E7><B1><BB><E5><9E><8B> , <E8><AF><AD><E8><A8><80><EF><BC><9A><E9><9C><80><E8><A6><81>  10001001 <E8><BF><99><E6><A0><B7><E7><9A><84>
+            List<Integer> roTypeCodeId = dbSupportHelper.getCodeIdByLikeDesc(8270, dto.getSearchRemark(), languageCode);
+            dto.setDbSupportRoTypes(roTypeCodeId);
         }

         IPage<TtAsWrRulemappingVo> poPage = ttAsWrRulemappingMapper.selectRuleMappingPageList(page,dto);
diff --git a/dms.services/aftersales-service/src/main/resources/mybatis/mapper/rule/ttAsWrRulemappingPOMapper.xml b/dms.services/aftersales-service/src/main/resources/mybatis/mapper/rule/ttAsWrRulemappingPOMapper.xml
index cda0fe7051..024c9997b8 100644
--- a/dms.services/aftersales-service/src/main/resources/mybatis/mapper/rule/ttAsWrRulemappingPOMapper.xml
+++ b/dms.services/aftersales-service/src/main/resources/mybatis/mapper/rule/ttAsWrRulemappingPOMapper.xml
@@ -92,6 +92,7 @@
                                         </otherwise>
                                     </choose>
                                          ))
+                <!--
                 or tawrd.currency_type in (select a.CODE_ID from dms_basedata.tc_code a where 1=1 and a.TYPE = 8050
                 <choose>
                     <when test="dto.language == null or dto.language == '' or dto.language == 'zh'">
@@ -118,6 +119,19 @@
                     </otherwise>
                 </choose>
                 )
+                -->
+                <if test="dto.dbSupportCurrencyTypes != null and dto.dbSupportCurrencyTypes.size > 0">
+                    or tawrd.currency_type in
+                    <foreach collection="dto.dbSupportCurrencyTypes" index="index" item="item" separator="," open="(" close=")">
+                        #{item}
+                    </foreach>
+                </if>
+                <if test="dto.dbSupportROTypes != null and dto.dbSupportROTypes.size > 0">
+                    or tawrd.ro_type in
+                    <foreach collection="dto.dbSupportROTypes" index="index" item="item" separator="," open="(" close=")">
+                        #{item}
+                    </foreach>
+                </if>
                 or (tawrd.dealer_type = 12151002 and tawrd.id in (select b.rulemapping_detail_id from  tt_as_wr_rulemapping_dealer b
                                     left join dms_sysmanage.tm_dealer_info tdi ON b.DEALER_ID = tdi.DEALER_ID
                                     where b.IS_DELETED = 0 and (b.DEALER_CODE like CONCAT('%', #{dto.searchRemark}, '%')) or tdi.DEALER_NAME like CONCAT('%', #{dto.searchRemark}, '%'))))
(END)
             dto.setDbSupportCurrencyTypes(currencyCodeId);

             // <E5><AD><97><E5><85><B8><E8><B7><A8><E5><BA><93><EF><BC><9A><E6><8E><88><E6><9D><83><E9><A1><B9><E5><B7><A5><E5><8D><95><E7><B1><BB><E5><9E>
<8B> , <E8><AF><AD><E8><A8><80><EF><BC><9A><E9><9C><80><E8><A6><81>  10001001 <E8><BF><99><E6><A0><B7><E7><9A><84>
+            List<Integer> roTypeCodeId = dbSupportHelper.getCodeIdByLikeDesc(8270, dto.getSearchRemark(), languageCode);
+            dto.setDbSupportRoTypes(roTypeCodeId);
         }

         IPage<TtAsWrRulemappingVo> poPage = ttAsWrRulemappingMapper.selectRuleMappingPageList(page,dto);
diff --git a/dms.services/aftersales-service/src/main/resources/mybatis/mapper/rule/ttAsWrRulemappingPOMapper.xml b/dms.services/aftersales-service/src/main/resources/mybatis/mapper/rule/ttAsWrRulemappingPOMapper.xml
index cda0fe7051..024c9997b8 100644
--- a/dms.services/aftersales-service/src/main/resources/mybatis/mapper/rule/ttAsWrRulemappingPOMapper.xml
+++ b/dms.services/aftersales-service/src/main/resources/mybatis/mapper/rule/ttAsWrRulemappingPOMapper.xml
@@ -92,6 +92,7 @@
                                         </otherwise>
                                     </choose>
                                          ))
+                <!--
                 or tawrd.currency_type in (select a.CODE_ID from dms_basedata.tc_code a where 1=1 and a.TYPE = 8050
                 <choose>
                     <when test="dto.language == null or dto.language == '' or dto.language == 'zh'">
@@ -118,6 +119,19 @@
                     </otherwise>
                 </choose>
                 )
+                -->
+                <if test="dto.dbSupportCurrencyTypes != null and dto.dbSupportCurrencyTypes.size > 0">
+                    or tawrd.currency_type in
+                    <foreach collection="dto.dbSupportCurrencyTypes" index="index" item="item" separator="," open="(" close=")">
+                        #{item}
+                    </foreach>
+                </if>
+                <if test="dto.dbSupportROTypes != null and dto.dbSupportROTypes.size > 0">
+                    or tawrd.ro_type in
+                    <foreach collection="dto.dbSupportROTypes" index="index" item="item" separator="," open="(" close=")">
+                        #{item}
+                    </foreach>
+                </if>
                 or (tawrd.dealer_type = 12151002 and tawrd.id in (select b.rulemapping_detail_id from  tt_as_wr_rulemapping_dealer b
                                     left join dms_sysmanage.tm_dealer_info tdi ON b.DEALER_ID = tdi.DEALER_ID
                                     where b.IS_DELETED = 0 and (b.DEALER_CODE like CONCAT('%', #{dto.searchRemark}, '%')) or tdi.DEALER_NAME like CONCAT('%', #{dto.searchRemark}, '%'))))
"""
    idx = text3.find("diff --git")
    text3 = text3[idx:]
    print("\n\n\n---------------------------------------------------threshold_k=1000------------------")
    # 创建分割器实例
    splitter = GitDiffSplitter(text3, threshold_k=1000)
    # 执行分割
    segments = splitter.split_git_diff()
    # 打印分割结果信息
    splitter.print_segments_info(segments)

    print("\n\n\n---------------------------------------------------threshold_k=3000------------------")
    # 创建分割器实例
    splitter = GitDiffSplitter(text3, threshold_k=3000)
    # 执行分割
    segments = splitter.split_git_diff()
    # 打印分割结果信息
    splitter.print_segments_info(segments)
