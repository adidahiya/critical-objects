#include <Servo.h>

#define HUMAN_BEHAVIOR_DATA_PREFIX "humanBehaviorState:"
#define GOOD_STATE "good"

//set up gate control servo
Servo gateControl;
const int servoPin = 4;
const int position1 = 5;
const int position2 = 80;

void setup() {
    Serial.begin(9600);
    Serial.write("hello world");
    pinMode(LED_BUILTIN, OUTPUT);

    gateControl.attach(servoPin);
    gateControl.write(position1);

}

bool isFeeding = false;
unsigned long timerAmt = 0;
unsigned long openAmt = 500;


String formerData = "humanBehaviorState:neutral";
String data = "humanBehaviorState:neutral";

void loop() {
    if (Serial.available() > 0) {
        data = Serial.readStringUntil('\n');

        if (data == "reward") {
            //open the gate and 'start' the timer
            gateControl.write(position2);
            timerAmt = millis();
        } else if (data == "punishment") {
            // make sure the gate closes immediately if state switches to "bad"
            gateControl.write(position1);
            timerAmt = 0;
        }
    }

     // once the gate has been open long enough, then shut it again
    if (millis() - timerAmt >= openAmt){
        gateControl.write(position1);
        timerAmt = 0;
    }
}
