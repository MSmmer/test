#!/bin/bash
#ckground-loop.sh

 for i in 1 2 3 4 5 6 7 8 9 10
 do
 echo -n "$i"
 done&
#第一个循环 #在后台运行这个循环
#在第 2 个循环之后,将在某些时候执行.
 echo #这个'echo'某些时候将不会显示. 11
 for i in 11 12 13 14 15 16 17 18 19 20
 do
 echo -n "$i"
 done

 echo "hello" #这个'echo'某些时候将不会显示.
 exit 0
