add_library(edge_core STATIC
    src/modbus_crc.c
    src/point.c
    src/queue.c
)

target_include_directories(edge_core
    PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}/include
)

target_compile_features(edge_core PUBLIC c_std_17)

if(CMAKE_C_COMPILER_ID MATCHES "GNU|Clang")
    target_compile_options(edge_core PRIVATE
        -Wall
        -Wextra
        -Wpedantic
        -Wconversion
        -Wshadow
        -Wstrict-prototypes
        -Werror
    )
endif()

if(BUILD_TESTING)
    add_executable(edge_core_tests tests/test_edge_core.c)
    target_link_libraries(edge_core_tests PRIVATE edge_core)
    target_compile_features(edge_core_tests PRIVATE c_std_17)

    if(CMAKE_C_COMPILER_ID MATCHES "GNU|Clang")
        target_compile_options(edge_core_tests PRIVATE
            -Wall
            -Wextra
            -Wpedantic
            -Wconversion
            -Wshadow
            -Wstrict-prototypes
            -Werror
        )
    endif()

    add_test(NAME edge_core_tests COMMAND edge_core_tests)
endif()
