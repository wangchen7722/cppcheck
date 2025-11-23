// Comprehensive test cases for Google C++ Style Guide naming conventions
// Each section tests a specific naming rule

// ============================================================================
// 1. FILE NAMING (RE_FILE: [a-z][a-z0-9_]*\.(cpp|cc|cxx|c|h|hpp|hxx)\Z)
// ============================================================================
// Valid: test_naming_comprehensive.cpp (lowercase with underscore)
// Invalid: TestNaming.cpp (uppercase), test-naming.cpp (hyphen not allowed)

// ============================================================================
// 2. NAMESPACE NAMING (RE_NAMESPACE: [a-z][a-z0-9_]*\Z)
// ============================================================================
namespace valid_namespace {  // Valid: lowercase
    int x = 0;
}

namespace valid_namespace_123 {  // Valid: lowercase with numbers
    int x = 0;
}

namespace InvalidNamespace {  // Invalid: uppercase
    int x = 0;
}

// namespace invalid-namespace {  // Invalid: hyphen (syntax error, commented out)
//     int x = 0;
// }

// ============================================================================
// 3. CLASS NAMING (RE_CLASS_NAME: [A-Z][a-zA-Z0-9]*\Z)
// ============================================================================
class ValidClass {  // Valid: PascalCase
public:
    void Method() {}
};

class ValidClass123 {  // Valid: PascalCase with numbers
public:
    void Method() {}
};

class invalid_class {  // Invalid: lowercase
public:
    void Method() {}
};

class Invalid_Class {  // Invalid: underscore
public:
    void Method() {}
};

// ============================================================================
// 4. FUNCTION NAMING (RE_FUNCTIONNAME: [A-Z][a-zA-Z0-9]*\Z)
// ============================================================================
void ValidFunction() {  // Valid: PascalCase
    int x = 0;
}

void ValidFunction123() {  // Valid: PascalCase with numbers
    int x = 0;
}

void invalid_function() {  // Invalid: lowercase
    int x = 0;
}

void Invalid_Function() {  // Invalid: underscore
    int x = 0;
}

class TestClass {
public:
    void ValidMethod() {}  // Valid: PascalCase
    void invalid_method() {}  // Invalid: lowercase
};

// ============================================================================
// 5. VARIABLE NAMING (RE_VARNAME: [a-z][a-z0-9_]*\Z)
// ============================================================================
void TestVariables() {
    int valid_variable = 0;  // Valid: snake_case
    int valid_variable_123 = 0;  // Valid: snake_case with numbers
    int InvalidVariable = 0;  // Invalid: PascalCase
    // int invalid-Variable = 0;  // Invalid: hyphen (syntax error, commented out)
}

// ============================================================================
// 6. PRIVATE MEMBER VARIABLE (RE_PRIVATE_MEMBER_VARIABLE: [a-z][a-z0-9_]*_\Z)
// ============================================================================
class MemberTest {
private:
    int valid_private_member_ = 0;  // Valid: snake_case ending with _
    int invalid_private_member = 0;  // Invalid: missing trailing _
    int InvalidPrivateMember_ = 0;  // Invalid: PascalCase
    int valid_123_ = 0;  // Valid: with numbers
};

// ============================================================================
// 7. PUBLIC MEMBER VARIABLE (RE_PUBLIC_MEMBER_VARIABLE: [a-z][a-z0-9_]*\Z)
// ============================================================================
class PublicMemberTest {
public:
    int valid_public_member = 0;  // Valid: snake_case
    int valid_public_123 = 0;  // Valid: with numbers
    int InvalidPublicMember = 0;  // Invalid: PascalCase
    int invalid_public_member_ = 0;  // Invalid: trailing _ (should not have)
};

// ============================================================================
// 8. GLOBAL VARIABLE (RE_GLOBAL_VARNAME: [a-z][a-z0-9_]*\Z)
// ============================================================================
int valid_global_variable = 0;  // Valid: snake_case
int valid_global_123 = 0;  // Valid: with numbers
int InvalidGlobalVariable = 0;  // Invalid: PascalCase
// int invalid-global = 0;  // Invalid: hyphen (syntax error, commented out)

// ============================================================================
// 9. SINGLE CHARACTER VARIABLES (skip_one_char_variables: false)
// ============================================================================
void TestSingleChar() {
    int x = 0;  // Should be checked (skip_one_char_variables = false)
    int y = 0;  // Should be checked
    int valid_name = 0;  // Valid: multi-character
}

// ============================================================================
// 10. MIXED VALID/INVALID EXAMPLES
// ============================================================================
namespace test_namespace {
    class ValidClass {
    public:
        void ValidMethod() {
            int local_var = 0;
        }
        
        int public_member = 0;
        
    private:
        int private_member_ = 0;
    };
    
    class invalid_class {
    public:
        void invalid_method() {
            int LocalVar = 0;
        }
        
        int PublicMember = 0;
        
    private:
        int private_member = 0;
    };
}

