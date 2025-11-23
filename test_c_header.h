#ifndef TEST_C_HEADER_H
#define TEST_C_HEADER_H

#include <stdint.h>
#include <stdbool.h>

typedef struct {
    int value;
    char name[32];
} TestStruct;

void test_function(int x, int y);
int calculate_sum(int a, int b);

#endif /* TEST_C_HEADER_H */

