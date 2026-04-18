#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/i2c.h"
#include "ssd1306.h"
#include "font.h"
#include "hardware/adc.h"

// I2C defines
// This example will use I2C0 on GPIO16 (SDA) and GPIO17 (SCL) running at 400KHz.
// Pins can be changed, see the GPIO function select table in the datasheet for information on GPIO assignments
#define I2C_PORT i2c0
#define I2C_SDA 16
#define I2C_SCL 17
#define LED_PIN 15

uint32_t nextBlink = 0;

int main()
{
    stdio_init_all();

    gpio_init(LED_PIN);
    gpio_set_dir(LED_PIN, GPIO_OUT);
    gpio_put(LED_PIN, 1);

    adc_init();
    adc_gpio_init(26);
    adc_select_input(0);
   
    i2c_init(I2C_PORT, 400*1000);
    
    gpio_set_function(I2C_SDA, GPIO_FUNC_I2C);
    gpio_set_function(I2C_SCL, GPIO_FUNC_I2C);
    gpio_pull_up(I2C_SDA);
    gpio_pull_up(I2C_SCL);
    // For more examples of I2C use see https://github.com/raspberrypi/pico-examples/tree/master/i2c

    ssd1306_setup();
    int state = 0;
    float fps = 0.0f;

    while (true) {
        uint32_t t_start = to_us_since_boot(get_absolute_time());
        ssd1306_clear();

        char message[50]; 
        char message2[50];
        char message3[50];
        char message4[50];

        uint16_t raw = adc_read();
        float voltage = raw * 3.3f / 4095.0f;

        sprintf(message, "If you're reading this"); 
        ssd1306_drawString(0,0,message);
        sprintf(message2, "It's too late already");
        ssd1306_drawString(0,8,message2);
        sprintf(message3, "Volt: %.3f V", voltage);
        ssd1306_drawString(0,16,message3);
        sprintf(message4, "FPS: %.1f", fps);
        ssd1306_drawString(0, 24, message4);

        ssd1306_update();

        uint32_t t_end = to_us_since_boot(get_absolute_time());
        float elapsed = t_end - t_start;
        fps = 1000000.0f / elapsed;

        if (time_us_32() > nextBlink) {
            gpio_put(LED_PIN, state);
            state = !state;
            nextBlink += 500000;
        }
    }
}
