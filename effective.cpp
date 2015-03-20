
#include <stdio.h>
#include<iostream>

using namespace std;

class Empty
{

};

class CBird
{
public:
    CBird() { cout << "CBird constructor." << endl; };
    ~CBird() { cout << "CBird destructor." << endl; };
    virtual void fly() { cout << "CBird fly." << endl; };
};

class CLark : public CBird
{
public:
    CLark() { cout << "CLark constructor." << endl; };
    ~CLark() { cout << "CLark destructor." << endl; };
    void fly() { cout << "CLark fly." << endl; }
};


void tellStory()
{
    printf("从前有座山\n");
    printf("山上有座庙\n");
    printf("庙里有个老和尚和一个小和尚\n");
    printf("有一天\n");
    printf("小和尚对老和尚说\n");
    printf("\"给我讲个故事吧\"\n");
    printf("于是, 老和尚说: \n");
    tellStory();
}
int main()
{
//    CBird * pBird = new CLark();
//    pBird->fly();
//    delete pBird;
//
	tellStory();
    return 0;
}





