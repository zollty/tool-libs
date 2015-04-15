'ChangeCharset.vbs
'@Verion 1.0
'@功能：遍历文件，获取特定后缀文件的列表，然后对文件进行编码转换。
'@说明：
'  获取特定文件的文件列表，参见“GetSubFolders”函数
'  文本文件编码装换，参见"UTF8ToAnsi"、"GBKToUTF8"等函数
'@Author: zollty<zollty#163.com>
'@Since: 2012/3/20

'---------------------------
FileList = ""
GetSubFolders(GetCurrentFolderFullPath)
Files = Split(FileList, vbCrLf)
for i=0 to UBound(Files)-1 '最后一个元素是空的
    'U8ToU8Bom Files(i) '如果要生成一个有BOM的文件，启用此行
    GBKToUTF8 Files(i)
next

function UTF8ToAnsi(strFile)
    dim ADOStrm
    dim s
    Set ADOStrm = CreateObject("ADODB.Stream")
    ADOStrm.Type = 2
    ADOStrm.Mode = 3
    ADOStrm.CharSet = "utf-8"
    ADOStrm.Open
    ADOStrm.LoadFromFile strFile
    s = ADOStrm.ReadText
    ADOStrm.Position = 0
    ADOStrm.CharSet = "gbk"
    ADOStrm.WriteText s
    ADOStrm.SetEOS
    ADOStrm.SaveToFile strFile, 2
    ADOStrm.Close
    Set ADOStrm = Nothing
end function

function GBKToUTF8(strFile)
    dim ADOStrm
    dim s
    Set ADOStrm = CreateObject("ADODB.Stream")
    ADOStrm.Type = 2
    ADOStrm.Mode = 3
    ADOStrm.CharSet = "gbk"
    ADOStrm.Open
    ADOStrm.LoadFromFile strFile
    s = ADOStrm.ReadText
    ADOStrm.Position = 0
    ADOStrm.CharSet = "utf-8"
    ADOStrm.WriteText s
    ADOStrm.SetEOS
    ADOStrm.SaveToFile strFile, 2
    ADOStrm.Close
    Set ADOStrm = Nothing
end function

function U8ToU8Bom(strFile)
    dim ADOStrm
    Set ADOStrm = CreateObject("ADODB.Stream")
    ADOStrm.Type = 2
    ADOStrm.Mode = 3
    ADOStrm.CharSet = "utf-8"
    ADOStrm.Open
    ADOStrm.LoadFromFile strFile
    ADOStrm.SaveToFile strFile & ".u8.csv", 2
    ADOStrm.Close
    Set ADOStrm = Nothing
end function

'得到脚本文件所在的当前目录
Function GetCurrentFolderFullPath
	Set fso = CreateObject("Scripting.FileSystemObject")
	GetCurrentFolderFullPath = fso.GetParentFolderName(WScript.ScriptFullName)
End Function

'vbs递归遍历当前目录下的所有文件夹和子文件夹
Function GetSubFolders(currentFolderFullPath)
	Set fso = CreateObject("Scripting.FileSystemObject")
	Set currentFolder = fso.GetFolder(currentFolderFullPath)
	
	'处理目录下面的特定后缀的文件
	for each oFile in currentFolder.Files
		if LCase(fso.GetExtensionName(oFile.Path)) = LCase("java") then
			FileList = FileList & oFile.Path & vbCrLf
		end if
	next
	
	Set subFolderSet = currentFolder.SubFolders
	For Each subFolder in subFolderSet
		GetSubFolders = subFolder.Path & ";" & GetSubFolders(subFolder.Path) &  GetSubFolders 
	Next
End Function
