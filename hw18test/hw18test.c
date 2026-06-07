#include "pico/stdlib.h"

#define IN1 13
#define IN2 12

int main() {
    gpio_init(IN1);
    gpio_init(IN2);
    gpio_set_dir(IN1, GPIO_OUT);
    gpio_set_dir(IN2, GPIO_OUT);

    while (1) {
        gpio_put(IN1, 1);
        gpio_put(IN2, 0);
        sleep_ms(500);

        gpio_put(IN1, 1);
        gpio_put(IN2, 1);
        sleep_ms(200);

        gpio_put(IN1, 0);
        gpio_put(IN2, 1);
        sleep_ms(500);

        gpio_put(IN1, 1);
        gpio_put(IN2, 1);
        sleep_ms(200);
    }
}