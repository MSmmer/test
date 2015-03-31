#include <utility>
#include <stdio.h>
#include<iostream>
#include<vector>

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

class A
{
	public:
    A() { id = ++count; cout << "create A" << id  <<  "\n"; }
    ~A() { cout << "destroy A" << id << "\n"; }
	private:
    static int count;
    int id;
};

int A::count = 0;

/*调用该函数会丢失掉所有权*/
void sink(auto_ptr<A> a)
{
    cout << "Enter sink()\n";
}

/*调用该函数会创建对象，并获取所有权*/
auto_ptr<A> create()
{
    cout << "Enter create()\n";
    auto_ptr<A> a(new A());
    return a;
}


int main()
{
//    CBird * pBird = new CLark();
//    pBird->fly();
//    delete pBird;
//
//	tellStory();//输出一个循环

//	auto_ptr<A> a1 = create();
//	auto_ptr<A> a2 = a1; /*转移所有权，此时a1无效了*/
//	auto_ptr<A> a3(new A());
//    cout << "Exit create()\n";
//    sink(a2);/*丢失所有权，会发现a2的释放在sink函数中进行*/
//    cout << "Exit sink()\n";
//
	int a[10] = {1,2,3,4,5,6,7,8,9,10};
    vector<int> vec1(a, a + 4);
    vector<int> vec2(a + 5, a + 10);

    swap(vec1, vec2);

    for (int i = 0; i < vec1.size(); i++)
    {
        cout<<vec1[i]<<" ";
    }
    return 0;
}





