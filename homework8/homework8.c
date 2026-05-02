#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/spi.h"
#include <math.h>

#define SPI_PORT spi0
#define PIN_MISO 16
#define PIN_CS_DAC 17
#define PIN_SCK  18
#define PIN_MOSI 19
#define PIN_CS_RAM 20  

#define NUM_SAMPLES 1000

#define RAM_WRITE 0x02
#define RAM_READ  0x03
#define RAM_SET_MODE 0x01
#define RAM_SEQ_MODE 0x40

static inline void cs_select(uint cs_pin);
static inline void cs_deselect(uint cs_pin);
void dac_write(uint8_t channel, float voltage);
void spi_ram_init();
void spi_ram_write(uint16_t address, uint8_t *data, size_t len);
void spi_ram_read(uint16_t address, uint8_t *data, size_t len);
void fill_ram_sine();
void update_dac_from_ram(uint16_t address);

int main() {
    stdio_init_all();

    spi_init(SPI_PORT, 1000*1000);
    gpio_set_function(PIN_MISO, GPIO_FUNC_SPI);
    gpio_set_function(PIN_SCK,  GPIO_FUNC_SPI);
    gpio_set_function(PIN_MOSI, GPIO_FUNC_SPI);

    gpio_init(PIN_CS_DAC);
    gpio_set_dir(PIN_CS_DAC, GPIO_OUT);
    gpio_put(PIN_CS_DAC, 1);

    gpio_init(PIN_CS_RAM);
    gpio_set_dir(PIN_CS_RAM, GPIO_OUT);
    gpio_put(PIN_CS_RAM, 1);

    spi_ram_init();
    fill_ram_sine();

    uint16_t addr = 0;
    while (true) {
        update_dac_from_ram(addr);
        addr += 2;
        if (addr >= NUM_SAMPLES * 2){ 
            addr = 0;
        }
        sleep_ms(1);
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

    cs_select(PIN_CS_DAC);
    spi_write_blocking(SPI_PORT, data, 2);
    cs_deselect(PIN_CS_DAC);
}


void spi_ram_init() {
    uint8_t cmd[2] = {RAM_SET_MODE, RAM_SEQ_MODE};
    cs_select(PIN_CS_RAM);
    spi_write_blocking(SPI_PORT, cmd, 2);
    cs_deselect(PIN_CS_RAM);
}

void spi_ram_write(uint16_t address, uint8_t *data, size_t len) {
    uint8_t header[3] = {
        RAM_WRITE,
        (address >> 8) & 0xFF,
        (address)      & 0xFF
    };
    cs_select(PIN_CS_RAM);
    spi_write_blocking(SPI_PORT, header, 3);
    spi_write_blocking(SPI_PORT, data, len);
    cs_deselect(PIN_CS_RAM);
}

void spi_ram_read(uint16_t address, uint8_t *data, size_t len) {
    uint8_t tx[3 + len];
    uint8_t rx[3 + len];

    tx[0] = RAM_READ;
    tx[1] = (address >> 8) & 0xFF;
    tx[2] = (address)      & 0xFF;
    for (size_t i = 3; i < 3 + len; i++) 
    {
        tx[i] = 0x00;
    }

    cs_select(PIN_CS_RAM);
    spi_write_read_blocking(SPI_PORT, tx, rx, 3 + len);
    cs_deselect(PIN_CS_RAM);

    for (size_t i = 0; i < len; i++) {
        data[i] = rx[3 + i];
    }
}


void fill_ram_sine() {
    for (int i = 0; i < NUM_SAMPLES; i++) {
        float voltage = (sinf(2 * M_PI * i / NUM_SAMPLES) + 1) / 2 * 3.3;

        uint16_t value = (voltage / 3.3) * 1023;
        value = value << 2;
        value |= 0x3000;

        uint8_t data[2] = {
            (value >> 8) & 0xFF,
            (value)      & 0xFF
        };

        spi_ram_write(i * 2, data, 2);
    }
}


void update_dac_from_ram(uint16_t address) {
    uint8_t data[2];
    spi_ram_read(address, data, 2);

    cs_select(PIN_CS_DAC);
    spi_write_blocking(SPI_PORT, data, 2);
    cs_deselect(PIN_CS_DAC);
}