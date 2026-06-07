#ifndef MPU6050_H
#define MPU6050_H

// MPU6050 I2C address
#define MPU6050_ADDR 0x68

// Register addresses
#define MPU6050_WHO_AM_I    0x75
#define MPU6050_PWR_MGMT_1  0x6B
#define MPU6050_ACCEL_XOUT_H 0x3B
#define MPU6050_ACCEL_CONFIG 0x1C
#define MPU6050_GYRO_CONFIG  0x1B

// Function declarations
void mpu6050_init(void);
void mpu6050_read_accel(float *ax, float *ay, float *az);

#endif