#include "mpu6050.h"
#include "hardware/i2c.h"
#include "hardware/gpio.h"
#include "pico/stdlib.h"
#include <math.h>

#define I2C_PORT i2c0

void mpu6050_init(void) {
    uint8_t buf[2];

    // Wake up the chip
    buf[0] = 0x6B;  // PWR_MGMT_1
    buf[1] = 0x00;
    i2c_write_blocking(I2C_PORT, MPU6050_ADDR, buf, 2, false);

    // Set accelerometer to +/- 2g
    buf[0] = 0x1C;  // ACCEL_CONFIG
    buf[1] = 0x00;
    i2c_write_blocking(I2C_PORT, MPU6050_ADDR, buf, 2, false);

    // Set gyro to +/- 2000 dps
    buf[0] = 0x1B;  // GYRO_CONFIG
    buf[1] = 0x18;
    i2c_write_blocking(I2C_PORT, MPU6050_ADDR, buf, 2, false);
}

void mpu6050_read_accel(float *ax, float *ay, float *az) {
    uint8_t raw[6];
    uint8_t reg = 0x3B;
    i2c_write_blocking(I2C_PORT, MPU6050_ADDR, &reg, 1, true);
    i2c_read_blocking(I2C_PORT, MPU6050_ADDR, raw, 6, false);

    int16_t ax_raw = (raw[0] << 8) | raw[1];
    int16_t ay_raw = (raw[2] << 8) | raw[3];
    int16_t az_raw = (raw[4] << 8) | raw[5];

    *ax = ax_raw * 0.000061f;
    *ay = ay_raw * 0.000061f;
    *az = az_raw * 0.000061f;
}