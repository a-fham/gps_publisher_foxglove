#include <SoftwareSerial.h>
#include <TinyGPS++.h>

// Define the RX and TX pins for the NEO-6M module
SoftwareSerial gpsSerial(10, 11);  // RX, TX

// Create a TinyGPS++ object
TinyGPSPlus gps;

void setup() {
  // Start serial communication with a baud rate of 9600
  Serial.begin(9600);
  
  // Start serial communication with the NEO-6M module
  gpsSerial.begin(9600);
}

void loop() {
  // Read data from the NEO-6M module
  while (gpsSerial.available() > 0) {
    if (gps.encode(gpsSerial.read())) {
      // If new data is parsed successfully, display information
      displayGPSInfo();
    }
  }
}

void displayGPSInfo() {
  // Check if there is valid GPS data
  if (gps.location.isValid()) {
    // Print latitude and longitude
    Serial.print("Latitude: ");
    Serial.println(gps.location.lat(), 6);
    Serial.print("Longitude: ");
    Serial.println(gps.location.lng(), 6);

    // Print altitude
    Serial.print("Altitude: ");
    Serial.println(gps.altitude.meters());

    // Print speed
    Serial.print("Speed: ");
    Serial.println(gps.speed.kmph());

    // Print date and time
    Serial.print("Date: ");
    Serial.print(gps.date.year());
    Serial.print("-");
    Serial.print(gps.date.month());
    Serial.print("-");
    Serial.print(gps.date.day());
    Serial.print(" Time: ");
    Serial.print(gps.time.hour());
    Serial.print(":");
    Serial.print(gps.time.minute());
    Serial.print(":");
    Serial.println(gps.time.second());
    
    // Print empty line for better readability
    Serial.println();
  } else {
    // If no valid data is available yet, print "Waiting for GPS fix..."
    Serial.println("Waiting for GPS fix...");
  }
}
