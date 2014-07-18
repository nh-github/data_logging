/*************************************************** 
 * Environmental Data logging
 * 
 * 
 * Connections for I2C devices:
 * GND (green): GND
 * VDD (red): 3.3V
 * SCL (white): A5 w/ inline 330 ohm resistor
 * SDA (yellow): A4 w/ inline 330 ohm resistor
 ****************************************************/

#include <Wire.h> 
#include <Adafruit_L3GD20.h>
#include <Adafruit_LSM303.h>
#include "HTU21D.h"
#include "TSL2561.h"
#include <Adafruit_L3GD20.h>
#include <Adafruit_LSM303.h>


// Light sensor, address can be 
// TSL2561_ADDR_LOW (0x29), ..._FLOAT (0x39), or ..._HIGH (0x49)
TSL2561 tsl(TSL2561_ADDR_FLOAT); 

// Humidity sensor
HTU21D htu;

// L3GD20 tri-axis gyroscope
Adafruit_L3GD20 gyro;

// LSM303 tri-axis accelerometer/magnetometer
Adafruit_LSM303 lsm;

void data_output();

void setup() 
{
  Serial.begin(115200);
  int counter = 0;
  Serial.print("Setup: Light sensor..");
  if (tsl.begin()) {
    Serial.print(".ok\n");
  } 
  else {
    Serial.print(".PROBLEM!/n");
  }
  Serial.print("Setup: Humidity sensor..");
  if (htu.begin()) {
    Serial.print(".ok\n");
  } 
  else {
    Serial.print(".PROBLEM!/n");
  }
  Serial.print("Setup: Gyroscope..");
  if (gyro.begin(gyro.L3DS20_RANGE_250DPS)) {
    Serial.print(".ok\n");
  } 
  else {
    Serial.print(".PROBLEM!/n");
  }
  Serial.print("Setup: Accel/Mag..");
  if (lsm.begin()) {
    Serial.print(".ok\n");
  } 
  else {
    Serial.print(".PROBLEM!/n");
  }

  delay(200); 

}
void loop() 
{
  tsl.setGain(TSL2561_GAIN_0X);
  tsl.setTiming(TSL2561_INTEGRATIONTIME_13MS);  //opt: 101, 402
  Serial.print(htu.readTemperature());
//  Serial.print(tsl.getLuminosity(TSL2561_VISIBLE));
//  Serial.print(",");
//  Serial.print(tsl.getLuminosity(TSL2561_INFRARED));
//  Serial.print(",");
//  Serial.print(tsl.getLuminosity(TSL2561_FULLSPECTRUM));
  // also available: TSL2561_FULLSPECTRUM, TSL2561_INFRARED

  Serial.print("\n");
  delay(100); 
}

void send_data_frame(){
  String label = "measure";
  String units = "units";
  float value = -1;
  float factor = 1;

  //*****
  // START
  Serial.print("#MFB\n");  // mark frame start

  //*****
  // LIGHT / TSL2561
  label = "visible light";
  units = "counts";
  value = tsl.getLuminosity(TSL2561_VISIBLE);
  // also available: TSL2561_FULLSPECTRUM, TSL2561_INFRARED

  Serial.print(label + ": ");
  Serial.print(value);
  Serial.print(", ");
  Serial.print(factor);
  Serial.print(" (" + units + ")\n");
  //*****


  // Time
  label = "time";
  units = "milliseconds";
  value = millis();

  Serial.print(label + ": ");
  Serial.print(value);
  Serial.print(", ");
  Serial.print(factor);
  Serial.print(" (" + units + ")\n");


  //*****
  // Humidity / HTU21D
  label = "humidity";
  units = "percent";
  value = htu.readHumidity();
  factor = 1;

  Serial.print(label + ": ");
  Serial.print(value );
  Serial.print(", ");
  Serial.print(factor);
  Serial.print(" (" + units + ")\n");

  //*****
  // Temperature / HTU21D
  label = "temperature";
  units = "degrees C";
  value = htu.readTemperature();
  factor = 1;

  Serial.print(label + ": ");
  Serial.print(value );
  Serial.print(", ");
  Serial.print(factor);
  Serial.print(" (" + units + ")\n");


  //*****
  // Rotation / L3GD20
  label = "rotation";
  units = "degree per second";
  value = -1;
  factor = 1;
  gyro.read();  // update data

  Serial.print(label + " X" + ": ");
  Serial.print(gyro.data.x);
  Serial.print(", ");
  Serial.print(factor);
  Serial.print(" (" + units + ")\n");

  Serial.print(label + " Y" + ": ");
  Serial.print(gyro.data.y);
  Serial.print(", ");
  Serial.print(factor);
  Serial.print(" (" + units + ")\n");

  Serial.print(label + " Z" + ": ");
  Serial.print(gyro.data.z);
  Serial.print(", ");
  Serial.print(factor);
  Serial.print(" (" + units + ")\n");


  //*****
  // Acceleration / LSM303
  label = "acceleration";
  units = "m/s";
  value = -1;  // lsm.();
  factor = 1;
  lsm.read();  // gather an update

  Serial.print(label + " X" + ": ");
  Serial.print(lsm.accelData.x);
  Serial.print(", ");
  Serial.print(factor);
  Serial.print(" (" + units + ")\n");

  Serial.print(label + " Y" + ": ");
  Serial.print(lsm.accelData.y);
  Serial.print(", ");
  Serial.print(factor);
  Serial.print(" (" + units + ")\n");

  Serial.print(label + " Z" + ": ");
  Serial.print(lsm.accelData.z);
  Serial.print(", ");
  Serial.print(factor);
  Serial.print(" (" + units + ")\n");


  //*****
  // Magnetometer / LSM303
  label = "magnetic field";
  units = "[?]";
  value = -1;  // lsm.();
  factor = 1;
  //lsm.read();  // use update from above (acceleration)

  Serial.print(label + " X" + ": ");
  Serial.print(lsm.magData.x);
  Serial.print(", ");
  Serial.print(factor);
  Serial.print(" (" + units + ")\n");

  Serial.print(label + " Y" + ": ");
  Serial.print(lsm.magData.y);
  Serial.print(", ");
  Serial.print(factor);
  Serial.print(" (" + units + ")\n");

  Serial.print(label + " Z" + ": ");
  Serial.print(lsm.magData.z);
  Serial.print(", ");
  Serial.print(factor);
  Serial.print(" (" + units + ")\n");

  //*****
  // STOP
  Serial.print("#MFE\n");  // mark frame stop

  delay(100); 
}


/* stub for future work: 
 *   read the sensor value(s) and 
 *    set gain/integration time appropriately
 */
void light_autogain(){
  // You can change the gain on the fly, to adapt to brighter/dimmer light situations
  //tsl.setGain(TSL2561_GAIN_0X);         // set no gain (for bright situtations)
  tsl.setGain(TSL2561_GAIN_16X);      // set 16x gain (for dim situations)

  // Changing the integration time gives you a longer time over which to sense light
  // longer timelines are slower, but are good in very low light situtations!
  tsl.setTiming(TSL2561_INTEGRATIONTIME_13MS);  // shortest integration time (bright light)
  //tsl.setTiming(TSL2561_INTEGRATIONTIME_101MS);  // medium integration time (medium light)
  //tsl.setTiming(TSL2561_INTEGRATIONTIME_402MS);  // longest integration time (dim light)
}

void light_get_lux(){
  // More advanced data read example. Read 32 bits with top 16 bits IR, bottom 16 bits full spectrum
  // That way you can do whatever math and comparisons you want!
  uint32_t lum = tsl.getFullLuminosity();
  uint16_t ir, full;
  ir = lum >> 16;
  full = lum & 0xFFFF;
  Serial.print("IR: "); 
  Serial.print(ir);   
  Serial.print("\t\t");
  Serial.print("Full: "); 
  Serial.print(full);   
  Serial.print("\t");
  Serial.print("Visible: "); 
  Serial.print(full - ir);   
  Serial.print("\t");

  Serial.print("Lux: "); 
  Serial.println(tsl.calculateLux(full, ir));
}


//********************************************
// OLD and busted

//#include <StandardCplusplus.h>
////#include <iostream>
////#include <serstream>
////usage (doesn't work): std::ohserialstream cout(Serial);
//#include <string>
//#include <vector>
//#include <iterator>


//// Data storage
//struct data_element {
//  std::string label;
//  std::string units;
//  uint32_t value;
//};
//std::vector<data_element> data_frame;

//void setup() 
//{
//  Serial.begin(115200);
//  cout << "Setup: Light sensor..";
//  if (tsl.begin()) {
//    cout << ".ok\n";
//  } 
//  else {
//    cout << ".PROBLEM!/n";
//  }
////  Serial.print("Setup: Light sensor..");
////  if (tsl.begin()) {
////    Serial.print(".ok\n");
////  } 
////  else {
////    Serial.print(".PROBLEM!/n");
////  }
//  delay(1000); 
//
//}
//void loop() 
//{
//  data_element el;
//  el.label = "visible light";
//  el.units = "counts";
//  ;
//  el.value = tsl.getLuminosity(TSL2561_VISIBLE);
//  // also available: TSL2561_FULLSPECTRUM, TSL2561_INFRARED
//  data_frame.push_back(el);
//  data_output(data_frame);
//  data_frame.clear();
//  delay(1000); 
//}

///* send data to computer via serial
// *
// */
//void data_output(std::vector<data_element> df){
//  data_element el = df[0];
//  Serial.print("#MFB\n");  // mark frame start
//  for (std::vector<data_element>::iterator iter = df.begin(); iter != df.end(); iter++)
//  {
//    Serial.print(iter->label.size());
//    //Serial.print("FOO");
//    //Serial.print(": ");
//    //Serial.print(iter->value);
//    //Serial.print(" ");
//    //Serial.print(iter->units);
//    //Serial.print("\n");
//  }
//  Serial.print("#MFE\n");  // mark frame stop
//
//  //  Serial.print(el.label);
//  //  Serial.print(": ");
//  //  Serial.print(el.value);
//  //  Serial.print(" ");
//  //  Serial.print(el.units);
//  //  Serial.print("\n");
//}





