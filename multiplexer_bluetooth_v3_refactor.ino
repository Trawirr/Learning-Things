#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_ADXL345_U.h>
#include "MPU6050.h"
#include <SoftwareSerial.h>

#define TCA9548A_ADDR 0x70
#define NUM_ACCELEROMETERS 6

SoftwareSerial btSerial(10, 11);

Adafruit_ADXL345_Unified accels[NUM_ACCELEROMETERS] = {
  Adafruit_ADXL345_Unified(12345),
  Adafruit_ADXL345_Unified(12346),
  Adafruit_ADXL345_Unified(12347),
  Adafruit_ADXL345_Unified(12348),
  Adafruit_ADXL345_Unified(12349),
  Adafruit_ADXL345_Unified(12350) 
};

int accels_channels[NUM_ACCELEROMETERS] = {
  1, // srodek/baza
  5, // kciuk
  7, // wskazujacy
  6, // srodkowy
  3, // serdeczny
  2  // maly

};

int prevX[NUM_ACCELEROMETERS] = {0};
int prevY[NUM_ACCELEROMETERS] = {0};
int prevZ[NUM_ACCELEROMETERS] = {0};

int baseDiffX[NUM_ACCELEROMETERS] = {0};
int baseDiffY[NUM_ACCELEROMETERS] = {0};
int baseDiffZ[NUM_ACCELEROMETERS] = {0};

// int previousX[NUM_ACCELEROMETERS] = {0};
// int previousY[NUM_ACCELEROMETERS] = {0};
// int previousZ[NUM_ACCELEROMETERS] = {0};

int baseX, baseY, baseZ, nowX, nowY, nowZ, realNowX, realNowY, realNowZ;

void selectTCAChannel(uint8_t channel) {
  if (channel > 7) return;
  Wire.beginTransmission(TCA9548A_ADDR);
  Wire.write(1 << channel);
  Wire.endTransmission();
}

bool initializeAccelerometer(uint8_t channel, Adafruit_ADXL345_Unified &accel) {
  selectTCAChannel(channel);
  if (!accel.begin()) {
    Serial.print("No ADXL345 detected on channel ");
    Serial.println(channel);
    return false;
  }
  accel.setRange(ADXL345_RANGE_16_G);
  Serial.print("ADXL345 on channel ");
  Serial.print(channel);
  Serial.println(" initialized!");
  return true;
}

void setup() {
  Serial.begin(9600);
  btSerial.begin(9600);
  Wire.begin();

  for (int i=0; i<6; i++){
    selectTCAChannel(accels_channels[i]);
    if (!accels[i].begin()) {
        Serial.print(F("Failed to find acc chip "));
        Serial.println(accels_channels[i]);
        while (1) {
          delay(10);
        }
    }
    Serial.println(accels_channels[i]);
  }
}

void normalizeVector(float v[3]) {
  float magnitude = sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2]);
  if (magnitude > 0) {
    v[0] /= magnitude;
    v[1] /= magnitude;
    v[2] /= magnitude;
  }
}

float calculateAngle(float v1, float v2, float v3) {
  float v_base[3] = {realNowX, realNowY, realNowZ};
  float v_finger[3] = {v1, v2, v3};
  normalizeVector(v_base);
  normalizeVector(v_finger);
  float dotProduct = v_base[0] * v_finger[0] + v_base[1] * v_finger[1] + v_base[2] * v_finger[2];
  // Serial.print("dot product: ");
  // Serial.print(dotProduct);
  // Serial.print("    ;");
  float angleRad = acos(dotProduct);
  return angleRad * 180.0 / PI;
}

float distance(float arr[]){
  float s = 0;
  for(int i=0; i<3; i++){
    s = s + arr[i] * arr[i];
  }
  return sqrt(s);
}

void readADXL345Data(uint8_t channel, Adafruit_ADXL345_Unified &accel, uint8_t index) {
  selectTCAChannel(channel);
  
  sensors_event_t event;
  accel.getEvent(&event);

  float mappedX, mappedY, mappedZ, realX, realY, realZ, diffX, diffY, diffZ;

  // główne odczyty dla wszystkich czujników
  realX = event.acceleration.x;
  realY = event.acceleration.y;
  realZ = event.acceleration.z;

  // BAZOWY
  if (index == 0){
    // poprawa przez obrócenie
    realY = -realY;
    realZ = -realZ;

    mappedX = (int)map(realX, -12, 12, 0, 255);
    mappedY = (int)map(realY, -12, 12, 0, 255);
    mappedZ = (int)map(realZ, -12, 12, 0, 255);

    // base X, base Y base Z
    btSerial.print(realX);
    btSerial.print(";");
    btSerial.print(realY);
    btSerial.print(";");
    btSerial.print(realZ);
    btSerial.print(";");

    // base v X, base v Y, base v Z
    btSerial.print(event.acceleration.v[0]);
    btSerial.print(";");
    btSerial.print(event.acceleration.v[1]);
    btSerial.print(";");
    btSerial.print(event.acceleration.v[2]);
    btSerial.print(";");

    realNowX = realX;
    realNowY = realY;
    realNowZ = realZ;

    nowX = mappedX;
    nowY = mappedY;
    nowZ = mappedZ;

    btSerial.print(calculateAngle(realX, realY, realZ));
    btSerial.print(";");
    btSerial.print(distance(event.acceleration.v));
    btSerial.print(";");
  }
  // PALCE
  else {
    mappedX = (int)map(realX, -12, 12, 0, 255);
    mappedY = (int)map(realY, -12, 12, 0, 255);
    mappedZ = (int)map(realZ, -12, 12, 0, 255);

    btSerial.print(calculateAngle(realX, realY, realZ));
    btSerial.print(";");
    btSerial.print(distance(event.acceleration.v));
    btSerial.print(";");
  }
}

void loop() {
  // Read data from each accelerometer and print differences
  for (uint8_t i = 0; i < NUM_ACCELEROMETERS; i++) {
    readADXL345Data(accels_channels[i], accels[i], i);
    if (i != NUM_ACCELEROMETERS - 1) btSerial.print(";");
  }
  
  btSerial.println();
  
  delay(50);
}