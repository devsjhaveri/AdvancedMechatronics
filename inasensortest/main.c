#include "pico/stdlib.h"
#include "hardware/pwm.h"
#include "hardware/timer.h"
#include "ina219.h"
#include <stdio.h>

#define IN1 13
#define IN2 12

#define KP 0.001f
#define KI 0.00001f

volatile float desired_current = 200.0f;
volatile float integral = 0.0f;
volatile bool controller_running = false;

#define NUM_SAMPLES 784
float log_desired[NUM_SAMPLES];
float log_actual[NUM_SAMPLES];
volatile int log_index = 0;

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

void brake() {
    uint slice = pwm_gpio_to_slice_num(IN1);
    pwm_set_chan_level(slice, PWM_CHAN_A, 6249);
    pwm_set_chan_level(slice, PWM_CHAN_B, 6249);
    integral = 0.0f;
}

bool repeating_timer_callback(struct repeating_timer *t) {
    if (!controller_running) return true;

    float actual = read_ina219();
    float error = desired_current - actual;

    integral += error;
    if (integral > 5000.0f) integral = 5000.0f;
    if (integral < -5000.0f) integral = -5000.0f;

    float output = KP * error + KI * integral;
    set_duty(output);

    if (log_index < NUM_SAMPLES) {
        log_desired[log_index] = desired_current;
        log_actual[log_index] = actual;
        log_index++;
    }

    static int counter = 0;
    counter++;
    if (counter % 14 == 0) {
        desired_current = -desired_current;
        integral = 0.0f;
    }

    if (log_index >= NUM_SAMPLES) {
        controller_running = false;
        brake();
    }

    return true;
}

int main() {
    stdio_init_all();
    init_ina219();
    pwm_init_motor();

    while (!stdio_usb_connected()) { sleep_ms(100); }
    sleep_ms(1000);

    while (1) {
        set_duty(0.2f);
        for (int i = 0; i < 13; i++) {
            float current = read_ina219();
            printf("%.2f mA\n", current);
            sleep_ms(5);
        }

        set_duty(-0.2f);
        for (int i = 0; i < 13; i++) {
            float current = read_ina219();
            printf("%.2f mA\n", current);
            sleep_ms(5);
        }
    }
}