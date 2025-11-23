// C++ 中，如果没有显式定义，编译器会自动生成：

class A {
    // 编译器自动生成：
    // - 默认构造函数 A()
    // - 默认析构函数 ~A()
    // - 默认拷贝构造函数 A(const A&)
    // - 默认拷贝赋值运算符 A& operator=(const A&)
    // - 默认移动构造函数 A(A&&) (C++11)
    // - 默认移动赋值运算符 A& operator=(A&&) (C++11)
};

// 等价于：
class B {
public:
    B() = default;              // 默认构造函数
    ~B() = default;             // 默认析构函数
    B(const B&) = default;      // 默认拷贝构造函数
    B& operator=(const B&) = default;  // 默认拷贝赋值
    B(B&&) = default;           // 默认移动构造函数 (C++11)
    B& operator=(B&&) = default; // 默认移动赋值 (C++11)
};
