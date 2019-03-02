#define HUMAN_BEHAVIOR_DATA_PREFIX "humanBehaviorState:"
#define GOOD_STATE "good"

void setup() {
    Serial.begin(9600);
    Serial.write("hello world");
    pinMode(LED_BUILTIN, OUTPUT);
}

bool isBlinking = false;

void loop() {
    if (Serial.available() > 0) {
        String data = Serial.readStringUntil('\n');

        if (data == "humanBehaviorState:good") {
            isBlinking = false;
        } else if (data == "humanBehaviorState:bad") {
            isBlinking = true;
        }

        // if (data.startsWith(HUMAN_BEHAVIOR_DATA_PREFIX)) {
        //     // "humanBehaviorState:good"
        //     // trim off prefix by indexing into char array
        //     char* state = &data[strlen(HUMAN_BEHAVIOR_DATA_PREFIX)];
        //     Serial.println("hello browser");
        // }
    }

    if (isBlinking) {
        digitalWrite(LED_BUILTIN, HIGH);
        delay(100);
        digitalWrite(LED_BUILTIN, LOW);
        delay(100);
    } else {
        digitalWrite(LED_BUILTIN, LOW);
    }
}
