#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/gpio.h"

#define HX711_SCK  14   
#define HX711_DT   15  

#define IIR_A  0.88f

void hx711_init(void) {
    gpio_init(HX711_SCK);
    gpio_set_dir(HX711_SCK, GPIO_OUT);
    gpio_put(HX711_SCK, 0);

    gpio_init(HX711_DT);
    gpio_set_dir(HX711_DT, GPIO_IN);
}

int32_t hx711_read(void) {
    while (gpio_get(HX711_DT)) {
        tight_loop_contents();
    }

    uint32_t raw = 0;

    for (int i = 0; i < 24; i++) {
        gpio_put(HX711_SCK, 1);
        sleep_us(1);
        raw = (raw << 1) | gpio_get(HX711_DT);
        gpio_put(HX711_SCK, 0);
        sleep_us(1);
    }

    gpio_put(HX711_SCK, 1);
    sleep_us(1);
    gpio_put(HX711_SCK, 0);
    sleep_us(1);

    if (raw & 0x800000) {
        raw |= 0xFF000000;
    }

    return (int32_t)raw;
}

int main(void) {
    stdio_init_all();
    hx711_init();

    sleep_ms(2000);

    while (true) {
        int n_samples = 0;
        if (scanf("%d", &n_samples) != 1 || n_samples <= 0) {
            continue;
        }

        float iir = (float)hx711_read();

        for (int i = 0; i < n_samples; i++) {
            uint32_t t  = to_ms_since_boot(get_absolute_time());
            int32_t raw = hx711_read();
            iir = IIR_A * iir + (1.0f - IIR_A) * (float)raw;
            printf("DBG %ld\n", (long)raw);
            printf("DATA %ld %.2f %lu\n", (long)raw, iir, (unsigned long)t);
        }
    }

    return 0;
}