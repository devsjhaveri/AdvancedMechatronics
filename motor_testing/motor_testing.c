#include "pico/stdlib.h"
#include "hardware/pwm.h"
#include "ina219 copy.h"
#include <stdio.h>

#define IN1 13
#define IN2 12

void pwm_init_motor() {
    gpio_set_function(IN1, GPIO_FUNC_PWM);
    gpio_set_function(IN2, GPIO_FUNC_PWM);

    uint slice = pwm_gpio_to_slice_num(IN1);
    pwm_set_clkdiv(slice, 1.0f);
    pwm_set_wrap(slice, 6249);

    pwm_set_chan_level(slice, PWM_CHAN_A, 6249);
    pwm_set_chan_level(slice, PWM_CHAN_B, 6249);
    pwm_set_enabled(slice, true);
}

void set_duty(float duty) {
    if (duty > 1.0f) duty = 1.0f;
    if (duty < -1.0f) duty = -1.0f;

    uint slice = pwm_gpio_to_slice_num(IN1);
    if (duty > 0) {
        pwm_set_chan_level(slice, PWM_CHAN_B, 6249);
        pwm_set_chan_level(slice, PWM_CHAN_A, (uint16_t)(duty * 6249));
    } else if (duty < 0) {
        pwm_set_chan_level(slice, PWM_CHAN_A, 6249);
        pwm_set_chan_level(slice, PWM_CHAN_B, (uint16_t)(-duty * 6249));
    } else {
        pwm_set_chan_level(slice, PWM_CHAN_A, 6249);
        pwm_set_chan_level(slice, PWM_CHAN_B, 6249);
    }
}

int main() {
    stdio_init_all();
    init_ina219();
    pwm_init_motor();

    while (!stdio_usb_connected()) { sleep_ms(100); }
    sleep_ms(1000);
    printf("Starting...\n");

    for (int i = 0; i < 30; i++) {
        set_duty(0.2f);
        sleep_ms(65);
        set_duty(-0.2f);
        sleep_ms(65);
        float current = read_ina219();
        printf("%d: %.2f mA\n", i, current);
    }

    set_duty(0.0f);
    printf("Done — braked\n");

    while(1) { sleep_ms(1000); }
}