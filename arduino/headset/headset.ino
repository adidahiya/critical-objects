#define WEBSITE_DATA_PREFIX "website:"

void setup() {
    Serial.begin(9600);
    Serial.write("hello world");
    pinMode(LED_BUILTIN, OUTPUT);
}

bool isBlinking = false;

void loop() {
    if (Serial.available() > 0) {
        String data = Serial.readStringUntil('\n');

        if (data.startsWith(WEBSITE_DATA_PREFIX)) {
            // "website:https://github.com"
            // trim off prefix by indexing into char array
            char* websiteName = &data[strlen(WEBSITE_DATA_PREFIX)];
            isBlinking = true;
            Serial.println("hello browser");
        } else {
            isBlinking = false;
        }
    }

    if (isBlinking) {
        digitalWrite(LED_BUILTIN, HIGH);
        delay(500);
        digitalWrite(LED_BUILTIN, LOW);
        delay(500);
    } else {
        digitalWrite(LED_BUILTIN, LOW);
    }
}
