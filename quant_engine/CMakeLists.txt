cmake_minimum_required(VERSION 3.16)

project(QuantLab
    VERSION 2.0
    LANGUAGES CXX
)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

include_directories(${PROJECT_SOURCE_DIR}/quant_engine/include)

set(SOURCES
    src/main.cpp
    src/strategy/moving_average_strategy.cpp
    src/execution/full_position_sizer.cpp
    src/execution/order_manager.cpp
    src/execution/execution_engine.cpp
    src/execution/execution_model.cpp
    src/execution/order_validator.cpp
)

add_executable(
    quantlab
    ${SOURCES}
)

if (CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
    target_compile_options(
        quantlab
        PRIVATE
        -Wall
        -Wextra
        -Wpedantic
    )
endif()
