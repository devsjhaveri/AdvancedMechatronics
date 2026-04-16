#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/i2c.h"

// I2C defines
// This example will use I2C0 on GPIO8 (SDA) and GPIO9 (SCL) running at 400KHz.
// Pins can be changed, see the GPIO function select table in the datasheet for information on GPIO assignments
#define I2C_PORT i2c0
#define I2C_SDA 12
#define I2C_SCL 13
#define LED_PIN 15

uint32_t nextBlink = 0;

int main()
{
    stdio_init_all();

    gpio_init(LED_PIN);
    gpio_set_dir(LED_PIN, GPIO_OUT);
    gpio_put(LED_PIN, 1);

    i2c_init(I2C_PORT, 400*1000);
    gpio_set_function(I2C_SDA, GPIO_FUNC_I2C);
    gpio_set_function(I2C_SCL, GPIO_FUNC_I2C);
    gpio_pull_up(I2C_SDA);
    gpio_pull_up(I2C_SCL);

    uint8_t buf[2];
    buf[0] = 0x00;      
    buf[1] = 0b01111111; 
    i2c_write_blocking(I2C_PORT, 0x20, buf, 2, false);

    while (true) {
        sleep_ms(100);
        uint8_t reg = 0x09;  
        uint8_t buf;
        i2c_write_blocking(I2C_PORT, 0x20, &reg, 1, true);
        i2c_read_blocking(I2C_PORT, 0x20, &buf, 1, false);
        uint8_t buttonState = buf;
        printf("buf: %d, buttonState: %d\n", buf, buttonState);
        if (buttonState == 0) {
            printf("turning LED on\n");
            uint8_t buf[2];
            buf[0] = 0x0A;        
            buf[1] = 0b10000000; 
            i2c_write_blocking(I2C_PORT, 0x20, buf, 2, false);
        } else {
            uint8_t buf[2];
            buf[0] = 0x0A;        
            buf[1] = 0b00000000; 
            i2c_write_blocking(I2C_PORT, 0x20, buf, 2, false);
}
        if (time_us_32() > nextBlink) {
        gpio_put(LED_PIN, !gpio_get(LED_PIN));
        nextBlink = time_us_32() + 500000;
    }
    }
}
