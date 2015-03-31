//数组和字符串
//B
//




#include <stdio.h>
#include <string.h>




//判断一个字符串是否包含重复字符
int IsUniqueChars2(char * str)
{
	int length = strlen(str)-1;
	int i = 0;
	int j = 0;
	for(i = 0 ;i < length; i++)
	{
		for(j = i+1; j <= length; j++)
		{
			if(str[i] ==str[j])
			{
				return false;
			}
		}

	}
	return true;
}

void reverse(char *str)
{
	while(str++!='\0')
	{

	}
}


int main()
{
	//判断一个字符串是否包含重复字符
//	if(IsUniqueChars2("abcda"))
//	{
//		printf("yes\n");
//	}
//	else
//	{
//		printf("no\n");
//	}
	return 0;
}

