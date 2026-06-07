#include "pico/stdlib.h"
#include "hardware/i2c.h"
#include <stdio.h>

#define I2C_PORT i2c0
#define SDA_PIN 4
#define SCL_PIN 5
#define AS5600_ADDR 0x36
#define AS5600_ANGLE_H 0x0C 
#define AS5600_ANGLE_L 0x0D  

#define HX711_SCK 15
#define HX711_DT  14

void as5600_init() {
    i2c_init(I2C_PORT, 400000);
    gpio_set_function(SDA_PIN, GPIO_FUNC_I2C);
    gpio_set_function(SCL_PIN, GPIO_FUNC_I2C);
    gpio_pull_up(SDA_PIN);
    gpio_pull_up(SCL_PIN);
}

uint16_t as5600_read_angle() {
    uint8_t reg = AS5600_ANGLE_H;
    uint8_t buf[2];
    i2c_write_blocking(I2C_PORT, AS5600_ADDR, &reg, 1, true);
    i2c_read_blocking(I2C_PORT, AS5600_ADDR, buf, 2, false);
    return ((uint16_t)(buf[0] & 0x0F) << 8) | buf[1];
}

void hx711_init() {
    gpio_init(HX711_SCK);
    gpio_init(HX711_DT);
    gpio_set_dir(HX711_SCK, GPIO_OUT);
    gpio_set_dir(HX711_DT, GPIO_IN);
    gpio_put(HX711_SCK, 0);
}

int32_t hx711_read() {
    while (gpio_get(HX711_DT)) { tight_loop_contents(); }
    uint32_t raw = 0;
    for (int i = 0; i < 24; i++) {
        gpio_put(HX711_SCK, 1);
        sleep_us(1);
        raw = (raw << 1) | gpio_get(HX711_DT);
        gpio_put(HX711_SCK, 0);
        sleep_us(1);
    }
    gpio_put(HX711_SCK, 1);
    sleep_us(1);
    gpio_put(HX711_SCK, 0);
    sleep_us(1);
    if (raw & 0x800000) raw |= 0xFF000000;
    return (int32_t)raw;
}

int main() {
    stdio_init_all();
    as5600_init();
    hx711_init();

    while (!stdio_usb_connected()) { sleep_ms(100); }
    sleep_ms(1000);

    int32_t zero_force = hx711_read(); 

    while (1) {
        uint16_t angle = as5600_read_angle();
        int32_t force = hx711_read() - zero_force;
        printf("%d,%d\n", angle, force);
    }
}