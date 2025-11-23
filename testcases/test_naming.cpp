// Test cases for naming conventions
// This file contains both valid and invalid examples

// Valid: lowercase file name
namespace valid_namespace {
    // Valid: uppercase class name
    class ValidClass {
    public:
        // Valid: uppercase function name
        void ValidFunction() {
            // Valid: lowercase variable name
            int valid_variable = 0;
        }
        
        // Valid: lowercase public member variable
        int public_member = 0;
        
    private:
        // Valid: lowercase private member variable ending with underscore
        int private_member_ = 0;
    };
}

// Invalid: uppercase file name (should be lowercase)
// Invalid: uppercase namespace name
namespace InvalidNamespace {
    // Invalid: lowercase class name (should be uppercase)
    class invalid_class {
    public:
        // Invalid: lowercase function name (should be uppercase)
        void invalid_function() {
            // Invalid: uppercase variable name (should be lowercase)
            int InvalidVariable = 0;
        }
        
        // Invalid: uppercase public member variable
        int PublicMember = 0;
        
    private:
        // Invalid: private member variable not ending with underscore
        int private_member = 0;
    };
}

// Global variable tests
int valid_global_variable = 0;  // Valid: lowercase
int InvalidGlobalVariable = 0;  // Invalid: uppercase

// Single character variable (should be checked since skip_one_char_variables = false)
void TestFunction() {
    int x = 0;  // Should be checked
}

