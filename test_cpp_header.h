#ifndef TEST_CPP_HEADER_H
#define TEST_CPP_HEADER_H

#include <cstdint>
#include <string>

namespace test {
class TestClass {
public:
    TestClass();
    virtual ~TestClass();
    
    void testMethod();
    template<typename T>
    T getValue() const;
    
private:
    int value_;
};

}  // namespace test

#endif /* TEST_CPP_HEADER_H */

