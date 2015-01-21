#include<stdio.h>
#include<string>

const char * test()
{
	//return "hello";
	return NULL;
}
int main()
{
	std::string stest;
	stest = "  192.168.12.23,1.1.1.1\r\n";
	const char * newtest;
//	if(stest.empty())
//	{
//		printf("is empty\n");
//	}
	printf("sub:%s**\n",stest.substr(2,14).c_str());
	//newtest = test();
//	if(test())
//	{
	//	stest = test();
//	}
	//printf("stest:%s\n",stest.c_str());
	printf("end\n");
	return 1;
}
