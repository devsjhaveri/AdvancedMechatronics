#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/i2c.h"
#include "hardware/adc.h"

bool button_is_pressed();

// I2C defines
// This example will use I2C0 on GPIO8 (SDA) and GPIO9 (SCL) running at 400KHz.
// Pins can be changed, see the GPIO function select table in the datasheet for information on GPIO assignments
#define I2C_PORT i2c0
#define I2C_SDA 8
#define I2C_SCL 9
#define LED_PIN 15
#define BUTTON_PIN 16

int main()
{
    stdio_init_all();
    while (!stdio_usb_connected()) {
        sleep_ms(100);
    }
    printf("Start!\n");

    gpio_init(LED_PIN);
    gpio_set_dir(LED_PIN, GPIO_OUT);
    gpio_put(LED_PIN, 1);

    gpio_init(BUTTON_PIN);
    gpio_set_dir(BUTTON_PIN, GPIO_IN);
    gpio_pull_up(BUTTON_PIN);

    adc_init(); 
    adc_gpio_init(28); 
    adc_select_input(2);

    while (!button_is_pressed()) {
        sleep_ms(100);
    }
    
    gpio_put(LED_PIN, 0);

    int num_samples;

    printf("Enter the number of samples to take from 1 to 100: ");
    scanf("%d", &num_samples);

    for (int i = 0; i < num_samples; i++) {
    uint16_t result = adc_read();
    printf("Sample (V): %d\n", result);
    sleep_ms(10);
}
}

bool button_is_pressed() {
    if (gpio_get(BUTTON_PIN) == 0) {
        return true;
    }
    return false;
}