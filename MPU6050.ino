#include <Wire.h>
#include <MPU6050.h>
#include <math.h>

MPU6050 mpu;

// Calibration values for the MPU6050 sensor
float ax_offset, ay_offset, az_offset, gx_offset, gy_offset, gz_offset;

// Roll, pitch, and yaw angles
float roll, pitch, yaw;

void setup() {
  Serial.begin(9600);
  Wire.begin();
  mpu.initialize();
  
  // Calibrate the MPU6050 sensor
  calibrateMPU6050();
}

void loop() {
  //calibrateMPU6050();
  // Read accelerometer and gyroscope data
  int16_t ax_raw, ay_raw, az_raw, gx_raw, gy_raw, gz_raw;
  mpu.getMotion6(&ax_raw, &ay_raw, &az_raw, &gx_raw, &gy_raw, &gz_raw);
  
  // Apply calibration offsets to the raw data
  float ax = (ax_raw - ax_offset) / 16384.0;
  float ay = (ay_raw - ay_offset) / 16384.0;
  float az = (az_raw - az_offset) / 16384.0;
  float gx = (gx_raw - gx_offset) / 131.0;
  float gy = (gy_raw - gy_offset) / 131.0;
  float gz = (gz_raw - gz_offset) / 131.0;
//  Serial.print("gz_offset : ");
//  Serial.println(gz_offset);
//  Serial.print("gz_raw : ");
//  Serial.println(gz_raw);
  // Calculate roll, pitch, and yaw angles
  roll = atan2(ay, az) * 180.0 / M_PI;
  pitch = atan2(-ax, sqrt(ay * ay + az * az)) * 180.0 / M_PI;
//  Serial.print("gz : ");
//  Serial.println(gz);
  yaw = yaw + (gz * 0.01);  // Integration of the gyroscope data over time (sampling interval is 10ms)

  // Print the angles to the serial monitor
  //Serial.print("roll: ");
  //Serial.print(roll);
  //Serial.print(" pitch: ");
  //Serial.print(pitch);
  Serial.print(" yaw: ");
  Serial.println(yaw);

  delay(10); // Sampling interval of 10ms
}

void calibrateMPU6050() {
  Serial.println("Calibrating MPU6050...");
  delay(10);
  int num_samples = 200;
  for (int i = 0; i < num_samples; i++) {
    // Read accelerometer and gyroscope data
    int16_t ax_raw, ay_raw, az_raw, gx_raw, gy_raw, gz_raw;
    mpu.getMotion6(&ax_raw, &ay_raw, &az_raw, &gx_raw, &gy_raw, &gz_raw);
    
    // Accumulate the offset values
    ax_offset += ax_raw;
    ay_offset += ay_raw;
    az_offset += az_raw;
    gx_offset += gx_raw;
    gy_offset += gy_raw;
    gz_offset += gz_raw;
    
    delay(2); // Sampling interval of 2ms
  }
  // Calculate the average offset values
  ax_offset /= num_samples;
  ay_offset /= num_samples;
  az_offset /= num_samples;
  gx_offset /= num_samples;
  gy_offset /= num_samples;
  gz_offset /= num_samples;
  Serial.println("Calibration complete.");
}
