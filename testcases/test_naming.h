// Header file test cases

// Valid: uppercase class name
class ValidClass {
public:
    // Valid: uppercase function name
    void ValidFunction();
    
    // Valid: lowercase public member
    int public_member;
    
private:
    // Valid: lowercase private member ending with underscore
    int private_member_;
};

// Invalid: lowercase class name
class invalid_class {
public:
    // Invalid: lowercase function name
    void invalid_function();
    
    // Invalid: uppercase public member
    int PublicMember;
    
private:
    // Invalid: private member not ending with underscore
    int private_member;
};

// Global variable in header
extern int valid_global;  // Valid
extern int InvalidGlobal;  // Invalid

