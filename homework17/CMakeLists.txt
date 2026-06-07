cmake_minimum_required(VERSION 3.13)

set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

if(WIN32)
    set(USERHOME $ENV{USERPROFILE})
else()
    set(USERHOME $ENV{HOME})
endif()
set(sdkVersion 2.2.0)
set(toolchainVersion 14_2_Rel1)
set(picotoolVersion 2.2.0-a4)
set(picoVscode ${USERHOME}/.pico-sdk/cmake/pico-vscode.cmake)
if (EXISTS ${picoVscode})
    include(${picoVscode})
endif()

set(PICO_BOARD pico CACHE STRING "Board type")

include(pico_sdk_import.cmake)

project(hw17 C CXX ASM)

pico_sdk_init()

add_executable(hw17 hw17.c)

pico_set_program_name(hw17 "hw17")
pico_set_program_version(hw17 "0.1")

pico_enable_stdio_uart(hw17 0)
pico_enable_stdio_usb(hw17 1)

target_link_libraries(hw17
        pico_stdlib
        hardware_i2c)

target_include_directories(hw17 PRIVATE
        ${CMAKE_CURRENT_LIST_DIR}
)

pico_add_extra_outputs(hw17)