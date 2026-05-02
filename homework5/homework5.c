#include <stdio.h>
#include <stdlib.h>
#include "pico/stdlib.h"
#include "hardware/i2c.h"
#include "hardware/gpio.h"
#include "ssd1306.h"

#define I2C_MPU  i2c0
#define I2C_OLED i2c1

#define I2C_SDA_MPU  12
#define I2C_SCL_MPU  13
#define I2C_SDA_OLED 6
#define I2C_SCL_OLED 7

#define WHO_AM_I 0x75
#define IMU_ADDR 0x68

int main() {
    stdio_init_all();

    // Init MPU on i2c0 (GP12/GP13)
    i2c_init(I2C_MPU, 400*1000);
    gpio_set_function(I2C_SDA_MPU, GPIO_FUNC_I2C);
    gpio_set_function(I2C_SCL_MPU, GPIO_FUNC_I2C);
    gpio_pull_up(I2C_SDA_MPU);
    gpio_pull_up(I2C_SCL_MPU);

    // Init OLED on i2c1 (GP6/GP7)
    i2c_init(I2C_OLED, 400*1000);
    gpio_set_function(I2C_SDA_OLED, GPIO_FUNC_I2C);
    gpio_set_function(I2C_SCL_OLED, GPIO_FUNC_I2C);
    gpio_pull_up(I2C_SDA_OLED);
    gpio_pull_up(I2C_SCL_OLED);

    // ssd1306 uses i2c1 internally (make sure ssd1306.c uses i2c1)
    ssd1306_setup();
    ssd1306_clear();
    ssd1306_update();

    // LED init
    gpio_init(16);
    gpio_set_dir(16, GPIO_OUT);
    gpio_put(16, 0);

    // WHO_AM_I check
    uint8_t reg = WHO_AM_I;
    uint8_t val;
    i2c_write_blocking(I2C_MPU, IMU_ADDR, &reg, 1, true);
    i2c_read_blocking(I2C_MPU, IMU_ADDR, &val, 1, false);

    if (val != 0x68 && val != 0x98) {
        while (true) {
            printf("IMU not found, check wiring!\n");
            gpio_put(16, 1);
            sleep_ms(1000);
        }
    }

    uint8_t buf[2];
    buf[0] = 0x6B; buf[1] = 0x00;
    i2c_write_blocking(I2C_MPU, IMU_ADDR, buf, 2, false);

    buf[0] = 0x1C; buf[1] = 0x00;
    i2c_write_blocking(I2C_MPU, IMU_ADDR, buf, 2, false);

    buf[0] = 0x1B; buf[1] = 0x18;
    i2c_write_blocking(I2C_MPU, IMU_ADDR, buf, 2, false);

    while (true) {
    uint8_t raw[14];
    reg = 0x3B;
    i2c_write_blocking(I2C_MPU, IMU_ADDR, &reg, 1, true);
    i2c_read_blocking(I2C_MPU, IMU_ADDR, raw, 14, false);

    int16_t accel_x_raw = (raw[0] << 8) | raw[1];
    int16_t accel_y_raw = (raw[2] << 8) | raw[3];

    float accel_x = accel_x_raw * 0.000061f;
    float accel_y = accel_y_raw * 0.000061f;

    int cx = 64;
    int cy = 16;

    int dx = (int)(accel_x * 150);
    int dy = (int)(accel_y * 150);

    printf("accel_x=%.2f accel_y=%.2f dx=%d dy=%d\n", accel_x, accel_y, dx, dy);

    int x0 = cx, y0 = cy;
    int x1 = cx + dx, y1 = cy + dy;

    if (x1 < 0)   x1 = 0;
    if (x1 > 127) x1 = 127;
    if (y1 < 0)   y1 = 0;
    if (y1 > 31)  y1 = 31;

    // precompute these so they don't change mid-loop
    int adx = abs(x1 - x0);
    int ady = abs(y1 - y0);
    int sx  = (x0 < x1) ? 1 : -1;
    int sy  = (y0 < y1) ? 1 : -1;
    int err = adx - ady;

    ssd1306_clear();

    while (1) {
        ssd1306_drawPixel(x0, y0, 1);
        if (x0 == x1 && y0 == y1) break;
        int e2 = 2 * err;
        if (e2 > -ady) { err -= ady; x0 += sx; }
        if (e2 <  adx) { err += adx; y0 += sy; }
    }

    ssd1306_update();
    sleep_ms(10);
}
}