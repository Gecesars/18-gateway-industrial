#ifndef EDGE18_STM32H563_BOARD_PINS_H
#define EDGE18_STM32H563_BOARD_PINS_H

/*
 * Single firmware-side source for the Rev. A signal assignment. The net and
 * physical pin are generated in docs/13-pinout-stm32h563-rev-a.md from KiCad;
 * changing this map requires changing and revalidating the native CAD.
 */
#define EDGE18_BOARD_SIGNAL_MAP(X) \
    X(DI1,              E,  5, "TIM/GPIO input") \
    X(DI2,              E,  6, "TIM/GPIO input") \
    X(RTC_INT,          F,  0, "EXTI input") \
    X(VIN_MON,          C,  0, "ADC input") \
    X(ETH_MDC,          C,  1, "ETH MDC") \
    X(MON_5V,           C,  2, "ADC input") \
    X(MON_3V3,          C,  3, "ADC input") \
    X(ETH_REF_CLK,      A,  1, "ETH RMII") \
    X(ETH_MDIO,         A,  2, "ETH MDIO") \
    X(ADC_CS,           A,  4, "GPIO output") \
    X(ADC_SCK,          A,  5, "SPI1 SCK") \
    X(ADC_MISO,         A,  6, "SPI1 MISO") \
    X(ETH_CRS_DV,       A,  7, "ETH RMII") \
    X(ETH_RXD0,         C,  4, "ETH RMII") \
    X(ETH_RXD1,         C,  5, "ETH RMII") \
    X(ADC_RESET,        B,  0, "GPIO output") \
    X(LED_RUN,          G,  0, "GPIO output") \
    X(LED_FAULT,        G,  1, "GPIO output") \
    X(WIFI_UART_RX,     E,  7, "UART7 RX") \
    X(WIFI_UART_TX,     E,  8, "UART7 TX") \
    X(DI3,              E,  9, "TIM/GPIO input") \
    X(WIFI_EN,          E, 10, "GPIO output") \
    X(DI4,              E, 11, "TIM/GPIO input") \
    X(WIFI_BOOT,        E, 13, "GPIO output") \
    X(EXP_UART_TX,      B, 10, "USART3 TX / expansion") \
    X(FLASH_CS,         B, 12, "GPIO output") \
    X(FLASH_SCK,        B, 13, "SPI2 SCK") \
    X(FLASH_MISO,       B, 14, "SPI2 MISO") \
    X(FLASH_MOSI,       B, 15, "SPI2 MOSI") \
    X(RS485B_TX,        D,  8, "USART3 TX") \
    X(RS485B_RX,        D,  9, "USART3 RX") \
    X(RS485B_DIR,       D, 12, "USART3 DE") \
    X(PGOOD_3V3,        G,  2, "EXTI input") \
    X(PGOOD_5V,         G,  3, "EXTI input") \
    X(SD_D0,            C,  8, "SDMMC1 D0") \
    X(SD_D1,            C,  9, "SDMMC1 D1") \
    X(USB_VBUS_SENSE,   A,  9, "USB FS VBUS") \
    X(USB_DM,           A, 11, "USB FS DM") \
    X(USB_DP,           A, 12, "USB FS DP") \
    X(SWDIO,            A, 13, "SWDIO") \
    X(SWCLK,            A, 14, "SWCLK") \
    X(SD_D2,            C, 10, "SDMMC1 D2") \
    X(SD_D3,            C, 11, "SDMMC1 D3") \
    X(SD_CLK,           C, 12, "SDMMC1 CK") \
    X(CAN_RX,           D,  0, "FDCAN1 RX") \
    X(CAN_TX,           D,  1, "FDCAN1 TX") \
    X(SD_CMD,           D,  2, "SDMMC1 CMD") \
    X(CAN_STB,          D,  3, "GPIO output") \
    X(RS485A_DIR,       D,  4, "USART2 DE") \
    X(RS485A_TX,        D,  5, "USART2 TX") \
    X(RS485A_RX,        D,  6, "USART2 RX") \
    X(EXP_GPIO,         D,  7, "GPIO expansion") \
    X(ETH_TX_EN,        G, 11, "ETH RMII") \
    X(ETH_TXD0,         G, 13, "ETH RMII") \
    X(ETH_TXD1,         G, 14, "ETH RMII") \
    X(SWO,              B,  3, "SWO") \
    X(ADC_MOSI,         B,  5, "SPI1 MOSI") \
    X(I2C_SCL,          B,  8, "I2C1 SCL") \
    X(I2C_SDA,          B,  9, "I2C1 SDA")

#define EDGE18_HSE_HZ 25000000UL
#define EDGE18_LSE_HZ 32768UL
#define EDGE18_SYSTEM_CLOCK_HZ 250000000UL
#define EDGE18_WATCHDOG_WINDOW_MS 2000UL

#endif
