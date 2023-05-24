#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>

#define SERVICE_UUID        "4f14d355-e5bd-4fa0-afa1-783e51d862fb"
#define CHARACTERISTIC_UUID "4f14d355-e5bd-4fa0-afa1-783e51d862fb"

BLECharacteristic *pCharacteristic;
bool deviceConnected = false;
int counter = 0;

class MyServerCallbacks : public BLEServerCallbacks {
    void onConnect(BLEServer* pServer) {
      deviceConnected = true;
    };

    void onDisconnect(BLEServer* pServer) {
      deviceConnected = false;
    }
};

void setup() {
  Serial.begin(115200);
  Serial.println("Starting ESP32 BLE Server");

  BLEDevice::init("ESP32-BLE");
  String bleAddress = BLEDevice::getAddress().toString().c_str();
  Serial.print("ESP32 BLE Address: ");
  Serial.println(bleAddress);
  BLEServer *pServer = BLEDevice::createServer();
  pServer->setCallbacks(new MyServerCallbacks());

  BLEService *pService = pServer->createService(SERVICE_UUID);
  pCharacteristic = pService->createCharacteristic(
                      CHARACTERISTIC_UUID,
                      BLECharacteristic::PROPERTY_READ |
                      BLECharacteristic::PROPERTY_WRITE |
                      BLECharacteristic::PROPERTY_NOTIFY |
                      BLECharacteristic::PROPERTY_INDICATE
                    );
  pCharacteristic->addDescriptor(new BLE2902());

  pService->start();
  pServer->getAdvertising()->start();
  Serial.println("BLE service started. Waiting for a connection...");
}

void loop() {
  if (deviceConnected) {
    pCharacteristic->setValue(counter);
    pCharacteristic->notify();
    counter++;
    delay(1000);
  }
}
