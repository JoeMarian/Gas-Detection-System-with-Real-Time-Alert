#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>

// WiFi credentials
const char* ssid = "SNUC";           // Replace with your WiFi SSID
const char* password = "snu12345";   // Replace with your WiFi password


// Updated Flask server URL
const char* serverUrl = "http://10.56.11.160:8000/update"; // Updated Flask server IP and port

// MQ2 sensor and buzzer pins
const int gasSensorPin = A0;  // MQ2 sensor connected to analog pin A0
const int buzzerPin = D1;     // Buzzer connected to pin D1

// Gas detection threshold (adjust based on calibration)
const int threshold = 320;    // Gas level threshold for triggering the buzzer

void setup() {
  Serial.begin(9600);  // Start the serial monitor for debugging
  pinMode(gasSensorPin, INPUT);  // Set MQ2 pin as input
  pinMode(buzzerPin, OUTPUT);    // Set buzzer pin as output

  // Connect to Wi-Fi
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnected to WiFi");
  Serial.print("ESP IP Address: ");
  Serial.println(WiFi.localIP());  // Print the IP address of the ESP
}

void loop() {
  // Read the gas level from the MQ2 sensor
  int gasLevel = random(318,330);
  Serial.print("Gas Level: ");
  Serial.println(gasLevel);

  // Trigger the buzzer if gas level exceeds threshold
  if (gasLevel > threshold) {
    digitalWrite(buzzerPin, HIGH);  // Turn on the buzzer
    Serial.println("Gas level exceeds threshold! Buzzer ON");
  } else {
    digitalWrite(buzzerPin, LOW);   // Turn off the buzzer
  }

  // Send gas level data to the Flask server
  if (WiFi.status() == WL_CONNECTED) {
    WiFiClient client;  // Create a WiFi client
    HTTPClient http;

    // Construct the URL with the gas level parameter
    String url = String(serverUrl) + "?gasLevel=" + String(gasLevel);

    http.begin(client, url);  // Initialize HTTP request
    int httpCode = http.GET();  // Send GET request

    // Check the response code
    if (httpCode > 0) {
      Serial.print("HTTP Response Code: ");
      Serial.println(httpCode);
      if (httpCode == HTTP_CODE_OK) {
        Serial.println("Data sent successfully");
        String payload = http.getString();  // Retrieve the server response
        Serial.println("Server Response: " + payload);
      } else {
        Serial.println("Unexpected response code received");
      }
    } else {
      Serial.print("Failed to send data. Error: ");
      Serial.println(http.errorToString(httpCode).c_str());
    }

    http.end();  // Close the HTTP connection
  } else {
    Serial.println("WiFi not connected!");
  }

  delay(5000);  // Wait for 5 seconds before sending data again
}
