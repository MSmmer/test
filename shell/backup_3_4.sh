#!/bin/bash
#rball"中(经过 tar 和 gzip 处理过的文件)
 #+ 备份最后 24 小时当前目录下 d 所有修改的文件.

 BACKUPFILE=backup-$(date +%m-%d-%Y)
 # 在备份文件中嵌入时间.
 # Thanks, Joshua Tschida, for the idea.
 archive=${1:-$BACKUPFILE}
 # 如果在命令行中没有指定备份文件的文件名,
 #+ 那么将默认使用"backup-MM-DD-YYYY.tar.gz".

 tar cvf - `find . -mtime -1 -type f -print` > $archive.tar
 gzip $archive.tar
 echo "Directory $PWD backed up in archive file \"$archive.tar.gz\"."

 # Stephane Chazelas 指出上边代码,
 #+ 如果在发现太多的文件的时候,或者是如果文件
 #+ 名包括空格的时候,将执行失败.

 #
 #
 #
 #
 #
 #
 #


 exit 0
