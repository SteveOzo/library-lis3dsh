"""This program handles the communication over I2C
between a Raspberry Pi and LIS3DSH .
Made by: SteveOzo
Based on : MrTijn/Tijndagamer
All Credits to the original author.
"""

import smbus

class lis3dsh:
    # Global Variables
    GRAVITIY_MS2 = 9.80665
    address = None
    bus = smbus.SMBus(1)

    ACCEL_SCALE_MODIFIER_2G = 16384.0
    ACCEL_SCALE_MODIFIER_4G = 8192.0
    ACCEL_SCALE_MODIFIER_6G = 5461.33333
    ACCEL_SCALE_MODIFIER_8G = 4096.0
    ACCEL_SCALE_MODIFIER_16G = 2048.0

    ACCEL_RANGE_2G = 0x00
    ACCEL_RANGE_4G = 0x08
    ACCEL_RANGE_6G = 0x10
    ACCEL_RANGE_8G = 0x18
    ACCEL_RANGE_16G = 0x20

    #Registers

    ACCEL_XOUT0 = 0x28
    ACCEL_YOUT0 = 0x2A
    ACCEL_ZOUT0 = 0x2C

    CTRL_REG4 = 0x20 #This register configure the sampling rate, refer to the datasheet
    CTRL_REG5 = 0x24 #This register configure the sensitivity and the bandwith filter

    def __init__(self, address):
        self.address = address
        # Wake up the lis3dsh and configure for sampling at 3.125 Hz
        self.bus.write_byte_data(self.address, self.CTRL_REG4, 0x1F)

    def read_i2c_word(self, register):
        """Read two i2c registers and combine them.

        register -- the first register to read from.
        Returns the combined read results.
        """
        # Read the data from the registers
        low = self.bus.read_byte_data(self.address, register)
        high = self.bus.read_byte_data(self.address, register + 1)

        value = (high << 8) + low

        if (value >= 0x8000):
            return -((65535 - value) + 1)
        else:
            return value

    def write_register(self, register, value):
        #uses this function to change the value of whatever register
        self.bus.write_byte_data(self.address, register, value)


    def read_accel_range(self, raw = False):
        """Reads the range the accelerometer is set to.

        If raw is True, it will return the raw value from the ACCEL_CONFIG
        register
        If raw is False, it will return an integer: -1, 2, 4, 8 or 16. When it
        returns -1 something went wrong.
        """
        raw_data = self.bus.read_byte_data(self.address, self.CTRL_REG5)

        if raw is True:
            return raw_data
        elif raw is False:
            if raw_data == self.ACCEL_RANGE_2G:
                return 2
            elif raw_data == self.ACCEL_RANGE_4G:
                return 4
            elif raw_data == self.ACCEL_RANGE_6G:
                return 6
            elif raw_data == self.ACCEL_RANGE_8G:
                return 8
            elif raw_data == self.ACCEL_RANGE_16G:
                return 16
            else:
                return -1

    def get_accel_data(self, g = False):
        """Gets and returns the X, Y and Z values from the accelerometer.

        If g is True, it will return the data in g
        If g is False, it will return the data in m/s^2
        Returns a dictionary with the measurement results.
        """
        x = self.read_i2c_word(self.ACCEL_XOUT0)
        y = self.read_i2c_word(self.ACCEL_YOUT0)
        z = self.read_i2c_word(self.ACCEL_ZOUT0)

        accel_scale_modifier = None
        accel_range = self.read_accel_range(True)

        if accel_range == self.ACCEL_RANGE_2G:
            accel_scale_modifier = self.ACCEL_SCALE_MODIFIER_2G
        elif accel_range == self.ACCEL_RANGE_4G:
            accel_scale_modifier = self.ACCEL_SCALE_MODIFIER_4G
        elif accel_range == self.ACCEL_RANGE_6G:
            accel_scale_modifier = self.ACCEL_SCALE_MODIFIER_6G
        elif accel_range == self.ACCEL_RANGE_8G:
            accel_scale_modifier = self.ACCEL_SCALE_MODIFIER_8G
        elif accel_range == self.ACCEL_RANGE_16G:
            accel_scale_modifier = self.ACCEL_SCALE_MODIFIER_16G
        else:
            print("Unkown range - accel_scale_modifier set to self.ACCEL_SCALE_MODIFIER_2G")
            accel_scale_modifier = self.ACCEL_SCALE_MODIFIER_2G

        print accel_scale_modifier

        x = x / accel_scale_modifier
        y = y / accel_scale_modifier
        z = z / accel_scale_modifier

        if g is True:
            return {'x': x, 'y': y, 'z': z}
        elif g is False:
            x = x * self.GRAVITIY_MS2
            y = y * self.GRAVITIY_MS2
            z = z * self.GRAVITIY_MS2
            return {'x': x, 'y': y, 'z': z}



if __name__ == "__main__":
    lis = lis3dsh(0x1D)
    while True:
        accel_data = lis.get_accel_data()
        print ("Valores")
        print("X: "+str(accel_data['x']))
        print("Y: "+str(accel_data['y']))
        print("Z: "+str(accel_data['z']))
