#include "ina219.h"

#define INA219_ADDR 0b1000000
#define INA219_REG_CONFIG 0x00
#define INA219_REG_CURRENT 0x04
#define INA219_REG_CALIBRATION 0x05

#define SDA_PIN 16
#define SCL_PIN 17
#define I2C_INST i2c0

void writeINA219(int reg, int value);
signed short readINA219(unsigned char reg);

void init_ina219(){
    i2c_init(I2C_INST, 400 * 1000);
    gpio_set_function(SDA_PIN, GPIO_FUNC_I2C);
    gpio_set_function(SCL_PIN, GPIO_FUNC_I2C);
    gpio_pull_up(SDA_PIN);
    gpio_pull_up(SCL_PIN);

    unsigned short ina219_calValue = 1024;
    unsigned short ina219_config = 0b0011000010001111;
    writeINA219(INA219_REG_CALIBRATION, ina219_calValue);
    writeINA219(INA219_REG_CONFIG, ina219_config);
}

float read_ina219(){
    float ma = 0;
    signed short value = readINA219(INA219_REG_CURRENT);
    ma = value / 3.0;
    return ma;
}

void writeINA219(int reg, int value){
    uint8_t buf[3];
    buf[0] = reg;
    buf[1] = value>>8;
    buf[2] = value&0xff;
    i2c_write_blocking(I2C_INST, INA219_ADDR, buf, 3, false);
}

signed short readINA219(unsigned char reg){
    i2c_write_blocking(I2C_INST, INA219_ADDR, &reg, 1, true);
    uint8_t buffer[2];
    i2c_read_blocking(I2C_INST, INA219_ADDR, buffer, 2, false);
    signed short value = (buffer[0]<<8)|buffer[1];
    return value;
}