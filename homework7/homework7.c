#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/spi.h"
#include <math.h>

#define SPI_PORT spi1
#define PIN_MISO 12
#define PIN_CS   16
#define PIN_SCK  14
#define PIN_MOSI 15

void dac_write(uint8_t channel, float voltage);
static inline void cs_select(uint cs_pin);
static inline void cs_deselect(uint cs_pin);

int main()
{
    stdio_init_all();

    spi_init(SPI_PORT, 1000*1000);
    gpio_set_function(PIN_MISO, GPIO_FUNC_SPI);
    gpio_set_function(PIN_SCK, GPIO_FUNC_SPI);
    gpio_set_function(PIN_MOSI, GPIO_FUNC_SPI);


    gpio_init(PIN_CS);
    gpio_set_dir(PIN_CS, GPIO_OUT);
    gpio_put(PIN_CS, 1);
    

    while (true) {
        for(int i=0; i<100; i++) {
            float voltage = (sin(2 * M_PI * 2 * (i/100.0)) + 1) / 2 * 3.3;
            dac_write(0, voltage);

            if(i<50){
            float voltage2 = (i/49.0) * 3.3;
            dac_write(1, voltage2);
            } else {
            float voltage2 = ((99-i)/49.0) * 3.3;
            dac_write(1, voltage2);
            }
            sleep_ms(10);
            printf("hello\n");
        }
    }
}

static inline void cs_select(uint cs_pin) {
    asm volatile("nop \n nop \n nop");
    gpio_put(cs_pin, 0);
    asm volatile("nop \n nop \n nop");
}

static inline void cs_deselect(uint cs_pin) {
    asm volatile("nop \n nop \n nop");
    gpio_put(cs_pin, 1);
    asm volatile("nop \n nop \n nop");
}

void dac_write(uint8_t channel, float voltage) {
    uint16_t value = (voltage / 3.3) * 1023;
    value = value << 2;
    value |= (channel == 0) ? 0x3000 : 0xB000;
    
    uint8_t data[2];
    data[0] = (value >> 8);
    data[1] = (value & 0xFF);
    
    cs_select(PIN_CS);
    spi_write_blocking(SPI_PORT, data, 2);
    cs_deselect(PIN_CS);
}