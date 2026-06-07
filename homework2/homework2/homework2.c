#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/pwm.h"

void initPWM();
void sweepServo();

#define mPWM 16

int main()
{
    initPWM();
    sleep_ms(1000);
    sweepServo();
    while(1);
}

void initPWM(){
    gpio_set_function(mPWM, GPIO_FUNC_PWM);
    unsigned int slice_m1a = pwm_gpio_to_slice_num(mPWM);
    pwm_set_clkdiv(slice_m1a, 64);
    pwm_set_wrap(slice_m1a, 39062);
    pwm_set_gpio_level(mPWM, 2930);
    pwm_set_enabled(slice_m1a, true);
}

void sweepServo(){
    for(int i = 1953; i <= 3906; i+= 100){
        pwm_set_gpio_level(mPWM, i);
        sleep_ms(100);
    }
    for(int i = 3906; i >= 1953; i-= 100){
        pwm_set_gpio_level(mPWM, i);
        sleep_ms(100);
    }
}